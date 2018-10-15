from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register$',views.register,name='register'),
    url(r'^register_handle$',views.register_handle,name='register_handle'),
    url(r'^register_exist$',views.register_exist,name='register_exist'),

    url(r'^login$',views.login,name='login'),
    url(r'^login_handle$', views.login_handle, name='login_handle'),
    url(r'^validate_code$', views.validate_code, name='validate_code'),

    url(r'^forget$', views.forget, name='forget'),
    url(r'^forget_handle$',views.forget_handle,name='forget_handle'),
    url(r'^active/(?P<token>.*)$', views.active, name='active'),

    url(r'^reset$', views.reset, name='reset'),
    url(r'^reset_handle$', views.reset_handle, name='reset_handle'),

    url(r'^index$', views.index, name='index'),

    url(r'^info$',views.info,name='info'),
    url(r'^order$',views.order,name='order'),
    url(r'^site$',views.site,name='site'),
]