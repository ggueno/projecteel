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
