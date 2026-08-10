import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import (
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

STATIC_IMG = Path(settings.BASE_DIR) / "static" / "core" / "img"


def _copy_image(src_name, dest_subdir, dest_name):
    src = STATIC_IMG / src_name
    dest_dir = Path(settings.MEDIA_ROOT) / dest_subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / dest_name
    if src.exists():
        shutil.copyfile(src, dest)
    return f"{dest_subdir}/{dest_name}"


class Command(BaseCommand):
    help = "Seed the database with sample IHeartCare content (idempotent)."

    def handle(self, *args, **options):
        self.seed_site_settings()
        self.seed_about_page()
        departments = self.seed_departments()
        self.seed_doctors(departments)
        self.seed_services(departments)
        self.seed_packages()
        self.seed_banners()
        self.seed_blog_posts()
        self.seed_testimonials()
        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))

    def seed_site_settings(self):
        settings_obj = SiteSettings.load()
        settings_obj.site_name = "IHeartCare"
        settings_obj.phone = "+91-9438397808"
        settings_obj.email = "drmadhuophtha@gmail.com"
        settings_obj.address = "Plot no -426/3205/3494, Lingipur, Bhubaneswar, Odisha"
        settings_obj.about_text = (
            "IHeartCare is a multi-specialty clinic in Bhubaneswar offering expert "
            "ophthalmology and cardiology care, with a mission centered on personalized, "
            "family-focused healthcare."
        )
        settings_obj.save()

    def seed_about_page(self):
        _copy_image("about.jpg", "about", "about.jpg")
        about_page = AboutPage.load()
        about_page.tagline = "About Us"
        about_page.heading = "Best Eye & Heart Care For Yourself and Your Family"
        about_page.description = (
            "IHeartCare is a multi-specialty clinic in Bhubaneswar offering expert "
            "ophthalmology and cardiology care, with a mission centered on personalized, "
            "family-focused healthcare."
        )
        about_page.image = "about/about.jpg"
        about_page.save()

        if not about_page.features.exists():
            features = [
                ("fa-user-md", "Qualified", "Doctors"),
                ("fa-procedures", "Emergency", "Services"),
                ("fa-microscope", "Accurate", "Testing"),
                ("fa-ambulance", "Free", "Ambulance"),
            ]
            for i, (icon, title, subtitle) in enumerate(features):
                AboutFeature.objects.create(
                    about_page=about_page, icon_class=icon, title=title, subtitle=subtitle, order=i
                )

    def seed_departments(self):
        names = ["Ophthalmology", "Cardiology"]
        departments = {}
        for name in names:
            dept, _ = Department.objects.get_or_create(name=name)
            departments[name] = dept
        return departments

    def seed_doctors(self, departments):
        if Doctor.objects.exists():
            return
        _copy_image("team-1.jpg", "doctors", "dr-madhumita-rout.jpg")
        _copy_image("team-2.jpg", "doctors", "dr-gobinda-nayak.jpg")
        doctors = [
            dict(
                name="Dr. Madhumita Rout",
                departments=[departments["Ophthalmology"]],
                designation="Ophthalmologist",
                qualification="MBBS, MS (Ophthalmology), FIOL",
                bio="Specializes in comprehensive eye care including myopia management, "
                "presbyopia treatment and astigmatism correction.",
                order=1,
                photo="doctors/dr-madhumita-rout.jpg",
            ),
            dict(
                name="Dr. Gobinda Prasad Nayak",
                departments=[departments["Cardiology"]],
                designation="Cardiologist",
                qualification="MBBS, MD, DM (Cardiology), FESC, AFESC",
                bio="Experienced cardiologist focused on preventive heart care and "
                "advanced cardiac treatment.",
                order=2,
                photo="doctors/dr-gobinda-nayak.jpg",
            ),
        ]
        for doctor_data in doctors:
            dept_list = doctor_data.pop("departments")
            doctor = Doctor.objects.create(**doctor_data)
            doctor.departments.set(dept_list)

    def seed_services(self, departments):
        if Service.objects.exists():
            return
        services = [
            ("fa-eye", "Comprehensive Eye Check-up",
             "Full eye examinations to detect and manage vision problems early. Our comprehensive "
             "check-up covers visual acuity, eye pressure, and retina health so issues are caught "
             "well before they affect your daily life.",
             "Ophthalmology", "about.jpg", "eye-checkup.jpg"),
            ("fa-heartbeat", "Cardiology Consultation",
             "Expert evaluation and management of heart health conditions. We review your medical "
             "history, run the right diagnostics, and build a treatment plan tailored to your "
             "heart's specific needs.",
             "Cardiology", "price-1.jpg", "cardiology-consultation.jpg"),
            ("fa-glasses", "Myopia Management",
             "Personalized plans to slow the progression of short-sightedness, especially in "
             "children and teens, using proven monitoring and correction techniques.",
             "Ophthalmology", "price-2.jpg", "myopia-management.jpg"),
            ("fa-user-md", "Presbyopia Treatment",
             "Solutions for age-related near vision loss, from updated prescriptions to modern "
             "correction options, so reading and close-up work stay comfortable.",
             "Ophthalmology", "price-3.jpg", "presbyopia-treatment.jpg"),
            ("fa-eye-dropper", "Astigmatism Correction",
             "Diagnosis and correction for blurred or distorted vision caused by astigmatism, with "
             "options ranging from corrective lenses to advanced treatment.",
             "Ophthalmology", "price-4.jpg", "astigmatism-correction.jpg"),
            ("fa-stethoscope", "ECG & Heart Screening",
             "Preventive cardiac screening including ECG and blood pressure checks to catch heart "
             "issues before they progress, backed by clear follow-up guidance.",
             "Cardiology", "blog-1.jpg", "ecg-heart-screening.jpg"),
        ]
        for i, (icon, title, desc, dept_name, src_img, dest_img) in enumerate(services):
            _copy_image(src_img, "services", dest_img)
            Service.objects.create(
                icon_class=icon,
                title=title,
                description=desc,
                department=departments.get(dept_name),
                image=f"services/{dest_img}",
                order=i,
            )

    def seed_packages(self):
        if Package.objects.exists():
            return
        _copy_image("price-1.jpg", "packages", "eye-care-checkup.jpg")
        _copy_image("price-2.jpg", "packages", "heart-health-screening.jpg")
        _copy_image("price-3.jpg", "packages", "family-wellness.jpg")
        _copy_image("price-4.jpg", "packages", "comprehensive-checkup.jpg")
        packages = [
            ("Eye Care Checkup", 25, "Year", "packages/eye-care-checkup.jpg",
             "Full Eye Examination\nMyopia & Astigmatism Screening\nExperienced Ophthalmologist\nFollow-up Consultation"),
            ("Heart Health Screening", 45, "Year", "packages/heart-health-screening.jpg",
             "ECG & Blood Pressure Check\nCardiology Consultation\nHighly Experienced Doctors\nFollow-up Consultation"),
            ("Family Wellness Package", 75, "Year", "packages/family-wellness.jpg",
             "Eye + Heart Screening\nFamily-Centered Care\nPriority Appointments\nTelephone Support"),
            ("Comprehensive Checkup", 99, "Year", "packages/comprehensive-checkup.jpg",
             "Full Eye & Cardiac Screening\nHighly Experienced Doctors\nHighest Success Rate\nTelephone Service"),
        ]
        for i, (title, price, period, image, features) in enumerate(packages):
            Package.objects.create(
                title=title, price=price, period=period, image=image, features=features, order=i
            )

    def seed_banners(self):
        if Banner.objects.exists():
            return
        _copy_image("about.jpg", "banners", "banner-placeholder.jpg")
        slides = [
            ("Welcome To IHeartCare", "Best Eye & Heart Care In Bhubaneswar"),
            ("Welcome To IHeartCare", "Personalized Family-Centered Healthcare"),
            ("Welcome To IHeartCare", "Expert Ophthalmology Care"),
            ("Welcome To IHeartCare", "Trusted Cardiology Specialists"),
            ("Welcome To IHeartCare", "Book Your Appointment Today"),
        ]
        for i, (subtitle, title) in enumerate(slides):
            Banner.objects.create(
                title=title,
                subtitle=subtitle,
                image="banners/banner-placeholder.jpg",
                order=i,
                is_active=True,
            )

    def seed_blog_posts(self):
        if BlogPost.objects.exists():
            return
        _copy_image("blog-1.jpg", "blog", "eye-health-tips.jpg")
        _copy_image("blog-2.jpg", "blog", "heart-health-basics.jpg")
        _copy_image("blog-3.jpg", "blog", "family-checkups.jpg")
        posts = [
            ("5 Everyday Habits That Protect Your Eyesight", "eye-health-tips",
             "eye-health-tips.jpg", "Simple daily habits — from screen breaks to proper lighting — that help "
             "protect your vision over the long term."),
            ("Understanding Your Heart Health: A Beginner's Guide", "heart-health-basics",
             "heart-health-basics.jpg", "What routine cardiology checkups look for, and why early screening "
             "matters for long-term heart health."),
            ("Why Family Health Checkups Matter", "family-checkups",
             "family-checkups.jpg", "How regular checkups for the whole family help catch eye and heart "
             "conditions before they become serious."),
        ]
        for title, slug, image, excerpt in posts:
            BlogPost.objects.create(
                title=title,
                slug=slug,
                image=f"blog/{image}",
                author_name="IHeartCare Team",
                excerpt=excerpt,
                content=excerpt + " " + excerpt,
                is_published=True,
            )

    def seed_testimonials(self):
        if Testimonial.objects.exists():
            return
        _copy_image("testimonial-1.jpg", "testimonials", "patient-1.jpg")
        _copy_image("testimonial-2.jpg", "testimonials", "patient-2.jpg")
        _copy_image("testimonial-3.jpg", "testimonials", "patient-3.jpg")
        testimonials = [
            ("Anita Sahoo", "Teacher", "testimonials/patient-1.jpg",
             "Dr. Rout took the time to explain my eye condition clearly and the treatment worked wonderfully. Highly recommended!"),
            ("Rajesh Mohanty", "Business Owner", "testimonials/patient-2.jpg",
             "Dr. Nayak's cardiology consultation gave me real peace of mind. The whole clinic staff was caring and professional."),
            ("Sunita Patra", "Homemaker", "testimonials/patient-3.jpg",
             "We bring the whole family here for checkups. IHeartCare genuinely feels family-centered, just like they promise."),
        ]
        for i, (name, profession, photo, message) in enumerate(testimonials):
            Testimonial.objects.create(
                patient_name=name, profession=profession, photo=photo, message=message, order=i
            )
