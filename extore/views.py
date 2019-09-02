import random

from django.http import JsonResponse
from django.utils.text import slugify
from django.shortcuts import render
from .models import Group
from .forms import GroupForm
from post.models import Post

# 익스토어 목록
def group_list(request):
    # group_list = extore 리스트
    if request.user.is_authenticated:
        group_list = request.user.members_groups.all()
        invited_groups = request.user.invited.all()
        invited_dates = request.user.invitedDate.all()
    else:
        group_list = None
        invited_groups = None
        invited_dates = None
    form = GroupForm()

    return render(request, 'extore/extore_index.html', {'group_list': group_list, 'invited_groups':invited_groups, 'invited_dates':invited_dates, 'form':form})


# 익스토어 상세
def group_detail(request, group_id):
    if request.method == 'GET':
        # group = the extore to see detail
        group = Group.objects.get(id=group_id)
        # group_list = extore list
        group_list = request.user.members_groups.all()
        posts = Post.objects.filter(extore_id=group_id)

        return render(request, 'post/post_list.html',{'object_list':posts, 'group':group, 'group_list':group_list})


# 익스토어 삭제
def group_delete(request, group_id):
    is_ajax = request.POST.get('is_ajax', None)
    if is_ajax:
        group = Group.objects.get(id=group_id)
        if not request.user.is_authenticated:
            return JsonResponse({'notLogin':True})
        if not request.user in group.member.all():
            return JsonResponse({'notMember':True})

        # 탈퇴하려는 그룹에 유저가 한명일 경우, 그룹 전체 삭제
        if group.member.all().count() == 1:
            group.delete()
            return JsonResponse({'leaved': True})

        # 탈퇴하려는 유저가 그룹 방장일 경우, 그 다음 순서에 있는 유저를 방장으로 위임
        if request.user == group.author:
            members = group.member.all()
            count = -1
            for member in members:
                count += 1
                if member == request.user:
                    # count(index)가 맨 마지막 index일 경우 맨 앞에 있는 사람을 방장으로 선정
                    if count == len(members)-1:
                        new_index = 0
                    else:
                        new_index = count+1
                    break

            new_author = members[new_index]
            group.author_id = new_author.id


        group.member.remove(request.user)
        group.save()

        return JsonResponse({'leaved':True})


# 익스토어 생성
def group_create(request):
    if request.is_ajax():
        # extoreTitle, extoreImage 데이터 모두 전달받지 못한 경
        if request.POST.get('extoreTitle', None) == "" and request.FILES.get('extoreImage', None) is None:
            return JsonResponse({'neither_data':True})
        # extoreTitle 데이터만 전달받지 못한 경우
        elif request.POST.get('extoreTitle', None) == "":
            return JsonResponse({'no_extoreTitle':True})
        # extoreImage 데이터만 전달받지 못한 경우
        elif request.FILES.get('extoreImage', None) is None:
            return JsonResponse({'no_extoreImage':True})
        # extoreTitle, extoreImage 데이터 모두 전달받은 경우
        else:
            extore_title = request.POST.get('extoreTitle')
            extore_slug = slugify(extore_title, allow_unicode=True)

            # request에서 전달받은 title이 기존 익스토어 이름과 중복되는지 확인
            if Group.objects.filter(slug=extore_slug).exists():
                return JsonResponse({'overlap':True})

            # request에서 전달받은 title이 기존 익스토어 이름과 중복안되는 경우
            group = Group.objects.create(title=request.POST.get('extoreTitle'), image=request.FILES.get('extoreImage'), author_id=request.user.id)
            group.member.add(request.user)

            return JsonResponse({'works':True})

    # ajax 요청이 아닌 경우
    return JsonResponse({'not_ajax':True})


# 익스토어 이름 중복 체크
def group_overlap(request):
    if request.is_ajax():
        extore_title = request.POST.get('extoreTitle', None)
        extore_slug = slugify(extore_title, allow_unicode=True)

        if extore_title == "":
            return JsonResponse({'no_data':True})
        # request에서 전달받은 title이 기존 익스토어 이름과 중복되는 경우
        elif Group.objects.filter(slug=extore_slug).exists():
            return JsonResponse({'overlap':True})
        # request에서 전달받은 title이 기존 익스토어 이름과 중복되지 않는 경우
        return JsonResponse({'works':True})
    # ajax 요청이 아닌 경우
    return JsonResponse({'not_ajax':True})
