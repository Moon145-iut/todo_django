from rest_framework import serializers
from .models import Todo, Category, PomodoroSession, PomodoroSettings, SubTask, Note

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']

class TodoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Todo
        fields = '__all__'

    def create(self, validated_data):
        return Todo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.category = validated_data.get('category', instance.category)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance

class PomodoroSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomodoroSettings
        fields = ['work_duration', 'short_break_duration', 'long_break_duration',
                 'long_break_interval', 'notification_sound', 'desktop_notification']

class PomodoroSessionSerializer(serializers.ModelSerializer):
    todo_title = serializers.CharField(source='todo.title', read_only=True)
    
    class Meta:
        model = PomodoroSession
        fields = ['id', 'todo', 'todo_title', 'start_time', 'end_time', 'duration',
                 'session_type', 'completed', 'interrupted']

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'todo', 'title', 'completed', 'created_at']
        read_only_fields = ['created_at']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'topic', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']