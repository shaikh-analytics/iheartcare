from .models import Doctor, Service, SiteSettings


def site_settings(request):
    return {
        "site_settings": SiteSettings.load(),
        "nav_services": Service.objects.all(),
        "nav_doctors": Doctor.objects.all(),
    }
