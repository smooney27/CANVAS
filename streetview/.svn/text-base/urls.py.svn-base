from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
APP_BASE_URL = getattr(settings, 'APP_BASE_URL', '')


urlpatterns = patterns('',
    # Example:
    # (r'^streetview/', include('streetview.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^' + APP_BASE_URL + 'admin/', include(admin.site.urls)),

    # streetview-specific    
    (r'^$', 'ratestreets.views.mainmenu'),
    (r'^' + APP_BASE_URL + '$', 'ratestreets.views.mainmenu'),
    (r'^' + APP_BASE_URL + 'main/$', 'ratestreets.views.mainmenu'),
    (r'^' + APP_BASE_URL + 'viewtasks/(?P<study_id>\d+)?$', 'ratestreets.views.viewtasks'),
    (r'^' + APP_BASE_URL + 'viewtasksummary/$', 'ratestreets.views.viewtasksummary'),
    (r'^' + APP_BASE_URL + 'start_rating/(?P<study_id>\d+)?', 'ratestreets.views.startrating'),
    (r'^' + APP_BASE_URL + 'viewadmintasks/$', 'ratestreets.views.viewadmintasks'),
    (r'^' + APP_BASE_URL + 'create_study/$', 'ratestreets.views.createstudy'),
    (r'^' + APP_BASE_URL + 'view_studies/$', 'ratestreets.views.viewstudies'),
    (r'^' + APP_BASE_URL + 'edit_study/(?P<study_id>\d+)$', 'ratestreets.views.editstudy'),
    (r'^' + APP_BASE_URL + 'study_results/(?P<study_id>\d+)$', 'ratestreets.views.studyresults'),
    (r'^' + APP_BASE_URL + 'total_results/$', 'ratestreets.views.totalresults'),
    (r'^' + APP_BASE_URL + 'rating_times/(?P<revision>\d+)?$', 'ratestreets.views.showratingtimes'),
    (r'^' + APP_BASE_URL + 'analyze_agreement/(?P<study_id>\d+)/(?P<item_id>\d+)$', 'ratestreets.views.analyzeagreement'),
    (r'^' + APP_BASE_URL + 'create_user/$', 'ratestreets.views.createuser'),
    (r'^' + APP_BASE_URL + 'view_users/(?P<study_id>\d+)?$', 'ratestreets.views.viewusers'),
    (r'^' + APP_BASE_URL + 'evaluate_raters/(?P<study_id>\d+)?$', 'ratestreets.views.evaluateraters'),
    (r'^' + APP_BASE_URL + 'edit_user/(?P<user_id>\d+)$', 'ratestreets.views.edituser'),
    (r'^' + APP_BASE_URL + 'view_modules/$', 'ratestreets.views.viewmodules'),
    (r'^' + APP_BASE_URL + 'edit_module/(?P<module_id>\d+)$', 'ratestreets.views.editmodule'),
    (r'^' + APP_BASE_URL + 'import_modules/$', 'ratestreets.views.importmodules'),
    (r'^' + APP_BASE_URL + 'import_segments/(?P<study_id>\d+)?$', 'ratestreets.views.startsegmentselection'),
    (r'^' + APP_BASE_URL + 'autoselect_segments/(?P<study_id>\d+)?$', 'ratestreets.views.startsegmentautoselect'),
    (r'^' + APP_BASE_URL + 'confirm_autoselect/(?P<study_id>\d+)?$', 'ratestreets.views.confirmautoselect'),
    (r'^' + APP_BASE_URL + 'create_tasks/(?P<study_id>\d+)?$', 'ratestreets.views.createtasks'),
    (r'^' + APP_BASE_URL + 'select_segments/(?P<study_id>\d+)?$', 'ratestreets.views.selectsegments'),
    (r'^' + APP_BASE_URL + 'list_segments/(?P<study_id>\d+)?', 'ratestreets.views.listsegments'),
    (r'^' + APP_BASE_URL + 'edit_segment/(?P<segment_id>\d+)?', 'ratestreets.views.editsegment'),
    (r'^' + APP_BASE_URL + 'reassigntasks/(?P<segment_id>\d+)?', 'ratestreets.views.reassigntasks'),
    (r'^' + APP_BASE_URL + 'reassignpending/(?P<study_id>\d+)?', 'ratestreets.views.reassignpending'),
    (r'^' + APP_BASE_URL + 'mapexperiment/', 'ratestreets.views.mapexperiment'),
    (r'^' + APP_BASE_URL + 'selectquickmap/(?P<study_id>\d+)', 'ratestreets.views.selectquickmap'),
    (r'^' + APP_BASE_URL + 'quickmap/(?P<study_id>\d+)/(?P<item_id>\d+)$', 'ratestreets.views.showquickmap'),
    (r'^' + APP_BASE_URL + 'samplemap/(?P<study_id>\d+)$', 'ratestreets.views.showsamplemap'),
    (r'^' + APP_BASE_URL + 'ratestreets/(?P<task_id>\d+)$', 'ratestreets.views.ratestreet'),
    (r'^' + APP_BASE_URL + 'ratestreets/pano/(?P<segment_id>\d+)?$', 'ratestreets.views.pano'),
    (r'^' + APP_BASE_URL + 'ratestreets/pano_v2/(?P<segment_id>\d+)?$', 'ratestreets.views.pano_v2'),
    (r'^' + APP_BASE_URL + 'ratestreets/show_help/(?P<help_text_id>\d+)?$', 'ratestreets.views.showhelp'),
    (r'^' + APP_BASE_URL + 'ratestreets/showallhelp/$', 'ratestreets.views.showallhelp'),
    (r'^' + APP_BASE_URL + 'export_data/(?P<study_id>\d+)$', 'ratestreets.views.export_data'),
    (r'^' + APP_BASE_URL + 'compute_and_save_kappas/$', 'ratestreets.views.compute_and_save_kappas'),
    (r'^' + APP_BASE_URL + 'accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^' + APP_BASE_URL + 'accounts/change_password/$', 'django.contrib.auth.views.password_change'),
    (r'^' + APP_BASE_URL + 'accounts/change_password_done/$', 'django.contrib.auth.views.password_change_done'),
    (r'^' + APP_BASE_URL + 'logout/$', 'ratestreets.views.logout_view'),
#    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media'}),
    # this is a giant hack.  Need to figure out the right way to do deployment
    (r'^' + APP_BASE_URL + 'media/admin/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/sjm2186/streetview/streetview/media/admin'}),
    # Hack for serving JS, etc.
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}),


)
