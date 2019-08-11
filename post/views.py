from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from .models import *
from .forms import *
# Create your views here.


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        form.instance.author_id = request.user.id
        if form.is_valid():
            post = form.save()
            print(post)
            return redirect(reverse('post:list'))
    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = PostForm(extore_id=group_id)
        else:
            raise Http404
        return render(request, 'post/post_create.html', {'form':form})


def post_list(request):
    if request.method == 'GET':
        group_id = request.GET.get('extore', None)
        if group_id:
            posts = Post.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            return render(request, 'post/post_list.html', {'object_list': posts, 'group':group, 'group_list':group_list})

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

    return render(request, 'post/post_detail.html', {'object':post, 'comments':comments, 'comment_form':comment_form, 'group':group, 'group_list':group_list})


def post_delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    # 로그인한 유저가 작성자일 경우, 해당 포스트 삭제 버튼 보이도록
    # ajax post요청일 경우, detail 페이지로 이동
    if request.method == "POST":
        if post.author != request.user or request.user:
            messages.warning(request, '삭제할 권한이 없습니다.')
            return redirect(reverse_lazy('post:detail', args=[post.id]))
    # ajax 요청이 아닌경우, delete 페이지로 이동
    return render(request, 'post/post_delete.html')

def post_update(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk=post_id)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect(post)
    else:
        post = Post.objects.get(pk=post_id)
        form = PostForm(instance=post)
    return render(request, 'post/post_update.html', {'form':form})

# 태그 기능 관련
from tagging.views import TaggedObjectList
from django.contrib.contenttypes.models import ContentType


class PostTaggedObjectList(TaggedObjectList):
    model = Post
    allow_empty = True
    template_name = 'post/post_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        group_id = self.request.GET.get('extore', None)
        group = Group.objects.get(id=group_id)
        group_list = self.request.user.members_groups.all()

        context_data['group'] =  group
        context_data['group_list'] = group_list

        return context_data

    def get_queryset(self):
        super().get_queryset()
        group_id = self.request.GET.get('extore', None)
        posts = Post.objects.filter(extore_id=group_id)

        return posts

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
        posts_year_dict = reduce(lambda dict, ch: dict.update({ch:dict.get(ch,0)+1}) or dict, posts_year_li, {})
        return render(request, 'post/last_memory.html', {'object_dict':posts_year_dict, 'object_list':posts, 'group':group, 'group-list':group_list})


def show_comments(request, post_id):
    post = Post.objects.get(pk=post_id)
    comment_form = CommentForm()
    comments = post.comments.all()
    return render(request, 'post/comments_list.html', {'object':post, 'comments':comments, 'comment_form':comment_form})


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