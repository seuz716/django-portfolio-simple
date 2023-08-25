from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import Project

def home(request):
    try:
        projects = Project.objects.all()
    except Exception as e:
        messages.error(request, f"Error al obtener los proyectos: {str(e)}")
        projects = []

    context = {
        'projects': projects
    }
    return render(request, 'home.html', context)
