from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from .models import *
# Create your views here.

def main_page(request):
    return HttpResponse('hihi')

def post_create(request):
    pass

def post_list(request):
    posts = Post.objects.all()
    return render(request, 'post_list', {'object_list':posts})

def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    return render(request, 'post_detail', {'object':post})
    # <script src="https://maps.googleapis.com/maps/api/js?key=[api키]&language=ko"
    # type="text/javascript">

def post_delete(request, post_id):
    post = Post.objects.get(pk=post_id)
    # 로그인한 유저가 작성자일 경우, 해당 포스트 삭제 버튼 보이도록
    if request.method == "POST":
        if post.author != request.user:
            messages.warning(request, '삭제할 권한이 없습니다.')
            return redirect(reverse_lazy('photo:detail'))
    return render(request, 'post')

def post_update(request, post_id):
    post = Post.objects.get(pk=post_id)


from tagging.views import TaggedObjectList
class PostTaggedObjectList(TaggedObjectList):
    model = Post
    allow_empty = True
    template_name = 'post/post_list.html'
from django.views.generic import TemplateView
class TagList(TemplateView):
    template_name = 'post/tag_list.html'
