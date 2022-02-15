from django import template

register = template.Library()


@register.filter(name='format_report')
def format_report(value, idx):
    lst = value[int(idx) - 1]
    return f"{round(float(lst[0]), 1)}/{round(float(lst[1]), 1)}"
