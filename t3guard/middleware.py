from django.contrib.auth import authenticate, login
from models import Device, Log

class MobileClientLoginMiddleware:
    def process_request(self, request):
#        print(request.META['REMOTE_HOST'])

#        if request.path.find('admin') == -1 and not request.user.is_authenticated():
#            if request.GET.get('mobile', None) == 'authenticate':
        if not request.user.is_authenticated():
             user = authenticate(username='admin', password='admin')
             if user and user.is_active:
                 login(request, user)

        # check for lost devices when web interface is opened...
        for d in Device.objects.filter(ip=request.META.get('REMOTE_ADDR'), authorized=True, is_home=False):
            d.is_home = True
            d.save()
            l = Log(device=d, status=True, log_type='DE', text='(django)')
            l.save()



class CorsMiddleware:
     def process_response(self, request, response):
        """
        Add the respective CORS headers
        """
        origin = request.META.get('HTTP_ORIGIN')
        #print(origin)
        server_ip = request.META.get('HTTP_HOST').split(':')[0]
        #print(server_ip)
        response['Access-Control-Allow-Origin'] = '*'
        return response
