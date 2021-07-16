from django.urls import path
from . import views
from . import views_ajax

urlpatterns = [
    path('', views.index, name="my_index"),
    path('success/', views.success, name="my_success"),
    path('register/', views.register, name="my_register"),
    path('login/', views.login, name="my_login"),
    path('homepage/', views.homepage, name="my_homepage"),
    path('books/', views.books, name="my_books"),
    path('books/add_book', views.add_book, name="my_add_book"),
    path('books/add_book_ajax', views_ajax.add_book_ajax, name="my_add_book_ajax"),
    path('books/<int:book_id>/edit/', views.edit, name="my_edit"),
    path('books/<int:book_id>/update/', views.update, name="my_update"),
    path('books/<int:book_id>/delete/', views.delete, name="my_delete"),
    path('books/<int:book_id>/favorite/<str:source>/', views.favorite, name="my_favorite"),
    path('books/<int:book_id>/unfavorite/<str:source>/', views.unfavorite, name="my_unfavorite"),
    path('books/<int:book_id>/view/', views.view, name="my_view"),
    path('books/all_favs/', views.all_favs, name="my_all_favs"),
    path('about/', views.about, name="my_about"),
    path('logout/', views.logout, name="my_logout"),
]