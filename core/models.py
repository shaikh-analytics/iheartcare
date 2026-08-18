from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SiteSettings(models.Model):
    """Singleton holding global clinic info shown in topbar/footer."""

    site_name = models.CharField(max_length=100, default="IHeartCare")
    phone = models.CharField(max_length=30, default="+012 345 6789")
    email = models.EmailField(default="info@iheartcare.com")
    address = models.CharField(max_length=255, default="123 Street, New York, USA")
    about_text = models.TextField(
        blank=True,
        default="IHeartCare is committed to providing personalized, family-centered "
        "healthcare with compassion and expertise.",
    )
    map_embed_url = models.URLField(blank=True, help_text="Google Maps embed URL for the contact page")
    facebook_url = models.URLField(blank=True, default="#!")
    twitter_url = models.URLField(blank=True, default="#!")
    linkedin_url = models.URLField(blank=True, default="#!")
    instagram_url = models.URLField(blank=True, default="#!")
    youtube_url = models.URLField(blank=True, default="#!")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutPage(models.Model):
    """Singleton holding the editable content for the About Us section."""

    tagline = models.CharField(max_length=100, default="About Us")
    heading = models.CharField(max_length=200, default="Best Medical Care For Yourself and Your Family")
    description = models.TextField(
        blank=True,
        default="IHeartCare is committed to providing personalized, family-centered "
        "healthcare with compassion and expertise.",
    )
    image = models.ImageField(upload_to="about/", blank=True, null=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutFeature(models.Model):
    """One of the small icon stat boxes shown in the About section (e.g. "Qualified Doctors")."""

    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name="features")
    icon_class = models.CharField(
        max_length=60, default="fa-user-md", help_text='Font Awesome icon class, e.g. "fa-user-md"'
    )
    title = models.CharField(max_length=50, help_text='Top line, e.g. "Qualified"')
    subtitle = models.CharField(max_length=50, help_text='Bottom line, e.g. "Doctors"')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} {self.subtitle}"


class Banner(models.Model):
    """A single slide in the homepage hero carousel."""

    title = models.CharField(max_length=200, default="Best Healthcare Solution In Your City")
    subtitle = models.CharField(max_length=100, blank=True, default="Welcome To IHeartCare")
    image = models.ImageField(upload_to="banners/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    departments = models.ManyToManyField(Department, blank=True, related_name="doctors")
    designation = models.CharField(max_length=150, blank=True, help_text='e.g. "Cardiology Specialist"')
    qualification = models.CharField(max_length=150, blank=True, help_text='e.g. "MBBS, MD, DM"')
    photo = models.ImageField(upload_to="doctors/", blank=True, null=True)
    bio = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True, default="#!")
    twitter_url = models.URLField(blank=True, default="#!")
    linkedin_url = models.URLField(blank=True, default="#!")
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Doctor.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:doctor_detail", args=[self.slug])


class Service(models.Model):
    icon_class = models.CharField(
        max_length=60, default="fa-user-md", help_text='Font Awesome icon class, e.g. "fa-user-md"'
    )
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="services"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2
            while Service.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:service_detail", args=[self.slug])


class Package(models.Model):
    title = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    period = models.CharField(max_length=30, default="Year", help_text='e.g. "Year", "Month"')
    image = models.ImageField(upload_to="packages/", blank=True, null=True)
    features = models.TextField(blank=True, help_text="One feature per line")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    @property
    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class GalleryPhoto(models.Model):
    """A single image in the public photo gallery, uploaded by the admin."""

    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to="gallery/photos/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"

    def __str__(self):
        return self.title or f"Photo #{self.pk}"


class GalleryVideo(models.Model):
    """A single video in the public video gallery — either an uploaded file or a YouTube link."""

    SOURCE_UPLOAD = "upload"
    SOURCE_YOUTUBE = "youtube"
    SOURCE_CHOICES = [
        (SOURCE_UPLOAD, "Uploaded Video"),
        (SOURCE_YOUTUBE, "YouTube Link"),
    ]

    title = models.CharField(max_length=150, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_YOUTUBE)
    video_file = models.FileField(
        upload_to="gallery/videos/", blank=True, null=True, help_text="Required when source is 'Uploaded Video'."
    )
    youtube_url = models.URLField(
        blank=True, help_text="Required when source is 'YouTube Link', e.g. https://www.youtube.com/watch?v=XXXXXXX"
    )
    thumbnail = models.ImageField(
        upload_to="gallery/video_thumbs/",
        blank=True,
        null=True,
        help_text="Optional cover image. YouTube videos use the official thumbnail automatically if left blank.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Gallery Video"
        verbose_name_plural = "Gallery Videos"

    def __str__(self):
        return self.title or f"Video #{self.pk}"

    def clean(self):
        super().clean()
        if self.source == self.SOURCE_UPLOAD and not self.video_file:
            raise ValidationError({"video_file": "Upload a video file, or switch the source to 'YouTube Link'."})
        if self.source == self.SOURCE_YOUTUBE and not self.youtube_url:
            raise ValidationError({"youtube_url": "Enter a YouTube URL, or switch the source to 'Uploaded Video'."})

    @property
    def is_youtube(self):
        return self.source == self.SOURCE_YOUTUBE

    @property
    def youtube_id(self):
        if not self.youtube_url:
            return ""
        parsed = urlparse(self.youtube_url)
        host = parsed.netloc.lower()
        if "youtu.be" in host:
            return parsed.path.lstrip("/")
        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [""])[0]
            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/embed/")[-1]
            if parsed.path.startswith("/shorts/"):
                return parsed.path.split("/shorts/")[-1]
        return ""

    @property
    def embed_url(self):
        video_id = self.youtube_id
        return f"https://www.youtube.com/embed/{video_id}" if video_id else ""

    @property
    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.is_youtube and self.youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
        return ""


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    author_name = models.CharField(max_length=100, default="Admin")
    excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True)
    views_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:blog_detail", args=[self.slug])


class Testimonial(models.Model):
    patient_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    message = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.patient_name


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, default="")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.preferred_date or 'no date'}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'No subject'}"
