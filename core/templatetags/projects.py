from django import template

register = template.Library()


@register.inclusion_tag('project/project_mini.html')
def project_mini(project, last, nb_col='fourcol'):
    return {'project': project, 'last': last, 'nb_col': nb_col}


@register.inclusion_tag('project/comment.html')
def comment_template(comment, user_id):
    return {'comment': comment, 'user_id': user_id}
