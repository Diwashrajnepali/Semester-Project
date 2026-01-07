from django.shortcuts import render, HttpResponse, redirect
from home.models import Contact
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def home(request):
    return render(request,'home/index.html')

def contact(request):

     if request.method=='POST':
          name=request.POST.get('name')
          email=request.POST.get('email')
          phone=request.POST.get('phone')
          content=request.POST.get('content')
          
          if len(name)<2 or len(email)<4 or len(phone)<10 or len(content)<4:
               messages.error(request, "Please fill the form correctly")

          else:
               print(name,email,phone,content)
               contact=Contact(name=name, phone=phone, email=email, content=content  )
               contact.save()
               messages.success(request, "Your message has been sucessfully sent")
     return render(request,'home/contact.html')

def about(request):
     return render(request,'home/about.html')

def handleSignup(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        # Validation
        if len(username) < 3:
            messages.error(request, "Username must be at least 3 characters long")
            return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect('home')
        
        if len(pass1) < 6:
            messages.error(request, "Password must be at least 6 characters long")
            return redirect('home')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('home')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('home')
        
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=pass1)
            user.first_name = fname
            user.last_name = lname
            user.save()
            
            # Auto login after signup
            login(request, user)
            messages.success(request, f"Welcome {fname}! Your account has been created successfully.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')
    
    return redirect('home')

def handleLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('home')
    
    return redirect('home')

def handleLogout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('home')