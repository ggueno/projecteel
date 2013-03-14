from django import template

register = template.Library()


@register.inclusion_tag('profile/profile_mini.html')
def profile_mini(profile, last, nb_col='fourcol'):
    return {'profile': profile, 'last': last, 'nb_col': nb_col}
