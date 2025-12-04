import json
import tempfile
import shutil
import os

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django import forms

from ...models import Article, Topic, Tag
from ...forms import ArticleForm, Html5DateInput


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticleFormTest(TestCase):
    """Test suite for ArticleForm"""

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary media directory after all tests"""
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.topic = Topic.objects.create(
            name="Technology",
            description="Tech topics"
        )
        self.tag1 = Tag.objects.create(name="Python", slug="python")
        self.tag2 = Tag.objects.create(name="Django", slug="django")

    def test_form_has_correct_fields(self):
        """Test that form includes all expected fields"""
        form = ArticleForm()
        expected_fields = ['title', 'status', 'topic', 'tags', 'content', 'excerpt', 'image_ids']
        self.assertEqual(list(form.fields.keys()), expected_fields)

    def test_form_content_widget_is_hidden(self):
        """Test that content field uses HiddenInput widget"""
        form = ArticleForm()
        self.assertIsInstance(form.fields['content'].widget, HiddenInput)

    def test_form_excerpt_widget_is_hidden(self):
        """Test that excerpt field uses HiddenInput widget"""
        form = ArticleForm()
        self.assertIsInstance(form.fields['excerpt'].widget, HiddenInput)

    def test_form_image_ids_widget_is_hidden(self):
        """Test that image_ids field uses HiddenInput widget"""
        form = ArticleForm()
        self.assertIsInstance(form.fields['image_ids'].widget, HiddenInput)

    def test_form_image_ids_not_required(self):
        """Test that image_ids field is not required"""
        form = ArticleForm()
        self.assertFalse(form.fields['image_ids'].required)

    def test_form_valid_with_minimal_required_fields(self):
        """Test form is valid with only required fields"""
        form_data = {
            'title': 'Test Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Test content here',
            'excerpt': '',
            'image_ids': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_all_fields(self):
        """Test form is valid with all fields populated"""
        form_data = {
            'title': 'Complete Article',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [self.tag1.id, self.tag2.id],
            'content': 'Full article content',
            'excerpt': 'Article summary',
            'image_ids': json.dumps([1, 2, 3]),
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_without_title(self):
        """Test form is invalid without title"""
        form_data = {
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_invalid_without_content(self):
        """Test form is invalid without content"""
        form_data = {
            'title': 'Test Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_invalid_without_status(self):
        """Test form is invalid without status"""
        form_data = {
            'title': 'Test Article',
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_form_invalid_without_topic(self):
        """Test form is invalid without topic (topic is required)"""
        form_data = {
            'title': 'Test Article',
            'status': Article.Status.DRAFT,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('topic', form.errors)

    def test_form_valid_with_draft_status(self):
        """Test form accepts DRAFT status"""
        form_data = {
            'title': 'Draft Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Draft content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_published_status(self):
        """Test form accepts PUBLISHED status"""
        form_data = {
            'title': 'Published Article',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Published content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_with_invalid_status(self):
        """Test form rejects invalid status values"""
        form_data = {
            'title': 'Article',
            'status': 'INVALID',
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)

    def test_form_valid_with_topic(self):
        """Test form accepts valid topic"""
        form_data = {
            'title': 'Article With Topic',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_with_nonexistent_topic(self):
        """Test form rejects non-existent topic ID"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': 99999,  # Non-existent ID
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('topic', form.errors)

    def test_form_valid_without_tags(self):
        """Test form is valid without tags (tags are optional)"""
        form_data = {
            'title': 'Article Without Tags',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_single_tag(self):
        """Test form accepts a single tag"""
        form_data = {
            'title': 'Article With Tag',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [self.tag1.id],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_multiple_tags(self):
        """Test form accepts multiple tags"""
        form_data = {
            'title': 'Article With Tags',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [self.tag1.id, self.tag2.id],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_with_nonexistent_tag(self):
        """Test form rejects non-existent tag ID"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [99999],  # Non-existent ID
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tags', form.errors)

    def test_form_valid_with_empty_excerpt(self):
        """Test form accepts empty excerpt"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_excerpt(self):
        """Test form accepts excerpt"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Full content here',
            'excerpt': 'Short summary',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_empty_image_ids(self):
        """Test form accepts empty image_ids"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
            'image_ids': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_valid_with_json_image_ids(self):
        """Test form accepts JSON array for image_ids"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
            'image_ids': json.dumps([1, 2, 3]),
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['image_ids'], json.dumps([1, 2, 3]))

    def test_form_valid_with_empty_json_array_image_ids(self):
        """Test form accepts empty JSON array for image_ids"""
        form_data = {
            'title': 'Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
            'image_ids': '[]',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_save_creates_article(self):
        """Test that saving form creates article in database"""
        form_data = {
            'title': 'New Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Article content',
            'excerpt': 'Summary',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        article = form.save(commit=False)
        article.author = self.user
        article.save()
        
        self.assertIsNotNone(article.id)
        self.assertEqual(article.title, 'New Article')
        self.assertEqual(article.status, Article.Status.DRAFT)

    def test_form_save_with_topic_and_tags(self):
        """Test saving form with topic and tags relationships"""
        form_data = {
            'title': 'Complete Article',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [self.tag1.id, self.tag2.id],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        article = form.save(commit=False)
        article.author = self.user
        article.save()
        form.save_m2m()  # Save many-to-many relationships
        
        self.assertEqual(article.topic, self.topic)
        self.assertEqual(article.tags.count(), 2)
        self.assertIn(self.tag1, article.tags.all())
        self.assertIn(self.tag2, article.tags.all())

    def test_form_edit_existing_article(self):
        """Test form can edit existing article"""
        article = Article.objects.create(
            title='Original Title',
            content='Original content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        
        form_data = {
            'title': 'Updated Title',
            'status': Article.Status.PUBLISHED,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Updated content',
            'excerpt': 'New excerpt',
        }
        form = ArticleForm(data=form_data, instance=article)
        self.assertTrue(form.is_valid())
        
        updated_article = form.save()
        
        self.assertEqual(updated_article.id, article.id)
        self.assertEqual(updated_article.title, 'Updated Title')
        self.assertEqual(updated_article.status, Article.Status.PUBLISHED)

    def test_form_preserves_slug_on_title_change(self):
        """Test that slug is not regenerated when title changes via form"""
        article = Article.objects.create(
            title='Original Title',
            content='Content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )
        original_slug = article.slug
        
        form_data = {
            'title': 'Completely Different Title',
            'status': Article.Status.DRAFT,
            'topic': self.topic.id,
            'tags': [],
            'content': 'Content',
            'excerpt': '',
        }
        form = ArticleForm(data=form_data, instance=article)
        self.assertTrue(form.is_valid())
        
        updated_article = form.save()
        
        # Slug should remain unchanged (as per model save() logic)
        self.assertEqual(updated_article.slug, original_slug)


class Html5DateInputTest(TestCase):
    """Test suite for Html5DateInput widget"""

    def test_input_type_is_date(self):
        """Test that Html5DateInput sets input_type to 'date'"""
        widget = Html5DateInput()
        self.assertEqual(widget.input_type, 'date')

    def test_widget_renders_with_date_type(self):
        """Test that widget renders HTML input with type='date'"""
        widget = Html5DateInput()
        html = widget.render('test_date', None)
        self.assertIn('type="date"', html)

    def test_widget_inherits_from_date_input(self):
        """Test that Html5DateInput inherits from forms.DateInput"""
        widget = Html5DateInput()
        self.assertIsInstance(widget, forms.DateInput)