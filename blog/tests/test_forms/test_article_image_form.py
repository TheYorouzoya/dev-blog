import io
import tempfile
import shutil
import os

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from ...models import Article, Topic
from ...forms import ArticleImageForm


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
class ArticleImageFormTest(TestCase):
    """Test suite for ArticleImageForm"""

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
        self.topic = Topic.objects.create(name="Technology")
        self.article = Article.objects.create(
            title='Test Article',
            content='Content',
            status=Article.Status.DRAFT,
            topic=self.topic,
            author=self.user
        )

    def test_form_has_correct_fields(self):
        """Test that form includes all expected fields"""
        form = ArticleImageForm()
        expected_fields = ['article', 'image']
        self.assertEqual(list(form.fields.keys()), expected_fields)

    def test_form_valid_with_article_and_image(self):
        """Test form is valid with article and image"""
        image = create_test_image('test.jpg')
        form_data = {'article': self.article.id}
        form_files = {'image': image}
        
        form = ArticleImageForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_without_article(self):
        """Test form is invalid without article"""
        image = create_test_image('test.jpg')
        form_files = {'image': image}
        
        form = ArticleImageForm(data={}, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('article', form.errors)

    def test_form_invalid_without_image(self):
        """Test form is invalid without image"""
        form_data = {'article': self.article.id}
        
        form = ArticleImageForm(data=form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_form_invalid_with_nonexistent_article(self):
        """Test form rejects non-existent article ID"""
        image = create_test_image('test.jpg')
        form_data = {'article': 99999}  # Non-existent ID
        form_files = {'image': image}
        
        form = ArticleImageForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('article', form.errors)

    def test_form_save_creates_article_image(self):
        """Test that saving form creates ArticleImage in database"""
        image = create_test_image('test.jpg')
        form_data = {'article': self.article.id}
        form_files = {'image': image}
        
        form = ArticleImageForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        
        article_image = form.save()
        
        self.assertIsNotNone(article_image.id)
        self.assertEqual(article_image.article, self.article)
        self.assertTrue(article_image.image)

    def test_form_accepts_different_image_formats(self):
        """Test form accepts various image formats"""
        image_formats = [
            ('test.jpg', 'JPEG'),
            ('test.png', 'PNG'),
        ]
        
        for filename, format_type in image_formats:
            with self.subTest(format=format_type):
                # Create image for each format
                file = io.BytesIO()
                image = Image.new('RGB', (100, 100), 'red')
                image.save(file, format_type)
                file.seek(0)
                
                uploaded_file = SimpleUploadedFile(
                    name=filename,
                    content=file.read(),
                    content_type=f'image/{format_type.lower()}'
                )
                
                form_data = {'article': self.article.id}
                form_files = {'image': uploaded_file}
                
                form = ArticleImageForm(data=form_data, files=form_files)
                self.assertTrue(form.is_valid(), 
                              f"Form should accept {format_type}: {form.errors}")
