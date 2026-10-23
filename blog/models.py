import re
from urllib.parse import quote

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='articles')
    video_url = models.URLField(blank=True, null=True, help_text="Lien YouTube ou Vimeo (optionnel)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if not self.image or self.image.name == "http://default":
            return "https://picsum.photos/400/300"
        return self.image.url

    @property
    def embed_url(self):
        url = self.video_url
        if not url:
            return None

        m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([\w-]{11})', url)
        if m:
            return f"https://www.youtube.com/embed/{m.group(1)}"

        m = re.search(r'vimeo\.com/(?:video/)?(\d+)', url)
        if m:
            return f"https://player.vimeo.com/video/{m.group(1)}"

        m = re.search(r'(?:dailymotion\.com/video/|dai\.ly/)([a-zA-Z0-9]+)', url)
        if m:
            return f"https://www.dailymotion.com/embed/video/{m.group(1)}"

        m = re.search(r'tiktok\.com/@[\w.\-]+/video/(\d+)', url)
        if m:
            return f"https://www.tiktok.com/embed/v2/{m.group(1)}"

        m = re.search(r'instagram\.com/(p|reel|tv)/([\w-]+)', url)
        if m:
            return f"https://www.instagram.com/{m.group(1)}/{m.group(2)}/embed"

        if re.search(r'facebook\.com/(?:.+/videos/|reel/|watch)', url):
            return f"https://www.facebook.com/plugins/video.php?href={quote(url, safe='')}&show_text=false"

        return None

    @property
    def embed_vertical(self):
        url = self.video_url or ""
        return any(d in url for d in ("tiktok.com", "instagram.com", "facebook.com/reel"))


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='videos')
    thumbnail = models.ImageField(upload_to='videos/thumbnails', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.title
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email
