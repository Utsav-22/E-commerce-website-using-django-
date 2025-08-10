from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('userlogin.urls' , namespace='userlogin')),
    path('',include('store.urls' , namespace='store')) ,
    path('cart/', include('cart.urls' , namespace='cart')) ,
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
