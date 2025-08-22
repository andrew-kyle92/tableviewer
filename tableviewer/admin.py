from django.contrib import admin
from .models import DynamicTable, TableColumn, URLShortcut, TableSettings


class TableColumnAdmin(admin.TabularInline):
    model = TableColumn
    extra = 1


class URLShortcutAdmin(admin.TabularInline):
    model = URLShortcut
    extra = 1


@admin.register(DynamicTable)
class DynamicTableAdmin(admin.ModelAdmin):
    inlines = [URLShortcutAdmin, TableColumnAdmin]
    # fields = ['name', 'description', 'table_file', 'settings']
    fieldsets = [
        ('Table Information', {
            'fields': [
                'name',
                'description',
                'table_file',
            ],
        }),
        ('Table Settings', {
            'fields': [
                'settings',
            ],
        }),
    ]


@admin.register(TableSettings)
class TableSettingsAdmin(admin.ModelAdmin):
    pass
