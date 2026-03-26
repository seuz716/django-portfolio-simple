"""
Test Fixtures for Django Portfolio Project
Provides reusable test data and utilities
"""
import pytest
import datetime
from django.contrib.auth.models import User
from django.utils import timezone

from blog.models import Post
from portfolio.models import Project, Technology


@pytest.fixture
def test_user():
    """Create a test user for authentication tests"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def superuser():
    """Create a superuser for admin tests"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def sample_technology():
    """Create a sample technology"""
    return Technology.objects.create(name='Django')


@pytest.fixture
def sample_technologies():
    """Create multiple technologies"""
    techs = [
        Technology.objects.create(name='Python'),
        Technology.objects.create(name='Django'),
        Technology.objects.create(name='PostgreSQL'),
        Technology.objects.create(name='React'),
    ]
    return techs


@pytest.fixture
def sample_project(sample_technologies):
    """Create a sample project with technologies"""
    project = Project.objects.create(
        title='Test Project',
        description='A test project description',
        url='https://example.com',
        slug='test-project'
    )
    project.technologies.set(sample_technologies[:2])
    return project


@pytest.fixture
def sample_projects(sample_technologies):
    """Create multiple sample projects"""
    projects = []
    for i in range(5):
        project = Project.objects.create(
            title=f'Project {i+1}',
            description=f'Description for project {i+1}',
            url=f'https://example{i+1}.com',
            slug=f'project-{i+1}'
        )
        project.technologies.set(sample_technologies[:i+1])
        projects.append(project)
    return projects


@pytest.fixture
def sample_post(test_user):
    """Create a sample blog post"""
    return Post.objects.create(
        title='Test Post',
        slug='test-post',
        author=test_user,
        content='This is test content for the blog post.',
        created_at=timezone.now(),
        date=datetime.date.today()
    )


@pytest.fixture
def sample_posts(test_user):
    """Create multiple blog posts"""
    posts = []
    for i in range(5):
        post = Post.objects.create(
            title=f'Test Post {i+1}',
            slug=f'test-post-{i+1}',
            author=test_user,
            content=f'Content for post number {i+1}',
            created_at=timezone.now(),
            date=datetime.date.today()
        )
        posts.append(post)
    return posts


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    client.force_login(test_user)
    return client


@pytest.fixture
def admin_client_authenticated(admin_client, superuser):
    """Ensure admin client is logged in as superuser"""
    admin_client.force_login(superuser)
    return admin_client
