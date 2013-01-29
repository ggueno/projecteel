from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView
from django.template import RequestContext

from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings

from core.models import *


from forms import ProjectForm, OfferForm, EducationForm, ExperienceForm, CommentForm

from taggit.models import Tag
from django.contrib.auth.decorators import login_required

from django.template import RequestContext

from django.views.decorators.csrf import requires_csrf_token, ensure_csrf_cookie

def home(request):
    return render_to_response('index.html')



def projects(request, projects):
    template = 'project/list_projects.html'
    endless_part = 'project/endless_part.html'
    context = {
        'projects': projects,
        'endless_part': endless_part,
    }
    if request.is_ajax():   
        template = endless_part
    return render_to_response(template, context, context_instance=RequestContext(request))


def projects_all(request):
    return projects(request, Project.objects.filter(published=True))


def search_projects(request):
    try:
        q = request.GET['query']
        projects_list = Project.objects.filter(title__icontains=q, published=True) | \
                Project.objects.filter(content__icontains=q, published=True)
        return projects(request, projects_list)
    except KeyError:
        return render_to_response('search/results.html')


def get_project(request, slug):
    project = Project.objects.get(slug=slug)

    #outagg = project.skills
    categoriesList = project.categories.get_query_set()
    skillsList = project.skills.get_query_set()
    tagsList = project.tags.get_query_set()
    equipementsList = project.equipments.get_query_set()
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    comments = Comment.objects.filter(project=project)
    comment_form = CommentForm()
    #TODO : delete slug from view and template
    return render_to_response('project/show_project.html', {'project': project, 'slug': slug, 'tags': tagsList, 'categories': categoriesList, 'skills': skillsList, 'equipments': equipementsList , 'user': applicant, 'comment_form': comment_form, 'comments': comments})


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
                embed = request.POST.getlist('embed')
                for embed in embed:
                    EmbedContent.objects.create(title=project.title, content=embed, project=project)

                cd = form.cleaned_data
                project_save = form.save(commit=False)
                project_save.published = True
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



@login_required
def remove_project(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        project = Project.objects.get(id=pk, owner=applicant)
        state = False
        if project.owner == applicant:
            state = Project.objects.get(id=pk).delete()
    except Project.DoesNotExist:
        response = JSONResponse(False, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    if request.is_ajax():
        response = JSONResponse(True, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/projects/')

def like(request, pk):
    try:
        nblikes = Like.objects.all().count()
        profile = Profile.objects.filter(user_id=request.user.id)[0]
        project = Project.objects.get(id=pk)
        if Like.objects.filter(profile=profile).count() == 0:
            Like.objects.create(profile=profile, project_id=pk)
            likecreate = 2 #create
        else:
            likecreate = 1 #not create because profile already push
    except Profile.DoesNotExist:
        likecreate = 0 #not create because error
        return False
    to_json = {
        "likecreate": likecreate,
        "nblikes": nblikes
    }
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def likeldknklsd(request, pk):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                profile = Profile.objects.filter(user_id=request.user.id)[0]
                project = Project.objects.get(id=pk)
                if Like.objects.filter(profile=profile).count() == 0:
                    message = "unpushed"
                    Like.objects.create(profile=profile, project_id=pk)
                else:
                    message = "pushed"      
            except Profile.DoesNotExist:
                return False
    return HttpResponse(message)


def get_my_self(request):
    return Profile.objects.get(user_id=request.user.id)

@login_required
def follow(request, pk):
    myself = get_my_self(request)
    if request.user.id == pk :
        result=False
    else:
        try:
            Follow.objects.get(follower_id=myself.id, following_id=pk)
            result = False
        except Follow.DoesNotExist:
            Follow.objects.create(follower_id=myself.id, following_id=pk)
            result = True

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        profile = Profile.objects.get(id=pk)
        return HttpResponseRedirect('/profile/'+profile.slug)


@login_required
def unfollow(request, pk):
    myself = get_my_self(request)
    if request.user.id == pk :
        result=False
    else:
        try:
            Follow.objects.get(follower_id=myself.id, following_id=pk).delete()
            result = True
        except Follow.DoesNotExist:
            result = False

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        profile = Profile.objects.get(id=pk)
        return HttpResponseRedirect('/profile/'+profile.slug)


def offers(request):
    template = 'offer/list_offers.html'
    endless_part = 'offer/endless_part.html'
    context = {
        'offers': Offer.objects.all(),
        'endless_part': endless_part,
    }
    if request.is_ajax():
        template = endless_part
    return render_to_response(template, context, context_instance=RequestContext(request))


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

@login_required
def apply_offer(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        if ApplicantOffer.objects.filter(applicant=applicant).count() == 0:
            ApplicantOffer.objects.create(applicant=applicant, offer_id=pk)
    except Applicant.DoesNotExist:
        return False

    if request.is_ajax():
        response = JSONResponse(True, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/offers/')


@login_required
def add_education(request):
    form = {}

    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            education = form.save(commit=False)
            applicant.educations.create(school=education.school, start=education.start, end=education.end, title=education.title, description=education.description)
            # education.save()
            # form.save_m2m()
            return HttpResponseRedirect('/')
    else:
        form = EducationForm()
    return render(request, 'education/add_education.html', {'form': form})


@login_required
def add_experience(request):
    form = {}

    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            experience = form.save(commit=False)
            applicant.experiences.create(company=experience.company, title=experience.title, city=experience.city, start=experience.start, end=experience.end, details=experience.details)
            # education.save()
            # form.save_m2m()
            return HttpResponseRedirect('/')
    else:
        form = ExperienceForm()
    return render(request, 'experience/add_experience.html', {'form': form})


#TODO : generic view for all profile
def get_applicant(request, slug):
    # myself = get_my_self(request)
    profile = Applicant.objects.get(slug=slug)
    projects = Project.objects.filter(Q(owner=profile.user) | Q(participant__in=[profile]))
    following = Follow.objects.filter(follower__user_id=request.user.id)
    #TODO : delete slug from view and template
    return render(request,'profile/profile_applicant.html', {'profile': profile, 'slug': slug, 'following': following, 'projects': projects})


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


def add_comment(request):
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    if request.method == 'POST':

        form = CommentForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            data = cd
            project = Project.objects.get(id=request.POST['project_id'])
            Comment.objects.create(project=project, profile=applicant, content=cd['content'])

            data = [{
                'name': applicant.name,
                'content': cd['content'],
                'avatar_url': '',
                'delete_url': '',
                'delete_type': "DELETE"
            }]
        else:
            data = request.POST
    else:
        data = 'False1'

    if request.is_ajax():
        response = JSONResponse(data, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

def delete_comment(request, pk):

    try:
        comment = Comment.objects.get(id=pk)

        if comment.profile.user.id == request.user.id:
            comment.delete()
            data = True
    except Comment.DoesNotExist:
            data = False

    if request.is_ajax():
        response = JSONResponse(data, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    #TO DO : Not Ajax Response



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
