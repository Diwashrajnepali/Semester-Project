from django.contrib import admin
from django.urls import path,include,re_path
from django.views.generic.base import RedirectView
from django.templatetags.static import static
from . import views 

urlpatterns = [
     path('',views.home, name='home'),
     path('contact/',views.contact, name='contact'),
     path('about/',views.about, name='about'),
     path('signup/',views.handleSignup, name='handleSignup'),
     path('login/',views.handleLogin, name='handleLogin'),
     path('logout/',views.handleLogout, name='handleLogout'),
]
