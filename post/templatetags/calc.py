from django import template

from datetime import datetime, date, timedelta


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

