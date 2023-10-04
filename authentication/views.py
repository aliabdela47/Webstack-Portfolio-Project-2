from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.admin.views.decorators import staff_member_required
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages, auth


def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate user
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.warning(request, "Your account is not active. Please contact the administrator.")
                return redirect('login')
        else:
            messages.warning(request, "Invalid login credentials!")
            return redirect('login')

    return render(request, "accounts/login.html")

@staff_member_required
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            role = form.cleaned_data['role']
            status = form.cleaned_data['status']

            # Create the user without setting is_admin initially
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
                phone_number=phone_number,
                role=role,
            )

            # Check the selected role and set attributes accordingly
            if role == 'admin':
                user.is_admin = True
                user.is_staff = True  # Assuming admin users should also have staff access

            # Check the selected status and set is_active accordingly
            if status == 'active':
                user.is_active = True
            elif status == 'inactive':
                user.is_active = False

            user.save()

            messages.success(request, "Successfully registered!")
            return redirect('manage_user')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'pages/add-user.html', context)



@login_required
def profile(request):
    user = request.user
    username = user.username
    email = user.email
    full_name = user.full_name
    phone_number = user.phone_number
    role = user.role

    context = {
        'user': user,
        'username': username,
        'email': email,
        'full_name':full_name,
        'phone_number':phone_number,
        'role':role,

    }

    return render(request, 'pages/profile.html', context)

login_required(login_url='/login')
@never_cache
def logout_view(request):
    logout(request)
    return redirect('login')