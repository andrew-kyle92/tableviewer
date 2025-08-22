from django import template

register = template.Library()


@register.filter(name='format_list')
def format_list(value, arg):
    """formats a list into a comma-separated string, with arg being the specific column to filter by"""
    dict_list = [v.__dict__ for v in value]
    return ", ".join([v[arg] for v in dict_list])
