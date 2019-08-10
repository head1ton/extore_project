from django.http import JsonResponse
from django.utils.text import slugify
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import BoardForm, CommentForm
from .models import Board, Comment



def board_create(request, group_id):
    if request.method == "POST":
        form = BoardForm(request.POST)
        form.instance.author_id = request.user.id

        if form.is_valid():
            form.instance.group_id = group_id
            form.save()

            return redirect(reverse('board:board_list'))
    else:
        form = BoardForm()
    
    return render(request, 'board/board_create.html', {'form':form})


def board_list(request, group_id):
    if request.method == 'GET':
        board_list = Board.objects.filter(group_id=group_id)

        return render(request, 'board/board_list.html', {'board_list':board_list})


def board_detail(request, board_id):
    if request.method == 'GET':
        board = Board.objects.get(id=board_id)

        return render(request, 'board/board_detail.html', {'board':board})


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
    comment_form = CommentForm(request.POST)
    comment_form.instance.nickname_id = request.user.id
    comment_form.instance.board_id = board_id
    if comment_form.is_valid():
        comment_form.save()

    return redirect(reverse('board:board_detail', args=[board_id]))


def comment_list(request, board_id):
    board = Board.objects.get(id=board_id)
    comments = board.comment_board.all()

    return render(request, 'board/comment_list', {'comments':comments})

def comment_update(request, comment_id):
    is_ajax, data = (request.GET.get('is_ajax'), request.GET) if 'is_ajax' in request.GET \
    else (request.POST.get('is_ajax', False), request.POST)

    comment = get_object_or_404(Comment, pk=comment_id)
    board = get_object_or_404(Board, pk=comment.board.id)

    if request.user != comment.nickname:
        messages.warning(request, "권한 없음")
        return redirect(reverse("board:board_detail", args=[board.id]))

    if is_ajax:
        form = CommentForm(data, instance=comment)
        if form.is_valid():
            form.save()
            return JsonResponse({'updated':True})

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
        return JsonResponse({'deleted':True})

    if request.method == "POST":
        comment.delete()
        return redirect(reverse("board:board_detail", args=[board.id]))

    else:
        return render(request, 'board/comment_delete.html',{'object':comment})
