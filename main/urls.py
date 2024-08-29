from django.contrib import admin
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

## Defines all the url paths, and what they connect up to
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.main),
    path("classify/", views.classify, name="classify"),
    path("train/", views.train, name="train"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("start_training/", views.start_training, name="start_training"),
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

