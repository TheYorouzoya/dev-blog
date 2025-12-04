import os
import tempfile
import shutil

from django.test import TestCase, override_settings
from django.db import IntegrityError

from ...models import Tag


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TagModelTest(TestCase):
    """Test suite for Tag model"""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def test_tag_creation(self):
        """Test basic tag creation"""
        tag = Tag.objects.create(name="Python", slug="python")
        self.assertEqual(tag.name, "Python")
        self.assertEqual(tag.slug, "python")

    def test_tag_name_uniqueness(self):
        """Test that tag names must be unique"""
        Tag.objects.create(name="Python", slug="python")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Python", slug="python-2")

    def test_tag_slug_uniqueness(self):
        """Test that tag slugs must be unique"""
        Tag.objects.create(name="Python", slug="python")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Python 2", slug="python")

    def test_tag_str_method(self):
        """Test string representation of tag"""
        tag = Tag.objects.create(name="Django", slug="django")
        self.assertEqual(str(tag), "Django")
