from django.db import models
from autoslug import AutoSlugField
#from taggit.managers import TaggableManager
from taggit.models import (TaggedItemBase, GenericTaggedItemBase, TaggedItem,
    TagBase, Tag)
from taggit_autosuggest.managers import TaggableManager
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


class Company(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name')
    about = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    #django enum : TODO
    #status = models
    address = models.ManyToManyField(Address)
    social_network = models.ManyToManyField(SocialNetwork)

    def __unicode__(self):
        return "%s" % (self.name)


class School(models.Model):
    name = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from='name')

    def __unicode__(self):
        return "%s" % (self.name)


class Applicant(models.Model):
    pseudo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from=lambda instance: u'%s-%s' % (instance.first_name, instance.last_name))
    profession = models.CharField(max_length=100, blank=False)
    search_location = models.CharField(max_length=100)
    social_network = models.ManyToManyField(SocialNetwork)

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
    description = models.TextField(max_length=500)

    def __unicode__(self):
        return "%s %s %s" % (self.title, str(self.school), str(self.start))





class CategoryOffer(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    description = models.TextField(blank=True, help_text="Optional")

    def __unicode__(self):
        return "%s" % (self.name)


class Tagg(models.Model):
    name = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='name', unique=True)

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
    contract = models.CharField(max_length=2, choices=OFFER_TYPE, default='CDI')
    salary = models.IntegerField(blank=True, null=True)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField()
    tags = models.ManyToManyField(Tagg)
    reference = models.CharField(max_length=30, blank=True, null=True)
    category = models.ManyToManyField(CategoryOffer)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.location)


class Equipment(models.Model):
    title = models.CharField(max_length=500)
    slug = AutoSlugField(populate_from='title', unique=True)
    description = models.CharField(max_length=500)

    def __unicode__(self):
        return "%s %s" % (self.title, self.description)


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
    tag = models.ForeignKey(SkillsTag, related_name="ee")


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
    skills = TaggableManager(verbose_name="SkillsTag", through=SkillsTaggedItem, blank=True)
    equipments = models.ManyToManyField(Equipment, blank=True, null=True)
    images = models.ManyToManyField(Image, blank=True, null=True)
    videos = models.ManyToManyField(VideoLink, blank=True, null=True)
    like = models.IntegerField(blank=False, null=False, default=0)
    view = models.IntegerField(blank=False, null=False, default=0)

    def get_tag_names(self):
        return [skills.name for skills in Tag.objects.get_for_object(self)]
