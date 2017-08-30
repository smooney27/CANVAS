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
    def test_kappa_calc(self):
        category_rating_type = RatingType.objects.create(description = 'Category Rating Type',
                                                         storage_type = 'CATEGORY')
        category_1 = Category.objects.create(name="1", description="1", db_value=1)
        category_2 = Category.objects.create(name="2", description="2", db_value=2)
        category_3 = Category.objects.create(name="3", description="3", db_value=3)
        category_rating_type.values.add(category_1)
        category_rating_type.values.add(category_2)
        category_rating_type.values.add(category_3)
        rater_1 = User.objects.create_user("rater 1", "rater1@bogus.edu")
        rater_2 = User.objects.create_user("rater 2", "rater2@bogus.edu")
        rater_3 = User.objects.create_user("rater 3", "rater3@bogus.edu")
        rater_4 = User.objects.create_user("rater 4", "rater4@bogus.edu")
        item = Item.objects.create(name="Item Name", 
                                   description="Item Description",
                                   instrument="Instrument",
                                   number=1.0,
                                   skip_pattern="",
                                   rating_type=category_rating_type)
        study = Study.objects.create(name="Study", description="Study", director=rater_1)
        segment_1 = Segment.objects.create(study=study,point_of_view=0, street_address="1 Main Street") 
        segment_2 = Segment.objects.create(study=study,point_of_view=0, street_address="2 Main Street") 
        segment_3 = Segment.objects.create(study=study,point_of_view=0, street_address="3 Main Street") 
        rating_11 = CategoryRating.objects.create(item=item, user=rater_1, segment=segment_1, rating=1)
        rating_21 = CategoryRating.objects.create(item=item, user=rater_2, segment=segment_1, rating=1)
        rating_31 = CategoryRating.objects.create(item=item, user=rater_3, segment=segment_1, rating=1)
        rating_41 = CategoryRating.objects.create(item=item, user=rater_4, segment=segment_1, rating=1)
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "1.000")
        rating_12 = CategoryRating.objects.create(item=item, user=rater_1, segment=segment_2, rating=1)
        rating_22 = CategoryRating.objects.create(item=item, user=rater_2, segment=segment_2, rating=1)
        rating_32 = CategoryRating.objects.create(item=item, user=rater_3, segment=segment_2, rating=2)
        rating_42 = CategoryRating.objects.create(item=item, user=rater_4, segment=segment_2, rating=2)
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "0.111")
        rating_13 = CategoryRating.objects.create(item=item, user=rater_1, segment=segment_3, rating=3)
        rating_23 = CategoryRating.objects.create(item=item, user=rater_2, segment=segment_3, rating=3)
        rating_33 = CategoryRating.objects.create(item=item, user=rater_3, segment=segment_3, rating=3)
        rating_43 = CategoryRating.objects.create(item=item, user=rater_4, segment=segment_3, rating=3)
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "0.636")
        rating_23.rating = 2
        rating_23.save()
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "0.378")
        rating_23.rating = 1
        rating_23.save()
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "0.317")
        rating_23.rating = 3
        rating_23.save()
        rating_12.rating = 2
        rating_12.save()
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "0.745")
        rating_22.rating = 2
        rating_22.save()
        self.assertEqual("%.3f" % item.get_kappa(study)[0], "1.000")
    def test_save_kappas(self):
        category_rating_type = RatingType.objects.create(description = 'Category Rating Type',
                                                         storage_type = 'CATEGORY')
        category_1 = Category.objects.create(name="1", description="1", db_value=1)
        category_2 = Category.objects.create(name="2", description="2", db_value=2)
        category_3 = Category.objects.create(name="3", description="3", db_value=3)
        category_rating_type.values.add(category_1)
        category_rating_type.values.add(category_2)
        category_rating_type.values.add(category_3)
        rater_1 = User.objects.create_user("rater 1", "rater1@bogus.edu")
        rater_2 = User.objects.create_user("rater 2", "rater2@bogus.edu")
        rater_3 = User.objects.create_user("rater 3", "rater3@bogus.edu")
        rater_4 = User.objects.create_user("rater 4", "rater4@bogus.edu")
        item = Item.objects.create(name="Item Name", 
                                   description="Item Description",
                                   instrument="Instrument",
                                   number=1.0,
                                   skip_pattern="",
                                   rating_type=category_rating_type)
        module = Module.objects.create(description="Module Description")
        module.items.add(item)
        study = Study.objects.create(name="Study", description="Study", director=rater_1)
        study.modules.add(module)
        segment_1 = Segment.objects.create(study=study,point_of_view=0, street_address="1 Main Street") 
        segment_2 = Segment.objects.create(study=study,point_of_view=0, street_address="2 Main Street") 
        segment_3 = Segment.objects.create(study=study,point_of_view=0, street_address="3 Main Street") 
        rating_11 = CategoryRating.objects.create(item=item, user=rater_1, segment=segment_1, rating=1)
        rating_21 = CategoryRating.objects.create(item=item, user=rater_2, segment=segment_1, rating=1)
        rating_31 = CategoryRating.objects.create(item=item, user=rater_3, segment=segment_1, rating=1)
        rating_41 = CategoryRating.objects.create(item=item, user=rater_4, segment=segment_1, rating=1)
        item.compute_and_save_kappa(study)
        kappa_stat = KappaStat.objects.get(item=item, study=study)
        self.assertEqual(kappa_stat.kappa, 1.000)
        rating_12 = CategoryRating.objects.create(item=item, user=rater_1, segment=segment_2, rating=1)
        rating_22 = CategoryRating.objects.create(item=item, user=rater_2, segment=segment_2, rating=1)
        rating_32 = CategoryRating.objects.create(item=item, user=rater_3, segment=segment_2, rating=2)
        rating_42 = CategoryRating.objects.create(item=item, user=rater_4, segment=segment_2, rating=2)
        # Wait a second before saving all kappas for the study to be sure we create a different one.
        time.sleep(1)
        study.compute_and_save_kappas()
        kappa_stats = KappaStat.objects.filter(item=item, study=study)
        self.assertEqual(kappa_stats.count(), 2)
        self.assertEqual("%.3f" % kappa_stats[1].kappa, "0.111")
        self.assertEqual("%.3f" % kappa_stats[0].kappa, "1.000")
        self.assertNotEqual(kappa_stats[1].timestamp, kappa_stats[0].timestamp)

class TestModule(TestCase):
    def test_simple_create(self):
        valid_module = Module.objects.create(description="Module Description")
        self.assertNotEqual(valid_module, None)
    def test_add_items_from_csv(self):
        valid_module = Module.objects.create(description="Module Description")
        items_file = File(open("data/items_with_help_text.csv", 'rU'))
        valid_module.add_items_from_csv('test_revision', items_file)
        self.assertEqual(valid_module.items.count(), 186)
        meta_3_item = Item.objects.get(number = 3, instrument='Meta')
        self.assertEqual(meta_3_item.rating_type.storage_type, 'CATEGORY')
        self.assertEqual(meta_3_item.rating_type.values.count(), 5)
        self.assertEqual(meta_3_item.description, "How many zoom levels are available?")
        self.assertEqual(meta_3_item.skip_pattern, "")
    def test_create_modules_from_csv(self):
        modules_file = File(open("data/items_with_help_text.csv", 'rU'))
        Module.create_modules_from_csv('test_revision', modules_file)
        self.assertEqual(Module.objects.count(), 8)

class TestCategoryRating(TestCase):
    def test_simple_create(self):
        category_rating_type = RatingType.objects.create(description = 'Category Rating Type',
                                                         storage_type = 'CATEGORY')
        category_1 = Category.objects.create(name="1", description="1", db_value=1)
        category_2 = Category.objects.create(name="2", description="2", db_value=2)
        category_3 = Category.objects.create(name="3", description="3", db_value=3)
        category_rating_type.values.add(category_1)
        category_rating_type.values.add(category_2)
        category_rating_type.values.add(category_3)
        item = Item.objects.create(name="Item Name", 
                                   description="Item Description",
                                   instrument="Instrument",
                                   number=1.0,
                                   skip_pattern="",
                                   rating_type=category_rating_type)
        rater = User.objects.create_user("rater", "rater@bogus.edu")
        study = Study.objects.create(name="Study", description="Study", director=rater)
        segment = Segment.objects.create(study=study,point_of_view=0, street_address="1 Main Street") 
        rating = CategoryRating.objects.create(user=rater, item=item, segment=segment, rating=1)
        self.assertNotEqual(rating, None)
    def test_add_elapsed_time(self):
        category_rating_type = RatingType.objects.create(description = 'Category Rating Type',
                                                         storage_type = 'CATEGORY')
        category_1 = Category.objects.create(name="1", description="1", db_value=1)
        category_2 = Category.objects.create(name="2", description="2", db_value=2)
        category_3 = Category.objects.create(name="3", description="3", db_value=3)
        category_rating_type.values.add(category_1)
        category_rating_type.values.add(category_2)
        category_rating_type.values.add(category_3)
        item = Item.objects.create(name="Item Name", 
                                   description="Item Description",
                                   instrument="Instrument",
                                   number=1.0,
                                   skip_pattern="",
                                   rating_type=category_rating_type)
        rater = User.objects.create_user("rater", "rater@bogus.edu")
        study = Study.objects.create(name="Study", description="Study", director=rater)
        segment = Segment.objects.create(study=study,point_of_view=0, street_address="1 Main Street") 
        rating = CategoryRating.objects.create(user=rater, item=item, segment=segment, rating=1)
        self.assertNotEqual(rating, None)
        rating.add_elapsed_time(timedelta(seconds=23))
        self.assertEqual(rating.elapsed_time, 23)
        rating.add_elapsed_time(timedelta(minutes=1))
        self.assertEqual(rating.elapsed_time, 83)
        rating.save()
        new_rating = CategoryRating.objects.get(user=rater, item=item, segment=segment)
        self.assertEqual(new_rating.elapsed_time, 83)