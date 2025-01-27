from django.urls import re_path

from core_apps.bid.views.views import BidView, BidManagementView, BidSummaryView

urlpatterns = [
    re_path(r'^bid/?(?P<object_id>[\d]+)?/$', BidView.as_view(), name='user'),
    re_path(r'^bid-summary/?$', BidSummaryView.as_view(), name='user'),
    re_path(r'^bid-manage/?(?P<object_id>[\d]+)?/$', BidManagementView.as_view(), name='user'),

]
