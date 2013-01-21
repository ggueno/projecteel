from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from taggit.models import (TaggedItemBase, GenericTaggedItemBase, TaggedItem,
    TagBase, Tag)
from taggit_autosuggest.managers import TaggableManager
from sorl.thumbnail import get_thumbnail
from django.core.files.base import ContentFile
# from utils import Address, Country


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


class SocialNetwork(models.Model):
    name = models.CharField(max_length=100, blank=False)
    url = models.URLField(blank=False)

    def __unicode__(self):
        return "%s" % (self.name)


class Profile(models.Model):
    user = models.ForeignKey(User)
    date_signin = models.DateField(auto_now=True, auto_now_add=True)
    avatar = models.ImageField(upload_to="upload/images/avatar", blank=False, null=False)
    description = models.TextField(blank=False, null=False)

    def save(self, *args, **kwargs):
        if not self.id:
            super(Profile, self).save(*args, **kwargs)
            resized = get_thumbnail(self.avatar, "200x200")
            self.avatar.save(resized.name, ContentFile(resized.read()), True)
        super(Profile, self).save(*args, **kwargs)

class Company(Profile):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name')
    url = models.URLField(blank=True, null=True)
    #django enum : TODO
    #status = models
    address = models.ManyToManyField(Address, blank=False, null=False)
    social_network = models.ManyToManyField(SocialNetwork, blank=False, null=False)

    def __unicode__(self):
        return "%s" % (self.name)


class School(Profile):
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    def __unicode__(self):
        return "%s" % (self.name)



class Applicant(Profile):
    pseudo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    slug = AutoSlugField(populate_from=lambda instance: u'%s-%s' % (instance.first_name, instance.last_name))
    profession = models.CharField(max_length=100, blank=False, null=False)
    search_location = models.CharField(max_length=100, blank=False, null=False)
    social_network = models.ManyToManyField(SocialNetwork, blank=False, null=False)

    def __unicode__(self):
        return "%s %s, %s" % (self.first_name, self.last_name, self.profession)


class Experience(models.Model):
    company = models.ForeignKey(Company)
    title = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    start = models.DateField(blank=False, null=False)
    end = models.DateField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.start)


class Education(models.Model):
    school = models.ForeignKey(School)
    start = models.DateField(blank=True, null=False)
    end = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=False, null=False)

    def __unicode__(self):
        return "%s %s %s" % (self.title, str(self.school), str(self.start))


class CommonTag(TagBase):
    pass


class CommonTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(CommonTag, related_name="common")



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
    contract = models.CharField(max_length=2, choices=OFFER_TYPE, default='CDI', blank=True)
    salary = models.IntegerField(blank=True, null=True)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField()
    tags = TaggableManager(verbose_name="CommonTag", through=CommonTaggedItem, blank=True)
    reference = models.CharField(max_length=30, blank=True, null=True)
    category = models.ManyToManyField(CategoryOffer, blank=True, null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.location)


class Media(models.Model):
    title = models.CharField(max_length=500)
    slug = AutoSlugField(populate_from='title', unique=True)
    description = models.TextField()

    def __unicode__(self):
        return "%s %s" % (self.title, self.description)


class Image(Media):
    image = models.ImageField(upload_to='upload/images/project')


class VideoLink(Media):
    content = models.TextField()


class SkillsTag(TagBase):
    pass


class SkillsTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(SkillsTag, related_name="skills")


class CategoryTag(TagBase):
    parent = models.ForeignKey('self', null=True, blank=True)


class CategoryTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(CategoryTag, related_name="categories")


class EquipmentTag(TagBase):
    pass


class EquipmentTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(EquipmentTag, related_name="equipment")


class Project(models.Model):
    PROJECT_STATE = (
        ('IP', "En Cours"),
        ('FN', "Termine"),
    )

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='title', unique=True)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    published = models.BooleanField(default=True)
    content = models.TextField()
    #TO DO : Multiple list
    period = models.IntegerField(blank=True, null=True)
    state = models.CharField(blank=True, max_length=2, choices=PROJECT_STATE, default='FINISHED')
    cadre = models.CharField(blank=True, max_length=100)
    location = models.CharField(blank=True, max_length=100)
    categories = TaggableManager(verbose_name="CategoryTag", through=CategoryTaggedItem, blank=True)
    skills = TaggableManager(verbose_name="SkillsTag", through=SkillsTaggedItem, blank=True)
    tags = TaggableManager(verbose_name="CommonTag", through=CommonTaggedItem, blank=True)
    equipments = TaggableManager(verbose_name="EquipmentTag", through=EquipmentTaggedItem, blank=True)
    images = models.ManyToManyField(Image, blank=True, null=True)
    videos = models.ManyToManyField(VideoLink, blank=True, null=True)

    view = models.IntegerField(blank=False, null=False, default=0)

    owner = models.ForeignKey(Applicant, related_name="Owner")
    participant = models.ManyToManyField(Applicant, blank=True, null=True)


class ApplicantOffer(models.Model):
    applicant = models.ForeignKey(Applicant)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField(max_length=500)
    offer = models.ForeignKey(Offer)


class Like(models.Model):
    profile = models.ForeignKey(Profile)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    project = models.ForeignKey(Project)


class Follow(models.Model):
    company = models.ForeignKey(Company)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    applicant = models.ForeignKey(Applicant)
