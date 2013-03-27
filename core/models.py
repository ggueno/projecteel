from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from taggit.models import (TaggedItemBase, GenericTaggedItemBase, ItemBase, TaggedItem,
    TagBase, Tag)
from taggit_autosuggest.managers import TaggableManager
from sorl.thumbnail import get_thumbnail, fields
from django.core.files.base import ContentFile
from django.core.validators import MaxLengthValidator
from elsewhere.models import SocialNetworkProfile
# from utils import Address, Country
from hitcount.models import *
from tinymce import models as tinymce_models
from django.db.models import Q, Count

class Country(models.Model):
    """Model for countries"""
    iso_code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=45, blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ["name", "iso_code"]


class Address(models.Model):
    """Model to store addresses for accounts"""
    address_line1 = models.CharField("Address line 1", max_length=45)
    address_line2 = models.CharField("Address line 2", max_length=45,
        blank=True)
    postal_code = models.CharField("Postal Code", max_length=10)
    city = models.CharField(max_length=50, blank=False)
    country = models.ForeignKey(Country, blank=False)

    def __unicode__(self):
        return "%s, %s" % (self.city,
                              str(self.country))

    class Meta:
        verbose_name_plural = "Addresses"
        unique_together = ("address_line1", "address_line2", "postal_code",
                           "city", "country")


class Profile(models.Model):
    slug = AutoSlugField(populate_from=lambda instance: u'%s' % (instance.name), unique=True, always_update=True)
    user = models.ForeignKey(User, blank=True, null=True)
    date_signin = models.DateField(auto_now=True, auto_now_add=True)
    name = models.CharField(max_length=150)
    avatar = fields.ImageField(upload_to="upload/images/avatar", blank=True, null=True)
    cover_image = fields.ImageField(upload_to="upload/images/cover_image", blank=True, null=True)
    cover_image_top = models.IntegerField(blank=True, null=True, default=0)
    description = models.TextField(blank=False, null=False)
    url = models.URLField(blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         super(Profile, self).save(*args, **kwargs)
    #         //resized = get_thumbnail(self.avatar, "180x180")
    #         //self.avatar.save(resized.name, ContentFile(resized.read()), True)
    #     super(Profile, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        print self.cover_image
        print kwargs
        super(Profile, self).save(*args, **kwargs)

        this = Profile.objects.get(id=self.id)

        if this.cover_image:
            change = True
            if this.cover_image != self.cover_image:
                this.cover_image.delete(save=False)
        else:
            print "NO COVER"

        if this.avatar:
            if this.avatar != self.avatar:
                this.avatar.delete(save=False)
        else:
            print "NO AVATAR"
        super(Profile, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % (self.name)


class Company(Profile):
    #django enum : TODO
    address = models.ManyToManyField(Address, blank=True, null=True)
    social_network = models.ManyToManyField(SocialNetworkProfile, blank=True, null=True)

    def __unicode__(self):
        return "%s" % (self.name)


class School(Profile):

    def __unicode__(self):
        return "%s" % (self.name)


class Applicant(Profile):
    profession = models.CharField(max_length=100, blank=False, null=False)
    search_location = models.CharField(max_length=100, blank=True, null=True)
    social_network = models.ManyToManyField(SocialNetworkProfile, blank=True, null=True)
    educations = models.ManyToManyField('Education', blank=True, null=True)
    experiences = models.ManyToManyField('Experience', blank=True, null=True)
    bookmarks = models.ManyToManyField('Offer', blank=True, null=True)
    available = models.NullBooleanField(null=True)

    def __unicode__(self):
        return "%s, %s" % (self.name, self.profession)

    @models.permalink
    def get_absolute_url(self):
       return ('applicant_view', [str(self.slug)])


    def get_tags(self):
        return SkillsTag.objects.filter(Q(skills__content_object__owner=self)).annotate(num_times=Count('skills__content_object__skillstaggeditem')).order_by('-num_times')

    @classmethod
    def get_tags_num_for(term):
        return SkillsTaggedItem.objects.filter(Q(tag__name="photoshop")).values('content_object__owner').annotate(num_times=Count('content_object__owner')).order_by('-num_times')




class Experience(models.Model):
    company_profile = models.ForeignKey(Company, blank=True, null=True)
    company = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    start = models.DateField(blank=False, null=False)
    end = models.DateField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(Applicant, related_name='experience')
    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.start)


class Education(models.Model):
    school_profile = models.ForeignKey(School, blank=True, null=True)
    school = models.CharField(max_length=150, blank=True, null=True)
    start = models.DateField(blank=False, null=False)
    end = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=False, null=False)
    owner = models.ForeignKey(Applicant, related_name='education')
    #domaine

    def __unicode__(self):
        return "%s %s %s" % (self.title, str(self.school), str(self.start))


class OfferTag(TagBase):
    pass

class OfferTaggedItem(ItemBase):
    tag = models.ForeignKey(OfferTag, related_name="offerTags")
    content_object = models.ForeignKey('Offer')

    # Appears one must copy this class method that appears in both TaggedItemBase and GenericTaggedItemBase
    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()




class CommonTag(TagBase):
    pass


class CommonTaggedItem(ItemBase):
    tag = models.ForeignKey(CommonTag, related_name="common")
    content_object = models.ForeignKey('Project')

    # Appears one must copy this class method that appears in both TaggedItemBase and GenericTaggedItemBase
    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class CategoryOffer(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    description = models.TextField(blank=True, help_text="Optional")

    def __unicode__(self):
        return "%s" % (self.name)


class Offer(models.Model):
    OFFER_TYPE = (
        ('INTERN', "Stage"),
        ('APPRENTICE', "Apprentissage"),
        ('CDD', "CDD"),
        ('CDI', "CDI"),
    )

    title = models.CharField(max_length=150, blank=False, null=False)
    slug = AutoSlugField(populate_from='title', unique=True)
    company = models.ForeignKey(Company)
    location = models.CharField(max_length=100, blank=False, null=False)
    start = models.DateField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    contract = models.CharField(max_length=10, choices=OFFER_TYPE, default='CDI', blank=True)
    salary = models.IntegerField(blank=True, null=True)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = tinymce_models.HTMLField()
    tags = TaggableManager(verbose_name="Tag", through=OfferTaggedItem, blank=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    category = models.ManyToManyField(CategoryOffer, blank=True, null=True)
    vacancy = models.BooleanField(default=True)
    published = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.location)

    @models.permalink
    def get_absolute_url(self):
       return ('offer_view', [str(self.slug)])


class Media(models.Model):
    title = models.CharField(max_length=500, blank=True, null=True)
    slug = AutoSlugField(populate_from='title', unique=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s %s" % (self.title, self.description)


class ImageProject(Media):
    image = models.ImageField(upload_to='upload/images/project')
    project = models.ForeignKey('Project', related_name='images', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now=True)

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.image.name
        super(ImageProject, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.image.delete(False)
        super(ImageProject, self).delete(*args, **kwargs)


class EmbedContent(Media):
    content = models.TextField()
    project = models.ForeignKey('Project', related_name='embed', blank=True, null=True)


class SkillsTag(TagBase):
    pass


class SkillsTaggedItem(ItemBase):
    tag = models.ForeignKey(SkillsTag, related_name="skills")
    content_object = models.ForeignKey('Project')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class CategoryTag(TagBase):
    parent = models.ForeignKey('self', null=True, blank=True)
    class Meta:
        verbose_name = "CategoryTag"
        verbose_name_plural = "CategoryTags"

    @models.permalink
    def get_absolute_url(self):
        return ('project-search')


class CategoryTaggedItem(ItemBase):
    tag = models.ForeignKey(CategoryTag, related_name="categories")
    content_object = models.ForeignKey('Project')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class EquipmentTag(TagBase):
    class Meta:
        verbose_name = "EquipmentTag"
        verbose_name_plural = "EquipmentTags"


class EquipmentTaggedItem(ItemBase):
    tag = models.ForeignKey(EquipmentTag, related_name="equipments")
    content_object = models.ForeignKey('Project')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()

class ProjectManager(models.Manager):
    def like_count(self):
        return self.like.count()

    def push_user(self, id_applicant):
        nb_push = 0
        projects = self.filter(owner_id=id_applicant)
        for project in projects:
            nb_push = project.likes.count()
        return nb_push


class Project(models.Model):
    PROJECT_STATE = (
        ('IP', "En Cours"),
        ('FN', "Termine"),
    )

    PROJECT_CADRE = (
        ('SCO', "Etudes"),
        ('PRO', "Professionnel"),
        ('PER', "Personnel"),
        ('ASO', "Associatif"),
    )

    PROJECT_DURATION = [
        (1, "1 jour"),
        (2, "1 semaine"),
        (3, "2 a 3 semaines"),
        (4, "1 mois"),
        (5, "3 mois"),
        (6, "6 mois et plus"),
    ]

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='title', unique=True, always_update=True)
    publish_date = models.DateField(auto_now_add=True)
    published = models.BooleanField(default=True)
    content = models.TextField()
    #TO DO : Multiple list
    period = models.IntegerField(blank=True, null=True, choices=PROJECT_DURATION)
    state = models.CharField(blank=True, max_length=2, choices=PROJECT_STATE, default='')
    cadre = models.CharField(blank=True, max_length=100, choices=PROJECT_CADRE, default='')
    location = models.CharField(blank=True, max_length=100)
    categories = TaggableManager(verbose_name="Category", through=CategoryTaggedItem, blank=True)
    skills = TaggableManager(verbose_name="Skills", through=SkillsTaggedItem, blank=True)
    tags = TaggableManager(verbose_name="Tags", through=CommonTaggedItem, blank=True)
    equipments = TaggableManager(verbose_name="Equipments", through=EquipmentTaggedItem, blank=True)
    thumbnail = fields.ImageField(upload_to='upload/images/project', blank=True, null=True)
    view = models.IntegerField(blank=False, null=False, default=0)
    hits = generic.GenericRelation(HitCount, content_type_field='content_type', object_id_field="object_pk")

    owner = models.ForeignKey(Applicant, related_name="project_owner")
    participant = models.ManyToManyField(Applicant, blank=True, null=True)

    objects = ProjectManager()

    def __unicode__(self):
        return "%s" % (self.title)

    def save(self):
        new = False
        if self.pk is None:
            new = True
        super(Project, self).save()
        if new == True:
            t1 = HitCount(content_object=self, object_pk=self.pk)
            t1.save()

    @property
    def views(self):
        # return self.hits.all()[0].hits
        return HitCount.objects.get(content_type=ContentType.objects.get_for_model(self), object_pk=self.id).hits


    @models.permalink
    def get_absolute_url(self):
        return ('project_view', [str(self.slug)])


class Comment(models.Model):
    project = models.ForeignKey(Project, related_name="comments")
    profile = models.ForeignKey(Profile)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField(validators=[MaxLengthValidator(500)])

    def __unicode__(self):
        return "%s %s" % (self.profile, self.content)


class ApplicantOffer(models.Model):
    APPLICANTOFFER_STATE = (
        ('POST', "Postulee"),
        ('READ', "Lue"),
        ('SAVE', "Retenue"),
        ('FAIL', "Rejetee"),
    )

    applicant = models.ForeignKey(Applicant)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField(max_length=500)
    offer = models.ForeignKey(Offer)
    state = models.CharField(blank=True, max_length=100, choices=APPLICANTOFFER_STATE, default='POST')


class Like(models.Model):
    profile = models.ForeignKey(Profile)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    project = models.ForeignKey(Project, related_name="likes")


class Follow(models.Model):
    follower = models.ForeignKey(Profile, related_name="followers")
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    following = models.ForeignKey(Profile, related_name="followings")
