from django.db import models
from django.contrib.auth.models import User

# 1. Station (Stop)
class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Short code e.g., KOT for Koteshwor")
    address = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

# 2. Route (The Line, e.g., Jadhibuti-Charikot)
class Route(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Jadhibuti - Charikot")
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='route_starts')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='route_ends')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# 3. RouteStation (Intermediate stops with Price/Ordering)
class RouteStation(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stations')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(help_text="Order in the route (1, 2, 3...)")
    price_from_start = models.DecimalField(max_digits=8, decimal_places=2, help_text="Cumulative price from route start")
    
    class Meta:
        ordering = ['order']
        unique_together = ('route', 'station')

    def __str__(self):
        return f"{self.route.name} - {self.station.name} ({self.order})"

# 4. Bus
class Bus(models.Model):
    BUS_TYPES = (
        ('AC', 'AC Bus'),
        ('DELUXE', 'Deluxe'),
        ('NORMAL', 'Normal'),
    )
    plate_number = models.CharField(max_length=20, unique=True)
    bus_type = models.CharField(max_length=10, choices=BUS_TYPES, default='NORMAL')
    total_seats = models.PositiveIntegerField(default=30)
    operator_name = models.CharField(max_length=100, blank=True, help_text="Name of the bus owner/operator")

    def __str__(self):
        return f"{self.plate_number} ({self.bus_type})"

# 5. Trip (A Bus running on a Route on a specific Day)
class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('SCHEDULED', 'Scheduled'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='SCHEDULED')

    def __str__(self):
        return f"{self.bus.plate_number} on {self.date} ({self.route.name})"

# 6. Promo Code
class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

# 7. Booking
class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    source_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='booking_sources')
    dest_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='booking_dests')
    
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=15)
    
    seat_numbers = models.CharField(max_length=50, help_text="Comma-separated seat numbers e.g. '1,2'")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Payment Fields
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=20, default='ESEWA')
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} - {self.passenger_name}"
