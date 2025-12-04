import os
import tempfile
import shutil

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from ...models import Article, ArticleImage


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ArticleImageModelTest(TestCase):
    """Test suite for ArticleImage model and its signals"""

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
        self.article = Article.objects.create(
            title="Test Article",
            content="Content",
            author=self.user
        )

    def test_article_image_creation(self):
        """Test basic article image creation"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        article_image = ArticleImage.objects.create(
            article=self.article,
            image=image
        )
        self.assertEqual(article_image.article, self.article)
        self.assertTrue(article_image.image)

    def test_article_image_cascade_delete(self):
        """Test that article images are deleted when article is deleted"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        article_image = ArticleImage.objects.create(
            article=self.article,
            image=image
        )
        image_id = article_image.id
        
        self.article.delete()
        
        self.assertFalse(ArticleImage.objects.filter(id=image_id).exists())

    def test_article_image_file_deleted_on_model_delete(self):
        """Test that image file is deleted from filesystem when model is deleted"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        article_image = ArticleImage.objects.create(
            article=self.article,
            image=image
        )
        
        # Get the file path
        image_path = article_image.image.path
        
        # Verify file exists
        self.assertTrue(os.path.isfile(image_path))
        
        # Delete the model instance
        article_image.delete()
        
        # Verify file is deleted
        self.assertFalse(os.path.isfile(image_path))

    def test_article_image_signal_handles_missing_file(self):
        """Test that signal doesn't crash if file doesn't exist"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        article_image = ArticleImage.objects.create(
            article=self.article,
            image=image
        )
        
        # Manually delete the file before deleting the model
        image_path = article_image.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)
        
        # This should not raise an exception
        try:
            article_image.delete()
        except Exception as e:
            self.fail(f"Deleting ArticleImage with missing file raised {type(e).__name__}: {e}")

    def test_article_image_signal_handles_no_image(self):
        """Test that signal handles ArticleImage without image gracefully"""
        # This tests the 'if instance.image:' check in the signal
        with patch('os.path.isfile') as mock_isfile:
            with patch('os.remove') as mock_remove:
                article_image = ArticleImage(article=self.article)
                article_image.image = None
                
                # Trigger the signal manually
                from ...models import auto_delete_image_file_on_delete
                auto_delete_image_file_on_delete(
                    sender=ArticleImage,
                    instance=article_image
                )
                
                # Verify os.path.isfile was never called
                mock_isfile.assert_not_called()
                mock_remove.assert_not_called()

    def test_multiple_images_per_article(self):
        """Test that multiple images can be associated with one article"""
        image1 = SimpleUploadedFile(
            name='test_image1.jpg',
            content=b'fake image content 1',
            content_type='image/jpeg'
        )
        image2 = SimpleUploadedFile(
            name='test_image2.jpg',
            content=b'fake image content 2',
            content_type='image/jpeg'
        )
        
        article_image1 = ArticleImage.objects.create(
            article=self.article,
            image=image1
        )
        article_image2 = ArticleImage.objects.create(
            article=self.article,
            image=image2
        )
        
        self.assertEqual(
            ArticleImage.objects.filter(article=self.article).count(),
            2
        )