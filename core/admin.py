from django.contrib import admin

from .models import (
    AboutFeature,
    AboutPage,
    Appointment,
    Banner,
    BlogPost,
    ContactMessage,
    Department,
    Doctor,
    Package,
    Service,
    SiteSettings,
    Testimonial,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 1


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [AboutFeatureInline]

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "department_list", "designation", "is_featured", "order")
    list_editable = ("order", "is_featured")
    list_filter = ("departments", "is_featured")
    search_fields = ("name", "designation")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("departments",)

    @admin.display(description="Departments")
    def department_list(self, obj):
        return ", ".join(obj.departments.values_list("name", flat=True)) or "—"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "icon_class", "order")
    list_editable = ("order",)
    list_filter = ("department",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "period", "order")
    list_editable = ("order",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author_name", "is_published", "published_at", "views_count")
    list_filter = ("is_published",)
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("patient_name", "profession", "order")
    list_editable = ("order",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "doctor", "preferred_date", "status", "created_at")
    list_filter = ("status", "department")
    list_editable = ("status",)
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read",)
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
