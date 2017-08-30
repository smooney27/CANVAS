from django.contrib.auth.models import User

# This code as suggested by Charles Offenbacher in 
# http://stackoverflow.com/questions/2242909/django-user-impersonation-by-admin
class ImpersonateMiddleware(object):
    def process_request(self, request):
        if request.user.is_superuser and "__impersonate" in request.GET:
            request.session['impersonate_id'] = int(request.GET["__impersonate"])
        elif "__unimpersonate" in request.GET:
            del request.session['impersonate_id']
        if request.user.is_superuser and 'impersonate_id' in request.session:
            request.logged_in_as = request.user
            request.user = User.objects.get(id=request.session['impersonate_id'])
