from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class News(models.Model):
    title = models.CharField(max_length=200, help_text="News article title")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL-friendly version of the title")
    content = models.TextField(help_text="Full article content")
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short summary for preview")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_articles')
    featured_image = models.ImageField(upload_to='news/images/', blank=True, null=True, help_text="Featured image for the article")
    published = models.BooleanField(default=False, help_text="Publish this article")
    published_at = models.DateTimeField(null=True, blank=True, help_text="When this article was published")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.published and self.published_at is not None