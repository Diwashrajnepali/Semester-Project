from django.contrib import admin
from .models import Station, Route, RouteStation, Bus, Trip, Booking, PromoCode

class RouteStationInline(admin.TabularInline):
    model = RouteStation
    extra = 1

class RouteAdmin(admin.ModelAdmin):
    inlines = [RouteStationInline]
    list_display = ('name', 'source', 'destination', 'is_active')

class TripAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'date', 'departure_time', 'status')
    list_filter = ('date', 'route', 'status')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger_name', 'trip', 'source_station', 'dest_station', 'total_price', 'status', 'is_paid')
    list_filter = ('status', 'is_paid', 'booking_date')

admin.site.register(Station)
admin.site.register(Route, RouteAdmin)
admin.site.register(Bus)
admin.site.register(Trip, TripAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(PromoCode)
