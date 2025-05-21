from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def dictget(value, arg):
    """Get item from a dictionary or list by key/index."""
    try:
        # Handle lists if value is a list of objects
        if isinstance(value, list):
            for item in value:
                if str(item.id) == str(arg):
                    return item
            return None
        # Handle dictionaries
        return value.get(arg)
    except (KeyError, AttributeError):
        return None

@register.filter
def attr(obj, attr_name):
    """Access an attribute of an object."""
    try:
        return getattr(obj, attr_name)
    except (AttributeError, TypeError):
        return None 