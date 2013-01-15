from django.shortcuts import render_to_response, render
from core.models import Project
from core.models import *
from forms import ProjectForm
from forms import OfferForm
from taggit.models import Tag


def home(request):
    return render_to_response('index.html')


def projects(request):
    list_projects = Project.objects.filter(published=True)
    return render_to_response('project/list_projects.html', {'theme': "themy", 'projects': list_projects})


def get_project(request, slug):
    project = Project.objects.get(slug=slug)

    #outagg = project.skills
    tagsList = project.skills.get_query_set()
    return render_to_response('project/show_project.html', {'project': project, 'slug': slug, 'tags': tagsList})


#@login_required
def add_project(request):
    form = {}
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            get_project(request, cd.slug)
    else:
        form = ProjectForm()
    return render(request, 'project/add_project.html', {'form': form})


def offers(request):
    list_offers = Offer.objects.all()
    return render_to_response('offers.html', {'offers': list_offers})


def get_offer(request, slug):
    offer = Offer.objects.get(slug=slug)
    return render_to_response('offer.html', {'offer': offer, 'slug': slug})


def add_offer(request):
    form = {}
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            get_offer(request, cd.slug)
    else:
        form = OfferForm()
    return render_to_response('offer/add_offer.html', {'form': form})


def get_profile(request, slug):
    profile = Applicant.objects.get(slug=slug)
    return render_to_response('profile/profile.html', {'profile': profile, 'slug': slug})