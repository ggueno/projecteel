from django.db import models


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


class Company(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    about = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    #django enum : TODO
    #status = models
    address = models.ManyToManyField(Address)
    social_network = models.ManyToManyField(SocialNetwork)


class School(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)


class Applicant(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=False)
    search_location = models.CharField(max_length=100)
    social_network = models.ManyToManyField(SocialNetwork)


class Experience(models.Model):
    company = models.OneToOneField(Company)
    city = models.CharField(max_length=100)
    start = models.DateField(blank=False, null=False)
    end = models.DateField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
