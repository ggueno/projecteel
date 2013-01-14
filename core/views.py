from django.shortcuts import render_to_response
from core.models import Project


def home(request):
    return render_to_response('index.html')


def projects(request):
    list_projects = Project.objects.filter(published=True)
    return render_to_response('projects.html', {'theme': "themy", 'projects': list_projects})


def get_project(request, slug):
    project = Project.objects.get(slug=slug)
    return render_to_response('project.html', {'project': project, 'slug': slug})
