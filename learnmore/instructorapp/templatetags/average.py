from django import template

register = template.Library()

@register.filter
def average(queryset, field):
    values = [getattr(obj, field, None) for obj in queryset if getattr(obj, field, None) is not None]
    if not values:
        return None
    return sum(values) / len(values) 