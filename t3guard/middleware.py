from django.contrib.auth import authenticate, login

class MobileClientLoginMiddleware:
    def process_request(self, request):
#        print(request.META['REMOTE_HOST'])
        
#        if request.path.find('admin') == -1 and not request.user.is_authenticated():
#            if request.GET.get('mobile', None) == 'authenticate':
        if not request.user.is_authenticated():
             user = authenticate(username='admin', password='admin')
             if user and user.is_active:
                 login(request, user)
