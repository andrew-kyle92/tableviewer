from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from core import urls
from . import views
from . import auth_views


urlpatterns = [
    path('', views.TablesListView.as_view(), name='index'),
    path('new-table/', views.AddTableView.as_view(), name='new-table'),
    path('edit-table/<int:pk>/', views.EditTableView.as_view(), name='edit-table'),
    path('tables/', views.TablesListView.as_view(), name='tables-list'),
    path('tables/detail/<int:pk>/', views.TableDetailView.as_view(), name='table-detail'),
    # ********** Table Viewing URLs **********
    path('tables/view/<int:table_id>/', views.TableView.as_view(), name='table-view'),
    # ********** Table searching URLs **********
    path('tables/search-table/<int:table_id>/', views.SearchTable.as_view(), name='search-table'),
    path('search-table/<str:shortcut>/', views.SearchTable.as_view(), name='search-table'),
    # ********** Authentication URLs **********
    path('login/', auth_views.UserLogin.as_view(), name='login'),
    path('logout/', auth_views.UserLogout.as_view(), name='logout'),
    # ********** Fetch Requests **********
    path('save-column/', views.save_column, name='save-column'),
    path('regenerate-columns/<int:table_id>/', views.regenerate_columns, name='regenerate-columns'),
    path('add-url-shortcut/<int:table_id>', views.add_url_shortcut, name='add-url-shortcut'),
    path('remove-shortcut/', views.remove_url_shortcut, name='remove-shortcut'),
    path('get-domain-name/', views.get_domain_name, name='get-domain-name'),
    path('save-table-settings/', views.save_table_settings, name='save-table-settings'),
    # Third-party URLS
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# URL shortcut URLs
urlpatterns += [
    re_path(r'^(?P<shortcut>.+)/$', views.TableView.as_view(), name='table-view'),
    re_path(r'^search-table/(?P<shortcut>.+)/$', views.SearchTable.as_view(), name='search-table'),
]
