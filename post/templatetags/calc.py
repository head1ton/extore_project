from django import template

from datetime import datetime, date, timedelta

from django.db.models import Q

register = template.Library()

@register.filter
def time_since(value):
    time_since = datetime.now() - value
    # 현재시간과의 차이가 1개월 이상일 경우
    if time_since > timedelta(days=30):
        return value.strftime("%Y.%m.%d")
    # 현재시간과의 차이가 24시간 이상일 경우
    if time_since > timedelta(days=1):
        return f'{time_since // timedelta(days=1)}일 전'
    # 현재시간과의 차이가 24시간 이하 1시간 이상일 경우
    elif time_since > timedelta(hours=1):
        return f'{time_since // timedelta(hours=1)}시간 전'
    # 현재시간과의 차이가 1시간 이하 1분 이상일 경우
    elif time_since > timedelta(minutes=1):
        return f'{time_since // timedelta(minutes=1)}분 전'
    # 현재시간과의 차이가 1분 이하 1초 이상일 경우
    elif time_since > timedelta(seconds=1):
        return f'{time_since // timedelta(seconds=1)}초 전'
    else:
        return '지금'


@register.filter
def return_year(value):
    return value.strftime("%Y")


@register.filter
def same_invitation_time_since(inviteStatus, inviteDates):
    invite_date = inviteDates.filter(group_id=inviteStatus.group.id)
    if invite_date.exists() :
        return time_since(invite_date[0].created)
    else:
        return None


@register.filter
def list_index(current_top_num,  forloop):
    return (current_top_num - forloop)