"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.files import File
from ratestreets.models import *

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

class TestRatingType(TestCase):
    def test_simple_create(self):
        valid_rating_type = RatingType.objects.create(description = 'Test Rating Type',
                                                      storage_type = 'BOOL')
        self.assertNotEqual(valid_rating_type, None)
        # Ensure that a valid instance doesn't throw validation errors.
        valid_rating_type.full_clean()
        invalid_rating_type = RatingType.objects.create(description = 'Test Rating Type',
                                                      storage_type = 'bogus')
        self.assertRaises(ValidationError, invalid_rating_type.full_clean)
        
class TestItem(TestCase):
    def test_simple_create(self):
        boolean_rating_type = RatingType.objects.create(description = 'Boolean Rating Type',
                                                        storage_type = 'BOOL')
        valid_item = Item.objects.create(name="Item Name", 
                                         description="Item Description",
                                         instrument="Instrument",
                                         number=1.0,
                                         skip_pattern="",
                                         rating_type=boolean_rating_type)
        self.assertNotEqual(valid_item, None)
        def assign_invalid_rating_type():
            valid_item.rating_type = None
        self.assertRaises(ValueError, assign_invalid_rating_type)
        
class TestModule(TestCase):
    def test_simple_create(self):
        valid_module = Module.objects.create(description="Module Description")
        self.assertNotEqual(valid_module, None)
    def test_add_items_from_csv(self):
        valid_module = Module.objects.create(description="Module Description")
        items_file = File(open("../data/items_with_skip_patterns.csv", 'rU'))
        valid_module.add_items_from_csv(items_file)
        self.assertEqual(valid_module.items.count(), 181)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

