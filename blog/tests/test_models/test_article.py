import os
import tempfile
import shutil

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import timedelta

from blog.models import Topic, Tag, Article


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticleModelTest(TestCase):
    """Test suite for Article model"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.topic = Topic.objects.create(name="Technology")
        self.tag1 = Tag.objects.create(name="Python", slug="python")
        self.tag2 = Tag.objects.create(name="Django", slug="django")

    def test_article_creation_with_minimal_fields(self):
        """Test article creation with only required fields"""
        article = Article.objects.create(
            title="Test Article",
            content="Test content",
            author=self.user
        )
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.status, Article.Status.DRAFT)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)

    def test_article_auto_slug_generation(self):
        """Test that slug is automatically generated from title"""
        article = Article.objects.create(
            title="My Awesome Article",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.slug, "my-awesome-article")

    def test_article_slug_uniqueness_with_duplicates(self):
        """Test that duplicate titles get unique slugs"""
        article1 = Article.objects.create(
            title="Same Title",
            content="Content 1",
            author=self.user
        )
        article2 = Article.objects.create(
            title="Same Title",
            content="Content 2",
            author=self.user
        )
        article3 = Article.objects.create(
            title="Same Title",
            content="Content 3",
            author=self.user
        )
        
        self.assertEqual(article1.slug, "same-title")
        self.assertEqual(article2.slug, "same-title-1")
        self.assertEqual(article3.slug, "same-title-2")

    def test_article_slug_with_special_characters(self):
        """Test slug generation with special characters"""
        article = Article.objects.create(
            title="Article with @#$% Special Chars!",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.slug, "article-with-special-chars")

    def test_article_custom_slug_not_overwritten(self):
        """Test that custom slug is preserved"""
        article = Article.objects.create(
            title="My Article",
            slug="custom-slug",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.slug, "custom-slug")

    def test_article_slug_not_changed_on_update(self):
        """Test that slug doesn't change when title is updated"""
        article = Article.objects.create(
            title="Original Title",
            content="Content",
            author=self.user
        )
        original_slug = article.slug
        
        article.title = "Updated Title"
        article.save()
        
        self.assertEqual(article.slug, original_slug)

    def test_article_with_topic(self):
        """Test article with topic relationship"""
        article = Article.objects.create(
            title="Tech Article",
            content="Content",
            author=self.user,
            topic=self.topic
        )
        self.assertEqual(article.topic, self.topic)

    def test_article_topic_set_null_on_delete(self):
        """Test that article's topic is set to null when topic is deleted"""
        article = Article.objects.create(
            title="Tech Article",
            content="Content",
            author=self.user,
            topic=self.topic
        )
        self.topic.delete()
        article.refresh_from_db()
        self.assertIsNone(article.topic)

    def test_article_with_tags(self):
        """Test article with many-to-many tags"""
        article = Article.objects.create(
            title="Tech Article",
            content="Content",
            author=self.user
        )
        article.tags.add(self.tag1, self.tag2)
        
        self.assertEqual(article.tags.count(), 2)
        self.assertIn(self.tag1, article.tags.all())
        self.assertIn(self.tag2, article.tags.all())

    def test_article_without_tags(self):
        """Test that article can exist without tags"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.tags.count(), 0)

    def test_article_status_choices(self):
        """Test all article status choices"""
        draft = Article.objects.create(
            title="Draft Article",
            content="Content",
            author=self.user,
            status=Article.Status.DRAFT
        )
        scheduled = Article.objects.create(
            title="Scheduled Article",
            content="Content",
            author=self.user,
            status=Article.Status.SCHEDULED
        )
        published = Article.objects.create(
            title="Published Article",
            content="Content",
            author=self.user,
            status=Article.Status.PUBLISHED
        )
        
        self.assertEqual(draft.status, "DR")
        self.assertEqual(scheduled.status, "SC")
        self.assertEqual(published.status, "PU")

    def test_article_default_status_is_draft(self):
        """Test that default status is DRAFT"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.status, Article.Status.DRAFT)

    def test_article_blank_excerpt(self):
        """Test that excerpt can be blank"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user
        )
        self.assertEqual(article.excerpt, "")

    def test_article_with_excerpt(self):
        """Test article with excerpt"""
        article = Article.objects.create(
            title="Article",
            content="Full content here",
            excerpt="Short excerpt",
            author=self.user
        )
        self.assertEqual(article.excerpt, "Short excerpt")

    def test_article_published_at_null_by_default(self):
        """Test that published_at is null by default"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user
        )
        self.assertIsNone(article.published_at)

    def test_article_is_published_returns_true(self):
        """Test is_published returns True for published articles"""
        past_time = timezone.now() - timedelta(hours=1)
        article = Article.objects.create(
            title="Published Article",
            content="Content",
            author=self.user,
            status=Article.Status.PUBLISHED,
            published_at=past_time
        )
        self.assertTrue(article.is_published())

    def test_article_is_published_returns_false_for_draft(self):
        """Test is_published returns False for draft articles"""
        article = Article.objects.create(
            title="Draft Article",
            content="Content",
            author=self.user,
            status=Article.Status.DRAFT
        )
        self.assertFalse(article.is_published())

    def test_article_is_published_returns_false_for_scheduled(self):
        """Test is_published returns False for scheduled articles"""
        future_time = timezone.now() + timedelta(hours=1)
        article = Article.objects.create(
            title="Scheduled Article",
            content="Content",
            author=self.user,
            status=Article.Status.SCHEDULED,
            published_at=future_time
        )
        self.assertFalse(article.is_published())

    def test_article_is_published_returns_false_without_published_at(self):
        """Test is_published returns False when published_at is None"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user,
            status=Article.Status.PUBLISHED,
            published_at=None
        )
        self.assertFalse(article.is_published())

    def test_article_is_published_returns_false_for_future_date(self):
        """Test is_published returns False for future published_at"""
        future_time = timezone.now() + timedelta(hours=1)
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user,
            status=Article.Status.PUBLISHED,
            published_at=future_time
        )
        self.assertFalse(article.is_published())

    def test_article_is_published_edge_case_exact_time(self):
        """Test is_published at exact boundary time"""
        now = timezone.now()
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user,
            status=Article.Status.PUBLISHED,
            published_at=now
        )
        # Should return True since published_at <= now
        self.assertTrue(article.is_published())

    def test_article_ordering(self):
        """Test that articles are ordered by published_at desc, then created_at desc"""
        now = timezone.now()
        
        article1 = Article.objects.create(
            title="First",
            content="Content",
            author=self.user,
            published_at=now - timedelta(days=3)
        )
        article2 = Article.objects.create(
            title="Second",
            content="Content",
            author=self.user,
            published_at=now - timedelta(days=1)
        )
        article3 = Article.objects.create(
            title="Third",
            content="Content",
            author=self.user
        )
        
        articles = list(Article.objects.all())
        self.assertEqual(articles[0], article2)  # Most recent published_at
        self.assertEqual(articles[1], article1)
        self.assertEqual(articles[2], article3)  # Null published_at comes last

    def test_article_author_cascade_delete(self):
        """Test that articles are deleted when author is deleted"""
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user
        )
        article_id = article.id
        
        self.user.delete()
        
        self.assertFalse(Article.objects.filter(id=article_id).exists())

    def test_article_with_featured_image(self):
        """Test article with featured image"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        article = Article.objects.create(
            title="Article",
            content="Content",
            author=self.user,
            featured_image=image
        )
        self.assertTrue(article.featured_image)
        self.assertIn('test_image', article.featured_image.name)

    def test_article_search_serialize(self):
        """Test search serialization of article"""
        article = Article.objects.create(
            title="Test Article",
            content="Content",
            author=self.user
        )
        serialized = article.search_serialize()
        
        self.assertEqual(serialized["title"], "Test Article")
        self.assertEqual(serialized["slug"], article.slug)
        self.assertEqual(len(serialized), 2)  # Only title and slug

    def test_article_str_method(self):
        """Test string representation of article"""
        article = Article.objects.create(
            title="My Article",
            content="Content",
            author=self.user
        )
        self.assertEqual(str(article), "My Article")

    def test_article_updated_at_changes_on_save(self):
        """Test that updated_at changes when article is saved"""
        article = Article.objects.create(
            title="Article",
            content="Original content",
            author=self.user
        )
        original_updated_at = article.updated_at
        
        # Wait a tiny bit and update
        article.content = "Updated content"
        article.save()
        
        self.assertGreater(article.updated_at, original_updated_at)
