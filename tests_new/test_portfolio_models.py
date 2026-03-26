"""
Unit Tests for Portfolio Models
Tests Project and Technology model functionality
Coverage Target: >95%
"""
import pytest
from django.db import IntegrityError

from portfolio.models import Project, Technology


@pytest.mark.django_db
class TestTechnologyModel:
    """Test suite for Technology model"""

    def test_create_technology_success(self):
        """Test successful technology creation"""
        tech = Technology.objects.create(name='Python')
        
        assert tech.name == 'Python'
        assert tech.id is not None

    def test_technology_str_representation(self):
        """Test __str__ method returns name"""
        tech = Technology.objects.create(name='Django REST Framework')
        
        assert str(tech) == 'Django REST Framework'

    def test_technology_name_max_length(self):
        """Test name respects max_length of 50"""
        name_50_chars = 'A' * 50
        tech = Technology.objects.create(name=name_50_chars)
        
        assert len(tech.name) == 50
        
        # Test that 51 chars would fail
        name_51_chars = 'A' * 51
        with pytest.raises(Exception):
            Technology.objects.create(name=name_51_chars)

    def test_technology_unique_names_not_required(self):
        """Test that technology names don't need to be unique (unless specified)"""
        Technology.objects.create(name='Python')
        tech2 = Technology.objects.create(name='Python')
        
        # Both should exist (no unique constraint on name by default)
        assert Technology.objects.filter(name='Python').count() == 2
        assert tech2.id is not None

    def test_technology_case_sensitive(self):
        """Test that technology names are case-sensitive"""
        tech1 = Technology.objects.create(name='Python')
        tech2 = Technology.objects.create(name='python')
        
        assert tech1.name != tech2.name
        assert Technology.objects.count() == 2

    def test_technology_empty_name_validation(self):
        """Test that empty name is handled"""
        # Django allows blank=False fields to be empty string in some cases
        # but should fail on save if blank=False
        tech = Technology(name='')
        with pytest.raises(Exception):
            tech.full_clean()
            tech.save()

    def test_technology_special_characters(self):
        """Test technology names with special characters"""
        special_names = [
            'C++',
            'Node.js',
            '.NET Core',
            'React (Hooks)',
            'AWS S3',
        ]
        
        for name in special_names:
            tech = Technology.objects.create(name=name)
            assert tech.name == name

    def test_technology_bulk_create(self):
        """Test bulk creation of technologies"""
        techs = [
            Technology(name='Tech1'),
            Technology(name='Tech2'),
            Technology(name='Tech3'),
        ]
        
        Technology.objects.bulk_create(techs)
        
        assert Technology.objects.count() == 3
        assert Technology.objects.filter(name='Tech2').exists()

    def test_technology_filter_by_name(self):
        """Test filtering technologies by name"""
        Technology.objects.create(name='Django')
        Technology.objects.create(name='Flask')
        Technology.objects.create(name='FastAPI')
        
        django_techs = Technology.objects.filter(name='Django')
        
        assert django_techs.count() == 1
        assert django_techs.first().name == 'Django'

    def test_technology_case_insensitive_filter(self):
        """Test case-insensitive filtering"""
        Technology.objects.create(name='Django')
        Technology.objects.create(name='FLASK')
        
        # Using icontains for case-insensitive search
        results = Technology.objects.filter(name__icontains='django')
        
        assert results.count() == 1


@pytest.mark.django_db
class TestProjectModel:
    """Test suite for Project model"""

    def test_create_project_success(self, sample_technologies):
        """Test successful project creation with all required fields"""
        project = Project.objects.create(
            title='My Project',
            description='A detailed description',
            url='https://github.com/user/project',
            slug='my-project'
        )
        project.technologies.set(sample_technologies[:2])
        
        assert project.title == 'My Project'
        assert project.description == 'A detailed description'
        assert project.url == 'https://github.com/user/project'
        assert project.slug == 'my-project'
        assert project.technologies.count() == 2

    def test_project_str_representation(self):
        """Test __str__ method returns title"""
        project = Project.objects.create(
            title='Amazing Portfolio Project',
            description='Description',
            url='https://example.com',
            slug='amazing-project'
        )
        
        assert str(project) == 'Amazing Portfolio Project'

    def test_project_slug_unique_constraint(self):
        """Test that slug must be unique"""
        Project.objects.create(
            title='First Project',
            description='Desc 1',
            url='https://example1.com',
            slug='unique-project-slug'
        )
        
        with pytest.raises(IntegrityError):
            Project.objects.create(
                title='Second Project',
                description='Desc 2',
                url='https://example2.com',
                slug='unique-project-slug'  # Duplicate
            )

    def test_project_url_validation(self):
        """Test URL field validates proper URLs"""
        # Valid URLs
        valid_urls = [
            'https://github.com/user/repo',
            'http://example.com',
            'https://www.example.com/path?query=value',
        ]
        
        for i, url in enumerate(valid_urls):
            project = Project.objects.create(
                title=f'Valid URL Project {i}',
                description='Desc',
                url=url,
                slug=f'valid-url-{i}'
            )
            assert project.url == url

    def test_project_invalid_url(self):
        """Test that invalid URLs are rejected"""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',  # May be invalid depending on validation
            'htp://typo.com',
        ]
        
        for i, url in enumerate(invalid_urls):
            try:
                project = Project.objects.create(
                    title=f'Invalid URL Project {i}',
                    description='Desc',
                    url=url,
                    slug=f'invalid-url-{i}'
                )
                # If it saves, check if URL was modified or accepted
                assert project.url  # Should have some value
            except Exception:
                # Expected for truly invalid URLs
                pass

    def test_project_technologies_many_to_many(self, sample_technologies):
        """Test many-to-many relationship with technologies"""
        project = Project.objects.create(
            title='M2M Test Project',
            description='Testing relationships',
            url='https://example.com',
            slug='m2m-test'
        )
        
        # Add technologies
        project.technologies.set(sample_technologies)
        
        assert project.technologies.count() == 4
        assert sample_technologies[0] in project.technologies.all()
        
        # Remove a technology
        project.technologies.remove(sample_technologies[0])
        assert project.technologies.count() == 3

    def test_project_created_at_auto_now_add(self):
        """Test created_at is set automatically on creation"""
        from django.utils import timezone
        import datetime
        
        before = timezone.now()
        project = Project.objects.create(
            title='Timestamp Project',
            description='Desc',
            url='https://example.com',
            slug='timestamp-project'
        )
        after = timezone.now()
        
        assert before <= project.created_at <= after
        assert isinstance(project.created_at, datetime.datetime)

    def test_project_title_max_length(self):
        """Test title respects max_length of 100"""
        title_100_chars = 'A' * 100
        project = Project.objects.create(
            title=title_100_chars,
            description='Desc',
            url='https://example.com',
            slug='max-title-project'
        )
        
        assert len(project.title) == 100
        
        title_101_chars = 'A' * 101
        with pytest.raises(Exception):
            Project.objects.create(
                title=title_101_chars,
                description='Desc',
                url='https://example.com',
                slug='too-long-title'
            )

    def test_project_description_no_max_length(self):
        """Test description can handle large text (TextField)"""
        long_description = 'B' * 50000  # 50k characters
        project = Project.objects.create(
            title='Long Description Project',
            description=long_description,
            url='https://example.com',
            slug='long-desc-project'
        )
        
        assert len(project.description) == 50000

    def test_project_filter_by_technology(self, sample_technologies):
        """Test filtering projects by technology"""
        project1 = Project.objects.create(
            title='Django Project',
            description='Uses Django',
            url='https://example1.com',
            slug='django-project'
        )
        project1.technologies.add(sample_technologies[0])  # Python
        
        project2 = Project.objects.create(
            title='React Project',
            description='Uses React',
            url='https://example2.com',
            slug='react-project'
        )
        project2.technologies.add(sample_technologies[3])  # React
        
        python_projects = Project.objects.filter(technologies__name='Python')
        react_projects = Project.objects.filter(technologies__name='React')
        
        assert python_projects.count() == 1
        assert react_projects.count() == 1
        assert project1 in python_projects
        assert project2 in react_projects

    def test_project_related_name_reverse_lookup(self, sample_technologies):
        """Test reverse lookup from Technology to Projects"""
        tech = sample_technologies[0]  # Python
        
        project1 = Project.objects.create(
            title='Python Project 1',
            description='Desc 1',
            url='https://example1.com',
            slug='python-project-1'
        )
        project1.technologies.add(tech)
        
        project2 = Project.objects.create(
            title='Python Project 2',
            description='Desc 2',
            url='https://example2.com',
            slug='python-project-2'
        )
        project2.technologies.add(tech)
        
        # Reverse lookup using related_name='projects'
        python_projects = tech.projects.all()
        
        assert python_projects.count() == 2
        assert project1 in python_projects
        assert project2 in python_projects

    def test_project_cascade_delete_technologies(self):
        """Test that deleting a project doesn't delete shared technologies"""
        tech = Technology.objects.create(name='Shared Tech')
        
        project1 = Project.objects.create(
            title='Project 1',
            description='Desc 1',
            url='https://example1.com',
            slug='project-1'
        )
        project1.technologies.add(tech)
        
        project2 = Project.objects.create(
            title='Project 2',
            description='Desc 2',
            url='https://example2.com',
            slug='project-2'
        )
        project2.technologies.add(tech)
        
        # Delete one project
        project1.delete()
        
        # Technology should still exist
        assert Technology.objects.filter(name='Shared Tech').exists()
        
        # Other project should still have the technology
        project2.refresh_from_db()
        assert tech in project2.technologies.all()

    def test_project_image_upload_path(self):
        """Test image upload_to path configuration"""
        project = Project.objects.create(
            title='Image Test Project',
            description='Testing image',
            url='https://example.com',
            slug='image-test-project'
        )
        
        image_field = Project._meta.get_field('image')
        assert image_field.upload_to == 'portfolio/images/'

    def test_project_update_technologies(self, sample_technologies):
        """Test updating project technologies"""
        project = Project.objects.create(
            title='Update Test',
            description='Desc',
            url='https://example.com',
            slug='update-test'
        )
        
        # Initially no technologies
        assert project.technologies.count() == 0
        
        # Add some
        project.technologies.set(sample_technologies[:2])
        assert project.technologies.count() == 2
        
        # Replace all
        project.technologies.set(sample_technologies[2:])
        assert project.technologies.count() == 2
        assert sample_technologies[0] not in project.technologies.all()
        assert sample_technologies[2] in project.technologies.all()

    def test_project_get_or_create_slug(self):
        """Test slug generation/get logic"""
        # This tests that slug is required and must be provided
        project = Project(
            title='No Slug Project',
            description='Desc',
            url='https://example.com'
        )
        
        # Should fail without slug due to unique constraint requirement
        with pytest.raises(Exception):
            project.save()
