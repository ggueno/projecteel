from django.shortcuts import render_to_response, render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView

from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings

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
    #TODO : delete slug from view and template
    return render_to_response('project/show_project.html', {'project': project, 'slug': slug, 'tags': tagsList, 'categories': categoriesList, 'skills': skillsList, 'equipments': equipementsList})


@login_required
def add_project(request):

    form = {}
    project_id = -1

    # user = User.objects.get(id=request.user.id)
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    if request.method == 'POST':
        project = get_object_or_404(Project, id=request.POST['project_id'], owner=applicant)
        # form = ProjectForm(request.POST)
        if project.owner == applicant:
            form = ProjectForm(request.POST, request.FILES, instance=project)

            if form.is_valid():
                cd = form.cleaned_data
                project_save = form.save(commit=False)
                project_save.save()
                form.save_m2m()

            return get_project(request, project_save.slug)
    else:
        p = Project(title="Untitled", content="  ", owner=applicant, published=False)
        p.save()
        project_id = p.id
        form = ProjectForm()
        return render(request, 'project/add_project.html', {'form': form, 'user_id': applicant, 'project_id': project_id})


@login_required
def add_project_image(request):
    # user = User.objects.get(id=request.user.id)
    return render(request, 'project/add_images.html')




def offers(request):
    list_offers = Offer.objects.all()
    return render_to_response('offer/list_offers.html', {'offers': list_offers})


def get_offer(request, slug):
    offer = Offer.objects.get(slug=slug)
    #TODO : delete slug from view and template
    return render_to_response('offer/show_offer.html', {'offer': offer, 'slug': slug})


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






# View For PictureUpload
def response_mimetype(request):
    return "application/json"
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"



class ImageProjectCreateView(CreateView):
    model = ImageProject

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JSONResponse(form.errors.FILES, status=400)
        else:
            return super(AjaxableResponseMixin, self).form_invalid(form)

    def form_valid(self, form):
        # return JSONResponse(self.request.POST, status=400)
        self.object = form.save()
        f = self.request.FILES.get('image')
        id_project = self.request.POST['project_id']
        if 'title' in self.request.POST:
            self.object.title = self.request.POST['title']
        else:
            self.object.title = f.name
        self.object.project = Project.objects.get(id=id_project)
        self.object.save()
        data = [{'name': f.name, 'url': settings.MEDIA_URL + "upload/images/project/" + f.name.replace(" ", "_"), 'thumbnail_url': settings.MEDIA_URL + "upload/images/project/" + f.name.replace(" ", "_"), 'delete_url': reverse('upload-delete', args=[self.object.id]), 'delete_type': "DELETE"}]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'

        return response


class ImageProjectDeleteView(DeleteView):
    model = ImageProject

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new')


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)
