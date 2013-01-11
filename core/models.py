from django.db import models
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
    slug = models.SlugField(max_length=100)
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
    slug = models.SlugField(max_length=150)

    def __unicode__(self):
        return "%s" % (self.name)


class Applicant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=False)
    search_location = models.CharField(max_length=100)
    social_network = models.ManyToManyField(SocialNetwork)

    def __unicode__(self):
        return "%s %s, %s" % (self.first_name, self.last_name, profession)


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


class Skills(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)

    def __unicode__(self):
        return "%s" % (self.name)


class CategoryOffer(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    description = models.TextField(blank=True, help_text="Optional")

    def __unicode__(self):
        return "%s" % (self.name)


class Tag(models.Model):
    name = models.CharField(max_length=30)
    slug = models.CharField(max_length=30)

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
    slug = models.SlugField(max_length=150)
    company = models.ForeignKey(Company)
    location = models.CharField(max_length=100, blank=False, null=False)
    contract = models.CharField(max_length=2, choices=OFFER_TYPE, default='CDI')
    salary = models.IntegerField(blank=True, null=True)
    publish_date = models.DateField(auto_now=True, auto_now_add=True)
    content = models.TextField()
    tags = models.ManyToManyField(Tag)
    reference = models.CharField(max_length=30, blank=True, null=True)
    category = models.ManyToManyField(CategoryOffer)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.company, self.location)

# class Project(models.Model):
#     title = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100)
#     publish_date = models.DateField(auto_now=True, auto_now_add=True)
#     content = models.TextField()

