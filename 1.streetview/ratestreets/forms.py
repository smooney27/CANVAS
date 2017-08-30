import logging
from django.forms import *
from ratestreets.models import *
from ratestreets.widgets import *
from django.forms.models import modelformset_factory

RatingFormSet = modelformset_factory(Rating)

class SegmentImportForm(Form):
    study = ModelChoiceField(queryset=None)
    SEGMENT_IMPORT_CHOICES = (
                              ('1', "Lat/Long Pairs"),
                              ('2', "Addresses"),
                              )
    format = TypedChoiceField(choices = SEGMENT_IMPORT_CHOICES, empty_value=None, label="File Format")
    segment_file = FileField()
    def __init__(self, request, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.fields['study'].queryset=Study.objects.filter(managers=request.user)


class UserForm(ModelForm):
    is_admin = BooleanField(required=False, label='Can administer studies')
    rated_studies = ModelMultipleChoiceField(None, required=False, label='Participating in:')
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
                          ('0', 'Other'),
                          ('1', 'Blocked'),
                          ('2', 'Too Far'),
                          ('3', 'Too Blurry'),
                          ('4', 'Too Dim'),
                          )
    impediment = TypedChoiceField(required=False, 
                                  choices=IMPEDIMENT_CHOICES, 
                                  coerce=coerce_impediment,
                                  empty_value=None,
                                  label='Why can\'t you tell?',
#                                  widget=forms.Select(attrs={'style':'display:none'}))
                                  widget=forms.Select())    

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
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['rating'].label = instance.item.name + ': ' + instance.item.description
    class Meta:
        model = BooleanRating
        fields = ('rating', 'impediment')
        
BooleanRatingFormSet = modelformset_factory(BooleanRating, form=BooleanRatingForm, extra=0)

class CountRatingForm(RatingForm):
    rating = IntegerField(required=False)
    cannot_tell = BooleanField(label="cannot tell", required=False)
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['rating'].label = instance.item.name + ': ' + instance.item.description
            self.fields['cannot_tell'].initial = instance.impediment != None
    def clean(self):
        rating = self.cleaned_data['rating']
        impediment = self.cleaned_data['impediment']
        logging.debug('rating: ' + str(rating))
        logging.debug('impediment: ' + str(impediment))
        if ((rating != None) and (impediment != None)):
            raise ValidationError("Please enter blank if you cannot tell for sure")
        elif ((rating == None) and (impediment == None)):
            raise ValidationError("Please enter a value or 'Cannot Tell' and a reason why not.")
        return self.cleaned_data
    class Meta:
        model = CountRating
        fields = ('rating', 'cannot_tell', 'impediment')

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
        ModelForm.__init__(self, *args, **kwargs)
        if instance:
            self.fields['rating'].label = instance.item.description
            category_choices = []
            for category in instance.item.rating_type.values.all():
                tuple = (category.db_value, category.name)
                category_choices.append(tuple)
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
        fields = ('rating', 'impediment')
        
CategoryRatingFormSet = modelformset_factory(CategoryRating, form=CategoryRatingForm, extra=0)


class FreeFormRatingForm(RatingForm):
    rating = CharField(max_length = 1024, required=False, widget=Textarea)
    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        instance = kwargs['instance']
        if instance:
            self.fields['rating'].label = instance.item.name + ': ' + instance.item.description
    class Meta:
        model = FreeFormRating
        fields = ('rating', 'impediment')

FreeFormRatingFormSet = modelformset_factory(FreeFormRating, form=FreeFormRatingForm, extra=0)

class StudyForm(ModelForm):
    segment_file = FileField(required=False)
    SEGMENT_IMPORT_CHOICES = (
                              ('1', "Lat/Long Pairs"),
                              ('2', "Addresses"),
                              )
    format = TypedChoiceField(choices = SEGMENT_IMPORT_CHOICES, empty_value=None, label="File Format")
    def __init__(self, request, *args, **kwargs):
        mode = None
        if ('mode' in kwargs):
            mode = kwargs['mode']
            # Strip the custom keywords arg so ModelForm doesn't barf.
            del kwargs['mode']
        ModelForm.__init__(self, *args, **kwargs)
        self.fields['director'].queryset = User.objects.filter(is_staff=True)
        self.fields['managers'].queryset = User.objects.filter(is_staff=True)
        self.fields['raters'].queryset = User.objects.all()
        logging.debug('kwargs is %s' % kwargs)
        if (mode == 'Edit'):
            self.fields['segment_file'].label = "Additional Segments (Optional):"
        else:
            self.fields['segment_file'].label = "Segments File (Optional):"
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

class ModuleImportForm(Form):
    module = ModelChoiceField(queryset=Module.objects.all(), label="Select Module", empty_label="Modules are defined in CSV", required=False)
    item_csv = FileField()
    def __init__(self, request, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

