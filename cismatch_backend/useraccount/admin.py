from django.contrib import admin

from .models import PromoCode, PromoCodeHistory, User, SkinBuyOrder

admin.site.register(User)
admin.site.register(PromoCode)
admin.site.register(PromoCodeHistory)
admin.site.register(SkinBuyOrder)