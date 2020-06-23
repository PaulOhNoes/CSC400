from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Drive)
admin.site.register(Organization)
admin.site.register(Donation)
admin.site.register(DonationItem)
admin.site.register(Notifications)