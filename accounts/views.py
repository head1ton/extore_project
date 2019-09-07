import re

from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string

from .models import User

from extore.models import Group, InviteStatus, InviteDate


# 사용자 회원가입
def user_signup(request):
    # Class Based View -> dispatch -> get, post
    if request.is_ajax():
        if request.POST.get('email') == "":
            return JsonResponse({'noEmail':True})
        elif request.POST.get('realName') == "":
            return JsonResponse({'noRealName':True})
        elif request.FILES.get('profile', None) is None:
            return JsonResponse({'noProfile':True})
        elif request.POST.get('phoneNumber') == "":
            return JsonResponse({'noPhoneNumber': True})
        elif request.POST.get('password') == "":
            return JsonResponse({'noPassword':True})
        elif request.POST.get('password2') == "":
            return JsonResponse({'noPassword2':True})



        # username(=email)에 이메일 형식이 아닌 경우
        signup_email = request.POST.get('email')
        if '@' not in signup_email or '.' not in signup_email:
            return JsonResponse({'wrongEmail':True})

        index = signup_email.index('.')
        try:
            signup_email[index + 1]
        except IndexError:
            return JsonResponse({'wrongEmail': True})

        # 이미 등록된 email인 경우
        if User.objects.filter(username=request.POST.get('email')).exists():
            return JsonResponse({'emailExists':True})

        # 이미 등록된 phoneNumber인 경우
        if User.objects.filter(phone_number=request.POST.get('phoneNumber')).exists():
            return JsonResponse({'phoneNumberExists':True})

        # phoneNumber 길이가 적합하지 않은 경우
        try:
            int(request.POST.get('phoneNumber'))
            pass
        except ValueError:
            return JsonResponse({'notNumber':True})

        if len(request.POST.get('phoneNumber'))>11:
            return JsonResponse({'tooLongNumber':True})
        if len(request.POST.get('phoneNumber')) < 10:
            return JsonResponse({'tooShortNumber':True})

        # realName에 영문자, 숫자, 특수문자가 존재하는 경우
        wrong_str = re.compile('[a-zA-Z0-9-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]')
        if wrong_str.search(request.POST.get('realName')):
            return JsonResponse({'wrongName':True})

        # realName이 5자리 초과한 경우
        if len(request.POST.get('realName')) > 5:
            return JsonResponse({'tooLongName':True})

        # password가 비밀번호 형식에 적합하지 않은 경우 (8자리이상 & 영어 소문자/대문자/특수문자/숫자 중 3개 이상 조합)
        password = request.POST.get('password')
        if len(password) < 8:
            return JsonResponse({'shortLength':True})
        lower_case = re.compile('[a-z]')
        higher_case = re.compile('[A-Z]')
        number = re.compile('[0-9]')
        symbol = re.compile('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]')

        i = 0
        count = 0
        if re.search(lower_case, password):
            count += 1
        if re.search(higher_case, password):
            count += 1
        if re.search(number, password):
            count += 1
        if re.search(symbol, password):
            count += 1
        # 문자 조합이 3가지 미만일 경우
        if count < 3:
            return JsonResponse({'wrongCombination':True})

        # password2와 password가 일치하지 않는 경우
        if request.POST.get('password') != request.POST.get('password2'):
            return JsonResponse({'notMatch':True})


        # 사용자가 작성한 회원가입 내용 형식이 적상인 경우
        real_name = request.POST.get('realName')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        password = request.POST.get('password')
        profile = request.FILES.get('profile')

        user = User(last_name = real_name[0], first_name=real_name[1:], profile=profile, phone_number=phone_number, username=email)
        user.set_password(password)
        user.save()

        return JsonResponse({'works':True})

    return JsonResponse({'notValid':True})


# 사용자 로그인
def user_login(request):
    if request.is_ajax():
        # 이메일 주소를 입력하지 않은 경우
        if request.POST.get('email')=="" :
            return JsonResponse({'noEmail':True})

        # 비밀번호를 입력하지 않은 경우
        elif request.POST.get('password')=="":
            return JsonResponse({'noPassword':True})

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'works':True})
        return JsonResponse({'wrongInformation':True})

    return JsonResponse({'notAjax':True})


# 사용자 로그아웃
def user_logout(request):
    if request.is_ajax():
        logout(request)
        return JsonResponse({'works':True})

    return JsonResponse({'notAjax':True})


# 특정 익스토어에 사용자 초대 위한 검색
def user_search(request):
    is_ajax = request.POST.get('is_ajax', None)
    if is_ajax:
        user_keyword = request.POST.get('userKeyword')
        # 유저가 어떠한 키워드도 입력하지 않았을 때
        if not user_keyword:
            return JsonResponse({'noKeyword':True})
        # 한글, 영어, 숫자가 아닌 문자들 제외
        not_hangul = re.compile('[^가-힣0-9a-z]+')
        converted_keyword = not_hangul.sub('', user_keyword)

        # 키워드 앞에 3자리가 010일 경우, 연락처 입력으로 간주
        if converted_keyword[:3] == '010':
            # 010만 검색한 경우, 조회 불가
            if converted_keyword == '010':
                html = render_to_string('accounts/user-search.html')
                return JsonResponse({'isSearched':True, 'html':html})
            users = User.objects.filter(Q(phone_number__icontains=converted_keyword))
        # 연락처를 입력하지 않고, 이름 혹은 닉네임으로 검색한 경우
        else:
            consistent_name = Q(last_name=converted_keyword[0]) & Q(first_name__icontains=converted_keyword[1:])
            consistent_name = consistent_name | Q(first_name__icontains=converted_keyword)
            users = User.objects.filter(Q(phone_number__icontains=converted_keyword)|Q(username__icontains=converted_keyword)|consistent_name)
        html = render_to_string('accounts/user-search.html', {'users':users})
        return JsonResponse({'isSearched':True, 'html':html})

    raise Http404


# 특정 익스토어에 사용자 초대
def user_invite(request):
    is_ajax = request.POST.get('is_ajax') if request.POST.get('is_ajax', None) else request.GET.get('is_ajax', None)
    if is_ajax:
        # 선택한 유저의 연락처 정보들을 배열로 저장
        users_number = request.POST.getlist('user_number_list[]')

        if not users_number:
            return JsonResponse({'notSelect':True})

        extore_title = request.POST.get('extore_title')
        # User 객체에서 phone_number가 user_number 배열에 속해있는 객체들을 users 변수가 참조
        users = User.objects.filter(phone_number__in=users_number)

        # 초대 요청한 익스토어 그룹명이 title인 Group 객체를 group 변수가 참조
        group = Group.objects.get(title=extore_title)

        if not request.user in group.member.all():
            raise Http404

        # InviteStatus 객체 중, group_id가 group.id와 일치하는 객체를 invite_status 변수(queryset 형태)가 참조
        invite_status = InviteStatus.objects.filter(group_id=group.id)

        # invite_status가 존재한다면, invite_status[0](클래스 형태) 을 invite_status 변수가 참조
        if invite_status.exists():
            invite_status = invite_status[0]
        # invite_status가 존재하지 않는다면, None을 invite_status 변수가 참조
        else:
            invite_status = None
        # 초대한 유저가 해당 그룹에 이미 존재하고 있는 경우, already_exists 배열에 유저 이름 추가
        already_exists = []
        # 초대한 유저가 이미 초대 요청받은 경우(승락, 거부하지 않은 상태), already_requested 배열에 유저 이름 추가
        already_requested = []
        for user in users:
            # 유저가 이미 해당 그룹 멤버인 경우
            if user in group.member.all():
                user_name = user.last_name + user.first_name
                already_exists.append(user_name)
            # invite_status 객체가 이미 존재하고, 유저가 이미 전에 초대 요청받은(승락, 거부하지 않은 상태) 경우
            if invite_status and user in invite_status.invited.all():
                user_name = user.last_name + user.first_name
                already_requested.append(user_name)

        if already_exists:
            already_exists = ','.join(already_exists)
            return JsonResponse({'already_exists':already_exists})

        if already_requested:
            already_requested = ','.join(already_requested)
            return JsonResponse({'already_requested':already_requested})

        if invite_status is None:
            invite_status = InviteStatus.objects.create(group_id=group.id)
        for user in users:
            invite_status.invited.add(user)
            InviteDate.objects.create(group_id=group.id, invited_id=user.id)

        return JsonResponse({'works':True})

    raise Http404


# 익스토어 초대 요청에 대한 사용자 승인
def user_accept(request, inviteStatus_id):
    is_ajax = request.POST.get('is_ajax') if request.POST.get('is_ajax', None) else request.GET.get('is_ajax', None)

    if is_ajax:
        if request.POST.get('result', None) == '승락':
            # InviteStatus id 데이터 전달받아야 함
            invite_status = InviteStatus.objects.get(pk=inviteStatus_id)
            if not request.user in invite_status.invited.all():
                raise Http404
            invite_status.invited.remove(request.user)

            # InviteDate 객체중, 초대 승낙한 그룹 id와 유저 id가 일치하는 객체를 삭제
            invite_date = InviteDate.objects.filter(Q(group_id=invite_status.group.id) and Q(invited_id=request.user.id))
            invite_date.delete()

            if request.user in invite_status.rejected.all():
                invite_status.rejected.remove(request.user)
            if request.user in invite_status.accepted.all():
                pass
            if not request.user in invite_status.accepted.all():
                invite_status.accepted.add(request.user)

            group = Group.objects.get(pk=invite_status.group.id)
            group.member.add(request.user)

            return JsonResponse({'accepted':True, 'groupTitle':group.title})

        elif request.POST.get('result', None) == '거부':
            invite_status = InviteStatus.objects.get(pk=inviteStatus_id)
            if not request.user in invite_status.invited.all():
                raise Http404
            invite_status.invited.remove(request.user)

            # InviteDate 객체중, 초대 승낙한 그룹 id와 유저 id가 일치하는 객체를 삭제
            invite_date = InviteDate.objects.filter(Q(group_id=invite_status.group.id) and Q(invited_id=request.user.id))
            invite_date.delete()

            if request.user in invite_status.accepted.all():
                invite_status.accepted.remove(request.user)
            if request.user in invite_status.rejected.all():
                pass
            else:
                invite_status.rejected.add(request.user)

            group = Group.objects.get(pk=invite_status.group.id)

            return JsonResponse({'rejected':True, 'groupTitle':group.title})

    raise Http404