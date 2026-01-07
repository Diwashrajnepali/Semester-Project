from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking, name='booking'),
    path('search/', views.booking, name='search_bus'), # Reusing booking view for search post
    path('schedule/', views.schedule, name='schedule'),
    path('book/<int:trip_id>/<int:source_id>/<int:dest_id>/', views.book_seat, name='book_seat'),
    path('payment/<int:booking_id>/', views.payment_init, name='payment_init'),
    path('esewa-success/', views.esewa_success, name='esewa_success'),
    path('esewa-failure/', views.esewa_failure, name='esewa_failure'),
]
