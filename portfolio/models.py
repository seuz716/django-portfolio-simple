from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/images/')
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    technologies = models.ManyToManyField('Technology', related_name='projects')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

class Technology(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
