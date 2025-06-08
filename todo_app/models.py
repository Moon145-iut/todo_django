from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)  # 1: Low, 2: Medium, 3: High
    tags = models.CharField(max_length=100, blank=True, null=True)  # Comma-separated tags
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.user.username}'

    class Meta:
        ordering = ['-created_at']  
        verbose_name_plural = 'Todos'

class PomodoroSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    work_duration = models.IntegerField(default=25)  # in minutes
    short_break_duration = models.IntegerField(default=5)
    long_break_duration = models.IntegerField(default=15)
    long_break_interval = models.IntegerField(default=4)
    notification_sound = models.BooleanField(default=True)
    desktop_notification = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Pomodoro Settings"

class PomodoroSession(models.Model):
    SESSION_TYPES = [
        ('work', 'Work'),
        ('short_break', 'Short Break'),
        ('long_break', 'Long Break'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    todo = models.ForeignKey('Todo', on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField()  # in minutes
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    completed = models.BooleanField(default=False)
    interrupted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s {self.session_type} session - {self.start_time.date()}"

    def complete_session(self):
        self.completed = True
        self.end_time = timezone.now()
        self.save()

class SubTask(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.todo.title}'

    class Meta:
        ordering = ['created_at']

class Note(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    topic = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.user.username}'

    class Meta:
        ordering = ['-updated_at']
