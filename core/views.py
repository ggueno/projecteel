from django.shortcuts import render_to_response, render
from core.models import Project, Applicant, Profile
from core.models import *
from forms import ProjectForm
from forms import OfferForm
from taggit.models import Tag
from django.contrib.auth.decorators import login_required

def home(request):
    return render_to_response('index.html')


def projects(request):
    list_projects = Project.objects.filter(published=True)
    return render_to_response('project/list_projects.html', {'theme': "themy", 'projects': list_projects})


def get_project(request, slug):
    project = Project.objects.get(slug=slug)

    #outagg = project.skills
    categoriesList = project.categories.get_query_set()
    skillsList = project.skills.get_query_set()
    tagsList = project.tags.get_query_set()
    equipementsList = project.equipments.get_query_set()
    return render_to_response('project/show_project.html', {'project': project, 'slug': slug, 'tags': tagsList, 'categories': categoriesList, 'skills': skillsList, 'equipments': equipementsList})


@login_required
def add_project(request):

    form = {}

    # user = User.objects.get(id=request.user.id)
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    if request.method == 'POST':

        form = ProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            project = form.save(commit=False)
            project.owner = applicant
            project.save()
            get_project(request, project.slug)
    else:
        form = ProjectForm()
    return render(request, 'project/add_project.html', {'form': form, 'user_id': applicant})


def offers(request):
    list_offers = Offer.objects.all()
    return render_to_response('offer/list_offers.html', {'offers': list_offers})


def get_offer(request, slug):
    offer = Offer.objects.get(slug=slug)
    return render_to_response('offer/show_offer.html', {'offer': offer, 'slug': slug})

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
