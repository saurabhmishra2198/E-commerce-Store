from django.contrib import admin
from django.urls import path
from SaurabhComputerApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register',views.register, name='Register'),
    path('login',views.loginUser, name='Login'),
    path('logout',views.logoutUser, name='Logout'),
    path('home', views.index, name='home'),
    path('about', views.about, name='Aboutus'),
    path('services', views.services, name='Services'),
    path('contact', views.contact, name='ContactUs'),
    path('tracker', views.tracker, name='Tracker'),
    path('search', views.search, name='Search'),
    path('productview/<int:myid>', views.prodView, name='ProductView'),
    path('checkout', views.checkout, name='Checkout'),
    path('blog', views.blog, name='Blog'), 
    path('blogpost/<int:id>', views.blogpost, name='Blogpost'), #blog/<int:id>
    path("handlerequest", views.handlerequest, name="HandleRequest"),

]