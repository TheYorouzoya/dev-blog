import os
import tempfile
import shutil

from django.test import TestCase, override_settings
from django.utils.text import slugify
from django.db import IntegrityError

from blog.models import Topic


# Use a temporary media root for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TopicModelTest(TestCase):
    """Test suite for Topic model"""

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary media directory after all tests"""
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def test_topic_creation(self):
        """Test basic topic creation"""
        topic = Topic.objects.create(
            name="Technology",
            description="All about tech"
        )
        self.assertEqual(topic.name, "Technology")
        self.assertEqual(topic.description, "All about tech")
        self.assertIsNotNone(topic.id)

    def test_topic_auto_slug_generation(self):
        """Test that slug is automatically generated from name"""
        topic = Topic.objects.create(name="Machine Learning")
        self.assertEqual(topic.slug, "machine-learning")

    def test_topic_slug_with_special_characters(self):
        """Test slug generation with special characters"""
        topic = Topic.objects.create(name="AI & Machine Learning!")
        self.assertEqual(topic.slug, "ai-machine-learning")

    def test_topic_slug_not_overwritten_if_provided(self):
        """Test that manually provided slug is not overwritten"""
        topic = Topic.objects.create(
            name="Technology",
            slug="custom-tech-slug"
        )
        self.assertEqual(topic.slug, "custom-tech-slug")

    def test_topic_slug_not_changed_on_update(self):
        """Test that slug doesn't change when name is updated"""
        topic = Topic.objects.create(name="Old Name")
        original_slug = topic.slug
        
        topic.name = "New Name"
        topic.save()
        
        self.assertEqual(topic.slug, original_slug)
        self.assertNotEqual(topic.slug, slugify("New Name"))

    def test_topic_name_uniqueness(self):
        """Test that topic names must be unique"""
        Topic.objects.create(name="Technology")
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="Technology")

    def test_topic_slug_uniqueness(self):
        """Test that topic slugs must be unique"""
        Topic.objects.create(name="Tech", slug="technology")
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="Technology", slug="technology")

    def test_topic_blank_description(self):
        """Test that description can be blank"""
        topic = Topic.objects.create(name="Technology")
        self.assertEqual(topic.description, "")

    def test_topic_str_method(self):
        """Test string representation of topic"""
        topic = Topic.objects.create(name="Technology")
        self.assertEqual(str(topic), "Technology")

    def test_topic_serialize_method(self):
        """Test serialization of topic"""
        topic = Topic.objects.create(
            name="Technology",
            description="Tech topics"
        )
        serialized = topic.serialize()
        
        self.assertEqual(serialized["id"], topic.id)
        self.assertEqual(serialized["name"], "Technology")
        self.assertEqual(serialized["slug"], topic.slug)
        self.assertEqual(serialized["description"], "Tech topics")
