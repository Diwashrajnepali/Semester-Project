import os
import django
from datetime import date
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'YatraBus.settings')
django.setup()

from booking.models import Station, Route, RouteStation, Bus, Trip

def create_data():
    print("Creating Test Data...")
    
    # 1. Create Stations
    stations = [
        ('Jadhibuti', 'JAD'),
        ('Banepa', 'BAN'),
        ('Dolalghat', 'DOL'),
        ('Mude', 'MUD'),
        ('Charikot', 'CHR')
    ]
    
    station_objs = {}
    for name, code in stations:
        s, created = Station.objects.get_or_create(name=name, code=code)
        station_objs[name] = s
        print(f"Station: {name}")

    # 2. Create Route
    route, created = Route.objects.get_or_create(
        name="Jadhibuti - Charikot",
        source=station_objs['Jadhibuti'],
        destination=station_objs['Charikot']
    )
    print(f"Route: {route.name}")

    # 3. Add RouteStations (Order & Price)
    # Price from Start (Jadhibuti)
    full_route = [
        ('Jadhibuti', 1, 0),
        ('Banepa', 2, 100),
        ('Dolalghat', 3, 220),
        ('Mude', 4, 380),
        ('Charikot', 5, 550)
    ]

    for name, order, price in full_route:
        RouteStation.objects.get_or_create(
            route=route,
            station=station_objs[name],
            defaults={
                'order': order,
                'price_from_start': price
            }
        )
    print("Route Stations Added.")

    # 4. Create Bus
    bus, created = Bus.objects.get_or_create(
        plate_number="BA 4 KHA 1999",
        defaults={
            'bus_type': 'DELUXE',
            'total_seats': 30,
            'operator_name': 'Araniko Yatayat'
        }
    )
    print(f"Bus: {bus.plate_number}")

    # 5. Create Trip for TODAY
    trip, created = Trip.objects.get_or_create(
        bus=bus,
        route=route,
        date=date.today(),
        defaults={
            'departure_time': '07:30:00',
            'arrival_time': '13:00:00',
            'status': 'SCHEDULED'
        }
    )
    print(f"Trip Created: {trip}")

if __name__ == "__main__":
    create_data()
