from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'todos', views.TodoViewSet, basename='todo-api')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    
    # Template URLs
    path('', views.todo_list, name='todo_list'),
    path('todo/<int:pk>/toggle/', views.toggle_todo, name='toggle_todo'),
    path('todo/<int:pk>/edit/', views.edit_todo, name='edit_todo'),
    path('todo/<int:pk>/delete/', views.delete_todo, name='delete_todo'),
]