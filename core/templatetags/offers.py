from django import template

register = template.Library()

@register.inclusion_tag('offer/offer_mini.html')
def offer_mini(offer):
	return { 'offer': offer }	