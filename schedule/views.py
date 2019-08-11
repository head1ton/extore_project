from urllib.parse import urlparse

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import CalendarEvent
from extore.models import Group
from .util import events_to_json, calendar_options
from django.contrib import messages
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
                minTime: 8,
                maxTime: 20,
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
    event_url = f'all_events/{group_id}/'
    if group_id:
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()

        return render(request, 'schedule/index.html', {'calendar_config_options': calendar_options(event_url, OPTIONS), 'group':group, 'group_list':group_list})

    raise Http404


def all_events(request, group_id):
    events = CalendarEvent.objects.filter(extore_id=group_id)

    return HttpResponse(events_to_json(events), content_type='application/json')


from .forms import ScheduleForm
from django.urls import reverse
from django.shortcuts import redirect


def schedule_create(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST, request.FILES)

        form.instance.author_id = request.user.id
        form.instance.extore_id = request.POST.get('group_id', None)

        if form.is_valid():
            schedule = form.save()
            group_id = schedule.extore_id
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()
            event_url = 'all_events/'

            return render(request, 'schedule/index.html', {'calendar_config_options': calendar_options(event_url, OPTIONS), 'group':group, 'group_list':group_list})

        else:
            group_id = form.instance.extore_id
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            messages.warning(request, '입력이 올바르지 않습니다.')
            return render(request, 'schedule/schedule_create.html', {'form':form, 'group':group, 'group_list':group_list})

    else:
        group_id = request.GET.get('extore', None)
        if group_id:
            form = ScheduleForm()
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            return render(request, 'schedule/schedule_create.html', {'form':form, 'group':group, 'group_list':group_list})

        raise Http404


def schedule_list(request):
    group_id = request.GET.get('extore', None)
    if group_id:
        schedules = CalendarEvent.objects.filter(extore_id=group_id)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        return render(request, 'schedule/schedule_list.html', {'object_list':schedules, 'group':group, 'group_list':group_list})


def schedule_update(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            group_id = request.POST.get('group_id', None)
            schedules = CalendarEvent.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            return render(request, 'schedule/schedule_list.html',
                          {'object_list': schedules, 'group': group, 'group_list': group_list})
        else:
            messages.warning(request, '입력이 올바르지 않습니다.')

            group_id = request.POST.get('group_id', None)
            schedules = CalendarEvent.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            return render(request, 'schedule/schedule_list.html',
                          {'object_list': schedules, 'group': group, 'group_list': group_list})
    else:
        group_id = request.GET.get('extore', None)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()
        form = ScheduleForm(instance=schedule)
    return render(request, 'schedule/schedule_update.html', {'form':form, 'group':group, 'group_list':group_list})


def schedule_delete(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        print(schedule.author.username, request.user)
        if schedule.author != request.user and not request.user.is_staff:
            messages.warning(request, '삭제할 권한이 없습니다.')

            group_id = request.POST.get('group_id', None)
            schedules = CalendarEvent.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            return render(request, 'schedule/schedule_list.html', {'object_list': schedules, 'group': group, 'group_list': group_list})

        else:
            schedule.delete()
            group_id = request.POST.get('group_id', None)
            schedules = CalendarEvent.objects.filter(extore_id=group_id)
            group = Group.objects.get(id=group_id)
            group_list = request.user.members_groups.all()

            return render(request, 'schedule/schedule_list.html', {'object_list':schedules, 'group':group, 'group_list':group_list})

    else:
        group_id = request.GET.get('extore', None)
        group = Group.objects.get(id=group_id)
        group_list = request.user.members_groups.all()

    return render(request, 'schedule/schedule_delete.html', {'group':group, 'group_list':group_list})