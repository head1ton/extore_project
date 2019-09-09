import math
from urllib.parse import urlparse

from django.db.models import Q
from django.shortcuts import render, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from .models import CalendarEvent
from extore.models import Group
from .util import events_to_json, calendar_options
from django.contrib import messages
from accounts.models import User
from django.urls import reverse_lazy
from django.template import loader

# This is just an example for this demo. You may get this value
# from a separate file or anywhere you want

OPTIONS = """{  timeFormat: "H:mm",
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay',
                },
                allDaySlot: false,
                firstDay: 0,
                weekMode: 'liquid',
                slotMinutes: 15,
                defaultEventMinutes: 30,
                minTime: 0,
                maxTime: 24,
                editable: false,
                dayClick: function(date, allDay, jsEvent, view) {
                    if (allDay) {       
                        $('#calendar').fullCalendar('gotoDate', date)      
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },
                eventClick: function(event, jsEvent, view) {
                    if (view.name == 'month') {     
                        $('#calendar').fullCalendar('gotoDate', event.start)      
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },
            }"""


def index(request):
    group_id = request.GET.get('extore', None)

    if group_id:
        event_url = f'all_events/{group_id}/'
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        users = User.objects.all()
        return render(request, 'schedule/index.html', {'calendar_config_options': calendar_options(event_url, OPTIONS), 'group':group, 'group_list':group_list, 'users':users})
    raise Http404



def all_events(request, group_id):
    if group_id:
        events = CalendarEvent.objects.filter(extore_id=group_id)
        return HttpResponse(events_to_json(events), content_type='application/json')
    raise Http404


from .forms import ScheduleForm
from django.urls import reverse
from django.shortcuts import redirect


def schedule_create(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST, request.FILES)

        form.instance.author_id = request.user.id
        form.instance.extore_id = request.POST.get('group_id', None)

        if request.POST.get('start') >= request.POST.get('end'):
            return JsonResponse({'wrongDateTime':True})

        if len(request.POST.get('title')) > 60:
            return JsonResponse({'tooLongTitle':True})

        if form.is_valid():
            # schedule = form.save()
            # group_id = schedule.extore_id
            # return redirect(reverse('schedule:list', args=[group_id]))
            form.save()
            return JsonResponse({'works': True})

        else:
            return JsonResponse({'notValid':True})
            # group_id = form.instance.extore_id
            # group = Group.objects.get(id=group_id)
            # group_list = request.user.members_groups.all()
            # users = User.objects.all()
            #
            # messages.warning(request, '입력이 올바르지 않습니다.')
            # return render(request, 'schedule/schedule_create.html', {'form':form, 'group':group, 'group_list':group_list, 'users':users})

    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = ScheduleForm()
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()

            return render(request, 'schedule/schedule_create.html', {'form':form, 'group':group, 'group_list':group_list, 'users':users})

        raise Http404


def schedule_list(request, group_id):
    if group_id:
        schedules = CalendarEvent.objects.filter(extore_id=group_id)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        users = User.objects.all()

        page = int(request.GET.get('page', 1))
        paginated_by = 6

        search_type = request.POST.getlist('search_type', None) if request.method == "POST" else request.GET.get(
            'searchType', None)

        search_q = None
        search_key = request.POST.get('search_key', None) if request.method == "POST" else request.GET.get('searchKey',
                                                                                                           None)

        # 검색어 입력한 경우
        if search_key:
            if 'title' in search_type:
                temp_q = Q(title__icontains=search_key)
                search_q = search_q | temp_q if search_q else temp_q
            if 'realName' in search_type:
                last_name = search_key[0]
                first_name = search_key[1:]
                temp_q = Q(author__last_name=last_name) & Q(author__first_name=first_name)
                search_q = search_q | temp_q if search_q else temp_q
            if len(search_type) == 0:
                total_count = len(schedules)
                total_page = math.ceil(total_count / paginated_by)
                page_range = range(1, total_page + 1)
                start_index = paginated_by * (page - 1)
                end_index = paginated_by * page
                schedules = schedules[start_index:end_index]
                return render(request, 'schedule/schedule_list.html', {'object_list': schedules, 'group': group, \
                                                                       'group_list': group_list, 'users': users,
                                                                       'total_page': total_page,
                                                                       'page_range': page_range})


            schedules = schedules.filter(search_q)
            total_count = len(schedules)
            total_page = math.ceil(total_count / paginated_by)
            page_range = range(1, total_page + 1)
            start_index = paginated_by * (page - 1)
            end_index = paginated_by * page
            schedules = schedules[start_index:end_index]
            return render(request, 'schedule/schedule_list.html', \
                          {'object_list': schedules, 'group': group, 'group_list': group_list, \
                           'users': users, 'total_page': total_page, 'page_range': page_range, 'searchKey': search_key,
                           'searchType': search_type})

        # 검색어 입력하지 않고 목록 조회하는 경우
        total_count = len(schedules)
        total_page = math.ceil(total_count / paginated_by)
        page_range = range(1, total_page + 1)
        start_index = paginated_by * (page - 1)
        end_index = paginated_by * page
        schedules = schedules[start_index:end_index]
        return render(request, 'schedule/schedule_list.html', {'object_list': schedules, 'group':group, \
                                                       'group_list':group_list, 'users':users, 'total_page':total_page, 'page_range':page_range})
    raise Http404


def schedule_update(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            group_id = request.POST.get('group_id', None)

            return redirect(reverse('schedule:list', args=[group_id]))
        else:
            messages.warning(request, '입력이 올바르지 않습니다.')
            group_id = request.POST.get('group_id', None)

            return redirect(reverse('schedule:list', args=[group_id]))
    else:
        group_id = request.GET.get('extore', None)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        form = ScheduleForm(instance=schedule)
        users = User.objects.all()
    return render(request, 'schedule/schedule_update.html', {'form':form, 'group':group, 'group_list':group_list, 'users':users})


def schedule_delete(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        print(schedule.author.username, request.user)
        if schedule.author != request.user and not request.user.is_staff:
            messages.warning(request, '삭제할 권한이 없습니다.')

            group_id = request.POST.get('group_id', None)
            # schedules = CalendarEvent.objects.filter(extore_id=group_id)
            # group = Group.objects.get(id=group_id)
            # group_list = request.user.members_groups.all()

            return redirect(reverse('schedule:list', args=[group_id]))

        else:
            schedule.delete()
            group_id = request.POST.get('group_id', None)
            # schedules = CalendarEvent.objects.filter(extore_id=group_id)
            # group = Group.objects.get(id=group_id)
            # group_list = request.user.members_groups.all()
            # return render(request, 'schedule/schedule_list.html', {'object_list':schedules, 'group':group, 'group_list':group_list})
            return redirect(reverse('schedule:list', args=[group_id]))

    else:
        if request.is_ajax():
            schedule = CalendarEvent.objects.get(pk=calendarevent_id)
            if request.user != schedule.author and not request.user.is_staff:
                return JsonResponse({'notAuthor':True})
            schedule.delete()
            return JsonResponse({'works': True})

        else:
            group_id = request.GET.get('extore', None)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            users = User.objects.all()
            return render(request, 'schedule/schedule_delete.html', {'group':group, 'group_list':group_list, 'users':users})