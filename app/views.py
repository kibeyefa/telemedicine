import re
from site import sethelper
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.views import View
from django.contrib.messages import add_message, info

from .views import *
from .models import *
from .forms import *
import requests


User = get_user_model()

def get_user_or_redirect_to_login(param):
    user = param.request.user
    if not user.is_authenticated:
        return redirect('/auth/login/')
    return user
    


# Create your views here.
def home(request):
    return redirect('/auth/login/')

class SignOutView(View):
    def get(self, request):
        user = self.request.user
        if user.is_authenticated:
            logout(request)
        return redirect("/auth/login/")

class LoginView(View):
    def get(self, request):
        user = request.user
        if self.request.user.is_authenticated:
            if PatientProfile.objects.filter(user=user).exists():
                return redirect('/dashboard/patient/')
            else:
                return redirect('/dashboard/doctor/')

        return render(request, 'login.html')
    
    def post(self, request):
        user = request.user
        if self.request.user.is_authenticated:
            return redirect('/')
        
        email = self.request.POST.get('email') 
        password = self.request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None and authenticated_user == user:
                login(request, authenticated_user)
                if PatientProfile.objects.filter(user=user).exists():
                    return redirect('/dashboard/patient/')
                else:
                    return redirect('/dashboard/doctor/')
            else:
                error_msg = "Incorrect email or password."
        except:
            error_msg = f"No account with email {email} found."

        return render(request, 'login.html', {"error_msg":error_msg})


class RegisterView(View):
    def get(self, request):
        user = request.user
        if self.request.user.is_authenticated:
            return redirect('/')

        return render(request, 'register.html')
    
    def post(self, request):
        print(request.GET)
        user = request.user
        if self.request.user.is_authenticated:
            return redirect('/')
        
        username = self.request.POST.get('username')
        email = self.request.POST.get('email')
        password = self.request.POST.get('password')
        profile = self.request.POST.get('profile')

        user = User.objects.create_user(username, email, password)
        login(request, user)
        return redirect(f"/profile/setup/?profile_type={profile}")
    

class ProfileSetup(View):
    def get(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/auth/login/')
        
        profile_type = self.request.GET.get('profile_type')
        # if profile_type != 'patient' or profile_type != 'doctor':
        #     user.delete()
        #     return redirect
        return render(request, 'profile-setup.html', dict(profile_type=profile_type))

    def post(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/auth/login/')
        
        profile_type = self.request.GET.get('profile_type')
        # form = PatientProfileForm(self.request.POST)
        name = self.request.POST.get('name')
        phone = self.request.POST.get('phone')
        email = self.request.POST.get('email')
        date_of_birth = self.request.POST.get('date_of_birth')
        gender = self.request.POST.get('gender')
        print("Gender:", gender)
        address = self.request.POST.get('address')
        bio = self.request.POST.get('bio')
        image = self.request.FILES.get('image')

        if profile_type == 'patient':
            patient_profile = PatientProfile.objects.create(
                name=name, email=email, phone=phone, address=address, date_of_birth=date_of_birth, gender=gender, user=user)
            patient_profile.image = image
            patient_profile.save()
            profile = patient_profile

        else:
            doctor_profile = DoctorProfile.objects.create(
                name=name, email=email, phone=phone, address=address, date_of_birth=date_of_birth, gender=gender, bio=bio, user=user)
            doctor_profile.image = image
            doctor_profile.save()
            profile = doctor_profile

        
        url = "https://263858aad3fc4c8b.api-us.cometchat.io/v3/users"

        payload = {
            "uid": profile.slug,
            "name": name,
            "image": profile.image.url
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "apikey": "70a2c3f8750bbf66525dc67de662fd3d864a9ba4"
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            if profile_type == "doctor":
                return redirect('/dashboard/doctor/')
            else:
                return redirect('/dashboard/patient/')

        else:
            profile.delete()
            return redirect(f"/profile/setup/?profile_type={profile_type}/")


class PatientProfileView(View):
    pass


class DoctorPofileView(View):
    pass


class PatientDashboardView(View):
    def get(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/auth/login/')
        
        patient_profile = PatientProfile.objects.filter(user=user)
        
        if len(patient_profile) < 1:
            add_message(request, 0, "You do not have a profile yet.")
            return redirect('/profile/setup/?profile_type=patient')
        else:
            patient_profile = patient_profile[0]
            doctors = DoctorProfile.objects.all()
            return render(request, 'dashboard.html', {"patient_profile":patient_profile, "doctors":doctors})
        
    def post(self, request):
        # for doctor search
        pass
        

class DoctorDashboardView(View):
    def get(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return redirect('/auth/login/')
        
        doctor_profile = DoctorProfile.objects.filter(user=user)
        
        if len(doctor_profile) < 1:
            add_message(request, 0, "You do not have a profile yet.")
            return redirect('/profile/setup/?profile_type=doctor')
        else:
            doctor_profile = doctor_profile[0]
            connection_requests = ConnectionRequest.objects.filter(doctor=doctor_profile, accepted=False)
            patients = doctor_profile.patients.all()
            return render(request, 'doctor-dashboard.html', 
                          {"doctor_profile": doctor_profile, "patients": patients, "connection_requests": connection_requests})

    def post(self, request):
        # For patient search
        pass


class CreateConnectionRequest(View):
    def get(self, request, slug):
        user = get_user_or_redirect_to_login(self)
        patient = PatientProfile.objects.get(user=user)
        doctor = DoctorProfile.objects.get(slug=slug)
        connection = ConnectionRequest.objects.create(doctor=doctor, patient=patient)
        info(request, "Request Sent Successfully.")

        return redirect('/dashboard/patient/')



class AcceptConnectionRequest(View):
    def get(self, request, id):
        user = get_user_or_redirect_to_login(self)
        connection = ConnectionRequest.objects.get(id=id)
        doctor = connection.doctor
        patient = connection.patient

        url = f"https://263858aad3fc4c8b.api-us.cometchat.io/v3/users/{patient.slug}/friends"

        payload = { "accepted": [doctor.slug.lower()] }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "apikey": "70a2c3f8750bbf66525dc67de662fd3d864a9ba4"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            doctor.patients.add(patient)
            doctor.save()
            patient.doctors.add(doctor)
            patient.save()
            connection.accepted = True
            connection.save()

            return redirect('/dashboard/doctor/')
        
        return redirect('/dashboard/doctor/')
    

class RejectConnectionRequest(View):
    def get(self, request, id):
        user = get_user_or_redirect_to_login(self)
        doctor = PatientProfile.objects.get(user=user)
        connection = ConnectionRequest.objects.get(id=id)
        connection.delete()
        info(request, "Request rejected Successfully.")

        return redirect('/dashboard/doctor/')