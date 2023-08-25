from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import render_posts, post_detail, handler404, handler500, pdf_viewer


app_name = 'blog'

urlpatterns = [
    path('', render_posts, name='posts'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('pdf-viewer/', pdf_viewer, name='pdf-viewer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'blog.views.handler404'
handler500 = 'blog.views.handler500'
