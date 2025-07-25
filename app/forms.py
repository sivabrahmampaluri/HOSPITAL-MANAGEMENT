from django import forms
from .models import FileUpload, Patient

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ('file',)

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'dob', 'phone_number',
            'admit_date', 'gender', 'doctor_specialty', 'appointment_slot', 'problem'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'admit_date': forms.DateInput(attrs={'type': 'date'}),
        }
