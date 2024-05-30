from django.urls import path

from . import views

urlpatterns = [
    path('homepage', views.homepage, name='homepage'),
    path('transaction_detail', views.transaction_detail, name='transaction_detail'),
    path('publish_message', views.publish_message, name='publish_message'),
    path('send_direct_message', views.send_direct_message, name='send_direct_message')
   ]