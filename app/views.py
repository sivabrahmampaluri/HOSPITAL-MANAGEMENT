from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import FileUpload, Patient
from .forms import FileUploadForm, PatientForm  # Ensure these forms are created
from azure.storage.blob import BlobServiceClient
import os
from datetime import date


# Load Azure environment variables
AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
AZURE_CONTAINER = os.getenv("AZURE_CONTAINER")

# Initialize Blob Service Client if credentials are set
blob_service_client = None
if AZURE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=AZURE_ACCOUNT_KEY,
    )

# Custom login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            # Redirect based on username
            if username == 'Doctor@16203':
                return redirect('doctor')  # Ensure this view is defined in urls.py
            elif username == 'Tester@16203':
                return redirect('index')  # Redirect to index view for authenticated users
            elif username == 'Reception@16203':
                return redirect('reception')  # Ensure this view is defined in urls.py
            else:
                return redirect('login')  # Default redirection back to login
        else:
            context = {'error_message': 'Incorrect username or password.'}
            return render(request, 'login.html', context)

    return render(request, 'login.html')

@login_required
def index(request):
    if request.method == 'POST':
        prefix = request.POST.get('prefix')
        uploaded_file = request.FILES.get('file')
        
        if prefix and uploaded_file:
            # Rename the file with the prefix
            new_filename = f"{prefix}_{uploaded_file.name}"
            
            # Save the file with the new name
            file_instance = FileUpload(
                user=request.user,
                file=uploaded_file
            )
            file_instance.file.name = new_filename  # Set the new file name
            file_instance.save()
            
            return redirect('index')

    context = {
        'form': FileUploadForm(),
        'files': FileUpload.objects.filter(user=request.user),
    }
    return render(request, 'index.html', context)

@login_required
def doctor(request):
    return render(request, 'doctor.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Patient
from django.views.decorators.csrf import csrf_protect

# Ensure Patient model and unique_id field are correctly defined in models.py


@login_required
def reception(request):
    # Get the current date
    current_date = date.today()

    # Fetch patients
    all_patients = Patient.objects.all()
    today_patients = all_patients.filter(admit_date=current_date)
    future_patients = all_patients.filter(admit_date__gt=current_date)
    past_patients = all_patients.filter(admit_date__lt=current_date)

    # Initialize checked-in patients
    if 'check_in_patients' not in request.session:
        request.session['check_in_patients'] = []
    check_in_ids = request.session['check_in_patients']
    check_in_patients = Patient.objects.filter(unique_id__in=check_in_ids)

    if request.method == 'POST':
        action = request.POST.get('action')
        patient_id = request.POST.get('patient_id')

        if patient_id:
            try:
                patient = Patient.objects.get(unique_id=patient_id)
                if action == 'check_in':
                    if patient_id not in check_in_ids:
                        check_in_ids.append(patient_id)
                        request.session['check_in_patients'] = check_in_ids
                return redirect('reception')
            except Patient.DoesNotExist:
                pass

    return render(request, 'reception.html', {
        'today_patients': today_patients,
        'future_patients': future_patients,
        'past_patients': past_patients,
        'check_in_patients': check_in_patients,
        'check_in_patients_ids': check_in_ids,
    })




@login_required
def view_files(request):
    if not blob_service_client:
        return render(request, 'view_files.html', {'error': 'Azure Blob Storage client is not configured properly.'})
    
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER)
    
    files = []
    try:
        for blob in container_client.list_blobs():
            files.append({
                'name': blob.name,
                'url': f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER}/{blob.name}",
            })
    except Exception as e:
        return render(request, 'view_files.html', {'error': str(e)})

    context = {'files': files}
    return render(request, 'view_files.html', context)

def patient(request):
    return render(request, 'patient.html')

def new_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return render(request, 'patient_submission_success.html', {'patient': patient})
    else:
        form = PatientForm()
    return render(request, 'new_patient.html', {'form': form})

def existing_patient(request):
    return render(request, 'existing_patient.html')

from django.http import JsonResponse
import random

# Mock OTP storage (in real scenarios, use a database or cache)
otp_store = {}

otp_store = {}

def generate_otp(phone):
    import random
    otp = str(random.randint(100000, 999999))
    otp_store[phone] = otp
    return otp

@login_required
def send_otp(request):
    phone = request.GET.get('phone')
    if not phone:
        return JsonResponse({'error': 'Phone number is required'}, status=400)
    
    otp = generate_otp(phone)
    # Simulate sending OTP (Integrate SMS API in real scenarios)
    print(f"OTP for {phone}: {otp}")
    
    return JsonResponse({'message': 'OTP sent successfully.'})


@login_required
def verify_patient(request):
    phone = request.GET.get('phone')  # Getting phone from the request
    otp = request.GET.get('otp')  # Getting OTP from the request

    if not phone or not otp:
        return JsonResponse({'error': 'Phone number or OTP missing.'}, status=400)

    # Check if OTP matches
    if otp_store.get(phone) == otp:  # Assuming otp_store is a dictionary holding OTPs
        del otp_store[phone]  # OTP is one-time use
        
        # Query the Patient model using the correct field name
        patient = Patient.objects.filter(phone_number=phone).first()
        if patient:
            return JsonResponse({
                'success': True,
                'patient_id': patient.unique_id
            })
        else:
            return JsonResponse({'success': False, 'error': 'No patient found with this phone number.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid OTP.'})
@login_required
def patient_details(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'patient_details.html', {'patient': patient})
