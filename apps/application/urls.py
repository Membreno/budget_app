from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^reset_bank$', views.reset_bank),
    url(r'^reset_bills$', views.reset_bills),
    url(r'^pay/(?P<id>[0-9]+)$', views.pay),
    url(r'^decrease$', views.decrease),
    url(r'^increase$', views.increase),
    url(r'^add_funds$', views.add_funds),
    url(r'^subtract_funds$', views.subtract_funds),
    url(r'^delete/(?P<id>[0-9]+)$', views.delete),
    url(r'^process_edit/(?P<id>[0-9]+)$', views.process_edit),
    url(r'^bills/(?P<id>[0-9]+)/edit$', views.edit),
    url(r'^add_bill$', views.add_bill),
    url(r'^bills/new$', views.new_bill),
    url(r'^logout$', views.logout),
    url(r'^login_user$', views.login_user),
    url(r'^add_user$', views.add_user),
    url(r'^dashboard$', views.dashboard),
    url(r'^$', views.index),
]
