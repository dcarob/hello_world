from django.conf.urls import url
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.auth.views import login

urlpatterns= [
    url(r'^profile/$',views.userprofile,name='profile'),
    url(r'^register/$',views.register.as_view(),name='register'),
    url(r'^login/$',views.logout,name='login'),
    url(r'^edit/$',views.editprofile,name='edit'),
    url(r'^groups/$', views.ProfileList.as_view(), name='profile-list'),
    url(r'^newgroup/$',views.GroupGroupMemberCreate.as_view(),name='GroupGroupMemberCreate'),
    url(r'^newgroupexcel/$',views.loadExcel,name='newexcelgroup'),
    url(r'^chooseSheet/$',views.chooseSheet,name='chooseSheet'),
    url(r'^pickColumns/$',views.pickcolumns,name='pickcolumns'),
    url(r'^formset_excel/$',views.formset_excel.as_view(),name='formset_excel'),

    url(r'^$', login, {'template_name': 'pfapp/login.html'}, name='login'),
    url(r'^edit/password/$',views.change_password,name='changepassword'),
    url(r'^prueba/$',views.codificacion ,name='photo'),
    url(r'^newCod/$',views.codificacionEdit ,name='editCod'),

    url(r'^(?P<group_grupo>[0-9]+)/$',views.GroupList, name='detail'),
    url(r'^upload/$', views.GroupPhotoEntry.as_view(), name='upload-photo'),
    url(r'^uppicture/$', views.pictureUpload, name='picture-upload'),
    url(r'^attendance/$',views.attendanceGenerator ,name='attendance'),
    url(r'^editgroup/$',views.editGroup.as_view(),name='editgroup'),
    url(r'^delete/(?P<part_id>.*)/$', views.Delete, name='delete_view'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)