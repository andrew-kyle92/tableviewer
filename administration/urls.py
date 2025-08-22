from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdministrationView.as_view(), name='index'),
    # Group URLs
    path('groups/', views.GroupsView.as_view(), name='groups'),
    path('add-group/', views.AddGroupView.as_view(), name='add-group'),
    path('edit-group/<int:pk>/', views.EditGroupView.as_view(), name='edit-group'),
    path('view-group/<int:pk>/', views.ViewGroupView.as_view(), name='view-group'),
    # User URLs
    path('add-user/', views.UserAddView.as_view(), name='add-user'),
    # ********** Fetch Requests **********
    path('fetch-ldap-users/', views.fetch_ldap_users, name='fetch-ldap-users'),
    path('check-user-exists/', views.check_user_exists, name='check-user-exists'),
    path('get-instances/', views.get_instances, name='get-instances'),
    path('change-user-membership/', views.change_user_membership, name='change-user-membership'),
]
