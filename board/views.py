from django.utils.text import slugify
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .forms import BoardForm, CommentForm
from .models import Board, Comment
from extore.models import Group


def board_create(request, group_id):
    if request.method == "POST":
        form = BoardForm(request.POST)
        form.instance.author_id = request.user.id
        form.instance.group = int(group_id)
        if form.is_valid():
            form.instance.slug = slugify(form.instance.title, allow_unicode=True)
            form.save()
            group = Group.objects.get(id=group_id)
            group.board.add(form.instance)

            return redirect(reverse('board:boardlist', args=[group_id]))
    else:
        form = BoardForm()

    return render(request, 'board/board_create.html', {'form': form, 'group_id': group_id})


def board_list(request, group_id):
    if request.method == 'GET':
        group = Group.objects.get(id=group_id)
        board_list = group.board.all()

        return render(request, 'board/board_list.html', {'board_list': board_list, 'group_id': group_id})


def board_detail(request, board_id):
    if request.method == 'GET':
        group_id = request.GET.get('group_id')
        print(group_id)
        return render(request, 'board/board_detail.html',
                      {'board': Board.objects.get(id=board_id), 'group_id': group_id})


def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    document = get_object_or_404(Board, pk=comment.document.id)
    # 관리자
    # user.is_staff 스태프가 더 하위 애들 (운영진)
    # user.is_superuser (마스터)
    if request.user != comment.author:
        messages.warning(request, "권한 없음")
        return redirect(reverse("board:boarddetail", args=[document.id]))

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(reverse("board:boarddetail", args=[document.id]))
    else:
        form = CommentForm(instance=comment)
    return render(request, 'board/comment_update.html', {'form': form})


def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    document = get_object_or_404(Board, pk=comment.document.id)

    if request.user != comment.author and not request.user.is_staff:
        messages.warning(request, "권한 없음")
        return redirect(reverse("board:boarddetail", args=[document.id]))

    if request.method == "POST":
        comment.delete()
        return redirect(reverse("board:boarddetail", args=[document.id]))
    else:
        return render(request, 'board/comment_delete.html', {'object': comment})


def comment_create(request, document_id):
    document = get_object_or_404(Board, pk=document_id)
    comment_form = CommentForm(request.POST)
    comment_form.instance.author_id = request.user.id
    comment_form.instance.document_id = document_id
    if comment_form.is_valid():
        comment = comment_form.save()

    # return redirect(document)
    return redirect(reverse('board:boarddetail', args=[document_id]))