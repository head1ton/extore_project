from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from .models import *
from .forms import *
# Create your views here.

def main_page(request):
    return HttpResponse('EXTORE에 오신 것을 환영합니다.')

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        form.instance.author_id = request.user.id
        if form.is_valid():
            post = form.save()
            print(post)
            return redirect(reverse('post:detail', args=[post.id]))
    else:
        form = PostForm()
        return render(request, 'post/post_create.html', {'form':form})

from django.utils import timezone
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post/post_list.html', {'object_list':posts})

def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)

    comment_form = CommentForm()
    comments = post.comments.all()

    return render(request, 'post/post_detail.html', {'object':post, 'comments':comments, 'comment_form':comment_form})

def post_delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    # 로그인한 유저가 작성자일 경우, 해당 포스트 삭제 버튼 보이도록
    # ajax post요청일 경우, detail 페이지로 이동
    if request.method == "POST":
        if post.author != request.user:
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
class PostTaggedObjectList(TaggedObjectList):
    model = Post
    allow_empty = True
    template_name = 'post/post_list.html'

from django.views.generic import TemplateView
class TagList(TemplateView):
    template_name = 'post/tag_list.html'


def comment_create(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        comment_form = CommentForm(request.POST)
        comment_form.instance.author_id = request.user.id
        comment_form.instance.post_id = post_id
        if comment_form.is_valid():
            comment_form.save()

        return redirect(post)

from urllib.parse import urlparse
def post_like(request, post_id):
    post = Post.objects.get(pk=post_id)
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
    if request.method == 'GET':
        if request.user in post.saved.all():
            post.saved.remove(request.user)
        else:
            post.saved.add(request.user)
        referer_url = request.META.get('HTTP_REFERER')
        path = urlparse(referer_url).path
        return HttpResponseRedirect(path)

def comment_like(request, comment_id):
    if request.method == "GET":
        comment = Comment.objects.get(pk=comment_id)
        post = Post.objects.get(pk=comment.post.id)

        comment.like += 1
        comment.save()
        return redirect(post)