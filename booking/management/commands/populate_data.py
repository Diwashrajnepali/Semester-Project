from django.core.management.base import BaseCommand
from booking.models import Station, Route, RouteStation, Bus, Trip
from datetime import date, timedelta, time

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating data...')
        
        # 1. Create Stations
        stations_data = [
            {'name': 'Jadhibuti', 'code': 'JAD'},
            {'name': 'Koteshwor', 'code': 'KOT'},
            {'name': 'Banepa', 'code': 'BAN'},
            {'name': 'Mude', 'code': 'MUD'},
            {'name': 'Charikot', 'code': 'CHA'},
        ]
        
        stations = {}
        for s_data in stations_data:
            station, created = Station.objects.get_or_create(
                code=s_data['code'],
                defaults={'name': s_data['name']}
            )
            stations[s_data['code']] = station
            if created:
                self.stdout.write(f"Created station: {station.name}")

        # 2. Create Route: Jadhibuti -> Charikot
        # We need a route specifically involving Banepa -> Mude as tested
        route, created = Route.objects.get_or_create(
            name="Jadhibuti - Charikot",
            defaults={
                'source': stations['JAD'],
                'destination': stations['CHA'],
                'is_active': True
            }
        )
        
        # 3. Create Route Stops (Jadhibuti -> Banepa -> Mude -> Charikot)
        stops = [
            (stations['JAD'], 1, 0),
            (stations['BAN'], 2, 100), # 100 from start
            (stations['MUD'], 3, 350), # 350 from start (so Banepa->Mude is 250)
            (stations['CHA'], 4, 500), # 500 from start
        ]
        
        for station, order, price in stops:
            RouteStation.objects.get_or_create(
                route=route,
                station=station,
                defaults={
                    'order': order,
                    'price_from_start': price
                }
            )

        # 4. Create Buses
        bus1, _ = Bus.objects.get_or_create(
            plate_number="BA 3 KHA 1234",
            defaults={'bus_type': 'DELUXE', 'total_seats': 30, 'operator_name': 'Super Express'}
        )
        
        bus2, _ = Bus.objects.get_or_create(
            plate_number="BA 4 KHA 5678",
            defaults={'bus_type': 'AC', 'total_seats': 30, 'operator_name': 'Green Line'}
        )

        # 5. Create Trips (For Today, Tomorrow, and specifically 2026-01-07 for the test)
        dates_to_create = [
            date.today(),
            date.today() + timedelta(days=1),
            date(2026, 1, 7) # The date used in the test
        ]

        for d in dates_to_create:
            # Morning Bus
            Trip.objects.get_or_create(
                bus=bus1,
                route=route,
                date=d,
                defaults={
                    'departure_time': time(7, 0),
                    'arrival_time': time(13, 0),
                    'status': 'SCHEDULED'
                }
            )
            # Day Bus
            Trip.objects.get_or_create(
                bus=bus2,
                route=route,
                date=d,
                defaults={
                    'departure_time': time(9, 0),
                    'arrival_time': time(15, 0),
                    'status': 'SCHEDULED'
                }
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully populated test data.'))
