from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^snippet/(?P<snippet_id>\d+)$', views.snippet, name='snippet'),
    url(r'^languages/(?P<lang>\w+)$', views.languages, name='languages'),
    url(r'^search$', views.search, name='search'),

    # signin, signup, contribute page
    url(r'^signin$', views.signin, name='signin'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^contribute$', views.contribute, name='contribute'),

    url(r'^profile/(?P<snippet_id>\w+)$', views.profile, name='profile'),
    url(r'^favorites/(?P<fav_user_id>\d+)/(?P<snippet_id>\w+)$', views.favorites, name='favorites'),
    url(r'^remove_favorite/(?P<id>\d+)$', views.remove_favorite, name='remove_favorite'),
    url(r'^add_favorite/(?P<snippet_id>\d+)/(?P<page>\w+)$', views.add_favorite, name='add_favorite'),
    url(r'^change_status$', views.change_status, name='change_status'),
    url(r'^post_comment$', views.post_comment, name='post_comment'),

    # URLS FOR PROFILE ACCOUNTS
    url(r'^register$', views.register, name='register'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^login$', views.login, name='login'),
    url(r'^update_personal$', views.update_personal, name='update_personal'),
    url(r'^update_password$', views.update_password, name='update_password'),
    url(r'^reset_password$', views.reset_password, name='reset_password'),
    url(r'^reset_new_password$', views.reset_new_password, name='reset_new_password'),

    url(r'^send_reset_email$', views.send_reset_email, name='send_reset_email'),
    url(r'^check_pin/(?P<pin>\d+)$', views.check_pin, name='check_pin'),

    # process contribution
    url(r'^process_contribute$', views.process_contribute, name='process_contribute'),
    
]