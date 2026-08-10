from django.contrib import messages
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static

from .forms import AppointmentForm, ContactForm
from .models import AboutPage, Banner, BlogPost, Department, Doctor, Package, Service, Testimonial

PAGES_GROUP = ["blog", "detail", "team", "testimonial", "appointment", "search"]


def _base_context(active):
    return {"active": active, "pages_group": PAGES_GROUP}


def home(request):
    about_page = AboutPage.load()
    context = _base_context("home")
    context.update(
        {
            "banners": Banner.objects.filter(is_active=True),
            "about_page": about_page,
            "about_features": about_page.features.all(),
            "services": Service.objects.all()[:6],
            "packages": Package.objects.all(),
            "doctors": Doctor.objects.filter(is_featured=True)[:3],
            "testimonials": Testimonial.objects.all()[:3],
            "blog_posts": BlogPost.objects.filter(is_published=True)[:3],
            "departments": Department.objects.all(),
            "appointment_form": AppointmentForm(),
        }
    )
    return render(request, "home/home.html", context)


def about(request):
    about_page = AboutPage.load()
    context = _base_context("about")
    context.update(
        {
            "about_page": about_page,
            "about_features": about_page.features.all(),
            "doctors": Doctor.objects.filter(is_featured=True)[:3],
            "departments": Department.objects.all(),
        }
    )
    return render(request, "about/about.html", context)


def service_list(request):
    context = _base_context("service")
    context.update(
        {
            "services": Service.objects.all(),
            "appointment_form": AppointmentForm(),
        }
    )
    return render(request, "services/service.html", context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    specialists = Doctor.objects.filter(departments=service.department) if service.department else Doctor.objects.none()
    context = _base_context("service")
    context.update(
        {
            "service": service,
            "other_services": Service.objects.exclude(pk=service.pk),
            "specialists": specialists,
        }
    )
    return render(request, "services/detail.html", context)


def pricing(request):
    context = _base_context("price")
    context.update(
        {
            "packages": Package.objects.all(),
            "doctors": Doctor.objects.filter(is_featured=True)[:3],
            "appointment_form": AppointmentForm(),
        }
    )
    return render(request, "pricing/price.html", context)


def blog_list(request):
    context = _base_context("blog")
    context["posts"] = BlogPost.objects.filter(is_published=True)
    return render(request, "blog/blog.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    BlogPost.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
    post.refresh_from_db()
    context = _base_context("detail")
    context.update(
        {
            "post": post,
            "related_posts": BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:4],
        }
    )
    return render(request, "blog/detail.html", context)


def blog_detail_latest(request):
    post = BlogPost.objects.filter(is_published=True).first()
    if post:
        return redirect(post.get_absolute_url())
    context = _base_context("detail")
    context.update({"post": None, "related_posts": []})
    return render(request, "blog/detail.html", context)


def team(request):
    context = _base_context("team")
    context["doctors"] = Doctor.objects.all()
    return render(request, "team/team.html", context)


def doctor_detail(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug)
    context = _base_context("team")
    context.update(
        {
            "doctor": doctor,
            "other_doctors": Doctor.objects.exclude(pk=doctor.pk),
        }
    )
    return render(request, "team/detail.html", context)


def testimonial(request):
    context = _base_context("testimonial")
    context["testimonials"] = Testimonial.objects.all()
    return render(request, "testimonial/testimonial.html", context)


def appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks! Your appointment request has been received — we'll contact you shortly to confirm.",
            )
            return redirect("core:appointment")
    else:
        form = AppointmentForm()
    context = _base_context("appointment")
    context["appointment_form"] = form
    return render(request, "appointment/appointment.html", context)


def search(request):
    departments = Department.objects.all()
    doctors = None
    query = request.GET.get("q", "").strip()
    department_id = request.GET.get("department", "")
    if query or department_id:
        doctors = Doctor.objects.all()
        if department_id:
            doctors = doctors.filter(departments__id=department_id)
        if query:
            doctors = doctors.filter(
                Q(name__icontains=query)
                | Q(designation__icontains=query)
                | Q(departments__name__icontains=query)
            )
        doctors = doctors.distinct()
    context = _base_context("search")
    context.update(
        {
            "departments": departments,
            "doctors": doctors,
            "query": query,
            "selected_department": department_id,
        }
    )
    return render(request, "search/search.html", context)


def doctor_search_suggest(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        doctors = Doctor.objects.prefetch_related("departments").filter(
            Q(name__icontains=query)
            | Q(designation__icontains=query)
            | Q(departments__name__icontains=query)
        ).distinct()[:8]
        results = [
            {
                "name": doctor.name,
                "designation": doctor.designation,
                "department": ", ".join(dept.name for dept in doctor.departments.all()),
                "url": doctor.get_absolute_url(),
                "photo": doctor.photo.url if doctor.photo else static("core/img/team-1.jpg"),
            }
            for doctor in doctors
        ]
    return JsonResponse({"results": results})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
            return redirect("core:contact")
    else:
        form = ContactForm()
    context = _base_context("contact")
    context["form"] = form
    return render(request, "contact/contact.html", context)
