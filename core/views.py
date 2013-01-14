from django.shortcuts import render_to_response
from core.models import Project
from forms import ProjectForm


def home(request):
    return render_to_response('index.html')


def projects(request):
    list_projects = Project.objects.filter(published=True)
    return render_to_response('projects.html', {'theme': "themy", 'projects': list_projects})


def get_project(request, slug):
    project = Project.objects.get(slug=slug)
    return render_to_response('project.html', {'project': project, 'slug': slug})


def add_project(request):
    form = {}
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            get_project(request, cd.slug)
    else:
        form = ProjectForm()
    return render_to_response('project/add_project.html', {'form': form})
