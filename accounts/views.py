from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import User
# Create your views here.

def user_search(request):
    is_ajax = request.POST.get('is_ajax', None)
    if is_ajax:
        user_number = request.POST.get('userNumber')
        user = User.objects.filter(phonenumber=user_number)
        user = user[0]
        html = render_to_string('accounts/user-search.html', {'user':user})
        return JsonResponse({'isSearched':True, 'html':html})

    raise Http404


