import logging
import csv
import geojson

from ratestreets.forms import SegmentForm
from ratestreets.forms import SegmentAutoselectForm
from ratestreets.models import Segment
from ratestreets.models import SamplePoint
from django.forms.models import modelformset_factory

class ViewUtils:
    @staticmethod
    def create_segment_formset_from_file(study, uploaded_file, *args, **kwargs):
        filetype = kwargs.pop('filetype', 'csv')
        segment_formset = None
        try:
            initial = []
            if (filetype == 'csv'):
                uploaded_file.read()
                reader = csv.reader(uploaded_file, dialect='excel')
                for index, row in enumerate(reader):
                    start_lng = float(row[3])
                    start_lat = float(row[4])
                    end_lng = float(row[5])
                    end_lat = float(row[6])
                    street = row[0] + ', ' + row[1]
                    sample_point,created = SamplePoint.objects.get_or_create(row_id=index, study=study)
                    sample_point.lat = start_lat
                    sample_point.lng = start_lng
                    sample_point.save()
                    default_data = {'study':study, 
                                    'sample_point': sample_point.id,
                                    'point_of_view':0, 
                                    'start_lat':start_lat, 
                                    'start_lng':start_lng, 
                                    'end_lat':end_lat, 
                                    'end_lng':end_lng}
                    if (street != None and street != ''):
                        default_data['street_address'] = street
                    initial.append(default_data)
            elif (filetype == 'geojson'):
                segment_list = geojson.load(uploaded_file)
                for segment in segment_list['features']:
                    if (segment['geometry']['type'] != 'LineString'):
                        raise ('unexpected feature in geojson segment import: %s' % segment['geometry']['type'])
                    coords = segment['geometry']['coordinates']
                    # TODO -- should track sample points in CSV, too?
                    sample_point,created = SamplePoint.objects.get_or_create(row_id=segment['id'], study=study)
                    sample_point.lat = coords[0][0]
                    sample_point.lng = coords[0][1]
                    sample_point.save()
                    default_data = {'study':study, 
                                    'point_of_view':0, 
                                    'sample_point':sample_point.id,
                                    'start_lat':coords[0][0], 
                                    'start_lng':coords[0][1], 
                                    'end_lat':coords[1][0], 
                                    'end_lng':coords[1][1]}
                    default_data['street_address'] = segment['properties']['Segment_ID_1']
                    default_data['should_save'] = True
                    initial.append(default_data)
            elif (filetype == 'address_list'):
                uploaded_file.read()
                for line in uploaded_file:
                    line = line.rstrip()
                    default_data = {'study':study,
                                    'point_of_view': 0,
                                    'street_address': line}
                    initial.append(default_data)
            SegmentFormSet = modelformset_factory(Segment, form=SegmentForm, extra=len(initial))
            segment_formset = SegmentFormSet(queryset=Segment.objects.none(), initial=initial)
        finally:
            uploaded_file.close()
        return segment_formset

    @staticmethod
    def create_segment_autoselect_formset_from_file(study, uploaded_file, *args, **kwargs):
        save_targets = kwargs.pop('save_targets', False)
        segment_autoselect_formset = None
        try:
            uploaded_file.read()
            initial = []
            reader = csv.DictReader(uploaded_file, dialect='excel')
            idColumns = ['ID', 'Id', 'id', 'Identifier', 'identifier']
            xColumns = ['X', 'POINT_X', 'LONGITUDE', 'longitude']
            yColumns = ['Y', 'POINT_Y', 'LATITUDE', 'latitude']
            idColumn = None
            xColumn = None
            yColumn = None
            for column in idColumns:
                if column in reader.fieldnames:
                    idColumn = column
                    break
            for column in xColumns:
                if column in reader.fieldnames:
                    xColumn = column
                    break
            if xColumn == None:
                raise Exception("No X column found in point file")
            for column in yColumns:
                if column in reader.fieldnames:
                    yColumn = column
                    break
            if yColumn == None:
                raise Exception("No Y column found in point file")
            for index, row in enumerate(reader):
                if row[xColumn] == '' or row[yColumn] == '':
                    continue
                if (idColumn is not None):
                    id = row[idColumn]
                else:
                    id=index
                lng = float(row[xColumn])
                lat = float(row[yColumn])
                # If approprate, save the autoselect targets
                if (save_targets):
                    sample_point,created = SamplePoint.objects.get_or_create(row_id=id, study=study)
#                    sample_point.study = study
# s                   sample_point.row_id = id
                    sample_point.lat = lat
                    sample_point.lng = lng
                    sample_point.save()
                default_data = {'study':study,
                                'point_of_view':0, 
                                'sample_point':sample_point.id,
                                'lat':lat, 
                                'lng':lng}
                initial.append(default_data)
            SegmentAutoselectFormSet = modelformset_factory(Segment, form=SegmentAutoselectForm, extra=len(initial))
            segment_autoselect_formset = SegmentAutoselectFormSet(queryset=Segment.objects.none(), initial=initial)
        finally:
            uploaded_file.close()
        return segment_autoselect_formset
