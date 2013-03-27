"""
filters for checking the type of objects and formfields

Usage:

{% if form|obj_type:'mycustomform' %}
  <form class="custom" action="">
{% else %}
  <form action="">
{% endif %}


{% if field|field_type:'checkboxinput' %}
  <label class="cb_label">{{ field }} {{ field.label }}</label>
{% else %}
  <label for="id_{{ field.name }}">{{ field.label }}</label> {{ field }}
{% endif %}

"""

from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

def check_type(obj, stype):
    try:
        t = obj.__class__.__name__
        print t
        return t.lower() == str(stype).lower()
    except:
        pass
    return False
register.filter('obj_type', check_type)

def field_type(field, ftype):
    return check_type(field.field.widget, ftype)
register.filter('field_type', field_type)

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]
upto.is_safe = True