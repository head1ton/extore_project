from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from extore.models import Group

User = get_user_model()

class CalendarEvent(models.Model):
    extore = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='schedules')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="schedules")
    title = models.CharField(_('Title'), max_length=200)
    start = models.DateTimeField(_('Start'))
    end = models.DateTimeField(_('End'))
    all_day = models.BooleanField(_('All day'), default=False)
    # models.DateTimeField(input_formats=["%d %b %Y %H:%M:%S %Z"])
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

        ordering = ['-start']

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title
