from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView
from django.template import RequestContext
from django.core.context_processors import csrf

from datetime import datetime, timedelta

from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q, Count, Sum

from core.models import *
from forms import *
from elsewhere.models import SocialNetworkProfile
from elsewhere.forms import SocialNetworkForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from notifications.models import Notification

import itertools
import difflib

from PIL import Image


def home(request):
    try:
        applicant = Applicant.objects.get(user_id=request.user.id)
        return HttpResponseRedirect('/dashboard/')
    except Applicant.DoesNotExist:
        print "ApplicantDoesNotExist"

    try:
        user = User.objects.get(id=request.user.id)
        return HttpResponseRedirect('/profile/')
    except User.DoesNotExist:
        print "UserDoesNotExist"


    projects = Project.objects.annotate(num=Count('likes')).order_by('-num')
    companies = Company.objects.all().annotate(num=Count('followers')).order_by('-num')[:5]

    form = AuthenticationForm(request.POST)

    context = {
        'projects': projects,
        'companies': companies,
        'form': form
    }
    return render_to_response('index.html', context, context_instance=RequestContext(request))


# def login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         if user.is_active:
#             login(request, user)
#             # Redirect to a success page.
#         else:
#             print "user is not active"
#             # Return a 'disabled account' error message
#     else:
#         print "invalid user"
#         # Return an 'invalid login' error message.


def get_my_self(request):
    app = ''
    try:
        app = Applicant.objects.get(user_id=request.user.id)
    except Applicant.DoesNotExist:
        app = ''
    return app


def projects(request, projects):
    template = 'project/list_projects.html'
    endless_part = 'project/endless_part.html'
    context = {
        'projects': projects,
        'categories': CategoryTag.objects.all(),
        'endless_part': endless_part,
        'tags': Project.tags.most_common(),
        'skills': Project.skills.most_common(),
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

        if 'query' in request.GET:
            q['title__icontains'] = request.GET['query']

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
        today = datetime.datetime.now()
        start_date = datetime.datetime.now() - timedelta(days=7)
        if when != 9999:
            q['publish_date__range'] = (start_date, today)

        if 'filter' in request.GET and request.GET['filter'] in ['comments', 'pushs']:
            filtre = request.GET['filter']
            if filtre == 'pushs':
                filtre = 'likes'
            projects_list = Project.objects.annotate(num=Count(filtre)).filter(**q).order_by('-num').distinct()
        elif 'filter' in request.GET and request.GET['filter'] in ['views']:
            projects_list = Project.objects.filter(**q).order_by('hits').distinct()
        else:
            projects_list = Project.objects.filter(**q).order_by('-publish_date').distinct()

        return projects(request, projects_list)


def search_offers(request):

    q = {}

    if(request.method == 'GET'):

        if 'query' in request.GET:
            q['title__icontains'] = request.GET['query']

        if 'location[]' in request.GET:
            q["location__in"] = request.GET.getlist('location[]')

        if 'tags[]' in request.GET:
            q["tags__name__in"] = request.GET.getlist('tags[]')

        if 'contract[]' in request.GET:
            q["contract__in"] = request.GET.getlist('contract[]')

        if 'categories' in request.GET:
            if request.GET['categories'] != 'all':
                q['categories__slug__in'] = [request.GET['categories']]

        # if 'when' in request.GET and int(request.GET['when']) != 0:
        #     when = int(request.GET['when'])
        # else:
        #     #first day for a project
        #     when = 9999

        #check if when is a number
        # today = datetime.now()
        # start_date = datetime.now() - timedelta(days=7)
        # # if when != 9999:
        # #     q['publish_date__range'] = (start_date, today)

        offers_list = Offer.objects.filter(**q).order_by('-publish_date')

        return offers(request, offers_list)
    # except KeyError:
    #     return render_to_response('search/results.html')


def get_project(request, slug):
    project = Project.objects.get(slug=slug)

    if request.user.id:
        following = Follow.objects.filter(follower__user_id=request.user.id, following__user_id=project.owner.user_id)
    else:
        following = {}

    # get all tags for project
    categoriesList = CategoryTaggedItem.objects.filter(content_object=project.id)
    skillsList = project.skills.get_query_set()
    tagsList = project.tags.get_query_set()
    equipementsList = project.equipments.get_query_set()

    comments = Comment.objects.filter(project=project)
    comment_form = CommentForm()

    my_self = get_my_self(request)

    context = {
        'project': project,
        'following': following,
        'tags': tagsList,
        'categories': categoriesList,
        'skills': skillsList,
        'equipments': equipementsList,
        'user': my_self,
        'comment_form': comment_form,
        'comments': comments
    }

    if my_self != '':
        if Like.objects.filter(project=project).filter(profile=my_self).count() == 0:
            push = "unpushed"
        else:
            push = "pushed"
        context['status'] = push

    return render(request, 'project/show_project.html', context)


def get_locations(request):

    if(request.method == 'GET'):
        q = ""
        if 'q' in request.GET:
            q = request.GET["q"]
        elif 'term' in request.GET:
            q = request.GET['term']
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


def get_participants2(request):
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


def get_participants(request):
    q = ""
    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise
    participants = Applicant.objects.filter(Q(user__first_name__startswith=q) | Q(user__last_name__startswith=q)).values_list('id','user__first_name', 'user__last_name', 'avatar')

    choices = [{"value": str(l[0]), "name": l[1]+ " "+l[2], "avatar": l[3]} for l in participants]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_list(request, tag):
    q = ""
    if tag == 'skills':
        objectKind = SkillsTag
    elif tag == 'tags':
        objectKind = CommonTag
    elif tag == 'offerTag':
        objectKind = OfferTag

    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise
    tags = objectKind.objects.filter(name__startswith=q).values_list('name', flat=True)

    choices = [{"name": l, "value": l} for l in tags]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_list_profile(request, type_profile):
    q = ""
    if type_profile == 'company':
        objectKind = SkillsTag
    elif type_profile == 'school':
        objectKind = CommonTag
    elif type_profile == 'applicant':
        return get_participants(request)

    if 'q' in request.GET:
        q = request.GET["q"]
    else:
        raise

    list_profile = objectKind.objects.filter(Q(name__startswith=q)).values_list('id','name', 'avatar')

    choices = [{"value": str(l[0]), "name": l[1], "avatar": l[2]} for l in list_profile]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_my_profile(request):
    app = {}
    try:
        app = Applicant.objects.get(user_id=request.user.id)
    except Applicant.DoesNotExist:
        print "Applicant DoestNotExist"
        return HttpResponseRedirect('/profile/create/')
    return get_applicant(request, app.slug)

@login_required
def update_profile_cover(request):

    if request.method == 'POST':
        myself = Profile.objects.get(user_id=request.user.id)
        form = CoverImageForm(request.POST, request.FILES, instance=myself)

        if form.is_valid():
            cover = form.save()
            if request.is_ajax():
                result = { 'state': True, 'image_src': cover.cover_image.url}
                response = JSONResponse(result, {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return HttpResponseRedirect('/profile/')
        else:
            print "FALSE"
            form = CoverImageForm(instance=myself)
            return render_to_response('profile/update_cover.html',form)


    else:
        c = {}
        c.update(csrf(request))
        form = CoverImageForm()
        return render_to_response('profile/update_cover.html',{'form' : form, 'c': c})


@login_required
def update_profile_cover_position(request):

    if request.method == 'POST':
        myself = Profile.objects.get(user_id=request.user.id)
        myself.cover_image_top = request.POST['cover_pos_top']
        myself.save();

        response = JSONResponse(True, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/profile/');


@login_required
def update_avatar(request, action="new"):

    if request.method == 'POST':
        myself = Profile.objects.get(user_id=request.user.id)


        if action != 'crop':
            form = AvatarForm(request.POST, request.FILES, instance=myself)
            if form.is_valid():
                avatar = form.save()
                if request.is_ajax():
                    result = { 'state': True, 'image_src': avatar.avatar.url}
                    response = JSONResponse(result, {}, response_mimetype(request))
                    response['Content-Disposition'] = 'inline; filename=files.json'
                    return response
                else:
                    return HttpResponseRedirect('/profile/')
            else:
                print "FALSE"
                return HttpResponseRedirect('/profile/')
        else:
            top = request.POST['top']
            left = request.POST['left']
            width = request.POST['width']
            height = request.POST['height']
            filename = str(myself.avatar.path)
            image = Image.open(filename)
            size = int(width), int(height)
            image.thumbnail(size, Image.ANTIALIAS)
            crop = image.crop((int(left), int(top), int(left)+190, int(top)+190))
            crop.save(filename)

            result = { 'state': True, 'image_src': myself.avatar.url}
            response = JSONResponse(result, {}, response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
    else:
        return HttpResponseRedirect('/profile/');


@login_required
def get_my_applications(request):
    myself = Applicant.objects.filter(user_id=request.user.id)[0]
    applications = ApplicantOffer.objects.filter(applicant=myself)
    context = {
        'applications':applications,
    }
    return render(request, 'profile/my_applications.html', context)


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
            # response = JSONResponse(request.POST, {}, response_mimetype(request))
            # response['Content-Disposition'] = 'inline; filename=files.json'
            # return response

            if form.is_valid():
                embed = request.POST.getlist('embed')
                for embed in embed:
                    EmbedContent.objects.create(title=project.title, content=embed, project=project)
                project_save = form.save(commit=False)
                project_save.published = True
                project_save.save()
                form.save_m2m()
                return HttpResponseRedirect('/project/'+project_save.slug)
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
        return HttpResponseRedirect('/projects/')
    except Project.DoesNotExist:
        return HttpResponseRedirect('/projects/')

    if project.owner == applicant:
        project = Project.objects.get(id=pk)
        if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES, instance=project)
            if form.is_valid():
                embed = request.POST.getlist('embed')
                for embed in embed:
                    EmbedContent.objects.create(title=project.title, content=embed, project=project)
                project_save = form.save(commit=False)
                project_save.published = True
                project_save.save()
                print request.POST
                print form.cleaned_data
                # project.save_m2m()
                form.save_m2m()
                slug = project.slug
                return HttpResponseRedirect('/project/'+project_save.slug)
        else:
            form = ProjectForm(instance=project)
            files = ImageProject.objects.filter(project=project)
            categories = CategoryTaggedItem.objects.filter(content_object=project.id)
            context = {
                'thumbnail' : project.thumbnail,
                'project_files' : files,
                'categories' : categories
            }
            print categories
            return render(request, 'project/edit_project.html', {'form': form, 'data' : context })

    else:
        return HttpResponseRedirect('/projects/')

@login_required
def delete_project(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        project = Project.objects.get(id=pk, owner=applicant)
        hitcount = HitCount.objects.filter(object_pk=project.id)
        if project.owner == applicant:
            project.delete()
            hitcount.delete()
    except Project.DoesNotExist:
        pass
    else:
        return HttpResponseRedirect('/profile/')


@login_required
def remove_project(request, pk):
    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        project = Project.objects.get(id=pk, owner=applicant)

        if project.owner == applicant:
            Project.objects.get(id=pk).delete()
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


def like2(request, pk):
    project = Project.objects.get(id=pk)
    profile = Profile.objects.filter(user_id=request.user.id)[0]
    if Like.objects.filter(project=project).filter(profile=profile).count() == 0:
        Like.objects.create(profile=profile, project_id=pk)
    likes = Like.objects.filter(project=project).count()
    return HttpResponse(likes)


def bookmark(request, state, pk):
    try:
        offer = Offer.objects.get(id=pk)
        myself = Applicant.objects.get(user_id=request.user.id)
        if state == 'add':
            myself.bookmarks.add(offer)
        else:
            myself.bookmarks.remove(offer)
        myself.save()
        result = {'state': True}
    except Applicant.DoesNotExist:
        result = {'state': False, 'message': 'Applicant DoesNotExist'}

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        if result['state']:
            return HttpResponseRedirect('/offer/get/'+offer.slug)
        else:
            #404
            return HttpResponseNotFound('404.html')


def like(request, pk):
    project = Project.objects.get(id=pk)
    myself = get_my_self(request)
    if request.user.id == project.owner.user_id:
        result = False
    else:
        try:
            Like.objects.get(project_id=pk, profile__user=request.user)
            result = False
        except Like.DoesNotExist:
            Like.objects.create(project_id=pk, profile=myself)
            result = True

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        profile = Profile.objects.get(id=pk)
        return HttpResponseRedirect('/profile/' + profile.slug)


def unlike(request, pk):
    project = Project.objects.get(id=pk)
    myself = get_my_self(request)
    if request.user.id == project.owner.user_id:
        result = False
    else:
        try:
            Like.objects.get(project_id=pk, profile__user_id=request.user.id).delete()
            result = True
        except Like.DoesNotExist:
            result = False

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        return HttpResponseRedirect('/project/' + project.slug)


@login_required
def make_profil(request):
    print "make_profil"
    form = {}
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        print 'make'
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return HttpResponseRedirect('/projects')

    else:
        form = ProfileForm()
        return render(request, 'profile/make_profile.html', {'form': form})


@login_required
def slug_validate(request):

    message = ''
    success = False

    if request.method == 'POST':
        slug = request.POST.get('slug')
        if Profile.objects.filter(slug__exact=slug).exists():
            message = 'Your slug name is already taken !'
        else:
            success = True
            message = 'Your slug name is correct !'
    ajax_vars = {'success': success, 'message':message}
    return HttpResponse(simplejson.dumps(ajax_vars), mimetype='application/javascript')


@login_required
def create_applicant(request, action="new"):
    user = User.objects.get(id=request.user.id)

    if action != 'new':
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    if request.method == 'POST':
        form_user = UserForm(request.POST, instance=user)
        form_social = SocialNetworkForm(request.POST)

        if action != 'new':
            form_applicant = ApplicantForm(request.POST, instance=applicant)
        else:
            form_applicant = ApplicantForm(request.POST)

        if form_user.is_valid() and form_applicant.is_valid():
            user = form_user.save()
            if action == 'new':
                app = form_applicant.save(commit=False)
                app.user_id = request.user.id
                app.save()
            else:
                app = form_applicant.save(commit=False)
                if form_social.is_valid():
                    social = form_social.save(commit=False)
                    social.content_type = ContentType.objects.get_for_model(applicant)
                    social.object_id = applicant.id
                    social.save()
                    app.social_network.add(social)
                app.save()
            # return render(request, 'profile/make_profile.html')
            # return get_applicant(app.slug)
            return HttpResponseRedirect('/profile/')
        else:
            form_user = UserForm(request.POST, instance=user)
            form_social = {}
            form_avatar = AvatarForm(request.POST)
            if action != 'new':
                form_social = SocialNetworkForm(request.POST)
                form_applicant = ApplicantForm(request.POST, instance=applicant)
                data = {
                            'form_user': form_user,
                            'form_applicant': form_applicant,
                            'form_social': form_social,
                            'edit_title': True,
                            'avatar' : applicant.avatar,
                            'form_avatar' : form_avatar,
                            'social_networks' : applicant.social_network
                            #'social_networks' : SocialNetworkProfile.objects.all(object_id=request.user.id)
                        }
            else:
                form_applicant = ApplicantForm(request.POST)
                data = { 'form_user': form_user, 'form_applicant': form_applicant, "form_social": form_social}
            return render(request, 'profile/make_profile.html', data)
    else:
        form_user = UserForm(instance=user)
        form_social = {}
        form_avatar = AvatarForm()
        if action != 'new':
            form_social = SocialNetworkForm()
            form_applicant = ApplicantForm(instance=applicant)
            data = {
                        'form_user': form_user,
                        'form_applicant': form_applicant,
                        'form_social': form_social,
                        'edit_title': True,
                        'avatar' : applicant.avatar,
                        'form_avatar' : form_avatar,
                        'social_networks' : applicant.social_network
                        #'social_networks' : SocialNetworkProfile.objects.all(object_id=request.user.id)
                    }
        else:
            form_applicant = ApplicantForm()
            data = {
                        'form_user': form_user,
                        'form_applicant': form_applicant,
                        'form_social': form_social,
                        'edit_title': False,
                        'form_avatar' : form_avatar,
                    }
        return render(request, 'profile/make_profile.html', data)


@login_required
def add_social_network(request):
    applicant = Applicant.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        form_social = SocialNetworkForm(request.POST)

        if form_social.is_valid():
            social = form_social.save(commit=False)
            social.content_type = ContentType.objects.get_for_model(applicant)
            social.object_id = applicant.id
            social.save()
            applicant.social_network.add(social)
            result={    'state': True,
                        'data': {
                            'username' : social.username,
                            'icon_url': social.network.icon_url,
                            'name': social.network.name,
                            'url': social.url,
                            'id': social.id
                        }
                    }
        else:
            result={ 'state': False }

        if request.is_ajax():
            response = JSONResponse(result, {}, response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            profile = Profile.objects.get(user_id=request.user.id)
            return HttpResponseRedirect('/profile/' + profile.slug)


@login_required
def remove_social_network(request):
    applicant = Applicant.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        network = SocialNetworkProfile.objects.get(pk=request.POST.get('network_id'))
        try:
            network.delete()
            result={ 'state': True }
        except SocialNetworkProfile.DoesNotExist:
            result={ 'state': False }

        if request.is_ajax():
            response = JSONResponse(result, {}, response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            profile = Profile.objects.get(user_id=request.user.id)
            return HttpResponseRedirect('/profile/' + profile.slug)


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


@login_required
def offers(request, list_offers):
    template = 'offer/list_offers.html'
    endless_part = 'offer/endless_part.html'
    context = {
        'offers': list_offers,
        'endless_part': endless_part,
    }
    if request.is_ajax():
        template = endless_part
    return render_to_response(template, context, context_instance=RequestContext(request))

def offers_all(request):
    return offers(request, Offer.objects.all)



def get_offer(request, slug):
    offer = Offer.objects.get(slug=slug)
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]
    status = {}
    if ApplicantOffer.objects.filter(offer=offer).filter(applicant=applicant).count() == 0:
        status['apply'] =  "nonapplied"
    else:
        status['apply'] = "applied"

    if applicant.bookmarks.filter(id=offer.id):
        status['bookmark'] = True
    else:
        status['bookmark'] = False
    #TODO : delete slug from view and template
    return render(request, 'offer/show_offer.html', {'offer': offer, 'apply_form': ApplyForm(),'slug': slug, 'user': applicant, 'status': status})


@login_required
def apply_offer(request):
    applicant = Applicant.objects.filter(user_id=request.user.id)[0]

    try:
        if request.method == 'POST':
            form = ApplyForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                data = cd
                offer = Offer.objects.get(id=int(request.POST['offer_id']))
                if ApplicantOffer.objects.filter(offer=offer).filter(applicant=applicant).count() < 1:
                    applyOffer = ApplicantOffer.objects.create(offer=offer, applicant=applicant, content=cd['content'])
                    data = [{
                        'state': True,
                        'id': applyOffer.id,
                        'content': cd['content']
                    }]
            else:
                data = request.POST
        else:
            data = False

    except Offer.DoesNotExist:
        data = False

    if request.is_ajax():
        response = JSONResponse(data, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        #TODO : urls /offer/<id>
        if data != False:
            return HttpResponseRedirect('/offer/get/' + offer.slug)
        else:
            return HttpResponseRedirect('/offers/')


@login_required
def get_applications(request, slug):
    try:
        company = Company.objects.filter(user_id=request.user.id)[0]
        offer = Offer.objects.get(slug=slug)
        applicantsOffer = ApplicantOffer.objects.filter(offer=offer)
        context = {
            'offer': offer,
            'applicantsOffer': applicantsOffer
        }
    except Offer.DoesNotExist:
        return HttpResponseRedirect('/offers/')
    except Company.DoesNotExist:
        return HttpResponseRedirect('/offers/')

    return render(request, 'offer/applications_offer.html', context)


@login_required
def posted_offers(request):
    company = Company.objects.filter(user_id=request.user.id)[0]
    offers = Offer.objects.filter(company=company)
    offers_all = Offer.objects.all()
    applications = ApplicantOffer.objects.all()
    #potentials = []
    #for offer_posted in offers:
    #    potentials.append(potentialApplicant(offer_posted.id))
    #print potentials[0]
    context = {
        'offers': offers,
        'applications': applications,
        #'potentials' : potentials,
    }
    return render(request, 'offer/posted_offers.html', context)


@login_required
def vacancy(request, state, pk):
    try:
        offer = Offer.objects.get(id=pk)
        myself = Company.objects.get(user_id=request.user.id)
        print offer
        if state == 'add':
            Offer.objects.filter(id=pk).update(vacancy=True)
        else:
            Offer.objects.filter(id=pk).update(vacancy=False)
        Offer.objects.get(id=pk).save()
        result = {'state': True }
    except Company.DoesNotExist:
        result = { 'state': False, 'message': 'Company DoesNotExist'}

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        if result['state']:
            return HttpResponseRedirect('/offer/posted_offers')
        else:
            return HttpResponseNotFound('404.html')


@login_required
def get_applications(request, slug):
    try:
        company = Company.objects.filter(user_id=request.user.id)[0]
        offer = Offer.objects.get(slug=slug)
        applicantsOffer = ApplicantOffer.objects.filter(offer=offer)
        context = {
            'offer': offer,
            'applicantsOffer': applicantsOffer
        }
    except Offer.DoesNotExist:
        return HttpResponseRedirect('/offers/')
    except Company.DoesNotExist:
        return HttpResponseRedirect('/offers/')

    return render(request, 'offer/applications_offer.html', context)


def potentialApplicant(pk):
    offer = Offer.objects.get(id=pk)
    offerTag = OfferTaggedItem.objects.filter(Q(content_object__id=pk));

    applicant = []
    for tag in offerTag:
        applicant.extend(SkillsTaggedItem.objects.filter(Q(tag__name=tag.tag.name)).values_list('content_object__owner', flat=True))

    applicants = set(applicant)

    p = Project.objects.filter(owner__id__in=applicant).order_by('owner')
    # p = p.values()

    poids_like = {}
    poids_dispo = {}
    poids_job = {}
    for project in p:
        if poids_like.has_key(project.owner_id):
            pushs = Like.objects.filter(Q(project=project)).count()
            if pushs is not None:
                poids_like[project.owner_id] += pushs * 0.8

            hits = HitCount.objects.filter(object_pk=project.id).aggregate(hits=Sum('hits')).values()[0]
            if hits is not None:
                poids_like[project.owner_id] += hits * 0.2

        else:
            pushs = Like.objects.filter(Q(project=project)).count()
            if pushs is not None:
                poids_like[project.owner_id] = pushs * 0.8

            hits = HitCount.objects.filter(object_pk=project.id).aggregate(hits=Sum('hits')).values()[0]
            if hits is not None:
                poids_like[project.owner_id] += hits * 0.2

        if not poids_dispo.has_key(project.owner_id):
            if project.owner.profession:
                diff = difflib.SequenceMatcher(None, offer.title, project.owner.profession)
                poids_job[project.owner_id] = diff.quick_ratio()

            if project.owner.available == True:
                poids_dispo[project.owner_id] = 1
            else:
                poids_dispo[project.owner_id] = 0

    # trie en fonction du poids
    applicant = []
    poids = {}
    for key in poids_like.keys():
        poids[key] = poids_like[key]/poids_like[max(poids_like)] + poids_dispo[key]*0.5 + poids_job[key]

    for key, value in sorted(poids.iteritems(), key=lambda (k,v): (v,k)):
        applicant.extend("%d" % key)

    return applicant

#         # Ceux qui apparaissent dans tag + metier + Dispo doivent ressortir


#         # Tag des projets avec un minimum de popular :
#         applicant_tags = Applicant.ge

#             # si il on a pas assez de personne on racherche les personnes avec les tags mais moins popular




#         getPopularity on ...

#         # Disponibilit : pour un CDD, CDI....TODO: Ajouter un status a un applicant En recherche + Type de contrat Choix Multiple Ajouter egalement une categorie generale ou plusieures

#         # TODO : Traiter le contenu de l'offre pour y trouver des mots cles.


#         # Trier l'ensemble des gens en fonction de leur popularite



@login_required
def edit_offer(request, model=None, slug=None):

    try:
        company = Company.objects.filter(user_id=request.user.id)[0]
    except Company.DoesNotExist:
        HttpResponseRedirect('/offers/')

    if model == u"edit":
        try:
            offer = Offer.objects.get(slug=slug, company=company)
        except Offer.DoesNotExist:
            return HttpResponseRedirect('/offers/')

        if offer.company == company:
            # applicant qui ont postule
            applicantsOffer = ApplicantOffer.objects.filter(offer_id=offer.id)

            #applicant suceptible de vous interesser

            if request.method == 'POST':
                form = OfferForm(request.POST)
                if form.is_valid():
                    form = OfferForm(request.POST, request.FILES, instance=offer)
                    print form
                    form.save()
                    offer.published = True
                    offer.save()
                    return get_offer(request, offer.slug)
            else:
                if offer.published is False:
                    offer.published = True
                    offer.save()
                    return get_offer(request, offer.slug)
                form = OfferForm(instance=offer)
            return render(request, 'offer/edit_offer.html', {'form': form, 'model': model, 'applicantsOffer': applicantsOffer})
        else:
            return HttpResponseRedirect('/offers/')

    elif model == u"delete":
        if Offer.objects.get(slug=slug).company == company:
            Offer.objects.get(slug=slug).delete()
        return HttpResponseRedirect('/offer/posted_offers')

    elif slug is None :
        if model == u"add":
            form = {}
            if request.method == 'POST':
                form = OfferForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    offer = form.save(commit=False)
                    offer.company = company
                    if '_publish' in request.POST:
                        offer.published = True
                    offer.save()
                    form.save_m2m()
                    return get_offer(request, offer.slug)
            else:
                form = OfferForm()
    return render(request, 'offer/edit_offer.html', {'form': form, 'model': model})


@login_required
def statusApplication(request, model, pk, slug):
    application = ApplicantOffer.objects.get(id=pk)
    offer = application.offer
    applicant = Applicant.objects.filter(slug=slug)
    if model == "read" and application.state is 'SAVE' and application.state is 'FAIL':
        ApplicantOffer.objects.filter(applicant=applicant, id=pk).update(state='READ')
    else:
        if model == "accept" and (ApplicantOffer.objects.filter(offer=offer).count > 1) and application.state is not 'FAIL':
            ApplicantOffer.objects.filter(applicant=applicant, id=pk).update(state='SAVE')
        else:
            if model == "decline" and application.state is not 'SAVE':
                ApplicantOffer.objects.filter(applicant=applicant, id=pk).update(state='FAIL')
    result = {'state': True }

    if request.is_ajax():
        response = JSONResponse(result, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    else:
        if result['state']:
            return HttpResponseRedirect('/offer/posted_offers/')
        else:
            #404
            return HttpResponseNotFound('404.html')


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
            if "school_profile" in request.POST:
                q = request.POST.get("school_profile")
                if q is not None and q != '':
                    education.school_profile = School.objects.filter(id=q)[0]
            education.owner = applicant
            if "id" in request.POST:
                education.id = request.POST.get("id")
            education.save()
            # form.save_m2m()
            if request.is_ajax():
                formData = {
                    'school': education.school,
                    'title': education.title,
                    'start': education.start.strftime("%d %B %Y"),
                    'end': education.end.strftime("%d %B %Y"),
                    'description': education.description,
                    'owner': education.owner,
                    'id': education.id,
                }
                user = request.user
                html = render(request, 'profile/education.html', {'education': formData, 'user': user})
                response = JSONResponse([True,{'data': html.content}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return HttpResponseRedirect('/')
        else:
            if request.is_ajax():
                response = JSONResponse([False,{'data': form.as_p()}], {}, response_mimetype(request))
                response['Content-Disposition'] = 'inline; filename=files.json'
                return response
            else:
                return render(request, 'education/add_education.html', {'form': form})
    else:
        form = EducationForm()
        return render(request, 'education/add_education.html', {'form': form})


@login_required
def edit_education(request, pk):

    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        education = Education.objects.get(id=pk)
        form = EducationForm(instance=education)
        # print form
        state = False
    except Education.DoesNotExist:
        response = JSONResponse(False, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    if request.is_ajax():
        return render(request, 'profile/education_form.html', {'formEducation': form, 'education': education})
    else:
        return HttpResponseRedirect('/profile/')


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

        form = ExperienceForm(request.POST)
        if form.is_valid():
            # cd = form.cleaned_data
            experience = form.save(commit=False)
            experience.owner = applicant
            if "company_profile" in request.POST:
                q = request.POST.get("company_profile")
                if q is not None and q != '':
                    experience.company_profile = Company.objects.filter(id=q)[0]
            # applicant.experiences.create(company=experience.company, title=experience.title, city=experience.city, start=experience.start, end=experience.end, details=experience.details)
            if "id" in request.POST:
                experience.id = request.POST.get("id")
            experience.save()
            # form.save_m2m()
            if request.is_ajax():
                formData = {
                    'company' : experience.company,
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
def edit_experience(request, pk):

    try:
        applicant = Applicant.objects.filter(user_id=request.user.id)[0]
        experience = Experience.objects.get(id=pk)
        form = ExperienceForm(instance=experience)
        # print form
        state = False
    except Experience.DoesNotExist:
        response = JSONResponse(False, {}, response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    if request.is_ajax():
        return render(request, 'profile/experience_form.html', {'formExperience': form, 'experience': experience})
    else:
        return HttpResponseRedirect('/profile/')


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
@login_required
def get_applicant(request, slug):
    # myself = get_my_self(request)
    try:
        profile = Applicant.objects.get(slug=slug)
    except Applicant.DoesNotExist:
        return HttpResponseRedirect("/")

    projects = Project.objects.filter(Q(owner=profile, published=True) | Q(participant__in=[profile], published=True)).distinct()
    following = Follow.objects.filter(follower__user_id=request.user.id, following__user_id=profile.user_id)
    followingNb = Follow.objects.filter(following__id=profile.id).count()
    followersNb = Follow.objects.filter(follower__id=profile.id).count()
    pushs = Like.objects.filter(Q(project__owner=profile.user) | Q(project__participant__in=[profile])).count()
    views = HitCount.objects.filter(content_type=ContentType.objects.get_for_model(Project), object_pk__in=projects.values_list('pk', flat=True)).aggregate(hits=Sum('hits'))
    tags = SkillsTag.objects.filter(Q(skills__content_object__owner=profile)).annotate(num_times=Count('skills__content_object__skillstaggeditem')).order_by('-num_times')[:3]
    formEducation = EducationForm()
    formExperience = ExperienceForm()
    #TODO : delete slug from view and template
    context = {
        'profile': profile,
        'following': following,
        'stats': {'followers': followersNb, 'following': followingNb, 'pushs': pushs, 'tags': tags, 'views': views },
        'projects': projects,
        'formEducation': formEducation,
        'formExperience': formExperience,
        # 'pushs': Applicant.objects.push_user()
        'pushs': Project.objects.push_user(profile.user_id),
        'coverImageForm' : CoverImageForm()
    }
    return render(request, 'profile/profile_applicant.html', context)


def update_applicant(request):
    myself = get_my_self(request)

    if request.method == 'POST':
        formApplicant = ApplicantForm(request.POST, instance=myself)

        if formApplicant.is_valid():
            formApplicant.save()
            return HttpResponseRedirect('/profile/')
    else:
        formApplicant = ApplicantForm(instance=myself)

    context = {
        'profile': myself,
        'formApplicant': formApplicant,
    }
    return render(request, 'profile/profile_applicant_update.html', context)


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


def get_companies(request):
    if(request.method == 'GET'):
        term = ""
        if 'term' in request.GET:
            term = request.GET["term"]
        else:
            raise
        companies = Company.objects.filter(name__startswith=term).values_list('id','name', flat=False)

    choices = [{"id": l[0], "value": l[1]} for l in set(companies)]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def get_school(request, slug):
    school = School.objects.get(slug=slug)
    return render_to_response('profile/profile_school.html', {'profile': school, 'slug': slug})


def get_schools(request):
    if(request.method == 'GET'):
        term = ""
        if 'term' in request.GET:
            term = request.GET["term"]
        else:
            raise
        schools = School.objects.filter(name__startswith=term).values_list('id','name', flat=False)

    choices = [{"id": l[0], "value": l[1]} for l in set(schools)]
    response = JSONResponse(choices, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


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


def get_follow_profiles(request, slug, type_url='followers'):
    if type_url == 'followers':
        feedbacks = list(Follow.objects.filter(follower__name=slug).values_list('id', flat=True))
    else:
        feedbacks = list(Follow.objects.filter(following__name=slug).values_list('id', flat=True))

    profiles = Profile.objects.filter(pk__in=feedbacks)

    template = 'network/followers.html'
    endless_part = 'network/endless_followers.html'
    context = {
        'profiles': profiles,
        'slug': slug,
        'endless_part': endless_part,
    }

    if request.is_ajax():
        template = endless_part

    return render_to_response(template, context, context_instance=RequestContext(request))


@login_required
def show_dashboard(request):

    user = User.objects.get(pk=request.user.id)
    profile = Applicant.objects.get(user_id=request.user.id)
    projects = Project.objects.filter(Q(owner=profile, published=True) | Q(participant__in=[profile], published=True))
    comments = Comment.objects.filter(project__owner=profile).count
    pushs = Like.objects.filter(Q(project__owner=profile.user) | Q(project__participant__in=[profile])).count()
    views = HitCount.objects.filter(content_type=ContentType.objects.get_for_model(Project), object_pk__in=projects.values_list('pk', flat=True)).aggregate(hits=Sum('hits'))
    tags = SkillsTag.objects.filter(Q(skills__content_object__owner=profile)).annotate(num_times=Count('skills__content_object__skillstaggeditem')).order_by('-num_times')[:3]
    following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
    # print following
    notifications = Notification.objects.filter(actor_object_id__in=following)
    unread = notifications.unread()

    projects = Project.objects.filter(published=True, owner__in=following)[:3]

    applications = ApplicantOffer.objects.filter(applicant=profile)[:3]

    context = {
        'profile': profile,
        'stats': {'pushs': pushs, 'tags': tags, 'views': views, 'comments' : comments },
        'projects': projects,
        'notifications' : notifications[:7],
        'unread_nb' : int(0+unread.count()),
        'pushs': Project.objects.push_user(profile.user_id),
        'projects' : projects,
        'applications' : applications
    }
    return render_to_response('notifications/dashboard.html', context, context_instance=RequestContext(request))


@login_required
def show_notifications(request):
    # print request.user.id
    user = User.objects.get(pk=request.user.id)
    profile = Applicant.objects.get(user_id=request.user.id)
    following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
    # print following
    # notifications2 = Notification.objects.filter(actor_object_id__in=following).extra({'timestamp' : "date(timestamp)"}).values('timestamp').annotate(created_count=Count('id'))
    notifications = Notification.objects.filter(actor_object_id__in=following)
    applications = ApplicantOffer.objects.filter(applicant=profile)

    unread = notifications.unread()

    # for key,group in itertools.groupby(notifications, key=lambda x: x[1][:11]):
    #    print key
    #    for element in group:
    #         print '   ', element

    projects = Project.objects.filter(published=True, owner__in=following)[:3]

    context = {
        'profile': profile,
        'notifications' : notifications[:15],
        'unread_nb' : int(0+unread.count()),
        'applications' : applications
    }
    return render_to_response('notifications/list.html', context, context_instance=RequestContext(request))


@login_required
def notifications_mark_as_read(request):
    user = User.objects.get(pk=request.user.id)
    following = Follow.objects.filter(follower__user_id=user.id).values('following_id')
    notifications = Notification.objects.filter(actor_object_id__in=following)
    notifications.mark_all_as_read()

    response = JSONResponse(True, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


@login_required
def has_visited(request):
    myself = Profile.objects.get(user_id=request.user.id)
    myself.first_visit = True
    myself.save()
    response = JSONResponse(True, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


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
        data = [{
            'name': f.name,
            'url': settings.MEDIA_URL + "upload/images/project/" + f.name.replace(" ", "_"),
            'thumbnail_url': settings.MEDIA_URL + "upload/images/project/" + f.name.replace(" ", "_"),
            'delete_url': reverse('upload-delete', args=[self.object.id]),
            'delete_type': "DELETE"
            }]
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
