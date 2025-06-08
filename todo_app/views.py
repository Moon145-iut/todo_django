from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Todo, Category, PomodoroSession, PomodoroSettings, SubTask, Note
from .serializers import TodoSerializer, PomodoroSettingsSerializer, PomodoroSessionSerializer, SubTaskSerializer, NoteSerializer

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['completed', 'created_at', 'due_date', 'priority']
    filterset_fields = ['completed', 'priority', 'tags']
    search_fields = ['title', 'description', 'tags']

    def get_queryset(self):
        """
        This view should return a list of all the TODOs
        for the currently authenticated user.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@login_required
def pomodoro_settings(request):
    settings, created = PomodoroSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        serializer = PomodoroSettingsSerializer(settings, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
    return JsonResponse(PomodoroSettingsSerializer(settings).data)

@login_required
def start_pomodoro(request, todo_id=None):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        session_type = data.get('session_type', 'work')
        duration = int(data.get('duration', 25))
        
        # End any active sessions
        PomodoroSession.objects.filter(
            user=request.user,
            completed=False,
            end_time__isnull=True
        ).update(interrupted=True, end_time=timezone.now())
        
        # Create new session
        session = PomodoroSession.objects.create(
            user=request.user,
            todo_id=todo_id,
            duration=duration,
            session_type=session_type,
            start_time=timezone.now()
        )
        return JsonResponse({
            'id': session.id,
            'duration': session.duration,
            'session_type': session.session_type
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def complete_pomodoro(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
        if not session.completed:
            session.completed = True
            session.end_time = timezone.now()
            session.save()
        return JsonResponse({
            'id': session.id,
            'completed': session.completed,
            'duration': session.duration
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_pomodoro_stats(request):
    # Get date range
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get sessions in date range
    sessions = PomodoroSession.objects.filter(
        user=request.user,
        start_time__gte=start_date
    )
    
    # Calculate statistics
    completed_sessions = sessions.filter(completed=True)
    stats = {
        'total_sessions': sessions.count(),
        'completed_sessions': completed_sessions.count(),
        'total_work_time': completed_sessions.aggregate(
            total=Sum('duration'))['total'] or 0,
        'average_completion_rate': (
            completed_sessions.count() * 100 / max(sessions.count(), 1)
        ),
        'sessions_by_type': {
            session_type: count
            for session_type, count in sessions.values_list('session_type')
            .annotate(count=Count('id'))
        },
        'sessions_by_todo': {
            title: count
            for title, count in sessions.exclude(todo=None)
            .values_list('todo__title')
            .annotate(count=Count('id'))
        }
    }
    
    return JsonResponse(stats)

@login_required
def todo_list(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 1)
        category_id = request.POST.get('category')
        new_category = request.POST.get('new_category')

        if title:
            if category_id == 'new' and new_category:
                # Create new category
                category = Category.objects.create(name=new_category, user=request.user)
            elif category_id:
                category = get_object_or_404(Category, id=category_id, user=request.user)
            else:
                category = None

            Todo.objects.create(
                title=title,
                description=description,
                priority=priority,
                category=category,
                user=request.user
            )
            messages.success(request, 'Todo added successfully!')
        return redirect('todo_list')

    todos = Todo.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    # Handle filters
    completed = request.GET.get('completed')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    
    if completed is not None:
        todos = todos.filter(completed=completed == 'True')
    if priority:
        todos = todos.filter(priority=priority)
    if category:
        todos = todos.filter(category_id=category)
    
    settings, created = PomodoroSettings.objects.get_or_create(user=request.user)
    return render(request, 'todo_app/todo_list.html', {
        'todos': todos,
        'categories': categories,
        'pomodoro_settings': settings,
    })

@login_required
def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        todo.completed = not todo.completed
        todo.save()
        messages.success(request, f'Todo marked as {"completed" if todo.completed else "incomplete"}!')
    return redirect('todo_list')

@login_required
def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        todo.priority = request.POST.get('priority')
        todo.due_date = request.POST.get('due_date') or None
        
        category_id = request.POST.get('category')
        new_category = request.POST.get('new_category')
        
        if category_id == 'new' and new_category:
            # Create new category
            category = Category.objects.create(name=new_category, user=request.user)
            todo.category = category
        elif category_id:
            todo.category = get_object_or_404(Category, id=category_id, user=request.user)
        else:
            todo.category = None
            
        todo.save()
        messages.success(request, 'Todo updated successfully!')
        return redirect('todo_list')
        
    return render(request, 'todo_app/edit_todo.html', {
        'todo': todo,
        'categories': categories,
    })

@login_required
def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
    return redirect('todo_list')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('todo_list')

    return render(request, 'todo_app/register.html')


@api_view(['POST'])
@login_required
def add_subtask(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    serializer = SubTaskSerializer(data={**request.data, 'todo': todo_id})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required
def toggle_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id, todo__user=request.user)
    subtask.completed = not subtask.completed
    subtask.save()
    return Response(SubTaskSerializer(subtask).data)

@api_view(['DELETE'])
@login_required
def delete_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id, todo__user=request.user)
    subtask.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@login_required
def notes_list(request):
    if request.method == 'GET':
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    
    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)