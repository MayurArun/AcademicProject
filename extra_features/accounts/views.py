from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Role, User, Student, Teacher
from django.contrib.sessions.models import Session
from django.contrib.auth.hashers import make_password, check_password



def home(request):
    # Initialize roles if they don't exist
    if not Role.objects.filter(name='Teacher').exists():
        Role.objects.create(name='Teacher')
    if not Role.objects.filter(name='Student').exists():
        Role.objects.create(name='Student')
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        roll_number = request.POST.get('roll_number')

        if not username or not email or not password:
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists.'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists.'})

        role_instance = Role.objects.get(name=role.capitalize())

        if role == 'teacher':
            user = User.objects.create(username=username, email=email,full_name=full_name, role=role_instance)
            user.set_password(password)
            user.save()
            Teacher.objects.create(user=user)
        elif role == 'student':
            if not full_name or not roll_number:
                return JsonResponse({'status': 'error', 'message': 'Full name and roll number are required for students.'})
            if Student.objects.filter(roll_number=roll_number).exists():
                return JsonResponse({'status': 'error', 'message': 'Roll number already exists.'})
            user = User.objects.create(username=username, email=email, full_name=full_name, role=role_instance)
            user.set_password(password)
            user.save()
            Student.objects.create(user=user, roll_number=roll_number)
        return JsonResponse({'status': 'success'})
    return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session['user_id'] = user.id
                if user.role.name == 'Teacher':
                    return JsonResponse({'status': 'success', 'redirect': 'teacher_dashboard'})
                elif user.role.name == 'Student':
                    return JsonResponse({'status': 'success', 'redirect': 'student_dashboard'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def teacher_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    classes = user.classes_taught.all()
    return render(request, 'accounts/teacher_dashboard.html', {'classes': classes})

def student_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    class_memberships = user.classes_joined.all()
    classes = [membership.class_joined for membership in class_memberships]
    return render(request, 'accounts/student_dashboard.html', {'classes': classes})

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('home')

def get_all_accounts(request):
    accounts = []
    for user in User.objects.all():
        account = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.name,
            'full_name': user.full_name if user.role.name == 'Student' else None,
            'roll_number': Student.objects.get(user=user).roll_number if user.role.name == 'Student' else None,
        }
        accounts.append(account)
    return JsonResponse({'accounts': accounts})

def delete_account(request, account_id):
    user = User.objects.get(id=account_id)
    user.delete()
    return JsonResponse({'status': 'success'})

def edit_account(request, account_id):
    user = get_object_or_404(User, id=account_id)

    if request.method == 'POST':
        # Get the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')  # New password
        confirm_password = request.POST.get('confirm_password')  # Confirm new password

        # Validate required fields (for teachers, just username and email)
        if not username or not email:
            return JsonResponse({'status': 'error', 'message': 'Username and email are required.'}, status=400)

        if password:
            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'}, status=400)
            user.set_password(password)  # Hash the new password

        # Update user details
        user.username = username
        user.email = email
        user.save()

        # Handle specific logic for students and teachers
        if user.role.name == 'Student':
            # Update student-specific fields (e.g., full_name and roll_number)
            full_name = request.POST.get('full_name')
            roll_number = request.POST.get('roll_number')

            if not full_name or not roll_number:
                return JsonResponse({'status': 'error', 'message': 'Full name and roll number are required for students.'}, status=400)

            user.full_name = full_name  # Only needed for students
            user.save()  # Save the user object with full_name

            # Update student-related data
            student = Student.objects.get(user=user)
            student.roll_number = roll_number
            student.save()

        elif user.role.name == 'Teacher':
            # For teachers, we assume only username and email need updating (no full_name or roll_number)
            # Teacher-specific logic here (if any additional fields in the future)
            teacher = Teacher.objects.get(user=user)
            # You can add more teacher-specific fields if necessary
            teacher.save()

        return JsonResponse({'status': 'success', 'message': 'Account updated successfully.'})

    # Pre-fill form with existing data for rendering
    context = {
        'user': user,
        'is_student': user.role.name == 'Student',
        'is_teacher': user.role.name == 'Teacher',
    }
    return render(request, 'accounts/edit_account.html', context)