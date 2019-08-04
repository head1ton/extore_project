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
            return redirect(reverse('post:list'))
    else:
        form = PostForm()
        return render(request, 'post/post_create.html', {'form':form})

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

from functools import reduce
def last_memory(request):
    posts = Post.objects.all()

    posts_year_li = []

    for post in posts:
        posts_year_li.append(post.created.strftime("%Y"))

    posts_year_dict = reduce(lambda dict, ch: dict.update({ch:dict.get(ch,0)+1}) or dict, posts_year_li, {})
    return render(request, 'post/last_memory.html', {'object_dict':posts_year_dict, 'object_list':posts})

# from django.http import JsonResponse
# def show_comment(request, post_id):
#     is_ajax = request.POST.get('is_ajax')
#     post = Post.objects.get(pk=post_id)
#     comments = post.comments.all()
#     if is_ajax:
#         div_comment = """
#         <div class="card" style="width: 40rem; margin-top:-10px;">
#               <div>
#                   <div class="img-profile" style="background-image:url({{user.profile.url}})"></div>
#                   <div style="float:right; height:70px; line-height:70px;">
#                       <div style="display:inline-block; vertical-align:middle; line-height:normal;">
#                           <form action="{% url 'post:comment_create' object.id %}" method="post">
#                               {% csrf_token %}
#                               <div class="row" style="width:590px; padding-right:10px;">
#                                   <div class="col-8" style="padding:0 0 0 5px;">{{comment_form.text}}</div>
#                                   <div class="col">
#                                     <input type="submit" value="댓글 입력" class="btn btn-outline-primary form-control">
#                                   </div>
#                               </div>
#                           </form>
#                       </div>
#                   </div>
#               </div>
#               <div id="comment_list">
#                   {% for comment in comments %}
#                     <div style="margin-bottom: 20px;">
#                         <div class="img-profile" style="background-image:url({{comment.author.profile.url}})"></div>
#                         <div style="float:left; height:100%; width:550px; line-height:100%;">
#                             <div style="display:inline-block; vertical-align:middle; line-height:normal;">
#                                 <p style="padding:10px; border-radius:25px; background-color:rgb(237,237,237); display:inline-block; margin:0">
#                                     <a style="color:rgb(37,71,194); font-weight:bold;" href="#">{{comment.author.last_name}}{{comment.author.first_name}}</a>&emsp;{{comment.text}}
#                                 </p>
#                                 <a class="btn-comment-like" href="{% url 'post:comment_like' comment.id %}">&emsp;좋아요 {% if comment.like %}{{comment.like}}개{% endif %}</a>
#                             </div>
#                         </div>
#                         <div style="clear:both;"></div>
#                     </div>
#                   {% endfor %}
#               </div>
#             </div>
#         """
#
#         return JsonResponse({'div_comment':div_comment})