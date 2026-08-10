from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.service_list, name="service"),
    path("pricing/", views.pricing, name="price"),
    path("blog/", views.blog_list, name="blog"),
    path("blog/detail/", views.blog_detail_latest, name="detail"),
    path("team/", views.team, name="team"),
    path("testimonials/", views.testimonial, name="testimonial"),
    path("appointment/", views.appointment, name="appointment"),
    path("search/", views.search, name="search"),
    path("search/suggest/", views.doctor_search_suggest, name="doctor_search_suggest"),
    path("contact/", views.contact, name="contact"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("team/<slug:slug>/", views.doctor_detail, name="doctor_detail"),
]
