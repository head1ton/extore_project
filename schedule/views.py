from django.shortcuts import render
from django.http import HttpResponse
from .models import CalendarEvent
from .util import events_to_json, calendar_options
from django.contrib import messages
from django.urls import reverse_lazy

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
    event_url = 'all_events/'
    return render(request, 'schedule/index.html', {'calendar_config_options': calendar_options(event_url, OPTIONS)})

def all_events(request):
    events = CalendarEvent.objects.all()
    return HttpResponse(events_to_json(events), content_type='application/json')

from .forms import ScheduleForm
from django.urls import reverse
from django.shortcuts import redirect
def schedule_create(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST, request.FILES)
        form.instance.author_id = request.user.id
        if form.is_valid():
            form.save()
            return redirect(reverse('schedule:index'))
        else:
            messages.warning(request, '입력이 올바르지 않습니다.')
            return render(request, 'schedule/schedule_create.html', {'form':form})
    else:
        form = ScheduleForm()
        return render(request, 'schedule/schedule_create.html', {'form':form})
    
def schedule_list(request):
    schedules = CalendarEvent.objects.all()
    return render(request, 'schedule/schedule_list.html', {'object_list':schedules})
    
def schedule_update(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save()
            return redirect(reverse('schedule:list'))
        else:
            messages.warning(request, '입력이 올바르지 않습니다.')
            return render(request, 'schedule/schedule_update.html', {'form': form})
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'schedule/schedule_update.html', {'form':form})

def schedule_delete(request, calendarevent_id):
    schedule = CalendarEvent.objects.get(pk=calendarevent_id)
    if request.method == "POST":
        print(schedule.author.username, request.user)
        if schedule.author != request.user:
            messages.warning(request, '삭제할 권한이 없습니다.')
            return redirect(reverse_lazy('schedule:list'))
        else:
            # print(schedule.start)
            schedule.delete()
            
            return redirect(reverse_lazy('schedule:list'))
    return render(request, 'schedule/schedule_delete.html')