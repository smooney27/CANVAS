import logging
import csv
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from ratestreets.validators import *
from ratestreets.utils import *
from django.core.exceptions import ValidationError

# A category is a specific value for a category data type
# (e.g. lowrise, for category development type)
class Category(models.Model):
    name = models.CharField(max_length = 64)
    description = models.CharField(max_length = 256)
    db_value = models.PositiveIntegerField()
#    category_group = models.ForeignKey(RatingType)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name;

# A rating type is a data type for items to record
# has many catagory only relevant for category rating type
class RatingType(models.Model):
    STORAGE_TYPE_CHOICES = (
        (u'BOOL', u'boolean'),
        (u'COUNT', u'count'),
        (u'CATEGORY', u'category'),
        (u'TEXT', u'free-form text'),
    )
    
    description = models.CharField(max_length = 256)
    storage_type = models.CharField(max_length = 32, choices = STORAGE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    values = models.ManyToManyField(Category)
    def __unicode__(self):
        return self.description;


# An item is an axis on which a street is rated
class Item(models.Model):
    name = models.CharField(max_length = 32)
    description = models.CharField(max_length = 256)
    instrument = models.CharField(max_length = 32, null=True)
    number = models.FloatField(null=True)
    skip_pattern = models.CharField(max_length = 256, null=True)
    rating_type = models.ForeignKey(RatingType)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name;
    def create_rating(self, user, segment):
        if (self.rating_type.storage_type == 'BOOL'):
            new_rating = BooleanRating()
        elif (self.rating_type.storage_type == 'COUNT'):
            new_rating = CountRating()
        elif (self.rating_type.storage_type == 'CATEGORY'):
            new_rating = CategoryRating()
        elif (self.rating_type.storage_type == 'TEXT'):
            new_rating = FreeFormRating()
        new_rating.user = user
        new_rating.segment = segment
        new_rating.item = self
        return new_rating
    def get_rating_class(self):
        if (self.rating_type.storage_type == 'BOOL'):
            return BooleanRating
        elif (self.rating_type.storage_type == 'COUNT'):
            return CountRating
        elif (self.rating_type.storage_type == 'CATEGORY'):
            return CategoryRating
        elif (self.rating_type.storage_type == 'TEXT'):
            return FreeFormRating
        else:
            logging.debug("unexpected lack of rating class.  Should explode here.")
    def get_category_codebook(self, separator='/'):
        if (self.rating_type.storage_type == 'BOOL'):
            return 'false=0/true=1/unknown=2'
        elif (self.rating_type.storage_type == 'COUNT'):
            return 'number'
        elif (self.rating_type.storage_type == 'CATEGORY'):
            category_index = []
            for category in self.rating_type.values.all():
                category_index.append(category.name + '=' + str(category.db_value)) 
            return separator.join(category_index)
        elif (self.rating_type.storage_type == 'TEXT'):
            return 'text'
    def get_kappa(self, study):
        if (self.rating_type.storage_type != 'CATEGORY'):
            return 'N/A'
        # Get the ratings for this item/study and build the rater table
        segment_results = {}
        category_ratings_queryset = CategoryRating.objects.filter(item = self, segment__study = study)
        overall_rating_count = 0 #category_ratings_queryset.count()
        # Start narrowing hack
        # todo$ need to narrow honestly -- maybe look for all users who 
        # completed all segments and go with that cross-product.
        # Note that generically finding the largest user/segment complete
        # combination is NP-Hard (equivalent to finding largest fully 
        # connected subgraph in a bi-partite graph)
#        valid_ratings = []
#        users = sets.Set([])
#        for rating in category_ratings_queryset.all():
#            users.add(rating.user)
#                valid_ratings.append(rating)
#        for rating in valid_ratings:
        # Alternate block for narrowing hack        
        for rating in category_ratings_queryset.all():
        # End narrowing hack
            segment = rating.segment
            category = rating.rating
            # Skip null values for now.
            if category == None:
                continue
            overall_rating_count = overall_rating_count + 1
            if (segment in segment_results):
                current_segment_results = segment_results[segment]
            else:
                current_segment_results = {}
            if (category in current_segment_results):
                logging.debug("adding one to entry for category %d for segment %d" % (category, segment.id))
                current_segment_results[category] = current_segment_results[category] + 1
            else:
                current_segment_results[category] = 1
            segment_results[segment] = current_segment_results

        # Start incompleteness hack -- drop segments rated by only one user
        segments_to_remove = []
        for segment,segment_result in segment_results.iteritems():
            total_ratings_for_segment = 0
            for rating_count in segment_result.itervalues():
                total_ratings_for_segment = total_ratings_for_segment + rating_count
            if total_ratings_for_segment <= 1:
                segments_to_remove.append(segment)
        for segment in segments_to_remove:
            del segment_results[segment]
            logging.debug("Only one rater for segment %s, so dropping it from analysis" % segment.street_address)
            overall_rating_count = overall_rating_count - 1
        # End incompleteness hack
        
        
        # Now sum up category totals to compute proportions
        category_totals = {}
        for segment,segment_result in segment_results.iteritems():
            for category in segment_result.iterkeys():
                if (category in category_totals):
                    category_totals[category] = category_totals[category] + segment_result[category]
                else:
                    category_totals[category] = segment_result[category]
        category_proportions = {}
        for category,category_total in category_totals.iteritems():
            logging.debug("category total is %d for category %d for item %s" % (category_total, category, self.__unicode__()))
            category_proportions[category] = category_total * 1.0/overall_rating_count
            logging.debug("Proportion is %f for category %d for item %s" % (category_proportions[category], category, self.__unicode__()))

        # Now compute P (measure of agreement) for each row.  If only one rater, skip row.
        P_measures = {}
        for segment,segment_result in segment_results.iteritems():
            total_ratings_for_segment = 0
            running_sum_of_squares = 0
            for rating_count in segment_result.itervalues():
                total_ratings_for_segment = total_ratings_for_segment + rating_count
                running_sum_of_squares = running_sum_of_squares + (rating_count * rating_count)
            if (total_ratings_for_segment > 1):
                P = (running_sum_of_squares - total_ratings_for_segment)/(total_ratings_for_segment * (total_ratings_for_segment-1))
                P_measures[segment] = P
                logging.debug("P for segment %s is %f" % (segment.street_address, P))
            else:
                raise "Should have dropped row with only one rating in incompleteness hack!"
        
        if len(P_measures) == 0:
            return "No data"

        # Compute P_bar, the average P.
        P_total = 0
        for P in P_measures.itervalues():
            P_total = P_total + P
        P_bar = P_total * 1.0/len(P_measures)
        logging.debug("P_bar is %f" % P_bar)

        # And compute P_bar_e, the expected P_bar from chance
        P_bar_e = 0
        for category_proportion in category_proportions.itervalues():
            P_bar_e = P_bar_e + (category_proportion * category_proportion)
        logging.debug("P_bar_e is %f" % P_bar_e)

        # From P_bar and P_bar_e, we can compute kappa
        if (P_bar_e == 1):
            # If all ratings are the same, P_bar_e is equal to 1.  This 
            # implies complete agreement, but runs into divide by zero 
            # errors, so special case it here.
            kappa = 1.0
        else:
            kappa = (P_bar - P_bar_e)/(1-P_bar_e)
            # Hack -- for the case where we not all raters rated everything, we 
            # can go overboard.  Round back down for the moment.
            if (kappa < -1.0):
                kappa = -1.0
        return kappa
    
# A module is a collection of items that get data collected
# together.  Note that an item can belong to more than one
# module
class Module(models.Model):
    description = models.CharField(max_length = 256)
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.description;
    def add_items_from_csv(self, csv_file):
        # First, create rating types
        rating_types_by_row = Module.create_rating_types_from_csv(csv_file)
        # Then create actual items
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            for row_index, row in enumerate(reader):
                if (not (row_index in rating_types_by_row)):
                    continue
                rating_type = rating_types_by_row[row_index]
                self.create_item_from_csv_row(row, rating_type)
        finally:
            csv_file.close()
    def create_item_from_csv_row(self, row, rating_type):
        instrument = row[0]
        number = row[1]
        measure = row[4]
        skip_pattern = row[7]
        question = row[8]
        # do some data cleaning/validation.
        if (question == '' or row[9] == ''):
            return
        if (number == ''):
            number = 0.0
        name = instrument + '-' + str(number)
        logging.debug('creating item with values name=%s, description=%s, instrument=%s' % (name, question, instrument))
        if (measure != ''):
            new_item = Item.objects.get_or_create(name=name, 
                                                  description=question,
                                                  instrument=instrument,
                                                  number=number,
                                                  skip_pattern=skip_pattern,
                                                  rating_type=rating_type)[0]
            self.items.add(new_item)
    @staticmethod
    def create_rating_types_from_csv(csv_file):
        # Ensure that the percentage type always exists.
        percent_rating_type = RatingType.objects.get_or_create(description='percentage', storage_type='COUNT')[0]
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            rating_types_by_row = {}
            rating_types_by_values = {}
            for row_index, row in enumerate(reader):
                first_code = row[9]
                # Hack for percentage ratings
                if (first_code == 'Write in %'):
                    rating_types_by_row[row_index] = percent_rating_type
                    continue
                # Now read in the categories.
                i = 0
                code_list = []
                while (True):
                    if (len(row) > 9+i and row[9+i] != ''):
                        code_list.append(row[9+i])
                    else:
                        break;
                    i+=1
                rating_type_name = '/'.join(code_list)
                if (rating_type_name in rating_types_by_values):
                    # if this type already exists, re-use the existing one
                    rating_type = rating_types_by_values[rating_type_name]
                    rating_types_by_row[row_index] = rating_type
                else:
                    # otherwise, create a new one.
                    new_rating_type = RatingType.objects.get_or_create(description=rating_type_name, storage_type='CATEGORY')[0]
                    for index, code in enumerate(code_list):
                        category_name = code[0:63]
                        category_description = rating_type_name + '-' + category_name
                        new_category = Category.objects.get_or_create(name=category_name,description=category_description,db_value=index)[0]
                        logging.debug("category %s has id %d" % (category_name, new_category.id))
                        new_rating_type.values.add(new_category)
                    new_rating_type.save()
                    rating_types_by_values[rating_type_name] = new_rating_type
                    rating_types_by_row[row_index] = new_rating_type
        finally:
            csv_file.close()
        return rating_types_by_row
    # Class method to create modules.
    @staticmethod
    def create_modules_from_csv(csv_file):
        # First, create rating types
        rating_types_by_row = Module.create_rating_types_from_csv(csv_file)
        # Then create actual items
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            current_module = None
            for row_index, row in enumerate(reader):
                # Todo -- better CSV validation
                # e.g. throw an error if no module defined intially?
                #      barf when rows invalid?
                #      etc
                logging.debug("Checking row %s" % str(row_index))
                if (row[0] == '' and row[1] == '' and row[2] == '' and row[8] != '' and row[9] == ''):
                    current_module = Module.objects.get_or_create(description=row[8])[0]
                if (not (row_index in rating_types_by_row)):
                    logging.debug("No rating types found for row %s" % str(row_index))
                    continue
                rating_type = rating_types_by_row[row_index]
                logging.debug("Rating type found for row %s" % str(row_index))
                if (current_module != None):
                    logging.debug("Creating item for row %s" % str(row_index))
                    current_module.create_item_from_csv_row(row, rating_type)
                else:
                    logging.debug("No module -- not creating item.for row %s" % str(row_index))
        finally:
            # Last, make sure we close the file.
            csv_file.close()

        
# A study is a data collection unit -- that is, it's the
# collection of locations and items that get rated in one
# block.  Results will be associated with studies.
class Study(models.Model):
    director = models.ForeignKey(User, related_name="directed_studies_set")
    managers = models.ManyToManyField(User, related_name="managed_studies_set", blank=True)
    raters = models.ManyToManyField(User, related_name="rated_studies_set", blank=True)
    name = models.CharField(max_length = 32)
    description = models.CharField(max_length = 256)
    modules = models.ManyToManyField(Module)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # has many Locations
    def __unicode__(self):
        return self.description;
    def percent_complete(self, *args, **kwargs):
        total_tasks = self.total_tasks(*args, **kwargs)
        if (total_tasks == 0):
            return 0
        else:
            completed_tasks = self.completed_tasks(*args, **kwargs)
            return (100*completed_tasks)/total_tasks
    def total_tasks(self, *args, **kwargs):
        if 'user' in kwargs:
            return RatingTask.objects.filter(segment__study=self, user=kwargs['user']).count();
        else:
            return RatingTask.objects.filter(segment__study=self).count();
    def completed_tasks(self, *args, **kwargs):
        if 'user' in kwargs:
            logging.debug("kwargs is %s" % kwargs)
            return RatingTask.objects.filter(segment__study=self, completed_at__isnull=False, user=kwargs['user']).count()
        else:
            logging.debug("kwargs is %s" % kwargs)
            return RatingTask.objects.filter(segment__study=self, completed_at__isnull=False).count()
    def save(self, *args, **kwargs):
        # Call the base class to do the real save.
        super(Study, self).save(*args, **kwargs)
        # Then make sure all tasks exist in the DB.
        self.ensure_all_tasks_exist()
    def ensure_all_tasks_exist(self):
        for rater in self.raters.all():
            for module in self.modules.all():
                for segment in self.segment_set.all():
                    task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
        existing_tasks = RatingTask.objects.filter(segment__study=self)
        for existing_task in existing_tasks.all():
            if (not (existing_task.module in self.modules.all()) or
                not (existing_task.user in self.raters.all())):
                existing_task.delete()
    def add_segments_from_csv(self, uploaded_file):
        try:
            uploaded_file.read()
            reader = csv.reader(uploaded_file, dialect='excel')
            for index, row in enumerate(reader):
                start_lng = float(row[4])
                start_lat = float(row[5])
                end_lng = float(row[6])
                end_lat = float(row[7])
                logging.debug("Adding street segment from (%f, %f)->(%f, %f) to study %s" % (start_lat, start_lng, end_lat, end_lng, self.description))
                new_segment = Segment.objects.get_or_create(study=self, point_of_view=0, start_lat=start_lat, start_lng=start_lng, end_lat=end_lat, end_lng=end_lng)[0]
            # Once we've added the segments, make sure the tasks exist.
            self.ensure_all_tasks_exist()
        finally:
            uploaded_file.close()
    def add_segments_from_address_list(self, uploaded_file):
        try:
            uploaded_file.read()
            for line in uploaded_file:
                logging.debug("Adding street segment with address %s" % (line))
                line = line.rstrip()
                new_segment = Segment.objects.get_or_create(study=self, point_of_view=0, street_address=line)[0]
            # Once we've added the segments, make sure the tasks exist.
            self.ensure_all_tasks_exist()
        finally:
            uploaded_file.close()

# A segment is physical location in the real world that 
# users of this application rate.  Note that a segment
# can be a single point if its start and end are the same
# points.
class Segment(models.Model):
    study = models.ForeignKey(Study)
    point_of_view = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_lat = models.FloatField(blank=True, null=True)
    start_lng = models.FloatField(blank=True, null=True)
    end_lat = models.FloatField(blank=True, null=True)
    end_lng = models.FloatField(blank=True, null=True)
    street_address = models.CharField(max_length = 256, blank=True, null=True)
    def __unicode__(self):
        if self.street_address != None:
            return '%s' % (self.street_address)
        else:
            return '(%f,%f)->(%f,%f)' % (self.start_lat, self.start_lng, self.end_lat, self.end_lng);
    def clean(self):
        if ((self.start_lat == None or
            self.start_lng == None or
            self.end_lat == None or
            self.end_lng == None) and 
            self.street_address == None):
            raise ValidationError('You must provide either a street address or a start lat/lng and an end lat/lng')
# A rating task is the item that tracks the need for a rating
# to be completed by a user
class RatingTask(models.Model):
    user = models.ForeignKey(User)
    segment = models.ForeignKey(Segment)
    module = models.ForeignKey(Module)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_prompted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        unique_together = ('user', 'segment', 'module')
    def __unicode__(self):
        if self.segment.street_address != None:
            return '%s:%s' % (self.segment.street_address, self.user.username)
        else:
            return '(%f,%f)->(%f,%f):%s' % (self.segment.start_lat, self.segment.start_lng, self.segment.end_lat, self.segment.end_lng, self.user.username);
    def find_or_create_ratings(self, type):
        if (type == BooleanRating):
            ratings = BooleanRating.find_or_create_ratings_for_task(self)
        elif (type == CountRating):
            ratings = CountRating.find_or_create_ratings_for_task(self)
        elif (type == CategoryRating):
            ratings = CategoryRating.find_or_create_ratings_for_task(self)
        elif (type == FreeFormRating):
            ratings = FreeFormRating.find_or_create_ratings_for_task(self)
        # todo$ other rating types
        return ratings

# A rating is the base class for a piece of data collected
# by a user
class Rating(models.Model):
    user = models.ForeignKey(User)
    segment = models.ForeignKey(Segment)
    item = models.ForeignKey(Item)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    impediment = models.PositiveIntegerField(validators = [validate_impediment], null=True)
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
    @classmethod
    def find_or_create_ratings_for_task(cls, task):
        ratings_queryset = cls.objects.filter(user=task.user).filter(segment=task.segment).filter(item__module=task.module)
        anything_added = False
        for item in task.module.items.all():
            if item.get_rating_class() == cls:
                found = False
                for rating_object in ratings_queryset:
                    if rating_object.item == item:
                        found = True
                        break
                if found == False:
                    new_rating = item.create_rating(task.user, task.segment)
                    new_rating.save()
                    anything_added = True
        # Refresh the queryset if we added any ratings
        if anything_added:
            ratings_queryset = cls.objects.filter(user=task.user).filter(segment=task.segment).filter(item__module=task.module)
        return ratings_queryset
    
    class Meta:
        abstract = True
        unique_together = ('user', 'segment', 'item')

class BooleanRating(Rating):
    rating = models.PositiveIntegerField(validators = [validate_boolean], null=True)

class CategoryRating(Rating):
    rating = models.PositiveIntegerField(validators = [validate_category], null=True)

class CountRating(Rating):
    rating = models.PositiveIntegerField(null=True)

class FreeFormRating(Rating):
    rating = models.CharField(max_length = 1024, null=True)

    