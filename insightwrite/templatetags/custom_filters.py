from django import template

register = template.Library()

@register.filter
def feedback_color(value):
    """Return bootstrap color class based on feedback type"""
    color_map = {
        'positive': 'success',
        'negative': 'danger', 
        'neutral': 'secondary',
        'not_interested': 'warning',
        'helpful': 'info',
        'not_helpful': 'light'
    }
    return color_map.get(value, 'secondary')

@register.filter
def accuracy_color(value):
    """Return bootstrap color class based on accuracy percentage"""
    try:
        accuracy = float(value)
        if accuracy >= 80:
            return 'success'
        elif accuracy >= 60:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'

@register.filter
def engagement_color(value):
    """Return bootstrap color class based on engagement rate"""
    try:
        engagement = float(value)
        if engagement >= 0.1:
            return 'success'
        elif engagement >= 0.05:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'

@register.filter
def performance_color(value):
    """Return bootstrap color class based on performance score"""
    try:
        score = float(value)
        if score >= 8.0:
            return 'success'
        elif score >= 6.0:
            return 'info'
        elif score >= 4.0:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'

@register.filter
def action_color(value):
    """Return bootstrap color class based on action type"""
    color_map = {
        'view': 'info',
        'like': 'danger',
        'comment': 'success',
        'share': 'primary',
        'bookmark': 'warning'
    }
    return color_map.get(value, 'secondary')

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def range(value):
    """Return range object for template iteration"""
    return range(1, int(value) + 1)
