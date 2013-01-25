from django.shortcuts import render_to_response, render
from core.models import Project, Applicant, Profile
from core.models import *
from forms import ProjectForm
from forms import OfferForm
from taggit.models import Tag
from django.contrib.auth.decorators import login_required
from django.db.models import Q


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
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    likes = Like.objects.filter(project_id=project.id)
    #TODO : delete slug from view and template
    return render_to_response('project/show_project.html', {'project': project, 'slug': slug, 'tags': tagsList, 'categories': categoriesList, 'skills': skillsList, 'equipments': equipementsList , 'user': applicant, 'likes': likes})


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
            form.save_m2m()
            get_project(request, project.slug)
    else:
        form = ProjectForm()
    return render(request, 'project/add_project.html', {'form': form, 'user_id': applicant})


def offers(request):
    list_offers = Offer.objects.all()
    return render_to_response('offer/list_offers.html', {'offers': list_offers})


def get_offer(request, slug):
    offer = Offer.objects.get(slug=slug)
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    #TODO : delete slug from view and template
    return render_to_response('offer/show_offer.html', {'offer': offer, 'slug': slug, 'user': applicant})


@login_required
def add_offer(request):
    form = {}

    company = Company.objects.filter(user_id=request.user.id)[0]
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            offer = form.save(commit=False)
            offer.company = company
            offer.save()
            form.save_m2m()
            return render(request, 'offer/show_offer.html', {'offer': offer, 'slug': offer.slug})
    else:
        form = OfferForm()
    return render(request, 'offer/add_offer.html', {'form': form})


#TODO : generic view for all profile
def get_applicant(request, slug):
    profile = Applicant.objects.get(slug=slug)

    projects = Project.objects.filter(Q(owner=profile.user) | Q(participant__in=[profile]))

    #TODO : delete slug from view and template
    return render_to_response('profile/profile_applicant.html', {'profile': profile, 'slug': slug, 'projects': projects})


def get_company(request, slug):
    company = Company.objects.get(slug=slug)
    #TODO : delete slug from view and template
    return render_to_response('profile/profile_company.html', {'profile': company, 'slug': slug})


def get_school(request, slug):
    school = School.objects.get(slug=slug)
    return render_to_response('profile/profile_school.html', {'profile': school, 'slug': slug})
