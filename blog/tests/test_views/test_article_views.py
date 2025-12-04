from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import json
import io
import tempfile
import shutil
import os

from blog.models import Article, ArticleImage, Topic, Tag
from blog.forms import ArticleForm


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def create_test_image(name='test.jpg', size=(100, 100), color='red'):
    """Helper function to create a valid test image"""
    file = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type='image/jpeg'
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class IndexViewTest(TestCase):
    """Test suite for index view"""

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary media directory after all tests"""
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        self.url = reverse('blog:index')

    def test_index_view_status_code(self):
        """Test index view returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        """Test index view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'blog/index.html')

    def test_index_view_shows_published_articles_only(self):
        """Test index only displays published articles, not drafts"""
        published = Article.objects.create(
            title='Published Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user,
            published_at=timezone.now()
        )
        draft = Article.objects.create(
            title='Draft Article',
            content='Content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        
        response = self.client.get(self.url)
        
        self.assertIn(published, response.context['page_obj'])
        self.assertNotIn(draft, response.context['page_obj'])

    def test_index_view_pagination(self):
        """Test index view paginates articles correctly"""
        # Create 7 articles (more than ARTICLES_PER_PAGE = 5)
        for i in range(7):
            Article.objects.create(
                title=f'Article {i}',
                content='Content',
                status=Article.Status.PUBLISHED,
                topic=self.topic,
                author=self.user,
                published_at=timezone.now()
            )
        
        # First page should have 5 articles
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['page_obj']), 5)
        
        # Second page should have 2 articles
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_index_view_empty_page_returns_200_with_message(self):
        """Test index view returns 200 with message for empty page"""
        # Create only 2 articles
        for i in range(2):
            Article.objects.create(
                title=f'Article {i}',
                content='Content',
                status=Article.Status.PUBLISHED,
                topic=self.topic,
                author=self.user
            )
        
        # Request page 5 (doesn't exist)
        response = self.client.get(self.url + '?page=5')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.context)

    def test_index_view_invalid_page_number(self):
        """Test index view handles invalid page numbers"""
        Article.objects.create(
            title='Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user
        )
        
        # Test non-integer page number
        response = self.client.get(self.url + '?page=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('page_obj', response.context)

    def test_index_view_negative_page_number(self):
        """Test index view handles negative page numbers"""
        Article.objects.create(
            title='Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user
        )
        
        response = self.client.get(self.url + '?page=-1')
        self.assertEqual(response.status_code, 200)

    def test_index_view_includes_topics_in_context(self):
        """Test index view includes topics with article counts"""
        topic2 = Topic.objects.create(name='Science')
        
        Article.objects.create(
            title='Tech Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user
        )
        Article.objects.create(
            title='Science Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=topic2,
            author=self.user
        )
        
        response = self.client.get(self.url)
        
        self.assertIn('topics', response.context)
        topics = response.context['topics']
        self.assertEqual(topics.count(), 2)
        # Check annotation works
        for topic in topics:
            self.assertTrue(hasattr(topic, 'article_count'))

    def test_index_view_with_no_articles(self):
        """Test index view with no published articles"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticlesViewTest(TestCase):
    """Test suite for articles (detail) view"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        
        self.published_article = Article.objects.create(
            title='Published Article',
            content='Published content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user,
            published_at=timezone.now()
        )
        
        self.draft_article = Article.objects.create(
            title='Draft Article',
            content='Draft content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )

    def test_articles_view_published_article_unauthenticated(self):
        """Test unauthenticated users can view published articles"""
        url = reverse('blog:articles', args=[self.published_article.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article.html')
        self.assertEqual(response.context['article'], self.published_article)

    def test_articles_view_draft_article_unauthenticated_returns_404(self):
        """Test unauthenticated users cannot view draft articles"""
        url = reverse('blog:articles', args=[self.draft_article.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_articles_view_published_article_authenticated(self):
        """Test authenticated users can view published articles"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog:articles', args=[self.published_article.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['article'], self.published_article)

    def test_articles_view_draft_article_authenticated(self):
        """Test authenticated users can view draft articles"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog:articles', args=[self.draft_article.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['article'], self.draft_article)

    def test_articles_view_nonexistent_article_returns_404(self):
        """Test viewing non-existent article returns 404"""
        url = reverse('blog:articles', args=['nonexistent-slug'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_articles_view_uses_correct_template(self):
        """Test articles view uses correct template"""
        url = reverse('blog:articles', args=[self.published_article.slug])
        response = self.client.get(url)
        
        self.assertTemplateUsed(response, 'blog/article.html')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class EditViewTest(TestCase):
    """Test suite for edit view"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        self.tag = Tag.objects.create(name='Python', slug='python')
        
        self.article = Article.objects.create(
            title='Test Article',
            content='Original content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user,
            published_at=timezone.now()
        )
        self.url = reverse('blog:edit', args=[self.article.slug])

    def test_edit_view_requires_authentication(self):
        """Test edit view returns 404 for unauthenticated users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_edit_view_get_authenticated(self):
        """Test authenticated users can access edit view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/write.html')

    def test_edit_view_context_has_form(self):
        """Test edit view provides ArticleForm in context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ArticleForm)

    def test_edit_view_context_has_topic_form(self):
        """Test edit view provides TopicForm in context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertIn('topic_form', response.context)

    def test_edit_view_context_is_edit_true(self):
        """Test edit view sets is_edit to True"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertTrue(response.context['is_edit'])

    def test_edit_view_context_has_article_id(self):
        """Test edit view provides article_id in context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.context['article_id'], self.article.id)

    def test_edit_view_context_has_status(self):
        """Test edit view provides STATUS choices in context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertIn('STATUS', response.context)
        self.assertEqual(response.context['STATUS'], Article.Status)

    def test_edit_view_post_valid_data(self):
        """Test editing article with valid data"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'excerpt': 'Updated excerpt',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [self.tag.id],
            'image_ids': '[]',
        }
        
        response = self.client.post(self.url, data)
        
        # Should redirect to article detail
        self.article.refresh_from_db()
        self.assertRedirects(
            response,
            reverse('blog:articles', args=[self.article.slug])
        )
        
        # Check article was updated
        self.assertEqual(self.article.title, 'Updated Title')
        self.assertEqual(self.article.content, 'Updated content')

    def test_edit_view_post_invalid_data(self):
        """Test editing article with invalid data shows form errors"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': '',  # Invalid - required field
            'content': 'Content',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
        }
        
        response = self.client.post(self.url, data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_edit_view_published_at_not_updated_when_already_set(self):
        """Test published_at is not updated when already set"""
        self.client.login(username='testuser', password='testpass123')
        
        original_published_at = self.article.published_at
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'excerpt': '',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': '[]',
        }
        
        response = self.client.post(self.url, data)
        
        self.article.refresh_from_db()
        # published_at should remain the same
        self.assertEqual(self.article.published_at, original_published_at)

    def test_edit_view_nonexistent_article_returns_404(self):
        """Test editing non-existent article returns 404"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog:edit', args=['nonexistent-slug'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DraftsViewTest(TestCase):
    """Test suite for drafts view"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        
        self.draft = Article.objects.create(
            title='Draft Article',
            content='Draft content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        
        self.published = Article.objects.create(
            title='Published Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user,
            published_at=timezone.now()
        )
        
        self.url = reverse('blog:drafts', args=[self.draft.id])

    def test_drafts_view_requires_authentication(self):
        """Test drafts view returns 404 for unauthenticated users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_drafts_view_get_authenticated(self):
        """Test authenticated users can access drafts view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/write.html')

    def test_drafts_view_context_is_edit_false(self):
        """Test drafts view sets is_edit to False"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertFalse(response.context['is_edit'])

    def test_drafts_view_only_shows_draft_articles(self):
        """Test drafts view only accepts draft status articles"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access published article via drafts view
        url = reverse('blog:drafts', args=[self.published.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_drafts_view_post_publish_draft(self):
        """Test publishing a draft sets published_at for first time"""
        self.client.login(username='testuser', password='testpass123')
        
        self.assertIsNone(self.draft.published_at)
        
        data = {
            'title': 'Published Draft',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': '[]',
        }
        
        response = self.client.post(self.url, data)
        
        self.draft.refresh_from_db()
        
        # Should now have published_at set
        self.assertIsNotNone(self.draft.published_at)
        self.assertEqual(self.draft.status, Article.Status.PUBLISHED)

    def test_drafts_view_post_keep_draft_status(self):
        """Test saving draft without publishing doesn't set published_at"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'title': 'Still Draft',
            'content': 'Updated content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': '[]',
        }
        
        response = self.client.post(self.url, data)
        
        self.draft.refresh_from_db()
        
        # Should still be None
        self.assertIsNone(self.draft.published_at)
        self.assertEqual(self.draft.status, Article.Status.DRAFT)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticleEditorImageDeletionTest(TestCase):
    """Test suite for image deletion logic in _article_editor"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        
        self.article = Article.objects.create(
            title='Test Article',
            content='Content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        
        # Create test images
        self.image1 = ArticleImage.objects.create(
            article=self.article,
            image=create_test_image('image1.jpg')
        )
        self.image2 = ArticleImage.objects.create(
            article=self.article,
            image=create_test_image('image2.jpg')
        )
        self.image3 = ArticleImage.objects.create(
            article=self.article,
            image=create_test_image('image3.jpg')
        )
        
        self.url = reverse('blog:drafts', args=[self.article.id])
        self.client.login(username='testuser', password='testpass123')

    def test_article_editor_deletes_unused_images(self):
        """Test that images not in image_ids are deleted"""
        # Keep only image1 and image2
        data = {
            'title': 'Updated',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': json.dumps([self.image1.id, self.image2.id]),
        }
        
        response = self.client.post(self.url, data)
        
        # image3 should be deleted
        self.assertTrue(ArticleImage.objects.filter(id=self.image1.id).exists())
        self.assertTrue(ArticleImage.objects.filter(id=self.image2.id).exists())
        self.assertFalse(ArticleImage.objects.filter(id=self.image3.id).exists())

    def test_article_editor_keeps_all_images_when_all_in_use(self):
        """Test that all images are kept when all are in image_ids"""
        data = {
            'title': 'Updated',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': json.dumps([self.image1.id, self.image2.id, self.image3.id]),
        }
        
        response = self.client.post(self.url, data)
        
        # All images should still exist
        self.assertEqual(ArticleImage.objects.filter(article=self.article).count(), 3)

    def test_article_editor_deletes_all_images_when_none_in_use(self):
        """Test that all images are deleted when image_ids is empty"""
        data = {
            'title': 'Updated',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': '[]',
        }
        
        response = self.client.post(self.url, data)
        
        # All images should be deleted
        self.assertEqual(ArticleImage.objects.filter(article=self.article).count(), 0)

    def test_article_editor_handles_empty_image_ids(self):
        """Test that empty image_ids string deletes all images"""
        data = {
            'title': 'Updated',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': '',
        }
        
        response = self.client.post(self.url, data)
        
        # All images should be deleted
        self.assertEqual(ArticleImage.objects.filter(article=self.article).count(), 0)

    def test_article_editor_handles_invalid_json_image_ids(self):
        """Test that invalid JSON in image_ids raises appropriate error"""
        data = {
            'title': 'Updated',
            'content': 'Content',
            'excerpt': '',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'image_ids': 'invalid json{',
        }
        
        # This should raise a JSONDecodeError
        with self.assertRaises(json.JSONDecodeError):
            response = self.client.post(self.url, data)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class WriteViewTest(TestCase):
    """Test suite for write view"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('blog:write')

    def test_write_view_requires_authentication(self):
        """Test write view returns 404 for unauthenticated users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_write_view_creates_draft_and_redirects(self):
        """Test write view creates a new draft and redirects to drafts view"""
        self.client.login(username='testuser', password='testpass123')
        
        initial_count = Article.objects.count()
        
        response = self.client.get(self.url)
        
        # Should create one new article
        self.assertEqual(Article.objects.count(), initial_count + 1)
        
        # Get the newly created draft
        new_draft = Article.objects.latest('created_at')
        
        # Should be a draft
        self.assertEqual(new_draft.status, Article.Status.DRAFT)
        self.assertEqual(new_draft.author, self.user)
        
        # Should redirect to drafts view
        expected_url = reverse('blog:drafts', args=[new_draft.id])
        self.assertRedirects(response, expected_url)

    def test_write_view_creates_draft_with_correct_author(self):
        """Test write view assigns correct author to draft"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.url)
        
        new_draft = Article.objects.latest('created_at')
        self.assertEqual(new_draft.author, self.user)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticleDeleteViewTest(TestCase):
    """Test suite for article_delete view"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.topic = Topic.objects.create(name='Technology')
        
        self.article = Article.objects.create(
            title='Test Article',
            content='Content',
            status=Article.Status.PUBLISHED,
            topic=self.topic,
            author=self.user,
            published_at=timezone.now()
        )
        self.url = reverse('blog:article_delete', args=[self.article.id])

    def test_article_delete_requires_authentication(self):
        """Test article_delete returns 404 for unauthenticated users"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_article_delete_requires_post(self):
        """Test article_delete only accepts POST requests"""
        self.client.login(username='testuser', password='testpass123')
        
        # GET should not be allowed
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_article_delete_deletes_article(self):
        """Test article_delete removes article from database"""
        self.client.login(username='testuser', password='testpass123')
        
        article_id = self.article.id
        
        response = self.client.post(self.url)
        
        # Article should be deleted
        self.assertFalse(Article.objects.filter(id=article_id).exists())

    def test_article_delete_redirects_to_dashboard(self):
        """Test article_delete redirects to dashboard after deletion"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(self.url)
        
        self.assertRedirects(response, reverse('blog:dashboard'))

    def test_article_delete_nonexistent_article_returns_404(self):
        """Test deleting non-existent article returns 404"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('blog:article_delete', args=[99999])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 404)

    def test_article_delete_works_for_drafts(self):
        """Test article_delete works for draft articles"""
        self.client.login(username='testuser', password='testpass123')
        
        draft = Article.objects.create(
            title='Draft',
            content='Content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        
        url = reverse('blog:article_delete', args=[draft.id])
        
        response = self.client.post(url)
        
        # Draft should be deleted
        self.assertFalse(Article.objects.filter(id=draft.id).exists())
        self.assertRedirects(response, reverse('blog:dashboard'))

    def test_article_delete_with_associated_images(self):
        """Test deleting article also deletes associated images"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create images for the article
        image1 = ArticleImage.objects.create(
            article=self.article,
            image=create_test_image('image1.jpg')
        )
        image2 = ArticleImage.objects.create(
            article=self.article,
            image=create_test_image('image2.jpg')
        )
        
        response = self.client.post(self.url)
        
        # Images should be deleted (cascade delete)
        self.assertFalse(ArticleImage.objects.filter(id=image1.id).exists())
        self.assertFalse(ArticleImage.objects.filter(id=image2.id).exists())