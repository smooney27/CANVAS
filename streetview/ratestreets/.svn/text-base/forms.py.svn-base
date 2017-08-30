import logging
import json

from django.forms import *
from ratestreets.models import *
from ratestreets.widgets import *
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

RatingFormSet = modelformset_factory(Rating)

class SegmentAutoselectFileForm(Form):
    study = ModelChoiceField(queryset=None)
    segment_file = FileField()
    def __init__(self, request, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.fields['study'].queryset=Study.objects.filter(managers=request.user)

class SegmentAutoselectForm(ModelForm):
    study = ModelChoiceField(queryset=None, widget=HiddenInput)
    sample_point = ModelChoiceField(queryset=None, widget=HiddenInput)
    start_attempts = IntegerField(label="Start Points Searched", required=False)
    end_attempts = IntegerField(label="End Points Searched", required=False)
    street_address = CharField(widget=HiddenInput, required=False)
    should_save = BooleanField(label="Use This Segment", required=False)
    def __init__(self, *args, **kwargs):
        super(SegmentAutoselectForm, self).__init__(*args, **kwargs)
        segment_data = {}
        if 'instance' in kwargs:
            instance = kwargs['instance']
            segment_data = {
                            'sample_point': instance.sample_point,
                            'lat': instance.lat,
                            'lng': instance.lng,
                            }
            self.title = "<h3>" + "%f, %f" % (instance.lat, instance.lng) + "</h3>"
        elif 'initial' in kwargs:
            initial = kwargs['initial']
            segment_data = {
                            }
            if ('sample_point' in initial):
                segment_data['sample_point'] = initial['sample_point'],
            if ('lat' in initial):
                segment_data['lat'] = initial['lat'],
            if ('lng' in initial):
                segment_data['lng'] = initial['lng'],
            self.title = "<h3>" + "%f, %f" % (initial['lat'], initial['lng']) + "</h3>"
        self.segment_js_block = mark_safe("<div auto_id=" + str(kwargs['prefix']) + "></div><script>add_to_queue('" + str(kwargs['prefix'])  + "'," + json.dumps(segment_data) + ",'" + str(kwargs['prefix']) + "-wrapper');</script>")
        # Note: this is slightly bogus, since we're not validating that the manager has the right to 
        # add segments to this study.
        self.fields['study'].queryset=Study.objects.all()
        self.fields['sample_point'].queryset=SamplePoint.objects.all()
        self.prefix = str(kwargs['prefix'])
    def render_script(self, *args, **kwargs):
        return self.segment_js_block
    def render_heading(self, *args, **kwargs):
        return self.title
    def item_id(self, *args, **kwargs):
        return self.prefix
    class Meta:
        model = Segment
        fields = ('sample_point', 'start_lat', 'start_lng', 'start_attempts', 'point_of_view', 'end_lat', 'end_lng', 'end_attempts', 'should_save', 'street_address', 'study') 
SegmentAutoselectFormSet = modelformset_factory(Segment, form=SegmentAutoselectForm, extra=0)

class CreateTaskForm(Form):
    task_allocation = TypedChoiceField(choices = Study.TASK_ALLOCATION_CHOICES, label="Allocation Choice")
    task_overlap = IntegerField()
    def __init__(self, *args, **kwargs):
        instance = None
        if 'instance' in kwargs:
            instance = kwargs['instance']
            del kwargs['instance']
        Form.__init__(self, *args, **kwargs)
        if instance is not None:
            self.fields['task_overlap'].initial = instance.task_overlap or 0
            self.fields['task_allocation'].initial = instance.task_allocation or 0

class TaskAssignForm(Form):
    active_raters = ModelMultipleChoiceField(queryset=User.objects.all(), required=False, label='Pending For:')
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            segment = kwargs['instance']
#            kwargs['initial'] = {'active_raters':segment.raters}
            del kwargs['instance']
        Form.__init__(self, *args, **kwargs)
        # Query set is shown -- This should be limited to the manager's users
#        active_raters.queryset = User.objects.all()
        # Initial is intially selected
        self.fields['active_raters'].initial = segment.rater_list


class SegmentFileForm(Form):
    study = ModelChoiceField(queryset=None)
    SEGMENT_IMPORT_CHOICES = (
                              ('1', "Lat/Long Pairs"),
                              ('2', "Addresses"),
                              ('3', "GeoJSON")
                              )
    format = TypedChoiceField(choices = SEGMENT_IMPORT_CHOICES, empty_value=None, label="File Format")
    skip_verify = BooleanField(label="Skip Manual Verify Step", required=False)
    segment_file = FileField()
    def __init__(self, request, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.fields['study'].queryset=Study.objects.filter(managers=request.user)

class SegmentForm(ModelForm):
    street_address = CharField(widget=HiddenInput)
    sample_point = ModelChoiceField(queryset=None, widget=HiddenInput)
    study = ModelChoiceField(queryset=None, widget=HiddenInput)
    should_save = BooleanField(label="Use This Segment", required=False)
    def __init__(self, *args, **kwargs):
        edit_description = False
        if 'edit_description' in kwargs:
            if kwargs['edit_description'] == True:
                edit_description = True
            del kwargs['edit_description']
        super(SegmentForm, self).__init__(*args, **kwargs)
        segment_data = {}
        street_address = ''
        if 'instance' in kwargs:
            instance = kwargs['instance']
            street_address = instance.street_address or ''
            segment_data = {
                            'sample_point': instance.sample_point,
                            'street_address': street_address,
                            'start_lat': instance.start_lat,
                            'start_lng': instance.start_lng,
                            'end_lat': instance.end_lat,
                            'end_lng': instance.end_lng
                            }
        elif 'initial' in kwargs:
            initial = kwargs['initial']
            street_address = initial['street_address'] or ''
            segment_data = {
                            'street_address': street_address
                            }
            if ('start_lat' in initial):
                segment_data['start_lat'] = initial['start_lat'],
            if ('start_lng' in initial):
                segment_data['start_lng'] = initial['start_lng'],
            if ('end_lat' in initial):
                segment_data['end_lat'] = initial['end_lat'],
            if ('end_lng' in initial):
                segment_data['end_lng'] = initial['end_lng'],
            if ('sample_point' in initial):
                segment_data['sample_point'] = initial['sample_point'],
        if 'prefix' in kwargs:
            prefix = str(kwargs['prefix'])
        else:
            prefix = '1'
        if edit_description:
            self.fields['street_address'].widget = TextInput(attrs={'title': 'Segment Name'})
        if 'hide_field' in kwargs and kwargs['hide_field']:
            self.segment_js_block = mark_safe("<div auto_id=" + prefix + "></div><script>add_to_queue('" + prefix  + "'," + json.dumps(segment_data) + "," + str(kwargs['prefix']) + "-wrapper');</script>")
        else:
            self.segment_js_block = mark_safe("<div auto_id=" + prefix + "></div><script>add_to_queue('" + prefix  + "'," + json.dumps(segment_data) + ");</script>")
        self.address_block = mark_safe("<h3>" + street_address + "</h3>")
        # Note: this is slightly bogus, since we're not validating that the manager has the right to 
        # add segments to this study.
        self.fields['study'].queryset=Study.objects.all()
        self.fields['sample_point'].queryset=SamplePoint.objects.all()
    def render_script(self, *args, **kwargs):
        return self.segment_js_block
    def render_heading(self, *args, **kwargs):
        return self.address_block
    class Meta:
        model = Segment
        fields = ('sample_point', 'start_lat', 'start_lng', 'point_of_view', 'end_lat', 'end_lng', 'street_address', 'should_save', 'study') 
SegmentFormSet = modelformset_factory(Segment, form=SegmentForm, extra=0)

class UserForm(ModelForm):
    is_admin = BooleanField(required=False, label='Can administer studies')
    rated_studies = ModelMultipleChoiceField(None, required=False, label='Participating in:')
    default_password = CharField(required=False)
    def __init__(self, request, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['rated_studies'].queryset = Study.objects.filter(managers=request.user)
        self.fields['rated_studies'].initial = Study.objects.filter(raters=self.instance)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'rated_studies')

class RatingForm(ModelForm):
    IMPEDIMENT_CHOICES = (
                          ('', 'Select'),
                          ('1', 'Other'),
                          ('2', 'Too Far'),
                          ('3', 'Too Blurry'),
                          ('4', 'Too Dim'),
                          ('5', 'Too Bright'),
                          ('6', 'Too Shady'),
                          ('7', 'Problems with Video Feed/Images'),
                          ('8', 'Blocked by Parked Cars'),
                          ('9', 'Blocked by Parked Trucks or Buses'),
                          ('10', 'Blocked by Car Traffic'),
                          ('11', 'Blocked by Truck or Bus Traffic'),
                          ('12', 'Blocked by Roadside Shrubs'),
                          ('13', 'Blocked by Roadside Trees'),
                          ('14', 'Blocked by Median Foliage'),
                          ('15', 'Blocked by Fence'),
                          ('16', 'Blocked by Awnings'),
                          ('17', 'Blocked by Scaffolding or Construction Equipment'),
                          ('18', 'Blocked by Other Obstruction'),
                          )
    impediment = TypedChoiceField(required=False, 
                                  choices=IMPEDIMENT_CHOICES, 
                                  coerce=coerce_impediment,
                                  empty_value=None,
                                  label='Why can\'t you tell?',
#                                  widget=forms.Select(attrs={'style':'display:none'}))
                                  widget=forms.Select())    
    image_date = DateField(widget=HiddenInput, input_formats=('%Y-%m',))
    help_text_id = None
    one_side_only= False
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['rating'].label = instance.item.name + ': ' + instance.item.description
            if (instance.item.help_text.exists()):
                self.help_text_id = instance.item.help_text.all()[0].id
            if (instance.item.one_side_only):
                self.one_side_only = True
    def as_p(self):
        base_html = ModelForm.as_p(self)
        pre_split, sep, post_split = base_html.partition('</label>')
        if (self.help_text_id != None):
            help_url = reverse("ratestreets.views.showhelp", args=[self.help_text_id])
            base_html = pre_split + sep + '&nbsp;(<a target="help_window" href=' + help_url + ' onclick="find_or_open_help_window(\''  + help_url + '\')">Help</a>)'
            if (not self.one_side_only):
                base_html = base_html + '&nbsp;&lt;-- Not limited to one side'
            base_html = base_html + post_split
        elif (not self.one_side_only):
            base_html = pre_split + sep + '&nbsp;&lt;-- Not limited to one side' + post_split
        return base_html
        
class BooleanRatingForm(RatingForm):
    YES_NO_CHOICES = (
                      ('', 'Select'),
                      ('1', 'Yes'),
                      ('2', 'No'),
                      ('0', 'Cannot tell'),
                      )
    rating = TypedChoiceField(required=False, 
                              choices=YES_NO_CHOICES, 
                              coerce=coerce_boolean,
                              empty_value=None)
    class Meta:
        model = BooleanRating
        fields = ('rating', 'impediment', 'image_date')
        
BooleanRatingFormSet = modelformset_factory(BooleanRating, form=BooleanRatingForm, extra=0)

class CountRatingForm(RatingForm):
    rating = IntegerField(required=False)
    cannot_tell = BooleanField(label="cannot tell", required=False)
    def __init__(self, *args, **kwargs):
        RatingForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['cannot_tell'].initial = instance.impediment != None
            if instance.item.skip_pattern != None:
                self.fields['rating'].widget.attrs['skip_pattern'] = instance.item.skip_pattern
    def clean(self):
        if ('rating' in self.cleaned_data and 'impediment' in self.cleaned_data):
            rating = self.cleaned_data['rating']
            impediment = self.cleaned_data['impediment']
            if ((rating != None) and (impediment != None)):
                raise ValidationError("Please enter blank if you cannot tell for sure")
            elif ((rating == None) and (impediment == None)):
                raise ValidationError("Please enter a value or 'Cannot Tell' and a reason why not.")
        return self.cleaned_data
    class Meta:
        model = CountRating
        fields = ('rating', 'cannot_tell', 'impediment', 'image_date')

CountRatingFormSet = modelformset_factory(CountRating, form=CountRatingForm, extra=0)

class CategoryRatingForm(RatingForm):
    DEFAULT_CHOICES = (
                      )
    rating = TypedChoiceField(required=False, 
                              choices=DEFAULT_CHOICES, 
                              coerce=coerce_category,
                              empty_value=None,
                              widget=RadioSelect)
    def __init__(self, *args, **kwargs):
        # Do "cannot tell" conversion before initing model form. 
        instance = kwargs['instance']
        if (instance and instance.rating == None and instance.impediment != None):
            instance.rating = -1
        RatingForm.__init__(self, *args, **kwargs)
        if instance:
            category_choices = []
            for category in instance.item.rating_type.values.all():
                tuple = (category.db_value, category.name)
                category_choices.append(tuple)
            category_choices.append(('-2','Skipped'))
            category_choices.append(('-1','Cannot Tell'))
            self.fields['rating'].choices = category_choices
            self.fields['rating'].widget.attrs={'question_id':instance.item.name}
            if instance.item.skip_pattern != None:
                self.fields['rating'].widget.attrs['skip_pattern'] = instance.item.skip_pattern
    def clean(self):
        rating = self.cleaned_data['rating']
        impediment = self.cleaned_data['impediment']
        if ((rating == None) and (impediment == None)):
            raise ValidationError("Please select a value or 'Cannot Tell' and a reason why not.")
        return self.cleaned_data
    class Meta:
        model = CategoryRating
        fields = ('rating', 'impediment', 'image_date')
        
CategoryRatingFormSet = modelformset_factory(CategoryRating, form=CategoryRatingForm, extra=0)


class FreeFormRatingForm(RatingForm):
    rating = CharField(max_length = 1024, required=False, widget=Textarea)
    cannot_tell = BooleanField(label="cannot tell", required=False)
    def __init__(self, *args, **kwargs):
        RatingForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['cannot_tell'].initial = instance.impediment != None
            if instance.item.skip_pattern != None:
                self.fields['rating'].widget.attrs['skip_pattern'] = instance.item.skip_pattern
    def clean(self):
        if ('rating' in self.cleaned_data and 'impediment' in self.cleaned_data):
            rating = self.cleaned_data['rating']
            impediment = self.cleaned_data['impediment']
            if ((rating != None) and (impediment != None)):
                raise ValidationError("Please enter blank if you cannot tell for sure")
            elif ((rating == None) and (impediment == None)):
                raise ValidationError("Please enter a value or 'Cannot Tell' and a reason why not.")
        return self.cleaned_data
    class Meta:
        model = FreeFormRating
        fields = ('rating', 'impediment', 'image_date')

FreeFormRatingFormSet = modelformset_factory(FreeFormRating, form=FreeFormRatingForm, extra=0)

class StudyForm(ModelForm):
    task_allocation = TypedChoiceField(label="Tasks per rater", choices=Study.TASK_ALLOCATION_CHOICES)
    task_overlap = IntegerField(label="Percentage Shared", required=False)
    def __init__(self, request, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['director'].queryset = User.objects.filter(is_staff=True)
        self.fields['managers'].queryset = User.objects.filter(is_staff=True)
        self.fields['raters'].queryset = User.objects.all()
    class Meta:
        model = Study

class ItemMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, item):
        if (item.rating_type.storage_type == 'CATEGORY'):
            options = []
            for category in item.rating_type.values.all():
                options.append(category.name) 
            choices = '(' + '/'.join(options) + ')'
        elif (item.rating_type.storage_type == 'COUNT'):
            choices = '(Number)'
        elif (item.rating_type.storage_type == 'TEXT'):
            choices = '(Text)'
        else:
            choices = ''
        return '%s -- %s -- %s' % (item.name, item.description, choices)

class ModuleForm(ModelForm):
    items = ItemMultipleChoiceField(queryset = Item.objects.all(), widget=CheckboxSelectMultiple)
    def __init__(self, request, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
    class Meta:
        model = Module

MODULE_IMPORT_FORMATS = (('CANVAS', 'CANVAS'),
                         ('REDCAP', 'REDCAP'))

class ModuleImportForm(Form):
    revision = CharField(max_length=32, label="Revision Name", required=True)
    module = ModelChoiceField(queryset=Module.objects.all(), label="Select Module", empty_label="Modules are defined in CSV", required=False)
    item_csv = FileField()
    source_format = ChoiceField(choices=MODULE_IMPORT_FORMATS)
    def __init__(self, request, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class RenderTimeForm(Form):
    render_time = DateTimeField(widget=HiddenInput)
