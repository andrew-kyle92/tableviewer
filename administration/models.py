from django.db import models
from django.contrib.auth.models import User


class SiteGroup(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    members = models.ManyToManyField(User, blank=True, related_name='group_memberships')
    owners = models.ManyToManyField(User, blank=True, related_name='group_ownerships')
    tables = models.ManyToManyField('tableviewer.DynamicTable', blank=True, related_name='group_tables')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Site Group'
        verbose_name_plural = 'Site Groups'
        ordering = ['name']
