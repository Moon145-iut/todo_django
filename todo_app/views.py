from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .serializers import TodoSerializer
from .models import Todo, Category

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
    
    return render(request, 'todo_app/todo_list.html', {
        'todos': todos,
        'categories': categories,
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