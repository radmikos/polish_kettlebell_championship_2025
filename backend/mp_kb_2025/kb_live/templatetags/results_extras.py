"""Custom template filters for export rendering."""

from __future__ import annotations

from django import template


register = template.Library()


@register.filter(name="getattribute")
def getattribute(value, attr_name):
    """Safely fetch an attribute or mapping key in templates."""
    if not attr_name:
        return None

    if isinstance(value, dict):
        return value.get(attr_name)

    if hasattr(value, attr_name):
        return getattr(value, attr_name)

    try:
        return value[attr_name]
    except (KeyError, TypeError, IndexError):
        return None
