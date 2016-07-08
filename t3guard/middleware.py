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
