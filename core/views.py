from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView
from django.template import RequestContext
from datetime import datetime, timedelta

from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q, Count

from core.models import *
from forms import ProjectForm, OfferForm, EducationForm, ExperienceForm, CommentForm
from django.contrib.auth.decorators import login_required


def home(request):
    return render_to_response('index.html')


def get_my_self(request):
    return Profile.objects.filter(user_id=request.user.id)[0]


def projects(request, projects):
    template = 'project/list_projects.html'
    endless_part = 'project/endless_part.html'
    context = {
        'projects': projects,
        'categories': CategoryTag.objects.all(),
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


def search_projects2(request):

    q = {}

    if(request.method == 'GET'):
        q['published'] = True


        if 'location[]' in request.GET:
            q["location__in"] = request.GET.getlist('location[]')

        if 'tags[]' in request.GET:
            q["tags__name__in"] = request.GET.getlist('tags[]')

        if 'skills[]' in request.GET:
            q["skills__name__in"] = request.GET.getlist('skills[]')

        if 'durationmin' in request.GET:
            # TODO : check if 'duration-min' is an number
            q["period__gte"] = request.GET['durationmin']

        if 'durationmax' in request.GET:
            # TODO : check if 'duration-min' is an number
            q["period__lte"] = request.GET['durationmax']

        if 'categories' in request.GET:
            if request.GET['categories'] != 'all':
                q['categories__slug__in'] = [request.GET['categories']]

        if 'when' in request.GET and int(request.GET['when']) != 0:
            when = int(request.GET['when'])
        else:
            #first day for a project
            when = 9999

        #check if when is a number
        today = datetime.now()
        start_date = datetime.now() - timedelta(days=7)
        if when != 9999:
            q['publish_date__range'] = (start_date, today)

        if 'filter' in request.GET and request.GET['filter'] in ['comments', 'pushs']:
            filtre = request.GET['filter']
            if filtre == 'pushs':
                filtre = 'likes'
            projects_list = Project.objects.annotate(num=Count('comments')).filter(**q).order_by('-num')
        else:
            projects_list = Project.objects.filter(**q).order_by('-publish_date')

        return projects(request, projects_list)
    # except KeyError:
    #     return render_to_response('search/results.html')



def get_project(request, slug):
    project = Project.objects.get(slug=slug)

    # get all tags for project
    categoriesList = CategoryTaggedItem.objects.filter(content_object=project.id)
    skillsList = project.skills.get_query_set()
    tagsList = project.tags.get_query_set()
    equipementsList = project.equipments.get_query_set()

    comments = Comment.objects.filter(project=project)
    comment_form = CommentForm()

    if Like.objects.filter(project=project).filter(profile=get_my_self(request)).count() == 0:
        push = "unpushed"
    else:
        push = "pushed"

    context = {
        'project': project,
        'tags': tagsList,
        'categories': categoriesList,
        'skills': skillsList,
        'equipments': equipementsList,
        'user': get_my_self(request),
        'comment_form': comment_form,
        'comments': comments,
        'status': push
    }
    return render(request, 'project/show_project.html', context)


def get_locations(request):

    if(request.method == 'GET'):
        q = ""
        if 'q' in request.GET:
            q = request.GET["q"]
        else:
            raise
        locations = Project.objects.filter(location__startswith=q).values_list('location', flat=True)

    choices = [{"name": l, "value": l} for l in set(locations)]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_tags(request):
    q = ""
    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise
    tags = CommonTag.objects.filter(name__startswith=q).values_list('name', flat=True)

    choices = [{"name": l, "value": l} for l in tags]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_participants(request):
    q = ""
    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise
    participants = Applicant.objects.filter(name__startswith=q).values_list('name',  'avatar')

    choices = [{"name": l[0], "value": l[0], "avatar": l[1]} for l in participants]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response



def get_list(request, tag):
    q = ""
    if tag == 'skills':
        objectKind = SkillsTag
    elif tag == 'tags':
        objectKind = CommonTag

    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise
    tags = objectKind.objects.filter(name__startswith=q).values_list('name', flat=True)

    choices = [{"name": l, "value": l} for l in tags]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_my_profile(request):
    app = Applicant.objects.get(user_id=request.user.id)
    return get_applicant(request, app.slug)


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
                project_save = form.save(commit=False)
                project_save.published = True
                project_save.save()
                form.save_m2m()
                return get_project(request, project_save.slug)
            else:
                # form = ProjectForm(instance=project)
                return render(request, 'project/add_project.html', {'form': form, 'project_id': project.id})
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
def edit_project(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        project = Project.objects.get(id=pk, owner=applicant)
    except Applicant.DoesNotExist:
        HttpResponseRedirect('/projects/')
    except Project.DoesNotExist:
        HttpResponseRedirect('/projects/')


    if project.owner == applicant:
        project = Project.objects.get(id=pk)
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            if form.is_valid():
                form = ProjectForm(request.POST, request.FILES, instance=project)
                form.save()
                slug = project.slug
                HttpResponseRedirect('/projects/')

        else:
            form = ProjectForm(instance=project)
            # thumbnails =
            return render(request,'project/edit_project.html', {'form': form,})

    else:
        HttpResponseRedirect('/projects/')


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
    project = Project.objects.get(id=pk)
    profile = Profile.objects.filter(user_id=request.user.id)[0]
    if Like.objects.filter(project=project).filter(profile=profile).count() == 0:
        Like.objects.create(profile=profile, project_id=pk)
    likes = Like.objects.filter(project=project).count()
    return HttpResponse(likes)


@login_required
def follow(request, pk):
    myself = get_my_self(request)
    if request.user.id == pk:
        result = False
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
        return HttpResponseRedirect('/profile/' + profile.slug)


@login_required
def unfollow(request, pk):
    myself = get_my_self(request)
    if request.user.id == pk:
        result = False
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
    if ApplicantOffer.objects.filter(offer=offer).filter(applicant=applicant).count() == 0:
        status = "nonapplied"
    else:
        status = "applied"
    #TODO : delete slug from view and template
    return render_to_response('offer/show_offer.html', {'offer': offer, 'slug': slug, 'user': applicant, 'status': status})


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
    offer = Offer.objects.get(id=pk)
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    if ApplicantOffer.objects.filter(offer=offer).filter(applicant=applicant).count() == 0:
        ApplicantOffer.objects.create(applicant=applicant, offer_id=pk)
        msg = "applied"
    else:
        msg = ""
    return HttpResponse(msg)


@login_required
def posted_offers(request):
    company = Company.objects.filter(user_id=request.user.id)[0]
    offers = Offer.objects.filter(company=company)
    applicantsOffer = ApplicantOffer.objects.all()
    endless_part = 'offer/endless_part.html'
    context = {
        'offers': offers,
        'applicants': applicantsOffer,
        'endless_part': endless_part,
    }
    return render(request, 'offer/posted_offers.html', context)


@login_required
def add_education(request):
    form = {}

    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            education = form.save(commit=False)
            # Education.create(school=education.school, start=education.start, end=education.end, title=education.title, description=education.description, owner=applicant)
            education.owner = applicant
            education.save()
            # form.save_m2m()
            if request.is_ajax():
                formData = {
                    'school' : {'name' :education.school.name },
                    'title' : education.title,
                    'start' : education.start.strftime("%d %B %Y"),
                    'end' : education.end.strftime("%d %B %Y"),
                    'description' : education.description,
                    'owner' : education.owner,
                    'id' : education.id,
                }
                user = request.user
                html = render(request, 'profile/education.html', {'education': formData, 'user' : user})
                response = JSONResponse([True,{'data' : html.content}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return HttpResponseRedirect('/')
        else:
            if request.is_ajax():
                response = JSONResponse([False,{'data' : form.as_p()}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return render(request, 'education/add_education.html', {'form': form})
    else:
        form = EducationForm()
        return render(request, 'education/add_education.html', {'form': form})

@login_required
def delete_education(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        education = Education.objects.get(id=pk)
        state = False
        if education.owner == applicant:
            state = Education.objects.get(id=pk).delete()
    except Education.DoesNotExist:
        response = JSONResponse(False, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    if request.is_ajax():
        response = JSONResponse(True, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/profile/')



@login_required
def add_experience(request):
    form = {}

    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    if request.method == 'POST':
        # company = Company.objects.get(slug=request.POST['company'])[0]

        form = ExperienceForm(request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            experience = form.save(commit=False)
            experience.owner = applicant
            # applicant.experiences.create(company=experience.company, title=experience.title, city=experience.city, start=experience.start, end=experience.end, details=experience.details)
            experience.save()
            # form.save_m2m()
            if request.is_ajax():
                formData = {
                    'company' : experience.company.name,
                    'city' : experience.city,
                    'title' : experience.title,
                    'start' : experience.start.strftime("%d %B %Y"),
                    'end' : experience.end.strftime("%d %B %Y"),
                    'details' : experience.details,
                    'owner' : experience.owner,
                    'id' : experience.id,
                }
                user = request.user
                html = render(request, 'profile/experience.html', {'experience': formData, 'user' : user})
                response = JSONResponse([True,{'data' : html.content}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
        else:
            if request.is_ajax():
                response = JSONResponse([False,{'data' : form.as_p()}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return render(request, 'experience/add_experience.html', {'form': form})
    else:
        form = ExperienceForm()
    return render(request, 'experience/add_experience.html', {'form': form})


@login_required
def delete_experience(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        experience = Experience.objects.get(id=pk)
        state = False
        if experience.owner == applicant:
            state = Experience.objects.get(id=pk).delete()
    except Experience.DoesNotExist:
        response = JSONResponse(False, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    if request.is_ajax():
        response = JSONResponse(True, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/profile/')


#TODO : generic view for all profile
def get_applicant(request, slug):
    # myself = get_my_self(request)

    profile = Applicant.objects.get(slug=slug)
    projects = Project.objects.filter(Q(owner=profile.user, published=True) | Q(participant__in=[profile], published=True))
    following = Follow.objects.filter(follower__user_id=request.user.id)
    formEducation = EducationForm()
    formExperience = ExperienceForm()
    #TODO : delete slug from view and template
    context = {
        'profile': profile,
        'following': following,
        'projects': projects,
        'formEducation': formEducation,
        'formExperience': formExperience,
        # 'pushs': Applicant.objects.push_user()
        'pushs': Project.objects.push_user(profile.user_id)
    }
    return render(request, 'profile/profile_applicant.html', context)


def update_applicant(request):
    return render(request, 'profile/profile_applicant.html', context)


def get_company(request, slug):
    profile = Company.objects.get(slug=slug)
    offers = Offer.objects.filter(Q(company=profile))
    following = Follow.objects.filter(follower__user_id=request.user.id)
    #TODO : delete slug from view and template
    context = {
        'profile': profile,
        'following': following,
        'offers': offers,
        # 'pushs': Applicant.objects.push_user()
        # 'pushs': Offer.objects.push_user(profile.user_id)
    }
    return render_to_response('profile/profile_company.html', context)


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

    try:
        if request.method == 'POST':

            form = CommentForm(request.POST)

            if form.is_valid():
                cd = form.cleaned_data
                data = cd
                project = Project.objects.get(id=int(request.POST['project_id']))
                comment = Comment.objects.create(project=project, profile=applicant, content=cd['content'])

                data = [{
                    'id': comment.id,
                    'name': applicant.user.first_name + " " + applicant.user.last_name,
                    'content': cd['content'],
                    'avatar_url': applicant.avatar.url,
                    'publish_date': comment.publish_date.strftime('%Y-%m-%d'),
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
        else:
            return HttpResponseRedirect('/project/' + request.POST['project_id'])

    except Project.DoesNotExist:
        response = JSONResponse(request, {}, response_mimetype(request))
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
