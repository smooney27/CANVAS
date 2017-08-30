import logging
import csv
import random
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from ratestreets.models import *
from ratestreets.forms import *
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse
from django.db import connection
from django.db.models import Q

# Create your views here.
@login_required
def mainmenu(request):
    if (request.user.is_superuser):
        return redirect('ratestreets.views.viewadmintasks')
    else:
        return redirect('ratestreets.views.viewtasksummary')

@login_required
def viewtasksummary(request):
    studies = Study.objects.filter(raters=request.user)
    return render_to_response('ratestreets/viewtasksummary.html', {'studies': studies}, context_instance=RequestContext(request))

@login_required
def startrating(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    tasks = RatingTask.objects.filter(user=request.user, segment__study=study, completed_at=None).order_by('segment', 'module')
    if tasks.count() > 0:
        return redirect('ratestreets.views.ratestreet', tasks[0].id)
    else:
        return redirect('ratestreets.views.viewtasksummary')
    
@login_required
def viewtasks(request, study_id=None):
    if (study_id != None):
        study = get_object_or_404(Study, pk=study_id)
        tasks = RatingTask.objects.filter(user=request.user, segment__study=study).order_by('segment', 'module')
    else:
        tasks = RatingTask.objects.filter(user=request.user).order_by('segment', 'module')
    return render_to_response('ratestreets/viewtasks.html', {'tasks': tasks}, context_instance=RequestContext(request))

@login_required
def viewadmintasks(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasksummary')
    tasks = [
             {'url':reverse('ratestreets.views.createstudy'), 'taskname':'Create a Study'},
             {'url':reverse('ratestreets.views.viewstudies'), 'taskname':'Manage My Studies'},
#             {'url':reverse('ratestreets.views.importsegments'), 'taskname':'Import Street Segments for a Study'},
             {'url':reverse('ratestreets.views.viewusers'), 'taskname':'Manage My Users'},
             {'url':reverse('ratestreets.views.viewmodules'), 'taskname':'Manage Modules'},
             {'url':reverse('ratestreets.views.importmodules'), 'taskname':'Import Module(s) From CSV'},
             {'url':reverse('ratestreets.views.viewtasksummary'), 'taskname':'Rate Streets'},
             ]
    return render_to_response('ratestreets/viewadmintasks.html', {'tasks': tasks}, context_instance=RequestContext(request))

@login_required
def createrater(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = RaterForm(request, request.POST)
        if (form.is_valid()):
            form.save()
            # todo$ redirect to show page?  Or create study page?
            return redirect('ratestreets.views.viewrater ')
    else:
        form = RaterForm(request)
    return render_to_response('ratestreets/new_form.html', {'form': form, 'item_type':'User'}, context_instance=RequestContext(request))

@login_required
def viewusers(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    studies = []
    if (study_id != None):
        study = get_object_or_404(Study, pk=study_id)
        studies.append(study)
    else:
        studies = Study.objects.filter(managers=request.user)
        logging.debug('Found %d studies from query' % studies.count())
    users = User.objects.filter(Q(rated_studies_set__in=studies) |
                                Q(managed_studies_set__in=studies) |
                                Q(directed_studies_set__in=studies)).distinct()
    return render_to_response('ratestreets/view_users.html', {'users': users}, context_instance=RequestContext(request))

@login_required
def edituser(request, user_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    user = get_object_or_404(User, pk=user_id)
    if (request.method =='POST'):
        form = UserForm(request, request.POST, instance=user)
        if (form.is_valid()):
            form.save()
            # todo$ redirect to show page?  Or create study page?
            return redirect('ratestreets.views.viewadmintasks')
    else:
        form = UserForm(request, instance=user)
    return render_to_response('ratestreets/edit_form.html', {'form': form, 'item_type':'User'}, context_instance=RequestContext(request))

@login_required
def createuser(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = UserForm(request, request.POST)
        if (form.is_valid()):
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_staff = form.cleaned_data['is_admin'] == True
            user.is_superuser = form.cleaned_data['is_admin'] == True
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            for study in form.cleaned_data['rated_studies']:
                study.raters.add(user)
            # todo$ redirect to show page?  Or create study page?
            return render_to_response('ratestreets/new_user_confirm.html', {'user': user, 'password':password}, context_instance=RequestContext(request))
    else:
        form = UserForm(request)
    return render_to_response('ratestreets/new_form.html', {'form': form, 'item_type':'User'}, context_instance=RequestContext(request))


@login_required
def createstudy(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = StudyForm(request, request.POST, request.FILES, mode='New')
        if (form.is_valid()):
            study = form.save()
            if ('segment_file' in request.FILES):
                if (form.cleaned_data['format'] == '2'):
                    study.add_segments_from_address_list(request.FILES['segment_file'])
                else:
                    study.add_segments_from_csv(request.FILES['segment_file'])
            else:
                logging.debug("no segment files found: %s" % request.FILES)
            # todo$ redirect to show page?  Or create study page?
            return redirect('ratestreets.views.viewadmintasks')
    else:
        form = StudyForm(request, mode='New')
    return render_to_response('ratestreets/new_form_with_attachment.html', {'form': form, 'item_type':'Study'}, context_instance=RequestContext(request))

@login_required
def viewstudies(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    studies = Study.objects.filter(managers=request.user)
    return render_to_response('ratestreets/viewstudies.html', {'studies': studies}, context_instance=RequestContext(request))

@login_required
def editstudy(request, study_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    if (request.method =='POST'):
        form = StudyForm(request, request.POST, request.FILES, instance=study, mode='Edit')
        if (form.is_valid()):
            form.save()
            if ('segment_file' in request.FILES):
                if (form.cleaned_data['format'] == '2'):
                    study.add_segments_from_address_list(request.FILES['segment_file'])
                else:
                    study.add_segments_from_csv(request.FILES['segment_file'])
            # Saving the form may not save the model (e.g. if only many-to-many
            # fields like raters have been updated) so ensure the tasks exist here. 
            study.ensure_all_tasks_exist()
            # todo$ redirect to show page?  Or create study page?
            return redirect('ratestreets.views.viewadmintasks')
    else:
        form = StudyForm(request, instance=study, mode='Edit')
    return render_to_response('ratestreets/edit_form_with_attachment.html', {'form': form, 'item_type':'Study'}, context_instance=RequestContext(request))

@login_required
def studyresults(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    results = []
    for item in Item.objects.filter(module__study = study):
        results.append({'item':item.description, 'kappa':item.get_kappa(study)})
    results = sorted(results, key=lambda result:result['kappa'])
    return render_to_response('ratestreets/studyresults.html', {'study':study, 'results': results}, context_instance=RequestContext(request))

@login_required
def listsegments(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    segments = Segment.objects.filter(study=study)
    return render_to_response('ratestreets/list_segments.html', {'segments': segments}, context_instance=RequestContext(request))

@login_required
def importsegments(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = SegmentImportForm(request, request.POST, request.FILES)
        if (form.is_valid()):
            study = form.cleaned_data['study']
            logging.debug("Format is %s " % form.cleaned_data['format'])
            if (form.cleaned_data['format'] == '2'):
                study.add_segments_from_address_list(request.FILES['segment_file'])
            else:
                study.add_segments_from_csv(request.FILES['segment_file'])
            return redirect('ratestreets.views.viewstudies')
    else:
        form = SegmentImportForm(request)
        if (study_id != None):
            form.initial['study']=study_id
    return render_to_response('ratestreets/import_from_csv.html', {'form': form, 'item_type': 'Segments'}, context_instance=RequestContext(request))

@login_required
def importmodules(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = ModuleImportForm(request, request.POST, request.FILES)
        if (form.is_valid()):
            if (form.cleaned_data['module'] == None):
                Module.create_modules_from_csv(request.FILES['item_csv'])
            else:
                module = form.cleaned_data['module']
                module.add_items_from_csv(request.FILES['item_csv'])
            return redirect('ratestreets.views.viewmodules')
    else:
        form = ModuleImportForm(request)
    return render_to_response('ratestreets/import_from_csv.html', {'form': form, 'item_type': 'Items'}, context_instance=RequestContext(request))


@login_required
def viewmodules(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    modules = Module.objects.all()
    return render_to_response('ratestreets/viewmodules.html', {'modules': modules}, context_instance=RequestContext(request))


@login_required
def editmodule(request, module_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    module = get_object_or_404(Module, pk=module_id)
    if (request.method =='POST'):
        form = ModuleForm(request, request.POST, instance=module)
        if (form.is_valid()):
            form.save()
            # todo -- should find associated studies and update task lists
            return redirect('ratestreets.views.viewadmintasks')
    else:
        form = ModuleForm(request, instance=module)
    return render_to_response('ratestreets/edit_form.html', {'form': form, 'item_type':'Module'}, context_instance=RequestContext(request))


@login_required
def pano(request, task_id):
    if (task_id == 0 or task_id == None):
        return render_to_response('ratestreets/emptypano.html', context_instance=RequestContext(request))
    else:
        task = get_object_or_404(RatingTask, pk=task_id)
        return render_to_response('ratestreets/showpano.html', {'task': task}, context_instance=RequestContext(request))

@login_required
def pano_v2(request, task_id):
    if (task_id == 0 or task_id == None):
        return render_to_response('ratestreets/emptypano.html', context_instance=RequestContext(request))
    else:
        task = get_object_or_404(RatingTask, pk=task_id)
        return render_to_response('ratestreets/showpano_v2.html', {'task': task}, context_instance=RequestContext(request))

@login_required
def ratestreet(request, task_id):
    task = get_object_or_404(RatingTask, pk=task_id)
    if (request.method =='POST'):
        boolean_formset = BooleanRatingFormSet(request.POST, prefix="boolean")
        count_formset = CountRatingFormSet(request.POST, prefix="count")
        freeform_formset = FreeFormRatingFormSet(request.POST, prefix="freeform")
        category_formset = CategoryRatingFormSet(request.POST, prefix="category")
        formsets = [category_formset, boolean_formset, count_formset, freeform_formset]
        all_formsets_valid = True
        for formset in formsets:
            if (formset.is_valid() == False):
                all_formsets_valid = False
                break
        
        if (all_formsets_valid):
            for formset in formsets:
                formset.save()
            # Find next task before updating this one.
            next_task = None
            unfinished_tasks = RatingTask.objects.filter(user=request.user, completed_at=None).order_by('segment', 'module')
            for index, unfinished_task in enumerate(unfinished_tasks):
                if unfinished_task == task:
                    if (index + 1) < unfinished_tasks.count(): 
                        next_task = unfinished_tasks[index+1]
                    break
            task.completed_at = datetime.now()
            task.save()
            # Move to next task.  If there are none, go back to list.
            if (next_task == None):
                return redirect('ratestreets.views.viewtasks')
            else:
                return redirect('ratestreets.views.ratestreet', task_id=next_task.id)
        else:
            # Failed validity check.  Redraw the same form
            return render_to_response('ratestreets/ratestreet.html', {'formsets': formsets, 'task': task}, context_instance=RequestContext(request))
    else:
        boolean_ratings = task.find_or_create_ratings(BooleanRating)
        boolean_formset = BooleanRatingFormSet(queryset=boolean_ratings, prefix="boolean")
        count_ratings = task.find_or_create_ratings(CountRating)
        count_formset = CountRatingFormSet(queryset=count_ratings, prefix="count")
        freeform_ratings = task.find_or_create_ratings(FreeFormRating)
        freeform_formset = FreeFormRatingFormSet(queryset=freeform_ratings, prefix="freeform")
        category_ratings = task.find_or_create_ratings(CategoryRating)
        category_formset = CategoryRatingFormSet(queryset=category_ratings, prefix="category")
        formsets = [category_formset, boolean_formset, count_formset, freeform_formset]
    return render_to_response('ratestreets/ratestreet.html', {'formsets': formsets, 'task': task}, context_instance=RequestContext(request))


@login_required
def dotask(request, task_id):
    task = RatingTask.objects.get(id = task_id)
    return render_to_response('ratestreets/dotask.html', {'task': task}, context_instance=RequestContext(request))


@login_required
def export_data(request, study_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    boolean_ratings_queryset = BooleanRating.objects.filter(segment__study = study)
    count_ratings_queryset = CountRating.objects.filter(segment__study = study)
    category_ratings_queryset = CategoryRating.objects.filter(segment__study = study)
    free_form_ratings_queryset = FreeFormRating.objects.filter(segment__study = study)

    querysets = [boolean_ratings_queryset, count_ratings_queryset, category_ratings_queryset, free_form_ratings_queryset]

    # Find the list of columns for our study, including the impediment columns
    data_columns = []
    data_column_codebooks = []
    items = Item.objects.filter(module__study=study)
    for item in items.all():
        data_columns.append(item.name)
        data_column_codebooks.append(item.get_category_codebook('/'))
        data_columns.append(item.name + "_impediment")
        data_column_codebooks.append('other=0/blocked=1/too far=2/too blurry=3/too dim=3')

    # Convert the data from tall to wide
    data_rows = {}
    for queryset in querysets:
        for rating in queryset.all():
            row_key = (rating.user.id, rating.segment.id)
            column_key = rating.item.name
            impediment_column_key = str(rating.item.name) + "_impediment" 
            if (row_key in data_rows):
                data_for_row = data_rows[row_key]
            else:
                data_for_row = {}
            data_for_row[column_key] = rating.rating
            data_rows[row_key] = data_for_row
            data_for_row[impediment_column_key] = rating.impediment

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = "attachment; filename=%s.csv" % slugify(study.description)

    writer = csv.writer(response)
    # First, write the headers
    header_row = ['User', 'Segment']
    for column_name in data_columns:
        header_row.append(column_name)
    writer.writerow(header_row) 
    
    codebook_row = ['', '']
    for data_column_codebook in data_column_codebooks:
        codebook_row.append(data_column_codebook)
    writer.writerow(codebook_row) 

    # Sort on segment ID, then on user ID
    def segment_user_sort (first,second):
        if (first[1] == second[1]):
            return int(first[0] - second[0])
        return int(first[1] - second[1])

    # Then write the data, leaving "" if no data present
    for row_key in sorted(data_rows.iterkeys(), cmp=segment_user_sort):
        row_to_write = [row_key[0], row_key[1]]
        data_for_row = data_rows[row_key]
        for column_name in data_columns:
            if (column_name in data_for_row):
                value = data_for_row[column_name]
            else:
                value = ''
            row_to_write.append(value)
        writer.writerow(row_to_write)
    return response

@login_required
def showallsegments(request):
    segments = Segment.objects.all()
    return render_to_response('ratestreets/showallsegments.html', {'segments': segments}, context_instance=RequestContext(request))
