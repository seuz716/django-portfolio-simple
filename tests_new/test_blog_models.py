"""
Unit Tests for Blog Models
Tests Post model functionality, validation, and business logic
Coverage Target: >95%
"""
import pytest
import datetime
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from blog.models import Post


@pytest.mark.django_db
class TestPostModel:
    """Test suite for Post model"""

    def test_create_post_success(self, test_user):
        """Test successful post creation with all required fields"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=test_user,
            content='Test content',
            date=datetime.date.today()
        )
        
        assert post.title == 'Test Post'
        assert post.slug == 'test-post'
        assert post.author == test_user
        assert post.content == 'Test content'
        assert isinstance(post.created_at, datetime.datetime)
        assert isinstance(post.updated_at, datetime.datetime)

    def test_post_str_representation(self, test_user):
        """Test __str__ method returns title"""
        post = Post.objects.create(
            title='My Amazing Post',
            slug='my-amazing-post',
            author=test_user,
            content='Content here'
        )
        
        assert str(post) == 'My Amazing Post'

    def test_post_slug_unique_constraint(self, test_user):
        """Test that slug must be unique"""
        Post.objects.create(
            title='First Post',
            slug='unique-slug',
            author=test_user,
            content='First content'
        )
        
        with pytest.raises(IntegrityError):
            Post.objects.create(
                title='Second Post',
                slug='unique-slug',  # Duplicate slug
                author=test_user,
                content='Second content'
            )

    def test_post_created_at_default(self, test_user):
        """Test created_at uses timezone.now as default"""
        before_creation = timezone.now()
        post = Post.objects.create(
            title='Time Test Post',
            slug='time-test-post',
            author=test_user,
            content='Testing timestamps'
        )
        after_creation = timezone.now()
        
        assert before_creation <= post.created_at <= after_creation

    def test_post_updated_at_auto_now(self, test_user):
        """Test updated_at is automatically updated on save"""
        post = Post.objects.create(
            title='Update Test Post',
            slug='update-test-post',
            author=test_user,
            content='Original content'
        )
        
        original_updated = post.updated_at
        
        # Wait a moment and update
        import time
        time.sleep(0.1)
        
        post.content = 'Updated content'
        post.save()
        
        # Reload from database
        post.refresh_from_db()
        assert post.updated_at > original_updated

    def test_post_date_default(self, test_user):
        """Test date field defaults to today"""
        post = Post.objects.create(
            title='Date Test Post',
            slug='date-test-post',
            author=test_user,
            content='Testing date'
        )
        
        assert post.date == datetime.date.today()

    def test_post_content_max_length_validation(self, test_user):
        """Test that content can handle large text"""
        long_content = 'A' * 10000  # 10k characters
        post = Post.objects.create(
            title='Long Content Post',
            slug='long-content-post',
            author=test_user,
            content=long_content
        )
        
        assert len(post.content) == 10000
        assert post.content == long_content

    def test_post_title_max_length(self, test_user):
        """Test title respects max_length of 100"""
        title_100_chars = 'A' * 100
        post = Post.objects.create(
            title=title_100_chars,
            slug='max-length-title',
            author=test_user,
            content='Content'
        )
        
        assert len(post.title) == 100
        
        # Test that 101 chars would fail (depends on DB backend)
        title_101_chars = 'A' * 101
        with pytest.raises(Exception):
            Post.objects.create(
                title=title_101_chars,
                slug='too-long-title',
                author=test_user,
                content='Content'
            )

    def test_post_author_cascade_delete(self, test_user):
        """Test that posts are deleted when author is deleted"""
        post = Post.objects.create(
            title='Cascade Test Post',
            slug='cascade-test-post',
            author=test_user,
            content='Will be deleted with user'
        )
        
        post_id = post.id
        test_user.delete()
        
        # Post should be deleted due to CASCADE
        assert not Post.objects.filter(id=post_id).exists()

    def test_post_queryset_ordering(self, test_user):
        """Test posts are ordered by created_at descending"""
        # Create posts in reverse order
        post3 = Post.objects.create(
            title='Third Post',
            slug='third-post',
            author=test_user,
            content='Third'
        )
        import time
        time.sleep(0.01)
        
        post1 = Post.objects.create(
            title='First Post',
            slug='first-post',
            author=test_user,
            content='First'
        )
        
        posts = list(Post.objects.all())
        # Most recent should be first
        assert posts[0] == post1

    def test_post_get_absolute_url(self, test_user):
        """Test get_absolute_url returns correct URL"""
        post = Post.objects.create(
            title='URL Test Post',
            slug='url-test-post',
            author=test_user,
            content='Testing URL'
        )
        
        # Note: This will fail if URL pattern doesn't exist
        # We're testing the method exists and returns a string
        url = post.get_absolute_url()
        assert isinstance(url, str)
        assert 'url-test-post' in url

    def test_post_image_upload_path(self, test_user):
        """Test image upload_to path configuration"""
        post = Post.objects.create(
            title='Image Test Post',
            slug='image-test-post',
            author=test_user,
            content='Testing image upload'
        )
        
        # Check the field configuration
        image_field = Post._meta.get_field('image')
        assert image_field.upload_to == 'blog/images/'

    def test_post_filter_by_author(self, test_user):
        """Test filtering posts by author"""
        author2 = User.objects.create_user(
            username='author2',
            email='author2@example.com',
            password='pass123'
        )
        
        Post.objects.create(
            title='Post by User 1',
            slug='post-user-1',
            author=test_user,
            content='Content 1'
        )
        Post.objects.create(
            title='Post by User 2',
            slug='post-user-2',
            author=author2,
            content='Content 2'
        )
        
        user1_posts = Post.objects.filter(author=test_user)
        user2_posts = Post.objects.filter(author=author2)
        
        assert user1_posts.count() == 1
        assert user2_posts.count() == 1
        assert user1_posts.first().title == 'Post by User 1'

    def test_post_filter_by_date_range(self, test_user):
        """Test filtering posts by date range"""
        old_date = datetime.date(2020, 1, 1)
        new_date = datetime.date.today()
        
        old_post = Post.objects.create(
            title='Old Post',
            slug='old-post',
            author=test_user,
            content='Old content',
            date=old_date
        )
        new_post = Post.objects.create(
            title='New Post',
            slug='new-post',
            author=test_user,
            content='New content',
            date=new_date
        )
        
        recent_posts = Post.objects.filter(date__gte=datetime.date(2023, 1, 1))
        
        assert recent_posts.count() >= 1
        assert new_post in recent_posts
        assert old_post not in recent_posts
