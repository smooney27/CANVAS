import sys
import os.path
import csv
from django.core.management import setup_environ
sys.path.append(os.path.join(os.path.dirname(__file__), '../streetview'))

import settings
setup_environ(settings)
from ratestreets.models import *

admin_user = User.objects.get(username='smooney')
rater_user = User.objects.get(username='rater')
module = Module.objects.get_or_create(description='Sample Varied Questions Module')[0]
bike_only_module = Module.objects.get_or_create(description='Sample Bike-Only Module')[0]

# Can take this out once the import script can import Kathy's spreadsheet in a meaningful way.
#count_rating_type = RatingType.objects.get_or_create(description='count', storage_type='CATEGORY')[0]
#for index in range(10):
#    count_category = Category.objects.get_or_create(name=index,description=index, db_value=index)[0]
#    count_rating_type.values.add(count_category)
#count_category = Category.objects.get_or_create(name='10 or more',description='10 or more', db_value=10)[0]
#count_rating_type.values.add(count_category)
#
#text_rating_type = RatingType.objects.get_or_create(description='free-form text', storage_type='TEXT')[0]

#yesno_rating_type = RatingType.objects.get_or_create(description='yes/no', storage_type='CATEGORY')[0]
#yes_category = Category.objects.get_or_create(name='yes',description='yes', db_value=0)[0]
#no_category = Category.objects.get_or_create(name='no',description='no', db_value=1)[0]
#yesno_rating_type.values.add(yes_category)
#yesno_rating_type.values.add(no_category)
#
#sometonone_rating_type = RatingType.objects.get_or_create(description='some or a lot/few/none', storage_type='CATEGORY')[0]
#some_category = Category.objects.get_or_create(name='some or a lot',description='some or a lot', db_value=0)[0]
#few_category = Category.objects.get_or_create(name='few',description='few', db_value=1)[0]
#none_category = Category.objects.get_or_create(name='none',description='none', db_value=2)[0]
#sometonone_rating_type.values.add(some_category)
#sometonone_rating_type.values.add(few_category)
#sometonone_rating_type.values.add(none_category)
#
#interesting_rating_type = RatingType.objects.get_or_create(description='interestingness', storage_type='CATEGORY')[0]
#interesting_category = Category.objects.get_or_create(name='interesting',description='interesting', db_value=2)[0]
#somewhat_interesting_category = Category.objects.get_or_create(name='somewhat interesting',description='somewhat interesting', db_value=1)[0]
#uninteresting_category = Category.objects.get_or_create(name='uninteresting',description='uninteresting', db_value=0)[0]
#interesting_rating_type.values.add(interesting_category)
#interesting_rating_type.values.add(somewhat_interesting_category)
#interesting_rating_type.values.add(uninteresting_category)
#
#
#Item.objects.get_or_create(name='activity-complexity', description='How many people are on your side of the street?', rating_type=count_rating_type)
#Item.objects.get_or_create(name='aesthetics-architecture', description='How interesting is the architecture?', rating_type=interesting_rating_type)
#Item.objects.get_or_create(name='amenities-dining', description='Are there outdoor dining establishments?', rating_type=sometonone_rating_type)
#Item.objects.get_or_create(name='bicycle-bike lane', description='Are there bike lanes', rating_type=yesno_rating_type)
##Item.objects.get_or_create(name='more information', description='Is there anything else to say about this street?', rating_type=text_rating_type)
#
#items = Item.objects.all()
#for index in range(items.count()):
#    module.items.add(items[index])
# Pick the first module, which should be our default spreadsheet items.
module = Module.objects.all()[0]
study = Study.objects.get_or_create(director=admin_user, name='Study #1 (Everything)', description='Simple Test Study')[0]
study.modules.add(module)
study.raters.add(rater_user)
study.managers.add(admin_user)

#bike_only_module.items.add(items[3])
#bike_only_study = Study.objects.get_or_create(director=admin_user, name='Study #2 (Bikes Only)', description='Bike-only Study')[0]
#bike_only_study.modules.add(bike_only_module)
#bike_only_study.raters.add(rater_user)
#bike_only_study.managers.add(admin_user)

segment_1 = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=40.74781, start_lng=-73.980812, end_lat=40.74781, end_lng=-73.980812)[0]
segment_2 = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=41.657984, start_lng=-81.455401, end_lat=41.657984, end_lng=-81.455401)[0]
segment_3 = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=42.402091, start_lng=-71.145142, end_lat=42.402091, end_lng=-71.145142)[0]
segment_4 = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=41.878355, start_lng=-87.686341, end_lat=41.878355, end_lng=-87.686341)[0]
segment_5 = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=29.919239, start_lng=-90.112968, end_lat=29.919239, end_lng=-90.112968)[0]
task_1 = RatingTask.objects.get_or_create(user=rater_user, segment=segment_1, module=module)
task_2 = RatingTask.objects.get_or_create(user=rater_user, segment=segment_2, module=module)
task_3 = RatingTask.objects.get_or_create(user=rater_user, segment=segment_3, module=module)
task_4 = RatingTask.objects.get_or_create(user=rater_user, segment=segment_4, module=module)
task_5 = RatingTask.objects.get_or_create(user=rater_user, segment=segment_5, module=module)
