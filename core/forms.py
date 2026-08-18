from django import forms

from .models import Appointment, ContactMessage, Doctor

TEXT_ATTRS = {"class": "form-control bg-light border-0", "style": "height: 55px;"}
SELECT_ATTRS = {"class": "form-select bg-light border-0", "style": "height: 55px;"}


class DoctorSelectWidget(forms.Select):
    """Tags each <option> with the doctor's department so JS can filter the
    doctor dropdown when a department is chosen on the appointment form."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        instance = getattr(value, "instance", None)
        if instance is not None and instance.pk:
            dept_ids = [dept.id for dept in instance.departments.all()]
            if dept_ids:
                option["attrs"]["data-department"] = " ".join(str(pk) for pk in dept_ids)
        return option


class DoctorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if obj.designation:
            return f"{obj.name} ({obj.designation})"
        return obj.name


class AppointmentForm(forms.ModelForm):
    doctor = DoctorChoiceField(
        queryset=Doctor.objects.prefetch_related("departments"),
        required=False,
        empty_label="Select Doctor",
        widget=DoctorSelectWidget(attrs=SELECT_ATTRS),
    )

    class Meta:
        model = Appointment
        fields = ["department", "doctor", "name", "email", "phone", "preferred_date", "preferred_time"]
        widgets = {
            "department": forms.Select(attrs=SELECT_ATTRS),
            "name": forms.TextInput(attrs={**TEXT_ATTRS, "placeholder": "Your Name"}),
            "email": forms.EmailInput(attrs={**TEXT_ATTRS, "placeholder": "Your Email"}),
            "phone": forms.TextInput(attrs={**TEXT_ATTRS, "placeholder": "Your Phone Number"}),
            "preferred_date": forms.TextInput(
                attrs={
                    **TEXT_ATTRS,
                    "class": TEXT_ATTRS["class"] + " datetimepicker-input",
                    "placeholder": "Date",
                    "data-target": "#date",
                    "data-toggle": "datetimepicker",
                }
            ),
            "preferred_time": forms.TextInput(
                attrs={
                    **TEXT_ATTRS,
                    "class": TEXT_ATTRS["class"] + " datetimepicker-input",
                    "placeholder": "Time",
                    "data-target": "#time",
                    "data-toggle": "datetimepicker",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].empty_label = "Choose Department"


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={**TEXT_ATTRS, "placeholder": "Your Name"}),
            "email": forms.EmailInput(attrs={**TEXT_ATTRS, "placeholder": "Your Email"}),
            "subject": forms.TextInput(attrs={**TEXT_ATTRS, "placeholder": "Subject"}),
            "message": forms.Textarea(
                attrs={"class": "form-control bg-light border-0", "rows": 5, "placeholder": "Message"}
            ),
        }
