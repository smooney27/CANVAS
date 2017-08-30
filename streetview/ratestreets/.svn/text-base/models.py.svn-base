import logging
import csv
import time
import re
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from ratestreets.validators import *
from ratestreets.utils import *
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache

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
    revision = models.CharField(max_length=32, null=True)
    skip_pattern = models.CharField(max_length = 256, null=True)
    rating_type = models.ForeignKey(RatingType)
    one_side_only = models.NullBooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name;
    def debug(self, message):
#        logging.debug(message)
        pass
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
    def get_help_text(self):
        def generate_image_url(matchobj):
            image_url = reverse('django.views.static.serve', args=['help/' + matchobj.group(1)])
            return image_url
        if (self.help_text.count() > 0):
            raw_help_text = self.help_text.all()[0]
            logging.debug("raw_help_text %s" % raw_help_text.text)
            item_help_text_with_brs = re.sub(r'\r', '<br>', raw_help_text.text)
            item_help_text_with_urls_updated = re.sub(r'\[([a-zA-Z_\.0-9]+)\]', generate_image_url, item_help_text_with_brs)
            return item_help_text_with_urls_updated
        else:
            return ""
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
    def get_rating_queryset(self, **kwargs):
        cache_key = self.__unicode__() + ":" + str(kwargs)
        cached_queryset = cache.get(cache_key)
        if (cached_queryset == None):
            if ('match_on_name' in kwargs and kwargs['match_on_name']):
                category_ratings_queryset = CategoryRating.objects.filter(item__name = self.name)
            else:
                category_ratings_queryset = CategoryRating.objects.filter(item = self)
            if ('study' in kwargs and kwargs['study'] is not None):
                category_ratings_queryset = category_ratings_queryset.filter(segment__study = kwargs['study'])
            elif ('study_queryset' in kwargs and kwargs['study_queryset'] is not None):
                category_ratings_queryset = category_ratings_queryset.filter(segment__study__in = kwargs['study_queryset'])
            if ('rater_ids' in kwargs and kwargs['rater_ids'] is not None):
                category_ratings_queryset = category_ratings_queryset.filter(user__in = kwargs['rater_ids'])
            category_ratings_queryset.order_by('segment')
            valid_ratings_queryset = category_ratings_queryset.exclude(rating=None).exclude(rating=-1).exclude(rating=-2)
            cache.set(cache_key, valid_ratings_queryset)
        else:
            valid_ratings_queryset = cached_queryset
        return valid_ratings_queryset
    def get_rating_times(self, study_queryset, match_on_name = False, rater_ids=None):
        category_ratings_queryset = self.get_rating_queryset(study_queryset=study_queryset, match_on_name=match_on_name, rater_ids=rater_ids)
        elapsed_times = []
        times = list(category_ratings_queryset.values_list('elapsed_time', flat=True))
        if (len(times) > 0):
            sorted_times = sorted(times)
            result = {
                      'min': sorted_times[0],
                      'median': sorted_times[len(sorted_times)/2],
                      'max': sorted_times[len(sorted_times)-1],
                      'total': len(sorted_times)}
            return result
        else:
            return None
    def get_percent_agreement(self, study, match_on_name = False, rater_ids = None):
        # A utility function to get percent agreement for an array
        def count_matching_pairs(array):
            if len(array) < 2:
                return 0
            matches = 0
            for i in range(0, len(array)):
                for j in range(i+1, len(array)):
                    if (array[i] == array[j]):
                        matches = matches + 1
            return matches
        category_ratings_queryset = self.get_rating_queryset(study=study, match_on_name=match_on_name, rater_ids=rater_ids)
        ratings_by_segment = {}
        for rating in category_ratings_queryset.all():
            if rating.segment in ratings_by_segment:
                ratings_for_segment = ratings_by_segment[rating.segment]
            else:
                ratings_for_segment = []
            ratings_for_segment.append(rating.rating)
            ratings_by_segment[rating.segment] = ratings_for_segment
        matches = 0
        possible_matches = 0
        for segment, segment_ratings in ratings_by_segment.iteritems():
            matches = matches + count_matching_pairs(segment_ratings)
            possible_matches = possible_matches + (len(segment_ratings) * (len(segment_ratings)-1))/2
        if (possible_matches == 0):
            percent_agreement = 'N/A'
        else:
            percent_agreement = float(matches)/possible_matches
        return (percent_agreement, category_ratings_queryset.count()) 
    def get_kappa(self, study, match_on_name = False, rater_ids = None):
        if (self.rating_type.storage_type != 'CATEGORY'):
            return ('N/A', 0)
        # Get the ratings for this item/study and build the rater table
        segment_results = {}
        category_ratings_queryset = self.get_rating_queryset(study=study, match_on_name=match_on_name, rater_ids=rater_ids)
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
            overall_rating_count = overall_rating_count + 1
            if (segment in segment_results):
                current_segment_results = segment_results[segment]
            else:
                current_segment_results = {}
            if (category in current_segment_results):
                self.debug("adding one to entry for category %d for segment %d" % (category, segment.id))
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
            self.debug("Only one rater for segment %s, so dropping it from analysis" % segment.street_address)
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
            self.debug("category total is %d for category %d for item %s" % (category_total, category, self.__unicode__()))
            category_proportions[category] = category_total * 1.0/overall_rating_count
            self.debug("Proportion is %f for category %d for item %s" % (category_proportions[category], category, self.__unicode__()))

        # Now compute P (measure of agreement) for each row.  If only one rater, skip row.
        P_measures = {}
        for segment,segment_result in segment_results.iteritems():
            total_ratings_for_segment = 0
            running_sum_of_squares = 0
            for rating_count in segment_result.itervalues():
                self.debug("found value %d for segment %s" % (rating_count, segment.street_address))
                total_ratings_for_segment = total_ratings_for_segment + rating_count
                running_sum_of_squares = running_sum_of_squares + (rating_count * rating_count)
            if (total_ratings_for_segment > 1):
                P = (1.0*running_sum_of_squares - total_ratings_for_segment)/(total_ratings_for_segment * (total_ratings_for_segment-1))
                self.debug("sum_of_squares: %d total_ratings_for_segment: %d, segment: %s" % (running_sum_of_squares, total_ratings_for_segment, segment.street_address))
                P_measures[segment] = P
                self.debug("P for segment %s is %f" % (segment.street_address, P))
            else:
                raise "Should have dropped row with only one rating in incompleteness hack!"
        
        if len(P_measures) == 0:
            return ("No data", 0)

        # Compute P_bar, the average P.
        P_total = 0
        for P in P_measures.itervalues():
            P_total = P_total + P
        P_bar = P_total * 1.0/len(P_measures)
        self.debug("P_bar is %f" % P_bar)

        # And compute P_bar_e, the expected P_bar from chance
        P_bar_e = 0
        for category_proportion in category_proportions.itervalues():
            P_bar_e = P_bar_e + (category_proportion * category_proportion)
        self.debug("P_bar_e is %f" % P_bar_e)

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
        return (kappa, overall_rating_count)
    def compute_and_save_kappa(self, study, *args, **kwargs):
        if ('date' in kwargs):
            timestamp = kwargs['date']
        else:
            timestamp = datetime.datetime.now()
        logging.debug("saving kappa with timestamp %s" % str(timestamp))
        stat_filter = KappaStat.objects.filter(study=study, item=self, timestamp=timestamp)
        kappa = self.get_kappa(study)[0]
        if kappa == 'No data':
            kappa = None
        if (stat_filter.count() > 0):
            kappa_stat_object = KappaStat.objects.get(study=study, item=self, timestamp=timestamp)
            kappa_stat_object.kappa = kappa
        else:
            kappa_stat_object = KappaStat.objects.create(study=study, item=self, timestamp=timestamp, kappa=kappa)
        kappa_stat_object.save()

class ItemHelpText(models.Model):
    item = models.ForeignKey(Item, related_name='help_text')
    text = models.CharField(max_length = 4096)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# A module is a collection of items that get data collected
# together.  Note that an item can belong to more than one
# module
class Module(models.Model):
    description = models.CharField(max_length = 256)
    items = models.ManyToManyField(Item)
    revision = models.CharField(max_length=32, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.get_name()
    def get_name(self):
        return self.description + ' (' + self.revision + ')';
    def add_items_from_csv(self, revision, format, csv_file):
        # First, create rating types
        if (format == 'CANVAS'):
            rating_types_by_row = Module.create_rating_types_from_canvas_csv(csv_file)
        elif (format == 'REDCAP'):
            rating_types_by_row = Module.create_rating_types_from_redcap_csv(csv_file)
        # Then create actual items
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            for row_index, row in enumerate(reader):
                if (not (row_index in rating_types_by_row)):
                    continue
                rating_type = rating_types_by_row[row_index]
                if (format == 'CANVAS'):
                    self.create_item_from_canvas_csv_row(row, revision, rating_type)
                elif (format == 'REDCAP'):
                    self.create_item_from_redcap_csv_row(row, revision, rating_type)
        finally:
            csv_file.close()
    def create_item_from_canvas_csv_row(self, row, revision, rating_type):
        instrument = row['instrument']
        number = row['number']
        one_side_only = row['one_side_only']
        skip_pattern = row['skip_pattern']
        # TODO -- is help going to come from items or be external?
        help_text = ''
        question = row['item_question']
        # do some data cleaning/validation.
        if (question == ''):
            return
        name = row['item_name']
#        logging.debug('creating item with values name=%s, description=%s, instrument=%s' % (name, question, instrument))
        if Item.objects.filter(instrument=instrument, number=number, revision=revision).exists():
            item = Item.objects.get(instrument=instrument, number=number, revision=revision)
            # Update all fields to match most recently read data
            item.name = name
            item.description = question
            item.skip_pattern = skip_pattern
            item.rating_type = rating_type
        else:
            item = Item(name=name, 
                        description=question,
                        instrument=instrument,
                        number=number,
                        revision=revision,
                        skip_pattern=skip_pattern,
                        rating_type=rating_type)
        if one_side_only == 'Yes' or one_side_only == '1':
            item.one_side_only = True 
        item.save()
        self.items.add(item)
        if (help_text != ''):
            if ItemHelpText.objects.filter(item=item).exists():
                item_help_text = ItemHelpText.objects.get(item=item)
                item_help_text.text = help_text
            else:
                item_help_text = ItemHelpText(item=item, text=help_text)
            item_help_text.save()
    def create_item_from_redcap_csv_row(self, row, revision, rating_type):
        instrument = row['Variable / Field Name']
        number = 1
        one_side_only = ''
        skip_pattern = row['Branching Logic (Show field only if...)']
        if (skip_pattern != ''):
            skip_pattern = "REDCAP:" + skip_pattern
        question = row['Field Label']
        # do some data cleaning/validation.
        if (question == ''):
            return
        name = row['Variable / Field Name']
        logging.debug('creating item with values name=%s, description=%s, instrument=%s' % (name, question, instrument))
        if Item.objects.filter(instrument=instrument, number=number, revision=revision).exists():
            item = Item.objects.get(instrument=instrument, number=number, revision=revision)
            # Update all fields to match most recently read data
            item.name = name
            item.description = question
            item.skip_pattern = skip_pattern
            item.rating_type = rating_type
        else:
            item = Item(name=name, 
                        description=question,
                        instrument=instrument,
                        number=number,
                        revision=revision,
                        skip_pattern=skip_pattern,
                        rating_type=rating_type)
        if one_side_only == 'Yes' or one_side_only == '1':
            item.one_side_only = True 
        item.save()
        self.items.add(item)

    @staticmethod
    def create_rating_types_from_redcap_csv(csv_file):
        # Ensure yesno and text types
        text_rating_type = RatingType.objects.get_or_create(description='redcap_text', storage_type='TEXT')[0]
        try:
            yesno_rating_type = RatingType.objects.get(description='redcap_yesno', storage_type='CATEGORY')
        except ObjectDoesNotExist:
            yesno_rating_type = RatingType.objects.get_or_create(description='redcap_yesno', storage_type='CATEGORY')[0]
            no_category = Category.objects.get_or_create(name='No',description='No',db_value=0)[0]
            yes_category = Category.objects.get_or_create(name='Yes',description='Yes',db_value=1)[0]
            yesno_rating_type.values.add(no_category)
            yesno_rating_type.values.add(yes_category)
            yesno_rating_type.save()

        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            rating_types_by_row = {}
            rating_types_by_values = {}
            for row_index, row in enumerate(reader):
                field_type = row['Field Type']
                # yesno and text ratings are easy
                if (field_type == 'yesno'):
                    rating_types_by_row[row_index] = yesno_rating_type
                    continue
                elif (field_type == 'text' or field_type == 'notes'):
                    rating_types_by_row[row_index] = text_rating_type
                    continue
                
                # Now read in the categories for radio buttons.
                if (field_type == "radio" or field_type == "dropdown"):
                    code_list = []
                    choices = row['Choices, Calculations, OR Slider Labels']
                    choices_list = choices.split("|")
                    for choice in choices_list:
                        values = choice.split(",")
                        code_list.append(values[1])
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


    @staticmethod
    def create_rating_types_from_canvas_csv(csv_file):
        # Ensure that the percentage type always exists.
        percent_rating_type = RatingType.objects.get_or_create(description='percentage', storage_type='COUNT')[0]
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            rating_types_by_row = {}
            rating_types_by_values = {}
            for row_index, row in enumerate(reader):
                response_codes = [
                                  'response_code_1',
                                  'response_code_2',
                                  'response_code_3',
                                  'response_code_4',
                                  'response_code_5',
                                  'response_code_6',
                                  'response_code_7',
                                  'response_code_8',
                                  'response_code_9',
                                  'response_code_10',
                                  'response_code_11',
                                  ]
                first_code = row[response_codes[0]]
                # Hack for percentage ratings
                if (first_code == 'Write in %'):
                    rating_types_by_row[row_index] = percent_rating_type
                    continue
                # Now read in the categories.
                
                code_list = []
                for response_code in response_codes:
                    if (response_code in row and row[response_code] != '' and row[response_code] is not None):
                        code_list.append(row[response_code])
                    else:
                        break;
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
#                        logging.debug("category %s has id %d" % (category_name, new_category.id))
                        new_rating_type.values.add(new_category)
                    new_rating_type.save()
                    rating_types_by_values[rating_type_name] = new_rating_type
                    rating_types_by_row[row_index] = new_rating_type
        finally:
            csv_file.close()
        return rating_types_by_row
    # Class method to create modules.
    @staticmethod
    def create_modules_from_csv(revision, format, csv_file):
        # First, create rating types
        if (format == 'CANVAS'):
            rating_types_by_row = Module.create_rating_types_from_canvas_csv(csv_file)
        elif (format == 'REDCAP'):
            rating_types_by_row = Module.create_rating_types_from_redcap_csv(csv_file)
        else: 
            raise 'Unexpected source format'
        # Then create actual items
        try:
            reader = Utils.get_csv_upload_file_reader(csv_file)
            current_module = None
            for row_index, row in enumerate(reader):
                # Todo -- better CSV validation
                # e.g. throw an error if no module defined intially?
                #      barf when rows invalid?
                #      etc
#                logging.debug("Checking row %s" % str(row_index))
                if (format == 'CANVAS'):
                    if ('module' in row and row['module'] != ''):
                        current_module = Module.objects.get_or_create(description=row['module'], revision=revision)[0]
                    if (not (row_index in rating_types_by_row)):
    #                    logging.debug("No rating types found for row %s" % str(row_index))
                        continue
                    rating_type = rating_types_by_row[row_index]
    #                logging.debug("Rating type found for row %s" % str(row_index))
                    if (current_module != None):
                        current_module.create_item_from_canvas_csv_row(row, revision, rating_type)
                elif (format == 'REDCAP'):
                    if ('Section Header' in row and row['Section Header'] != ''):
                        current_module = Module.objects.get_or_create(description=row['Section Header'], revision=revision)[0]
                    if (not (row_index in rating_types_by_row)):
                        logging.debug("No rating types found for row %s" % str(row_index))
                        continue
                    rating_type = rating_types_by_row[row_index]
                    current_module.create_item_from_redcap_csv_row(row, revision, rating_type)
                    
#                else:
#                    logging.debug("No module -- not creating item.for row %s" % str(row_index))
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
    TASK_ALLOCATION_CHOICES = (
        (0, u'All Raters Rate All Segments'),
        (1, u'Each Segment Rated Once'),
        (2, u'All Raters Rate Shared Core')
    )
    task_allocation = models.PositiveIntegerField(validators = [validate_task_allocation], choices=TASK_ALLOCATION_CHOICES)
    task_overlap = models.PositiveIntegerField(validators = [validate_task_overlap], null=True)
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
            return RatingTask.objects.filter(segment__study=self, completed_at__isnull=False, user=kwargs['user']).count()
        else:
            return RatingTask.objects.filter(segment__study=self, completed_at__isnull=False).count()
    def save(self, *args, **kwargs):
        # Call the base class to do the real save.
        super(Study, self).save(*args, **kwargs)
        # Then make sure all tasks exist in the DB.
        self.ensure_all_tasks_exist()
    def clean(self):
        if (self.task_allocation == 2 and self.task_overlap is None):
            raise ValidationError("Must select an overlap proportion if task allocation is All Raters Rate Shared Core")
        elif (self.task_allocation != 2 and self.task_overlap is not None):
            self.task_overlap = None
        models.Model.clean(self)
    def ensure_all_tasks_exist(self):
        if self.task_allocation == 0:
            for rater in self.raters.all():
                for module in self.modules.all():
                    for segment in self.segment_set.all():
                        task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
            existing_tasks = RatingTask.objects.filter(segment__study=self)
            for existing_task in existing_tasks.all():
                if (not (existing_task.module in self.modules.all()) or
                    not (existing_task.user in self.raters.all())):
                    existing_task.delete()
        elif self.task_allocation == 1 or self.task_allocation == 2:
            existing_task_count = RatingTask.objects.filter(segment__study=self).count()
            if existing_task_count == 0:
                self.allocate_tasks()
            else: 
                # Don't change anything if tasks already exist.  Will need to re-allocate manually.
                # todo$ implement manual reallocation trigger.
                pass
        else:
            logging.debug('unexpected task allocation %s' % self.task_allocation)
    def allocate_tasks(self):
        # Is there a batch way to do this?
        existing_tasks = RatingTask.objects.filter(segment__study=self)
        for existing_task in existing_tasks.all():
            existing_task.delete()
        segment_count = self.segment_set.count()
        rater_count = self.raters.count()
        if rater_count == 0:
            return
        if self.task_allocation == '2':
            overlap = self.task_overlap
        else:
            overlap = 0
        overlap_count = (overlap * segment_count) / 100
        random_segments = self.segment_set.order_by('?')
        random_raters = self.raters.order_by('?')
        rater_iter = iter(random_raters)
        for segment_index, segment in enumerate(random_segments):
            if segment_index < overlap_count:
                for rater in random_raters:
                    for module in self.modules.all():
                        task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
            else:
                rater = random_raters[segment_index % rater_count]
                for module in self.modules.all():
                    task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
    def reallocate_pending_tasks(self):
        # Remove all pending tasks for this study  
        pending_tasks = RatingTask.objects.filter(segment__study=self, completed_at__isnull=True)
        for pending_task in pending_tasks.all():
            # If this task is for a rater still assigned to the project and the street was 
            # already rated, don't remove it -- it might be partially finished and it might be
            # part of the shared core.
            if (RatingTask.objects.filter(segment=pending_task.segment, completed_at__isnull=False).exists()
                and pending_task.user in self.raters.all()):
                continue
            else:
                pending_task.delete()
        # Now, find the full list of segments to rate
        segments_to_rate = Segment.objects.filter(study=self)
        segment_count = segments_to_rate.count()
        rater_count = self.raters.count()
        if rater_count == 0:
            return
        random_segments = segments_to_rate.order_by('?')
        random_raters = self.raters.order_by('?')
        unrated_segments = []
        for segment_index, segment in enumerate(random_segments):
            # If this segment has already been at least partially rated, continue
            if RatingTask.objects.filter(segment=segment, completed_at__isnull=False).exists():
                continue
            # otherwise, assign to a rater
            else:
                rater = random_raters[segment_index % rater_count]
                for module in self.modules.all():
                    task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
                unrated_segments.append(segment)
        # Now, check how many segments have already been rated by more than one rater if we need to ensure overlap
        if self.task_allocation == 2:
            overlap = self.task_overlap
            overlap_count = (overlap * self.segment_set.count()) / 100
            completed_tasks = RatingTask.objects.filter(segment__study=self, completed_at__isnull=False)
            completed_segments = {}
            completed_overlap_count = 0
            for completed_task in completed_tasks:
                if completed_task.segment in completed_segments:
                    current = completed_segments[completed_task.segment]
                    if current != 'multiple' and current != completed_task.user:
                        completed_segments[completed_task.segment] = 'multiple'
                        completed_overlap_count = completed_overlap_count + 1
                else:
                    completed_segments[completed_task.segment] = completed_task.user
            if completed_overlap_count < overlap_count:
                # So, create tasks for all raters for the next n segments
                for i in range(overlap_count-completed_overlap_count):
                    if (i < len(unrated_segments)-1):
                        segment = unrated_segments[i]
                        for rater in random_raters:
                            for module in self.modules.all():
                                task = RatingTask.objects.get_or_create(user=rater, module=module, segment=segment)
                        
    def compute_and_save_kappas(self, *args, **kwargs):
        today = Utils.get_start_of_utc_day()
        for module in self.modules.all():
            for item in module.items.all():
                item.compute_and_save_kappa(self, date=today)
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
    sample_point = models.ForeignKey('SamplePoint', blank=True, null=True, related_name = 'segment_sample_point')
    def __unicode__(self):
        if self.street_address != None:
            return '%s' % (self.street_address)
        else:
            return '(%f,%f)->(%f,%f)' % (self.start_lat, self.start_lng, self.end_lat, self.end_lng);
    def raters(self):
        raters = self.rater_list()
        rater_names = []
        for rater in raters:
            rater_names.append(rater.username)
        return ', '.join(rater_names)
    def rater_list(self):
        tasks = RatingTask.objects.filter(segment=self)
        raters = {}
        for task in tasks:
            raters[task.user] = 1
        return raters.keys()
    def pending_for_list(self):
        tasks = RatingTask.objects.filter(segment=self, completed_at__isnull=True)
        raters = {}
        for task in tasks:
            raters[task.user] = 1
        return raters.keys()
    def pending_for(self):
        raters = self.pending_for_list()
        rater_names = []
        for rater in raters:
            rater_names.append(rater.username)
        return ', '.join(rater_names)
    def completed_by_list(self):
        tasks = RatingTask.objects.filter(segment=self, completed_at__isnull=False)
        raters = {}
        for task in tasks:
            raters[task.user] = 1
        return raters.keys()
    def completed_by(self):
        raters = self.completed_by_list()
        rater_names = []
        for rater in raters:
            rater_names.append(rater.username)
        return ', '.join(rater_names)
    def reallocate_tasks(self, newusers):
        current_tasks = RatingTask.objects.filter(segment=self)
        for current_task in current_tasks:
            if current_task.completed_at is None:
                current_task.delete()
        modules = self.study.modules
        for user in newusers:
            for module in modules.all():
                RatingTask.objects.get_or_create(segment=self, user=user, module=module)
    
#    def clean(self):
#        if ((self.start_lat == None or
#            self.start_lng == None or
#            self.end_lat == None or
#            self.end_lng == None) and 
#            self.street_address == None):
#            raise ValidationError('You must provide either a street address or a start lat/lng and an end lat/lng')

class SamplePoint(models.Model):
    study = models.ForeignKey(Study)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    row_id = models.IntegerField(blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    street_address = models.CharField(max_length = 256, blank=True, null=True)



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
    elapsed_time = models.PositiveIntegerField(null=True)
    image_date = models.DateField(null=True)
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
    def add_elapsed_time(self, elapsed_time):
        if (elapsed_time != None):
            elapsed_to_date_seconds = self.elapsed_time
            if elapsed_to_date_seconds == None:
                timedelta_to_date = timedelta()
            else:
                timedelta_to_date = timedelta(seconds=elapsed_to_date_seconds)
            timedelta_for_self = (timedelta_to_date + elapsed_time)
            self.elapsed_time = (timedelta_for_self.seconds + timedelta_for_self.days * 24 * 3600)

        
    class Meta:
        abstract = True
        unique_together = ('user', 'segment', 'item')

class BooleanRating(Rating):
    rating = models.IntegerField(validators = [validate_boolean], null=True)

class CategoryRating(Rating):
    rating = models.IntegerField(validators = [validate_category], null=True)

class CountRating(Rating):
    rating = models.IntegerField(null=True)

class FreeFormRating(Rating):
    rating = models.CharField(max_length = 1024, null=True)

class KappaStat(models.Model):
    kappa = models.FloatField(null=True)
    timestamp = models.DateTimeField()
    study = models.ForeignKey(Study)
    item = models.ForeignKey(Item)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
