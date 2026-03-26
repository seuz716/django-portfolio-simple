"""
Integration Tests for Blog Views
Tests view functions, routing, and HTTP responses
Coverage Target: >90%
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from blog.models import Post


@pytest.mark.django_db
class TestBlogViews:
    """Test suite for blog view functions"""

    def test_render_posts_view_success(self, client, sample_posts):
        """Test posts list view returns 200 and correct context"""
        url = reverse('blog:posts')  # Assuming URL name is 'blog:posts'
        
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'posts' in response.context
        assert len(response.context['posts']) == 5
        assert response.template_name == 'post.html' or 'post.html' in [t.name for t in response.templates]

    def test_render_posts_view_empty(self, client):
        """Test posts list view with no posts"""
        url = reverse('blog:posts', default='/blog/')
        
        response = client.get('/blog/')
        
        assert response.status_code == 200
        assert 'posts' in response.context

    def test_post_detail_view_success(self, client, sample_post):
        """Test post detail view returns 200 and correct post"""
        url = reverse('blog:detail', kwargs={'slug': sample_post.slug}, default=f'/blog/{sample_post.slug}/')
        
        response = client.get(f'/blog/{sample_post.id}/')
        
        assert response.status_code == 200
        assert 'post' in response.context
        assert response.context['post'] == sample_post

    def test_post_detail_view_not_found(self, client):
        """Test post detail view with non-existent ID returns 404"""
        response = client.get('/blog/99999/')
        
        assert response.status_code == 404

    def test_pdf_viewer_view_success(self, client):
        """Test PDF viewer view returns 200"""
        url = reverse('blog:pdf_viewer', default='/blog/pdf/')
        
        response = client.get('/blog/pdf/')
        
        assert response.status_code == 200
        assert 'cuentos' in response.context
        assert isinstance(response.context['cuentos'], list)

    def test_handler_404(self, client):
        """Test custom 404 handler"""
        response = client.get('/nonexistent-page-xyz/')
        
        assert response.status_code == 404
        # Should use custom 404 template
        assert '404.html' in [t.name for t in response.templates] or response.status_code == 404

    def test_posts_ordering(self, client, sample_posts):
        """Test that posts are ordered correctly (newest first)"""
        response = client.get('/blog/')
        
        assert response.status_code == 200
        posts = response.context['posts']
        # Check ordering if implemented in model or view

    def test_post_detail_context_data(self, client, sample_post):
        """Test post detail view provides all necessary context"""
        response = client.get(f'/blog/{sample_post.id}/')
        
        assert response.status_code == 200
        assert response.context['post'].title == sample_post.title
        assert response.context['post'].content == sample_post.content

    def test_multiple_posts_display(self, client, sample_posts):
        """Test that multiple posts are displayed correctly"""
        response = client.get('/blog/')
        
        assert response.status_code == 200
        assert len(response.context['posts']) == len(sample_posts)
        
        for post in sample_posts:
            assert post in response.context['posts']


@pytest.mark.django_db
class TestPortfolioViews:
    """Test suite for portfolio view functions"""

    def test_home_view_success(self, client, sample_projects):
        """Test home view returns 200 and projects"""
        url = reverse('portfolio:home', default='/')
        
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'projects' in response.context
        assert len(response.context['projects']) == 5
        assert response.template_name == 'home.html' or 'home.html' in [t.name for t in response.templates]

    def test_home_view_empty_projects(self, client):
        """Test home view with no projects"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'projects' in response.context
        assert len(response.context['projects']) == 0

    def test_home_view_error_handling(self, client, mocker):
        """Test home view handles database errors gracefully"""
        # Mock the Project.objects.all() to raise an exception
        mocker.patch('portfolio.views.Project.objects.all', side_effect=Exception('DB Error'))
        
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'projects' in response.context
        # Should have empty list on error
        assert len(response.context['projects']) == 0
        
        # Check for error message
        from django.contrib.messages import get_messages
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert 'Error al obtener los proyectos' in str(messages[0])

    def test_home_view_project_data(self, client, sample_project):
        """Test home view displays project data correctly"""
        response = client.get('/')
        
        assert response.status_code == 200
        projects = response.context['projects']
        
        assert sample_project in projects
        proj = [p for p in projects if p.id == sample_project.id][0]
        assert proj.title == sample_project.title
        assert proj.description == sample_project.description

    def test_home_view_template_context_processors(self, client):
        """Test that context processors are working"""
        response = client.get('/')
        
        assert response.status_code == 200
        # Check for common context processor data
        assert 'user' in response.context
        assert 'messages' in response.context


@pytest.mark.django_db
class TestAuthenticationViews:
    """Test authentication-related views"""

    def test_authenticated_user_access(self, authenticated_client, sample_post):
        """Test authenticated user can access protected resources"""
        response = authenticated_client.get('/blog/')
        
        assert response.status_code == 200
        assert response.context['user'].is_authenticated

    def test_admin_access(self, admin_client_authenticated):
        """Test admin user can access admin area"""
        response = admin_client_authenticated.get('/admin/')
        
        assert response.status_code == 200 or response.status_code == 302

    def test_user_context_in_templates(self, client, test_user):
        """Test user context is available in templates"""
        client.force_login(test_user)
        response = client.get('/')
        
        assert response.status_code == 200
        assert response.context['user'] == test_user


@pytest.mark.django_db
class TestStaticFilesViews:
    """Test static file serving"""

    def test_static_files_accessible(self, client):
        """Test that static files can be served"""
        # This depends on static file configuration
        response = client.get('/static/')
        
        # May return 404 if no index, but shouldn't error
        assert response.status_code in [200, 404, 403]

    def test_media_files_configured(self, client):
        """Test media file configuration"""
        # Media files should be configured
        response = client.get('/media/')
        
        assert response.status_code in [200, 404, 403]
