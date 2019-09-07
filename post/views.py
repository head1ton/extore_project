import math

from django.db.models import Q
from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from .models import *
from .forms import *
from accounts.models import User


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        group_id = request.POST.get('group_id', None)
        form.instance.author_id = request.user.id
        form.instance.extore_id = group_id
        if form.is_valid():
            form.save()

            posts = Post.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            page = int(request.GET.get('page', 1))
            paginated_by = 3

            search_type = request.POST.getlist('search_type', None) if request.method == "POST" else request.GET.get('searchType', None)

            search_q = None
            search_key = request.POST.get('search_key', None) if request.method == "POST" else request.GET.get('searchKey', None)

            total_count = len(posts)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            posts = posts[start_index:end_index]

            users = User.objects.all()
            return render(request, 'post/post_list.html', {'object_list': posts, 'group': group, \
                                                           'group_list': group_list, 'users': users,
                                                           'total_page': total_page, 'page_range': page_range})
    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = PostForm()
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()
            return render(request, 'post/post_create.html', {'form':form, 'group':group, 'group_list':group_list, 'users':users})
        raise Http404



def post_list(request):
    group_id = request.GET.get('extore', None) if request.method == "GET" else request.POST.get('extore', None)
    if group_id:
        posts = Post.objects.filter(extore_id=group_id)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()

        page = int(request.GET.get('page', 1))
        paginated_by = 3

        search_type = request.POST.getlist('search_type', None) if request.method == "POST" else request.GET.get('searchType', None)

        search_q = None
        search_key = request.POST.get('search_key', None) if request.method == "POST" else request.GET.get('searchKey', None)

        # 검색어 입력한 경우
        if search_key:
            if 'text' in search_type:
                temp_q = Q(text__icontains=search_key)
                search_q = search_q | temp_q if search_q else temp_q
            if 'realName' in search_type:
                last_name = search_key[0]
                first_name = search_key[1:]
                temp_q = Q(author__last_name=last_name) & Q(author__first_name=first_name)
                search_q = search_q | temp_q if search_q else temp_q

            posts = posts.filter(search_q)
            total_count = len(posts)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            posts = posts[start_index:end_index]
            users = User.objects.all()
            return render(request, 'post/post_list.html', \
                          {'object_list': posts, 'group': group, 'group_list': group_list, \
                           'users': users, 'total_page': total_page, 'page_range': page_range, 'searchKey': search_key,
                           'searchType': search_type})

        # 검색어 입력하지 않고 목록 조회하는 경우
        total_count = len(posts)
        total_page = math.ceil(total_count / paginated_by)
        page_range = range(1, total_page + 1)
        start_index = paginated_by * (page - 1)
        end_index = paginated_by * page
        posts = posts[start_index:end_index]

        users = User.objects.all()
        return render(request, 'post/post_list.html', {'object_list': posts, 'group':group, \
                                                       'group_list':group_list, 'users':users, 'total_page':total_page, 'page_range':page_range})

    raise Http404


def post_detail(request, post_id):
    if request.method == 'GET':
        group_id = request.GET.get('extore', None)
        if group_id:
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            post = Post.objects.get(pk=post_id)

            comment_form = CommentForm()
            comments = post.comments.all()
            users = User.objects.all()

            return render(request, 'post/post_detail.html', {'object':post, 'comments':comments, 'comment_form':comment_form, 'group':group, 'group_list':group_list, 'users':users})
    raise Http404


def post_delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    # 로그인한 유저가 작성자일 경우, 해당 포스트 삭제 버튼 보이도록
    # ajax post요청일 경우, detail 페이지로 이동
    if request.is_ajax():
        if post.author != request.user and not request.user.is_staff:
            messages.warning(request, '삭제할 권한이 없습니다.')
            return JsonResponse({'noAuthor':True})
        post.delete()
        return JsonResponse({'works':True})

    # ajax 요청이 아닌경우, Http404 에러 발생
    raise Http404


def post_update(request, post_id):
    if request.is_ajax():
        post = Post.objects.get(pk=post_id)
        text = request.POST.get('text')

        # 수정 요청한 유저가 글 작성자 혹은 staff 가 아닌 경우
        if request.user != post.author and not request.user.is_staff:
            return JsonResponse({'noAuthor':True})

        # 수정 요청한 유저가 글 작성자 혹우은 staff인 경우
        post.text = text
        post.save()
        return JsonResponse({'works': True})

    # ajax 요청이 아닌 경우
    raise Http404


# 태그 기능 관련
from tagging.views import TaggedObjectList
from tagging.models import TaggedItem
from django.core.exceptions import ImproperlyConfigured

class PostTaggedObjectList(TaggedObjectList):
    model = Post
    allow_empty = True
    template_name = 'post/post_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        group_id = self.request.GET.get('extore', None)
        group = Group.objects.get(id=group_id)
        group_list = self.request.user.members_groups.all()
        users = User.objects.all()

        context_data['group'] =  group
        context_data['group_list'] = group_list
        context_data['users'] = users

        return context_data

    def get_queryset(self):
        super().get_queryset()
        group_id = self.request.GET.get('extore', None)
        posts = Post.objects.filter(extore_id=group_id)

        self.queryset_or_model = posts
        self.tag_instance = self.get_tag()
        return TaggedItem.objects.get_by_model(
            self.queryset_or_model, self.tag_instance)


# from django.views.generic import TemplateView
# class TagList(TemplateView):
#     template_name = 'post/tag_list.html'


def comment_create(request, post_id):
    is_ajax = request.POST.get('is_ajax')
    post = Post.objects.get(pk=post_id)
    comment_form = CommentForm(request.POST)
    comment_form.instance.author_id = request.user.id
    comment_form.instance.post_id = post_id
    if comment_form.is_valid():
        comment = comment_form.save()
    if is_ajax:
        html = render_to_string('post/comment_single.html',{'comment':comment, 'user':request.user})
        return JsonResponse({'html':html})

    return redirect(post)



from urllib.parse import urlparse
def post_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET else (
    request.POST.get('is_ajax', False), request.POST)

    if is_ajax:
        if request.user in post.like.all():
            post.like.remove(request.user)
            print("좋아요 해제")
            return JsonResponse({'liked':False})
        else:
            post.like.add(request.user)
            print("좋아요 클릭")
            return JsonResponse({'liked': True})

    if request.method == "GET":
        # if not request.user.is_authenticated:
        #     return HttpResponseRedirect('/accounts/signin')
        if request.user in post.like.all():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        referer_url = request.META.get('HTTP_REFERER')
        path = urlparse(referer_url).path
        return HttpResponseRedirect(path)

def post_saved(request, post_id):
    post = Post.objects.get(pk=post_id)
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET else (request.POST.get('is_ajax', False), request.POST)

    if is_ajax:
        if request.user in post.saved.all():
            post.saved.remove(request.user)
            print("북마크 해제")
            return JsonResponse({'saved':False})
        else:
            post.saved.add(request.user)
            print("북마크 등록")
            return JsonResponse({'saved': True})

    if request.method == 'GET':
        if request.user in post.saved.all():
            post.saved.remove(request.user)
        else:
            post.saved.add(request.user)
        referer_url = request.META.get('HTTP_REFERER')
        path = urlparse(referer_url).path
        return HttpResponseRedirect(path)


from functools import reduce
def last_memory(request):
    group_id = request.GET.get('extore', None)
    if group_id:
        posts = Post.objects.filter(extore_id=group_id)
        posts_year_li = []
        for post in posts:
            posts_year_li.append(post.created.strftime("%Y"))

        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        users = User.objects.all()

        posts_year_dict = reduce(lambda dict, ch: dict.update({ch:dict.get(ch,0)+1}) or dict, posts_year_li, {})
        return render(request, 'post/last_memory.html', {'object_dict':posts_year_dict, 'object_list':posts, 'group':group, 'group_list':group_list, 'users':users})


# def show_comments(request, post_id):
#     post = Post.objects.get(pk=post_id)
#     comment_form = CommentForm()
#     comments = post.comments.all()
#     return render(request, 'post/comments_list.html', {'object':post, 'comments':comments, 'comment_form':comment_form})


def comment_like(request, comment_id):
    is_ajax = request.GET.get('is_ajax') if 'is_ajax' in request.GET else request.POST.get('is_ajax',False)

    if is_ajax:
        comment = Comment.objects.get(pk=comment_id)
        comment.like = comment.like + 1
        comment.save()

        return JsonResponse({'works':True})
    return redirect('/')

def comment_delete(request, comment_id):
    is_ajax = request.GET.get('is_ajax') if 'is_ajax' in request.GET else request.POST.get('is_ajax',False)

    comment = Comment.objects.get(pk=comment_id)
    post = Post.objects.get(pk=comment.post.id)
    if request.user != comment.author and not request.user.is_staff and request.user != post.author:
        messages.warning(request, "권한 없음")
        return redirect(post)

    if is_ajax:
        comment.delete()
        return JsonResponse({'works':True})

    if request.method == "POST":
        comment.delete()
        return redirect(post)

    else:
        return render(request, 'post/comment_delete.html',{'object':comment})



def comment_update(request, comment_id):
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET else (request.POST.get('is_ajax', False), request.POST)

    comment = Comment.objects.get(id=comment_id)
    if is_ajax:
        form = CommentForm(data, instance=comment)
        if form.is_valid():
            form.save()
            return JsonResponse({'works':True})
        else:
            return JsonResponse({'works':False})