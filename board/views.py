import math

from django.db.models import Q
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
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

        if form.is_valid():
            form.save()

            page = int(request.GET.get('page', 1))
            paginated_by = 3
            board_list = Board.objects.filter(extore_id=group_id)
            total_count = len(board_list)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            board_list = board_list[start_index:end_index]

            users = User.objects.all()

            current_top_num = len(Board.objects.filter(extore_id=group_id)) - paginated_by * (page - 1)

            return render(request, 'board/board_list.html', \
                          {'board_list': board_list, 'group': group, 'group_list': group_list, \
                           'users': users, 'total_page': total_page, 'page_range': page_range,
                           'currentTopNum': current_top_num})

        raise Http404
    # 게시물 작성 화면 이동 시,
    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = BoardForm()
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()
            return render(request, 'board/board_create.html', {'form': form, 'group': group, 'group_list': group_list, 'users': users})
        raise Http404




def board_list(request):
    group_id = request.GET.get('extore', None) if request.method=="GET" else request.POST.get('extore', None)

    if group_id:
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        board_list = Board.objects.filter(extore_id=group_id)

        page = int(request.GET.get('page', 1))
        paginated_by = 3

        search_type = request.POST.getlist('search_type', None) if request.method=="POST" else request.GET.get('searchType', None)

        search_q = None
        search_key = request.POST.get('search_key', None) if request.method=="POST" else request.GET.get('searchKey', None)

        # 검색어 입력한 경우
        if search_key:
            if 'title' in search_type:
                temp_q = Q(title__icontains=search_key)
                search_q = search_q | temp_q if search_q else temp_q
            if 'text' in search_type:
                temp_q = Q(text__icontains=search_key)
                search_q = search_q | temp_q if search_q else temp_q
            if 'realName' in search_type:
                last_name = search_key[0]
                first_name = search_key[1:]
                temp_q = Q(author__last_name=last_name) & Q(author__first_name=first_name)
                search_q = search_q | temp_q if search_q else temp_q

            board_list = get_list_or_404(board_list, search_q)
            total_count = len(board_list)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            board_list = board_list[start_index:end_index]
            users = User.objects.all()
            return render(request, 'board/board_list.html', \
                      {'board_list': board_list, 'group': group, 'group_list': group_list, \
                       'users': users, 'total_page': total_page, 'page_range': page_range, 'searchKey':search_key, 'searchType':search_type})

        # 검색어 입력하지 않고 목록 조회하는 경우
        total_count = len(board_list)
        total_page = math.ceil(total_count / paginated_by)
        page_range = range(1, total_page + 1)
        start_index = paginated_by * (page - 1)
        end_index = paginated_by * page
        board_list = board_list[start_index:end_index]
        users = User.objects.all()

        # num_in_turn = []
        # for i in range(len(board_list)):
        #     num_in_turn.append(i+1)
        #     num_in_turn.sort(reverse=True)

        current_top_num = len(Board.objects.filter(extore_id=group_id)) - paginated_by*(page-1)

        return render(request, 'board/board_list.html',\
                      {'board_list':board_list, 'group':group, 'group_list':group_list,\
                       'users':users, 'total_page':total_page, 'page_range':page_range, 'currentTopNum':current_top_num})

    raise Http404


def board_detail(request, board_id):
    if request.method == 'GET':
        board = Board.objects.get(id=board_id)
        group_id = request.GET.get('extore', None)

        if not request.user in Group.objects.get(pk=group_id).member.all():
            raise Http404

        if group_id:
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            comment_form = CommentForm()
            comments = board.comments.all()
            users = User.objects.all()
            return render(request, 'board/board_detail.html', {'board':board, 'comments':comments, 'comment_form':comment_form, 'group':group, 'group_list':group_list, 'users':users})

    raise Http404


def board_update(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.user != board.author and not request.user.is_staff:
        raise Http404

    if request.method == 'POST':
        group_id = request.POST.get('group_id', None)
        form = BoardForm(request.POST, request.FILES, instance=board)
        form.instance.author_id = request.user.id
        form.instance.extore_id = group_id
        if form.is_valid():
            form.save()
            group = Group.objects.get(pk=group_id)
            group_list = request.user.members_groups.all()

            page = int(request.GET.get('page', 1))
            paginated_by = 3
            board_list = Board.objects.filter(extore_id=group_id)
            total_count = len(board_list)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            board_list = board_list[start_index:end_index]

            users = User.objects.all()

            current_top_num = len(Board.objects.filter(extore_id=group_id)) - paginated_by*(page-1)

            return render(request, 'board/board_list.html',\
                          {'board_list':board_list, 'group':group, 'group_list':group_list,\
                           'users':users, 'total_page':total_page, 'page_range':page_range, 'currentTopNum':current_top_num})

    else:
        form = BoardForm(instance=board)
        group_id = request.GET.get('extore', None)
        if group_id:
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()
            return render(request, 'board/board_update.html', {'form':form, 'group': group, 'group_list': group_list, 'user': users})
        return Http404


def board_delete(request, board_id):
    if request.is_ajax():
        board = Board.objects.get(id=board_id)
        # 삭제 요청한 유저가 해당 글 작성자가 아니거나, staff가 아닌 경우
        if board.author != request.user and not request.user.is_staff:
            messages.warning(request, '삭제할 권한이 없습니다.')
            return JsonResponse({'noAuthor': True})
        # 삭제 요청한 유저가 해당 글 작성자 혹은 staff 인 경우
        board.delete()
        return JsonResponse({'works':True})
    # ajax 요청이 아닌 경우
    raise Http404


def comment_create(request, board_id):
    is_ajax = request.POST.get('is_ajax')
    board = Board.objects.get(pk=board_id)
    if not request.user in board.extore.member.all():
        raise Http404
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
    if not request.user in board.extore.member.all():
        raise Http404
    comments = board.comments.all()

    return render(request, 'board/comment_list', {'comments':comments})


def comment_like(request, comment_id):
    is_ajax = request.GET.get('is_ajax') if 'is_ajax' in request.GET else request.POST.get('is_ajax',False)
    comment = Comment.objects.get(id=comment_id)
    board = Board.objects.get(id=comment.board.id)
    if not request.user in board.extore.member.all():
        raise Http404
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

    if request.user != comment.nickname and not request.user.is_staff:
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
