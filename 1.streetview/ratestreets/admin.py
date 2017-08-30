from ratestreets.models import *
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email', 'first_name', 'last_name', 'is_staff', 'impersonate')
    def impersonate(self, user):
        # This is very cheesy.
        url = reverse('ratestreets.views.viewtasks') + '?__impersonate=' + str(user.id)
        return url

class RatingTypeAdmin(admin.ModelAdmin):
    list_display = ('description','created_at')

class StudyAdmin(admin.ModelAdmin):
    list_display = ('description','created_at')

class SegmentAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'start_lat','start_lng','end_lat','end_lng','created_at')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('description','created_at')

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('description','created_at')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','description','db_value')

# This is just for debugging at the moment -- we'll want progress UI
# in the long term
class RatingTaskAdmin(admin.ModelAdmin):
    list_display = ('user','segment','module','created_at','completed_at')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(RatingType, RatingTypeAdmin)
admin.site.register(RatingTask, RatingTaskAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Rating)

