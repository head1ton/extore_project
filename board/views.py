from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import BoardForm, CommentForm
from .models import *
from accounts.models import User



def board_create(request):
    if request.method == "POST":
        form = BoardForm(request.POST)
        form.instance.author_id = request.user.id
        group_id = request.POST.get('group_id', None)
        form.instance.extore_id = group_id
        group = Group.objects.get(pk=group_id)
        group_list = request.user.members_groups.all()
        board_list = Board.objects.filter(extore_id=group_id)
        users = User.objects.all()
        if form.is_valid():
            form.save()
            return render(request, 'board/board_list.html', {'board_list':board_list, 'group':group, 'group_list':group_list, 'user':users})
        raise Http404
    # 게시물 작성 화면 이동 시,
    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = BoardForm()
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()
            return render(request, 'board/board_create.html', {'form': form, 'group': group, 'group_list': group_list, 'user': users})
        raise Http404




def board_list(request):
    if request.method == 'GET':
        group_id = request.GET.get('extore', None)
        if group_id:
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            board_list = Board.objects.filter(extore_id=group_id)
            users = User.objects.all()
            return render(request, 'board/board_list.html', {'board_list':board_list, 'group':group, 'group_list':group_list, 'users':users})
    raise Http404


def board_detail(request, board_id):
    if request.method == 'GET':
        board = Board.objects.get(id=board_id)
        group_id = request.GET.get('extore', None)
        if group_id:
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            comment_form = CommentForm()
            comments = board.comments.all()
            users = User.objects.all()
            return render(request, 'board/board_detail.html', {'board':board, 'comments':comments, 'comment_form':comment_form, 'group':group, 'group_list':group_list, 'users':users})

    raise Http404


def board_update(request, board_id):
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET \
        else (request.POST.get('is_ajax', False), request.POST)

    board = Board.objects.get(id=board_id)

    if is_ajax:
        form = BoardForm(data, instance=board)
        form.instance.author_id = request.user.id
        if form.is_valid():
            form.save()
            return JsonResponse({'updated':True})


def board_delete(request, board_id):
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET \
        else (request.POST.get('is_ajax', False), request.POST)

    board = Board.objects.get(id=board_id)

    if is_ajax:
        board.delete()
        return JsonResponse({'deleted':True})


def comment_create(request, board_id):
    is_ajax = request.POST.get('is_ajax')
    board = Board.objects.get(pk=board_id)
    comment_form = CommentForm(request.POST)
    comment_form.instance.nickname_id = request.user.id
    comment_form.instance.board_id = board_id
    if comment_form.is_valid():
        comment = comment_form.save()

    if is_ajax:
        html = render_to_string('board/comment_single.html', {'comment':comment, 'user':request.user})
        return JsonResponse({'html':html})

    return redirect(board)


def comment_list(request, board_id):
    board = Board.objects.get(id=board_id)
    comments = board.comments.all()

    return render(request, 'board/comment_list', {'comments':comments})


def comment_like(request, comment_id):
    is_ajax = request.GET.get('is_ajax') if 'is_ajax' in request.GET else request.POST.get('is_ajax',False)
    comment = Comment.objects.get(id=comment_id)
    board = Board.objects.get(id=comment.board.id)
    if is_ajax:
        comment = Comment.objects.get(pk=comment_id)
        comment.like = comment.like + 1
        comment.save()

        return JsonResponse({'works':True})
    return redirect(board)


def comment_update(request, comment_id):
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET \
    else (request.POST.get('is_ajax', False), request.POST)

    comment = get_object_or_404(Comment, pk=comment_id)
    board = get_object_or_404(Board, pk=comment.board.id)

    if request.user != comment.nickname:
        messages.warning(request, "권한 없음")
        return redirect(board)

    if is_ajax:
        form = CommentForm(data, instance=comment)
        if form.is_valid():
            form.save()
            return JsonResponse({'works':True})
        else:
            return JsonResponse({'works':False})

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(reverse("board:board_detail", args=[board.id]))

    else:
        form = CommentForm(instance=comment)
        return render(request, 'board/comment_update.html',{'form':form})


def comment_delete(request, comment_id):
    is_ajax = request.GET.get('is_ajax') if 'is_ajax' in request.GET else request.POST.get('is_ajax', False)

    comment = get_object_or_404(Comment, pk=comment_id)
    board = get_object_or_404(Board, pk=comment.board.id)

    if request.user != comment.nickname and not request.user.is_staff and request.user != board.author:
        messages.warning(request, "권한 없음")
        return redirect(reverse("board:board_detail", args=[board.id]))

    if is_ajax:
        comment.delete()
        return JsonResponse({'works':True})

    if request.method == "POST":
        comment.delete()
        return redirect(reverse("board:board_detail", args=[board.id]))

    else:
        return render(request, 'board/comment_delete.html',{'object':comment})
