from django.contrib import admin
from core.models import *
from sorl.thumbnail.admin import AdminImageMixin

admin.site.register(Country)
admin.site.register(Address)
admin.site.register(SocialNetwork)
admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(School)
admin.site.register(Experience)


class ApplicantAdmin(AdminImageMixin, admin.ModelAdmin):
    pass

admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Education)
admin.site.register(SkillsTag)
admin.site.register(CommonTag)
admin.site.register(EquipmentTag)
admin.site.register(CategoryOffer)
admin.site.register(Offer)
admin.site.register(Media)
admin.site.register(ImageProject)
admin.site.register(EmbedContent)
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(ApplicantOffer)
admin.site.register(Like)
admin.site.register(Follow)
