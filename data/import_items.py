import sys
import os.path
import csv
from django.core.management import setup_environ
sys.path.append(os.path.join(os.path.dirname(__file__), '../streetview'))

import settings
setup_environ(settings)
from ratestreets.models import *

# todo -- verify that get_or_create saves us from duplicates.
#count_rating_type = RatingType.objects.get_or_create(description='count', storage_type='CATEGORY')[0]
#for index in range(10):
#    count_category = Category.objects.get_or_create(name=index,description=index, db_value=index)[0]
#    count_rating_type.values.add(count_category)
#count_category = Category.objects.get_or_create(name='10 or more',description='10 or more', db_value=10)[0]
#count_rating_type.values.add(count_category)
#text_rating_type = RatingType.objects.get_or_create(description='free-form text', storage_type='TEXT')[0]
percent_rating_type = RatingType.objects.get_or_create(description='percentage', storage_type='COUNT')[0]

# rU here is to deal with excel's use of newline chars
f = open("./modules.csv", 'rU')
try:
    reader = csv.reader(f, dialect='excel')
    # First, generate rating types
    rating_types_by_row = {}
    rating_types_by_values = {}
    for row_index, row in enumerate(reader):
        print 'looking at row %s' % (row)
        first_code = row[7]
        print ("First code is %s" % first_code)
        if (first_code != ''):
            # Hack for percentage ratings
            if (first_code == 'Write in %'):
                rating_types_by_row[row_index] = percent_rating_type
                continue
            # Now read in the categories.
            i = 0
            code_list = []
            while (True):
                if (len(row) > 7+i and row[7+i] != ''):
                    code_list.append(row[7+i])
                else:
                    break;
                i+=1
            name = '/'.join(code_list)
            if (name in rating_types_by_values):
                # if this type already exists, re-use the existing one
                rating_type = rating_types_by_values[name]
                rating_types_by_row[row_index] = rating_type
            else:
                # otherwise, create a new one.
                print ("Creating item for %s" % name)
                new_rating_type = RatingType.objects.get_or_create(description=name, storage_type='CATEGORY')[0]
                for index, code in enumerate(code_list):
                    name = code[0:31]
                    new_category = Category.objects.get_or_create(name=name,description=code, db_value=index)[0]
                    new_rating_type.values.add(new_category)
                new_rating_type.save()
                rating_types_by_values[name] = new_rating_type
                rating_types_by_row[row_index] = new_rating_type

    # reset the reader to the start of the file to generate items.
    f.seek(0)
    current_module = None
    for row_index, row in enumerate(reader):
        # If nothing in the first three columns but something in column 6, this is a module header
        if (row[0] == '' and row[1] == '' and row[2] == '' and row[7] == '' and row[6] != ''):
            current_module = Module.objects.get_or_create(description=row[6])[0]
        if (not (row_index in rating_types_by_row)):
            continue
        rating_type = rating_types_by_row[row_index]
        instrument = row[0]
        number = row[1]
        category_1 = row[2]
        category_2 = row[3]
        measure = row[4]
        question = row[6]
        # do some data cleaning.
        if (number == ''):
            number = 0.0

        name = instrument + '-' + str(number)
        
        if (measure != ''):
            new_item = Item.objects.get_or_create(name=name, 
                                                  description=question,
                                                  instrument=instrument,
                                                  number=number,
                                                  category_1=category_1,
                                                  category_2=category_2, 
                                                  rating_type=rating_type)[0]
            # Last, add the item to the module corresponding to the header
            if (current_module != None):
                current_module.items.add(new_item)
finally:
    f.close()