from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('search-config/<int:resume_id>/', views.search_config, name='search_config'),
    path('search/<int:search_id>/', views.search_results, name='search_results'),
    path('delete-resume/<int:resume_id>/', views.delete_resume, name='delete_resume'),
    path('history/', views.search_history, name='search_history'),
    path('api/suggest-categories/<int:resume_id>/', views.suggest_categories_api, name='suggest_categories_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)