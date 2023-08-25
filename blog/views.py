from django.conf import settings
import os
from .models import Post
from django.shortcuts import render, get_object_or_404

def render_posts(request):
    posts = Post.objects.all()
    context = {
        'posts': posts
    }
    return render(request, 'post.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post
    }
    return render(request, 'post_detail.html', context)


def pdf_viewer(request):
   

    # Ruta a la carpeta de cuentos
    carpeta_cuentos = os.path.join(settings.BASE_DIR, 'blog/static/blog/')

    # Obtener la lista de archivos en la carpeta de cuentos
    cuentos = os.listdir(carpeta_cuentos)

    # Pasar la lista de cuentos al contexto
    context = {
        'cuentos': cuentos
    }

    return render(request, 'pdf_viewer.html', context)




def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
