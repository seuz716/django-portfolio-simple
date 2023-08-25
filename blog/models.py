from django.db import models
from django.utils import timezone
import datetime

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/images/')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
