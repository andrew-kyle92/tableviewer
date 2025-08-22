import json

from django.db import models

from ckeditor.fields import RichTextField


def table_directory_path(filename):
    # file will be uploaded to MEDIA_ROOT/table_files/<filename>
    return f'table_files/{filename}'

def logo_directory_path(instance, filename):
    return f'logos/{filename}'


class DynamicTable(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    table_file = models.FileField(upload_to=table_directory_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    results_shown = models.IntegerField(default=5, help_text="Number of results shown in the table")
    logo = models.ImageField(upload_to=logo_directory_path, blank=True)
    before_table_text = RichTextField(blank=True, help_text="Text before the table")
    after_table_text = RichTextField(blank=True, help_text="Text after the table")
    settings = models.OneToOneField('TableSettings', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_active_columns(self, column='label'):
        return list(self.columns.filter(use_column=True).values_list(column, flat=True))

    class Meta:
        ordering = ('id',)
        verbose_name = 'Dynamic Table'
        verbose_name_plural = 'Dynamic Tables'


class TableColumn(models.Model):
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    use_column = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.table.name})"

    def to_json(self):
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'order': self.order,
            'use_column': self.use_column
        })

    class Meta:
        ordering = ['order']
        verbose_name = "Table Column"
        verbose_name_plural = "Table Columns"

class URLShortcut(models.Model):
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE, related_name='shortcuts')
    url = models.CharField(max_length=100, unique=True, help_text="No spaces are allowed; if spaces are needed, please use dashes or underscores, instead.")

    def __str__(self):
        return self.url

    class Meta:
        ordering = ['id']
        verbose_name = "URL Shortcut"
        verbose_name_plural = "URL Shortcuts"


class TableSettings(models.Model):
    name = models.CharField(max_length=255)
    published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} Settings"

    class Meta:
        verbose_name = "Table Settings"
        verbose_name_plural = "Table Settings"
