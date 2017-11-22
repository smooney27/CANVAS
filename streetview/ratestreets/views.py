import logging
import csv
import random
import re
import smtplib

from email.mime.text import MIMEText
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from ratestreets.models import *
from ratestreets.forms import *
from ratestreets.viewutils import *
from ratestreets.profile import *
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db import connection
from django.db.models import Q, Max

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
#             {'url':reverse('ratestreets.views.evaluateraters'), 'taskname':'Evaluate Raters'},
             {'url':reverse('ratestreets.views.viewmodules'), 'taskname':'Manage Modules'},
             {'url':reverse('ratestreets.views.importmodules'), 'taskname':'Import Module(s) From CSV'},
             {'url':reverse('ratestreets.views.viewtasksummary'), 'taskname':'Rate Streets'},
#             {'url':reverse('ratestreets.views.showallhelp'), 'taskname':'Show all help text'},
#            {'url':reverse('ratestreets.views.totalresults'), 'taskname':'Show Kappas across all completed studies'},
#             {'url':reverse('ratestreets.views.showratingtimes'), 'taskname':'Rating time analysis'},
#             {'url':reverse('ratestreets.views.mapexperiment'), 'taskname':'Compare Streetview Coverage'},
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
def evaluateraters(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    studies = []
    if (study_id != None):
        study = get_object_or_404(Study, pk=study_id)
        studies.append(study)
    else:
        studies = Study.objects.filter(managers=request.user)
    now = datetime.now()
    two_weeks_ago = datetime.today() - timedelta(weeks=2)
    completed_tasks = RatingTask.objects.filter(completed_at__lt=now, completed_at__gte=two_weeks_ago, segment__study__in=studies)
    users = User.objects.filter(Q(rated_studies_set__in=studies) |
                                Q(managed_studies_set__in=studies) |
                                Q(directed_studies_set__in=studies)).distinct().annotate(last_task=Max('ratingtask__completed_at')).order_by('last_task').reverse()
    rater_hash = {}
    segment_hash = {}
    for completed_task in completed_tasks:
        if completed_task.user in rater_hash:
            already_completed = rater_hash[completed_task.user]
        else:
            already_completed = 0
        rater_hash[completed_task.user] = already_completed + 1
        if completed_task.user in segment_hash:
            segments_for_user = segment_hash[completed_task.user]
        else:
            segments_for_user = {}
        segments_for_user[completed_task.segment] = 1
        segment_hash[completed_task.user] = segments_for_user
    results = []
    for user in users:
        result = {'username':user.username,
                  'last_task':user.last_task,
                  'last_login':user.last_login}
        if user in rater_hash:
            result['tasks_completed'] = rater_hash[user]
        if user in segment_hash:
            result['segments_affected'] = len(segment_hash[user])
        result['tasks_completed_ever'] = RatingTask.objects.filter(segment__study__in=studies, user=user, completed_at__lt=now).count()
        # This is not technically right: the overall median rating time is not the sum of the median rating times.  But we're going to squint here.
        median_rating_time = 0
        for module in Module.objects.filter(study__in=studies).distinct():
            first_item = module.items.filter(rating_type__storage_type='CATEGORY')[:1][0]
            rating_times = first_item.get_rating_times(studies, rater_ids=[user.id])
            if rating_times is not None:
                median_rating_time = median_rating_time + rating_times['median']
        result['median_rating_time']= median_rating_time
        results.append(result)
    return render_to_response('ratestreets/evaluate_raters.html', {'total_tasks_completed': completed_tasks.count(), 'results': results}, context_instance=RequestContext(request))


@login_required
def edituser(request, user_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    user = get_object_or_404(User, pk=user_id)
    if (request.method =='POST'):
        form = UserForm(request, request.POST, instance=user)
        if (form.is_valid()):
            user = form.save()
            user.is_staff = form.cleaned_data['is_admin'] == True
            user.is_superuser = form.cleaned_data['is_admin'] == True
            user.save()
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
            if form.cleaned_data['default_password'] == '':
                password = User.objects.make_random_password()
            else:
                password = form.cleaned_data['default_password']
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
        form = StudyForm(request, request.POST)
        if (form.is_valid()):
            study = form.save()
            return redirect('ratestreets.views.viewstudies')
    else:
        form = StudyForm(request)
    return render_to_response('ratestreets/new_form.html', {'form': form, 'item_type':'Study'}, context_instance=RequestContext(request))

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
        form = StudyForm(request, request.POST, request.FILES, instance=study)
        if (form.is_valid()):
            form.save()
            # Saving the form may not save the model (e.g. if only many-to-many
            # fields like raters have been updated) so ensure the tasks exist here. 
            study.ensure_all_tasks_exist()
            return redirect('ratestreets.views.viewstudies')
    else:
        form = StudyForm(request, instance=study)
    return render_to_response('ratestreets/edit_form.html', {'form': form, 'item_type':'Study'}, context_instance=RequestContext(request))

@login_required
def studyresults(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    results = []
    for item in Item.objects.filter(module__study = study):
        item_title = item.name + ':' + item.description
        kappa_pair = item.get_kappa(study)
        agreement_pair = item.get_percent_agreement(study)
        results.append({'item':item_title,
                        'kappa':kappa_pair[0],
                        'kappa_rating_count':kappa_pair[1], 
                        'percent_agreement':agreement_pair[0],
                        'item_id': item.id})
    # Use custom comparison function to sort items by instrument name (as string)
    # then question ID (as int)
    def compare_item_names(key1,key2):
        key1_details = key1.split('-')
        key2_details = key2.split('-')
        if key1_details[0] == key2_details[0]:
            number_pattern = re.compile("(MIUDQ|Minn-Irvine|Meta|PEDS|Streetview|NYC HVS|PHDCN|CCAHS)-(\d+)")
            dot_pattern = re.compile("(MIUDQ|Minn-Irvine|Meta|PEDS|Streetview|NYC HVS|PHDCN|CCAHS).(\d+)")
            match1 = number_pattern.search(key1)
            if (match1 is None):
                match1 = dot_pattern.search(key1)
            match2 = number_pattern.search(key2)
            if (match2 is None):
                match2 = dot_pattern.search(key2)
            item1_number = int(match1.group(2))
            item2_number = int(match2.group(2))
            logging.debug("key1: %s, number: %d" % (key1, item1_number))
            logging.debug("key2 %s, number: %d" % (key2, item2_number))
            return cmp(item1_number, item2_number)
        else:
            return cmp(key1_details[0], key2_details[0])
    results = sorted(results, key=lambda result:result['item'], cmp=compare_item_names)
    return render_to_response('ratestreets/studyresults.html', {'study':study, 'results': results}, context_instance=RequestContext(request))

@login_required
def totalresults(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    manager_studies = Study.objects.filter(managers=request.user)
    complete_studies = filter(lambda study:study.percent_complete() == 100, list(manager_studies))
    results = []
    for item in Item.objects.filter(module__study__in=complete_studies):
        item_title = item.name + ':' + item.description
        # todo -- is there a better way to ensure items distinct by name?
        already_found = False
        for result in results:
            if (result['item_name'] == item.name):
                already_found = True
                break
        if not already_found:
            kappa_pair = item.get_kappa(None, True)
            agreement_pair = item.get_percent_agreement(None, True)
            # Note that the percent agreement rating count isn't really valid -- it includes 
            # ratings that are the only valid rating for a segment.  The kappa rating count is 
            # actually the rating count used for percent agreement.
            # todo$ clean this up.
            results.append({'item_name':item.name,
                            'item':item_title,
                            'kappa':kappa_pair[0],
                            'kappa_rating_count':kappa_pair[1], 
                            'percent_agreement':agreement_pair[0],
                            'item_id': item.id})
    results = sorted(results, key=lambda result:result['kappa'])
    return render_to_response('ratestreets/totalresults.html', {'studies':complete_studies, 'results': results}, context_instance=RequestContext(request))

@login_required
def showratingtimes(request, revision=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    manager_studies = Study.objects.filter(managers=request.user)
    if revision == None:
        studies = filter(lambda study:study.percent_complete() == 100, list(manager_studies))
    else:
        studies = filter(lambda study:study.revision == revision, list(manager_studies))
    results = []
    for module in Module.objects.filter(study__in=studies).distinct():
        first_item = module.items.filter(rating_type__storage_type='CATEGORY')[:1][0]
        rating_times = first_item.get_rating_times(studies)
        if rating_times is not None:
            results.append({'module_revision':module.revision,
                            'module_name':module.get_name(),
                            'min':rating_times['min'],
                            'median':rating_times['median'],
                            'max':rating_times['max'],
                            'total':rating_times['total']})
    return render_to_response('ratestreets/ratingtimes.html', {'studies':studies, 'results': results}, context_instance=RequestContext(request))
    

@login_required
@profile("list_segments.prof")
def listsegments(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    segments = Segment.objects.filter(study=study)
    return render_to_response('ratestreets/list_segments.html', {'segments': segments, 'study':study}, context_instance=RequestContext(request))

@login_required
def startsegmentautoselect(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = SegmentAutoselectFileForm(request, request.POST, request.FILES)
        if (form.is_valid()):
            study = form.cleaned_data['study']
            confirm_url = reverse('ratestreets.views.confirmautoselect', args=[study.id])
            if (form.cleaned_data['segment_type'] == '2'):
                segment_type = "points"
            else:
                segment_type = "segments"
            segment_autoselect_formset = ViewUtils.create_segment_autoselect_formset_from_file(study, request.FILES['segment_file'], save_targets=True, filetype="address_list")
            return render_to_response('ratestreets/autoselect_segments.html', {'segment_autoselect_formset': segment_autoselect_formset, 'confirm_url': confirm_url, 'segment_type': segment_type}, context_instance=RequestContext(request))
    else:
        form = SegmentAutoselectFileForm(request)
        if (study_id != None):
            form.initial['study']=study_id
    return render_to_response('ratestreets/import_from_csv.html', {'form': form, 'item_type': 'Segments'}, context_instance=RequestContext(request))


@login_required
def startsegmentselection(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = SegmentFileForm(request, request.POST, request.FILES)
        if (form.is_valid()):
            study = form.cleaned_data['study']
            confirm_url = reverse('ratestreets.views.selectsegments', args=[study.id])
            if (form.cleaned_data['format'] == '2'):
                filetype = "address_list"
            if (form.cleaned_data['format'] == '3'):
                filetype = "geojson"
            else:
                filetype= "csv"
            segment_formset = ViewUtils.create_segment_formset_from_file(study, request.FILES['segment_file'], filetype=filetype)
            if (form.cleaned_data['skip_verify']):
                return render_to_response('ratestreets/select_segments_noverify.html', {'segment_formset': segment_formset, 'confirm_url': confirm_url}, context_instance=RequestContext(request))
            else:    
                return render_to_response('ratestreets/select_segments.html', {'segment_formset': segment_formset, 'confirm_url': confirm_url}, context_instance=RequestContext(request))
    else:
        form = SegmentFileForm(request)
        if (study_id != None):
            form.initial['study']=study_id
    return render_to_response('ratestreets/import_from_csv.html', {'form': form, 'item_type': 'Segments'}, context_instance=RequestContext(request))

@login_required
def confirmautoselect(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    if (request.method =='POST'):
        segment_autoselect_formset = SegmentAutoselectFormSet(request.POST)
        if (segment_autoselect_formset.is_valid()):
            for segment_autoselect_form in segment_autoselect_formset.forms:
                if (segment_autoselect_form.cleaned_data['should_save'] == True):
                    segment = segment_autoselect_form.save()
#            study.ensure_all_tasks_exist()
            return redirect('ratestreets.views.createtasks', study_id=study.id)
        else:
            confirm_url = reverse('ratestreets.views.confirmautoselect', args=[study.id])
            return render_to_response('ratestreets/autoselect_segments.html', {'segment_autoselect_formset': segment_autoselect_formset, 'confirm_url': confirm_url}, context_instance=RequestContext(request))
    else:
        # Unexpected
        return redirect('ratestreets.views.viewtasks')

@login_required
def createtasks(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    if (request.method =='POST'):
        form = CreateTaskForm(request.POST, instance=study)
        if (form.is_valid()):
            study.task_allocation = form.cleaned_data['task_allocation']
            if (form.cleaned_data['task_allocation'] == '2'):
                study.task_overlap = form.cleaned_data['task_overlap']
            study.save()
            
            if (study.task_allocation == 0):
                study.ensure_all_tasks_exist()
            else:
                study.allocate_tasks()
            return redirect('ratestreets.views.viewstudies')
    else:
        form = CreateTaskForm(instance=study)
    return render_to_response('ratestreets/create_tasks_form.html', {'form': form, 'study': study}, context_instance=RequestContext(request))
    

@login_required
def selectsegments(request, study_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    if (request.method =='POST'):
        segment_formset = SegmentFormSet(request.POST)
        if (segment_formset.is_valid()):
            for segment_form in segment_formset.forms:
                if (segment_form.cleaned_data['should_save'] == True):
                    segment = segment_form.save()
            logging.debug("Saved segments")
            study.ensure_all_tasks_exist()
            return redirect('ratestreets.views.listsegments', study_id=study.id)
        else:
            confirm_url = reverse('ratestreets.views.selectsegments', args=[study.id])
            return render_to_response('ratestreets/select_segments.html', {'segment_formset': segment_formset, 'confirm_url': confirm_url}, context_instance=RequestContext(request))
    else:
        # Unexpected
        return redirect('ratestreets.views.viewtasks')

@login_required
def editsegment(request, segment_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    segment = get_object_or_404(Segment, pk=segment_id)
    if (request.method =='POST'):
        form = SegmentForm(request.POST, instance=segment)
        if (form.is_valid()):
            segment = form.save()
            return redirect('ratestreets.views.listsegments', study_id=segment.study.id)
    else:
        form = SegmentForm(instance=segment, edit_description=True)
    return render_to_response('ratestreets/edit_segment.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def reassigntasks(request, segment_id=None):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    segment = get_object_or_404(Segment, pk=segment_id)
    if (request.method =='POST'):
        form = TaskAssignForm(request.POST, instance=segment)
        if (form.is_valid()):
            segment.reallocate_tasks(form.cleaned_data['active_raters'])
            return redirect('ratestreets.views.listsegments', study_id=segment.study.id)
    else:
        form = TaskAssignForm(instance=segment)
    return render_to_response('ratestreets/generic_form.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def reassignpending(request, study_id=None):
    # This is totally not REST-friendly, what with changing data on a GET.  Think about the UI paradigm.
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    study.reallocate_pending_tasks()
    return redirect('ratestreets.views.listsegments', study_id=study.id)

@login_required
def importmodules(request):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    if (request.method =='POST'):
        form = ModuleImportForm(request, request.POST, request.FILES)
        if (form.is_valid()):
            format = form.cleaned_data['source_format']
            revision = form.cleaned_data['revision']
            if (form.cleaned_data['module'] == None):
                Module.create_modules_from_csv(revision, format, request.FILES['item_csv'])
            else:
                if (format in ['CANVAS', 'REDCAP']):
                    module.add_items_from_csv(revision, format, request.FILES['item_csv'])
                else:
                    raise 'Unexpected source format in import'
            return redirect('ratestreets.views.viewmodules')
    else:
        form = ModuleImportForm(request)
    return render_to_response('ratestreets/import_from_csv.html', {'form': form, 'item_type': 'Items'}, context_instance=RequestContext(request))

@login_required
def mapexperiment(request):
    return render_to_response('ratestreets/mapexperiment.html', context_instance=RequestContext(request))

@login_required
def selectquickmap(request, study_id):
    study = get_object_or_404(Study, pk=study_id)
    modules = Module.objects.filter(study=study).all()
    items_for_study = Item.objects.filter(module__in=modules)
    return render_to_response('ratestreets/selectquickmap.html', {'items': items_for_study, 'study':study}, context_instance=RequestContext(request))

@login_required
def showquickmap(request, study_id, item_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    item = get_object_or_404(Item, pk=item_id)
    if item.rating_type.storage_type == 'CATEGORY':
        ratings = CategoryRating.objects.filter(item=item, segment__study=study)
    elif item.rating_type.storage_type == 'COUNT':
        ratings = CountRating.objects.filter(item=item, segment__study=study)
    ratings_with_segment_info = []
    for rating in ratings.all():
        if rating.rating is not None:
            segment = rating.segment
            rating_with_segment_info = {
                     'start_lat': segment.start_lat,
                     'start_lng': segment.start_lng,
                     'end_lat': segment.end_lat,
                     'end_lng': segment.end_lng,
                     'rating': rating.rating,
                     }
            ratings_with_segment_info.append(rating_with_segment_info)
    categories = item.rating_type.values.all()
    return render_to_response('ratestreets/quickmap.html', {'segments': ratings_with_segment_info, 'item':item, 'study': study, 'categories': categories}, context_instance=RequestContext(request))


@login_required
def showsamplemap(request, study_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)
    segments = Segment.objects.filter(study=study)
    sample_points = SamplePoint.objects.filter(study=study)
    return render_to_response('ratestreets/samplemap.html', {'sample_points': sample_points, 'segments':segments, 'study': study}, context_instance=RequestContext(request))


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
def pano_v2(request, segment_id):
    if (task_id == 0 or segment_id == None):
        return render_to_response('ratestreets/emptypano.html', context_instance=RequestContext(request))
    else:
        segment = get_object_or_404(RatingTask, pk=segment_id)
        return render_to_response('ratestreets/showpano_v2.html', {'segment': segment}, context_instance=RequestContext(request))

@login_required
def pano(request, segment_id):
    if (segment_id == 0 or segment_id == None):
        return render_to_response('ratestreets/emptypano.html', context_instance=RequestContext(request))
    else:
        segment = get_object_or_404(Segment, pk=segment_id)
        return render_to_response('ratestreets/showpano.html', {'segment': segment}, context_instance=RequestContext(request))


@login_required
def ratestreet(request, task_id):
    task = get_object_or_404(RatingTask, pk=task_id)
    relative_pano_location = reverse('ratestreets.views.pano', args=[task.segment.id])
    absolute_pano_url = request.build_absolute_uri(relative_pano_location)
    if task.user != request.user:
        return redirect('django.contrib.auth.views.logout')
    # Create ratings querysets upfront, else Django loads all instances of the 
    # underlying model into the cache by default (!)
    boolean_ratings = task.find_or_create_ratings(BooleanRating)
    count_ratings = task.find_or_create_ratings(CountRating)
    freeform_ratings = task.find_or_create_ratings(FreeFormRating)
    category_ratings = task.find_or_create_ratings(CategoryRating)
    if (request.method =='POST'):
        render_time_form = RenderTimeForm(request.POST, prefix="elapsed_time")
        boolean_formset = BooleanRatingFormSet(request.POST, queryset=boolean_ratings, prefix="boolean")
        count_formset = CountRatingFormSet(request.POST, queryset=count_ratings, prefix="count")
        freeform_formset = FreeFormRatingFormSet(request.POST, queryset=freeform_ratings, prefix="freeform")
        category_formset = CategoryRatingFormSet(request.POST, queryset=category_ratings, prefix="category")
        formsets = [category_formset, boolean_formset, count_formset, freeform_formset]
        all_formsets_valid = True
        for formset in formsets:
            if (formset.is_valid() == False):
                all_formsets_valid = False
                break
        elapsed_time = None
        if (render_time_form.is_valid()):
            logging.debug("Render time form is valid")
            render_time = render_time_form.cleaned_data['render_time']
            elapsed_time = datetime.now() - render_time
        else:
            logging.debug("Render time form is invalid: %s" % render_time_form.errors)
        logging.debug("Time elapsed: %s" % str(elapsed_time))
        if (all_formsets_valid):
            for formset in formsets:
#                formset.save()
                # Update elapsed_time field in ratings.
                for form in formset.forms:
                    rating = form.save(commit=False)
                    rating.add_elapsed_time(elapsed_time)
                    rating.save()
                    form.save_m2m()
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
            return render_to_response('ratestreets/ratestreet.html', {'formsets': formsets, 'pano_url': absolute_pano_url, 'render_time_form': render_time_form, 'task': task}, context_instance=RequestContext(request))
    else:
        boolean_formset = BooleanRatingFormSet(queryset=boolean_ratings, prefix="boolean")
        count_formset = CountRatingFormSet(queryset=count_ratings, prefix="count")
        freeform_formset = FreeFormRatingFormSet(queryset=freeform_ratings, prefix="freeform")
        category_formset = CategoryRatingFormSet(queryset=category_ratings, prefix="category")
        # Note that we need the cheesy strftime because the datetimefield can't roundtrip with milliseconds and a hidden input
        render_time_form = RenderTimeForm(initial={'render_time':datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, prefix="elapsed_time")
        formsets = [category_formset, boolean_formset, count_formset, freeform_formset]
    return render_to_response('ratestreets/ratestreet.html', {'formsets': formsets, 'pano_url': absolute_pano_url, 'render_time_form': render_time_form, 'task': task}, context_instance=RequestContext(request))

@login_required
def showhelp(request, help_text_id=None):
    def generate_image_url(matchobj):
        image_url = reverse('django.views.static.serve', args=['help/' + matchobj.group(1)])
        return image_url
    if ItemHelpText.objects.filter(pk=help_text_id).exists():
        item_help_text = ItemHelpText.objects.get(pk=help_text_id)
        item_help_text_with_brs = re.sub(r'\r', '<br>', item_help_text.text)
        item_help_text_with_urls_updated = re.sub(r'\[([a-zA-Z_\.0-9]+)\]', generate_image_url, item_help_text_with_brs)
        item = item_help_text.item
    return render_to_response('ratestreets/help_text.html', {'help_text': item_help_text_with_urls_updated, 'item': item}, context_instance=RequestContext(request))


@login_required
def dotask(request, task_id):
    task = RatingTask.objects.get(id = task_id)
    return render_to_response('ratestreets/dotask.html', {'task': task}, context_instance=RequestContext(request))

@login_required
def analyzeagreement(request, study_id, item_id):
    study = get_object_or_404(Study, pk=study_id)
    item = get_object_or_404(Item, pk=item_id)
    raters = []
    if item.rating_type.storage_type == 'CATEGORY':
        ratings = CategoryRating.objects.filter(item=item, segment__study=study)
    elif item.rating_type.storage_type == 'COUNT':
        ratings = CountRating.objects.filter(item=item, segment__study=study)
    ratings_by_segment = {}
    for rating in ratings.all():
        if rating.segment in ratings_by_segment:
            ratings_by_user = ratings_by_segment[rating.segment]
        else:
            ratings_by_user = {}
        ratings_by_user[rating.user] = rating.rating
        ratings_by_segment[rating.segment] = ratings_by_user
        if rating.user not in raters:
            raters.append(rating.user)
    categories = item.rating_type.values.all()
    return render_to_response('ratestreets/results_for_item.html', {'ratings_by_segment': ratings_by_segment, 'item':item, 'categories':categories, 'raters':raters}, context_instance=RequestContext(request))
    

@login_required
def export_data(request, study_id):
    if (not request.user.is_superuser):
        return redirect('ratestreets.views.viewtasks')
    study = get_object_or_404(Study, pk=study_id)

    # Create the HttpResponse object with the appropriate CSV header.
    time_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = "attachment; filename=%s-%s.csv" % (slugify(study.description),time_string) 

    writer = csv.writer(response)
    # First, write the headers
    
    # Get the list of columns, including the hard-coded ones
    data_columns = ['User', 'Segment ID', 'description', 'start_lat', 'start_lng', 'end_lat', 'end_lng', 'image_date', 'rating_date']
    items = Item.objects.filter(module__study=study)
    for item in items.all():
        data_columns.append(item.name)
        data_columns.append(item.name + "_impediment")
    
    # Write the columns
    writer.writerow(data_columns) 
    
    raters = User.objects.filter(Q(categoryrating__segment__study=study)).distinct()
    logging.debug("Raters for study %s are %s" % (raters, study))
    segments = Segment.objects.filter(study=study).all()
    for segment in segments:
        for rater in raters:
            boolean_ratings_queryset = BooleanRating.objects.filter(segment__study = study).filter(user = rater).filter(segment=segment)
            count_ratings_queryset = CountRating.objects.filter(segment__study = study).filter(user = rater).filter(segment=segment)
            category_ratings_queryset = CategoryRating.objects.filter(segment__study = study).filter(user = rater).filter(segment=segment)
            free_form_ratings_queryset = FreeFormRating.objects.filter(segment__study = study).filter(user = rater).filter(segment=segment)
        
            querysets = [boolean_ratings_queryset, count_ratings_queryset, category_ratings_queryset, free_form_ratings_queryset]

            # If no ratings, skip row.
            if (boolean_ratings_queryset.count() == 0 and 
                count_ratings_queryset.count() == 0 and
                category_ratings_queryset.count() == 0 and 
                free_form_ratings_queryset.count() == 0):
                continue

            data_for_row = {}
            data_for_row['User'] = rater.id
            data_for_row['Segment ID'] = segment.id
            data_for_row['description'] = segment.street_address
            data_for_row['start_lat'] = segment.start_lat
            data_for_row['start_lng'] = segment.start_lng
            data_for_row['end_lat'] = segment.end_lat
            data_for_row['end_lng'] = segment.end_lng
            for queryset in querysets:
                for rating in queryset.all():
                    column_key = rating.item.name
                    impediment_column_key = str(rating.item.name) + "_impediment" 
                    data_for_row[column_key] = rating.rating
                    data_for_row[impediment_column_key] = rating.impediment
                    if not('image_date' in data_for_row):
                        data_for_row['image_date'] = rating.image_date
                    if not('rating_date' in data_for_row):
                        data_for_row['rating_date'] = rating.updated_at.date()
            values = []
            for column_name in data_columns:
                if (column_name in data_for_row):
                    value = data_for_row[column_name]
                else:
                    value = ''
                values.append(value)
            
            writer.writerow(values)
            logging.debug('Wrote row for %s, %s' % (rater.username, segment.id))
        response.flush()
    return response

@login_required
def showallsegments(request):
    segments = Segment.objects.all()
    return render_to_response('ratestreets/showallsegments.html', {'segments': segments}, context_instance=RequestContext(request))

@login_required
def showallhelp(request):
    items = Item.objects.all()
    item_count = items.count()
    help_text_count = ItemHelpText.objects.count()
    if item_count > 0:
        rate = float(help_text_count)/item_count
    else:
        rate = 0.0
    return render_to_response('ratestreets/showallhelptext.html', {'items': items, 'item_count': item_count, 'help_text_count': help_text_count, 'rate': rate}, context_instance=RequestContext(request))


def compute_and_save_kappas(request):
    datetime_50daysago = datetime.today() - timedelta(days=50)
    studies = Study.objects.filter(created_at__gt=datetime_50daysago)
    studies_completed = []
# todo$ once we're automating the saving, neeed to catch exceptions and notify me.
#    try:
    for study in studies:
        study.compute_and_save_kappas()
        studies_completed.append(study)
#    except Exception as exception:
#        msg = MIMEText(str(exception))
#        msg['Subject'] = 'Exception computing kappas'
#        msg['From'] = 'Streetview Exception Automailer'
#        msg['To'] = 'smooney27@gmail.com'
#        s = smtplib.SMTP('localhost')
#        s.sendmail('Streetview Exception Automailer', ['smooney27@gmail.com'], msg.as_string())
    return render_to_response('ratestreets/savekappas.html', {'studies': studies_completed}, context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('django.contrib.auth.views.login')