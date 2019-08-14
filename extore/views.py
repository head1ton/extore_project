from django.http import JsonResponse
from django.utils.text import slugify
from django.shortcuts import render
from .models import Group
from .forms import GroupForm
from post.models import Post

def group_list(request):
    # group_list = extore list
    group_list = request.user.members_groups.all()
    return render(request, 'extore/extore_index.html', {'group_list': group_list})


def group_detail(request, group_id):
    if request.method == 'GET':
        # group = the extore to see detail
        group = Group.objects.get(id=group_id)
        # group_list = extore list
        group_list = request.user.members_groups.all()
        posts = Post.objects.filter(extore_id=group_id)

        return render(request, 'post/post_list.html',{'object_list':posts, 'group':group, 'group_list':group_list})


def group_delete(request, group_id):
    is_ajax = request.POST.get('is_ajax', None)
    if is_ajax:
        group = Group.objects.get(id=group_id)
        if not request.user.is_authenticated:
            return JsonResponse({'notLogin':True})
        if not request.user in group.member.all():
            return JsonResponse({'notMember':True})
        user = request.user
        group.remove(user)
        return JsonResponse({'leaved':True})


def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        form.instance.author_id = request.user.id
        if form.is_valid():
            form.instance.slug = slugify(form.instance.title)
            form.save()
            return render(request, 'extore/extore_index.html')
    else:
        form = GroupForm()

    return render(request, 'extore/extore_create.html', {'form':form})
