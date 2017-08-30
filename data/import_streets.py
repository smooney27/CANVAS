import sys
import os.path
import csv
from django.core.management import setup_environ
sys.path.append(os.path.join(os.path.dirname(__file__), '../streetview'))

import settings
setup_environ(settings)
from ratestreets.models import *

# rU here is to deal with excel's use of newline chars
f = open("./streets.csv", 'rU')
try:
    reader = csv.reader(f, dialect='excel')
    # First, find the study.
    # todo$ take from command line?  Or assume this will always be done from within the app?
    study = Study.objects.get(pk=1)
    # todo$ should specify these formally.
    rater_user = User.objects.get(username='rater')
    module = Module.objects.get(pk=1)
    segments = []
    
    for index, row in enumerate(reader):
        start_lng = float(row[4])
        start_lat = float(row[5])
        end_lng = float(row[6])
        end_lat = float(row[7])
        print "Adding street segment from (%f, %f)->(%f, %f)" % (start_lat, start_lng, end_lat, end_lng)
        new_segment = Segment.objects.get_or_create(study=study, point_of_view=0, start_lat=start_lat, start_lng=start_lng, end_lat=end_lat, end_lng=end_lng)[0]
        new_segment.save()
        segments.append(new_segment)

    for segment in segments:
        new_task = RatingTask.objects.get_or_create(user=rater_user, module=module, segment=segment)[0]
        new_task.save()

finally:
    f.close()


