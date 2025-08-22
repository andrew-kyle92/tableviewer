from django.contrib import admin

from .models import SiteGroup


@admin.register(SiteGroup)
class SiteGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'get_tables')
    search_fields = ('name',)
    filter_horizontal = ('members', 'owners', 'tables',)

    def get_members(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

    get_members.short_description = 'Members'

    def get_owners(self, obj):
        return ", ".join([user.username for user in obj.owners.all()])

    get_owners.short_description = 'Owners'

    def get_tables(self, obj):
        return ", ".join([str(table) for table in obj.tables.all()])

    get_tables.short_description = 'Tables'
