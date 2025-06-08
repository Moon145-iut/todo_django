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
      # Pomodoro URLs
    path('pomodoro_settings/', views.pomodoro_settings, name='pomodoro_settings'),
    path('start_pomodoro/<int:todo_id>/', views.start_pomodoro, name='start_pomodoro'),
    path('start_pomodoro/', views.start_pomodoro, name='start_pomodoro_no_todo'),
    path('complete_pomodoro/<int:session_id>/', views.complete_pomodoro, name='complete_pomodoro'),
    path('pomodoro_stats/', views.get_pomodoro_stats, name='pomodoro_stats'),
    
    # Template URLs
    path('', views.todo_list, name='todo_list'),
    path('todo/<int:pk>/toggle/', views.toggle_todo, name='toggle_todo'),
    path('todo/<int:pk>/edit/', views.edit_todo, name='edit_todo'),
    path('todo/<int:pk>/delete/', views.delete_todo, name='delete_todo'),

    # Subtask URLs
    path('subtask/add/<int:todo_id>/', views.add_subtask, name='add_subtask'),
    path('subtask/toggle/<int:subtask_id>/', views.toggle_subtask, name='toggle_subtask'),
    path('subtask/delete/<int:subtask_id>/', views.delete_subtask, name='delete_subtask'),
    
    # Note URLs
    path('notes/', views.notes_list, name='notes_list'),
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
]