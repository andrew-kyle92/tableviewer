from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='get_list')
def get_list(_list):
    items = []

    for column in _list:
        if column.use_column:
            items.append(column)

    return items


@register.filter(name='get_range')
def get_range(value, arg=None):
    """Returns a list containing range made from given value.
    Optional argument can be used to specify the starting value."""
    if arg:
        return range(arg, value)
    return range(value)

@register.filter(name='split_path')
def split_path(path):
    return path.split('/')


@register.filter(name='get_copy_url')
def get_copy_url(url):
    full_url = settings.DOMAIN_NAME + '/' + url
    return full_url