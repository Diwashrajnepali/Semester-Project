from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Trip, Station, RouteStation, Booking
from .forms import SearchBusForm, PassengerForm
import uuid

def booking(request):
    stations = Station.objects.all()
    
    # Check if this is a Search request (GET with params)
    if 'source' in request.GET and 'destination' in request.GET and 'date' in request.GET:
        form = SearchBusForm(request.GET)
        if form.is_valid():
            source = form.cleaned_data['source']
            dest = form.cleaned_data['destination']
            date = form.cleaned_data['date']
            
            possible_trips = Trip.objects.filter(date=date, status='SCHEDULED')
            
            valid_trips = []
            for trip in possible_trips:
                try:
                    start_node = RouteStation.objects.get(route=trip.route, station=source)
                    end_node = RouteStation.objects.get(route=trip.route, station=dest)
                    
                    if start_node.order < end_node.order:
                        price = end_node.price_from_start - start_node.price_from_start
                        valid_trips.append({
                            'trip': trip,
                            'price': price,
                            'start_node': start_node,
                            'end_node': end_node
                        })
                except RouteStation.DoesNotExist:
                    continue
            
            return render(request, 'booking/bus_list.html', {
                'trips': valid_trips, 
                'source': source, 
                'dest': dest, 
                'date': date
            })
    else:
        form = SearchBusForm()

    return render(request, 'booking/booking.html', {'form': form, 'stations': stations})

def book_seat(request, trip_id, source_id, dest_id):
    trip = get_object_or_404(Trip, id=trip_id)
    source = get_object_or_404(Station, id=source_id)
    dest = get_object_or_404(Station, id=dest_id)
    
    # Re-calculate price to be safe
    start_node = RouteStation.objects.get(route=trip.route, station=source)
    end_node = RouteStation.objects.get(route=trip.route, station=dest)
    per_seat_price = end_node.price_from_start - start_node.price_from_start

    # Get booked seats
    # Logic: If booking status is CONFIRMED or PENDING (maybe hold for 10 mins?)
    existing_bookings = Booking.objects.filter(trip=trip, status__in=['CONFIRMED', 'PENDING'])
    booked_seats = []
    for b in existing_bookings:
        seats = b.seat_numbers.split(',')
        booked_seats.extend(seats)

    if request.method == "POST":
        form = PassengerForm(request.POST)
        if form.is_valid():
            # Create Booking (Pending Payment)
            selected_seats = form.cleaned_data['seat_numbers']
            seat_count = len(selected_seats.split(',')) if selected_seats else 0
            
            if seat_count == 0:
                messages.error(request, "Please select at least one seat.")
                return redirect(request.path)

            total_price = per_seat_price * seat_count
            
            booking = Booking.objects.create(
                user=request.user if request.user.is_authenticated else None,
                trip=trip,
                source_station=source,
                dest_station=dest,
                passenger_name=form.cleaned_data['passenger_name'],
                passenger_phone=form.cleaned_data['passenger_phone'],
                seat_numbers=selected_seats,
                total_price=total_price,
                status='PENDING'
            )
            
            # Redirect to payment page
            return redirect('payment_init', booking_id=booking.id)
            
    else:
        form = PassengerForm()

    return render(request, 'booking/seat_selection.html', {
        'trip': trip,
        'source': source,
        'dest': dest,
        'price': per_seat_price,
        'booked_seats': booked_seats,
        'total_seats': range(1, trip.bus.total_seats + 1),
        'form': form
    })

def payment_init(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Imports needed for signature generation
    import hmac
    import hashlib
    import base64
    import random

    # eSewa Test Config
    secret_key = '8gBm/:&EnhH.1/q'  # Default eSewa Test Secret Key
    product_code = 'EPAYTEST'

    # 1. Total Amount 
    # Force 2 decimal places as standard string "280.00"
    total_amount = f"{booking.total_price:.2f}"
    
    import time
    # 2. Transaction UUID
    # Format: {booking_id}-{unique_suffix} to ensure uniqueness for every attempt
    transaction_uuid = f"{booking.id}-{uuid.uuid4().hex[:8]}"
    
    # 3. Signature Generation
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    # DEBUG logic
    print(f"DEBUG ESEWA MESSAGE: {message}") 
    
    hash_obj = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
    signature = base64.b64encode(hash_obj.digest()).decode()
    
    print(f"DEBUG ESEWA SIGNATURE: {signature}")

    context = {
        'booking': booking,
        'amount': total_amount, 
        'tax_amount': 0,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code, 
        'product_service_charge': 0,
        'product_delivery_charge': 0,
        'success_url': request.build_absolute_uri('/booking/esewa-success/'),
        'failure_url': request.build_absolute_uri('/booking/esewa-failure/'),
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
    }
    return render(request, 'booking/payment.html', context)

def esewa_success(request):
    # eSewa returns params: ?oid=xxx&amt=xxx&refId=xxx (in v1) or encoded data in v2
    # For this project, we assume simple redirection for now, or check generic params.
    # Since we used booking ID as transaction_uuid, checking 'oid' or similar is key.
    
    # In V2, eSewa sends a GET request with 'data' which is base64 encoded JSON
    import base64
    import json
    
    data = request.GET.get('data')
    if data:
        try:
            decoded_data = base64.b64decode(data).decode('utf-8')
            json_data = json.loads(decoded_data)
            # json_data keys: transaction_code, status, total_amount, transaction_uuid, etc.
            
            if json_data.get('status') == 'COMPLETE':
                transaction_uuid = json_data.get('transaction_uuid')
                transaction_code = json_data.get('transaction_code')
                
                # Extract Booking ID from transaction_uuid (Format: {booking_id}-{unique_suffix})
                try:
                    if "-" in transaction_uuid:
                        booking_id = transaction_uuid.split("-")[0]
                        
                        booking = Booking.objects.get(id=booking_id)
                        booking.status = 'CONFIRMED'
                        booking.is_paid = True
                        booking.transaction_id = transaction_code
                        booking.save()
                        
                        messages.success(request, "Payment Successful! Your ticket is confirmed.")
                        return render(request, 'booking/success.html', {'booking': booking})
                    else:
                        raise ValueError("Invalid transaction UUID format")
                except (ValueError, Booking.DoesNotExist, IndexError):
                     messages.error(request, "Invalid booking record found.")
                     return redirect('booking')
        except Exception as e:
            print(e)
            pass
            
    # Fallback/Failure
    messages.error(request, "Payment verification failed.")
    return redirect('booking')

def esewa_failure(request):
    messages.error(request, "Payment failed. Please try again.")
    return redirect('booking')

def schedule(request):
    trips = Trip.objects.filter(status='SCHEDULED').order_by('date', 'departure_time')
    
    # Filter by date if provided
    date_query = request.GET.get('date')
    if date_query:
        trips = trips.filter(date=date_query)

    # Prepare trip data with source/dest inference for the 'Book' button
    trip_data = []
    for trip in trips:
        # Assuming Route has RouteStations ordered by 'order'
        stations = trip.route.stations.order_by('order')
        if stations.exists():
            start_station = stations.first().station
            end_station = stations.last().station
            
            # Calculate available seats
            existing_bookings = Booking.objects.filter(trip=trip, status__in=['CONFIRMED', 'PENDING'])
            booked_seat_count = 0
            for booking in existing_bookings:
                if booking.seat_numbers:
                    seats = booking.seat_numbers.split(',')
                    booked_seat_count += len(seats)
            
            available_seats = trip.bus.total_seats - booked_seat_count
            
            # Calculate base price (from first to last station)
            start_node = stations.first()
            end_node = stations.last()
            base_price = end_node.price_from_start - start_node.price_from_start
            
            trip_data.append({
                'trip': trip,
                'source_id': start_station.id,
                'dest_id': end_station.id,
                'source_name': start_station.name,
                'dest_name': end_station.name,
                'available_seats': available_seats,
                'base_price': base_price
            })

    return render(request, 'booking/schedule.html', {
        'trips': trip_data,
        'date_query': date_query
    })
