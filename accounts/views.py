import re

from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import User


def user_search(request):
    is_ajax = request.POST.get('is_ajax', None)
    if is_ajax:
        user_keyword = request.POST.get('userKeyword')
        not_hangul = re.compile('[^가-힣0-9a-z]+')
        converted_keyword = not_hangul.sub('', user_keyword)
        if converted_keyword[:3] == '010':
            if converted_keyword == '010':
                html = render_to_string('accounts/user-search.html')
                return JsonResponse({'isSearched':True, 'html':html})
            users = User.objects.filter(Q(phonenumber__icontains=converted_keyword[1:]))
        else:
            consistent_name = Q(last_name=converted_keyword[0]) & Q(first_name__icontains=converted_keyword[1:])
            consistent_name = consistent_name | Q(first_name__icontains=converted_keyword)
            users = User.objects.filter(Q(phonenumber__icontains=converted_keyword)|Q(username__icontains=converted_keyword)|consistent_name)
        html = render_to_string('accounts/user-search.html', {'users':users})
        return JsonResponse({'isSearched':True, 'html':html})

    raise Http404


