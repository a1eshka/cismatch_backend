from django.urls import path
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from . import api
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='rest_register'),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    path('user/<uuid:user_id>/', api.user_info, name='user_info'),
    path('user/<uuid:user_id>/upload-background/', api.upload_background, name='upload_background'),
    path('user/<uuid:user_id>/delete-background/', api.delete_background, name='delete_background'),
    path('promocode/activate/', api.activate_promo_code, name='activate_promo_code'),
    path('link-steam/', link_steam, name='link_steam'),
    path('user/<uuid:user_id>/inventory/', api.get_inventory, name='inventory'),
    path('inventory/steam/prices/', api.get_csgo_market_prices, name='get_steam_price'),
    path('create-payment-server/', api.create_payment_server, name='create_payment_server'),
    path('create-payment/', api.create_payment, name='create_payment'),
    path('webhook/', api.payment_webhook, name='payment_webhook'),
    path("create-payout/", api.create_payout, name="create_payout"),
    path("payout-webhook/", api.payout_webhook, name="payout_webhook"),
    path("get-sbp-banks/", api.get_sbp_banks, name="get_sbp_banks"),
    path('sell-item/', api.sell_item, name='sell_item'),
    path('user/buying-orders/', api.user_orders_list, name='user-orders'),
]