from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Class, ClassMembership, Assignment, AssignmentFile, AssignmentSubmission, SubmissionFile, DiscussionPost, DiscussionReply, Quiz, Question, Option, QuizSubmission, SelectedOption
from accounts.models import User
from django.utils import timezone
from .models import Notification



def create_class(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        section = request.POST.get('section')
        description = request.POST.get('description')
        teacher = User.objects.get(id=request.session['user_id'])
        new_class = Class.objects.create(teacher=teacher, name=name, section=section, description=description)
        return JsonResponse({'status': 'success', 'class_code': new_class.class_code})
    return render(request, 'classes/create_class.html')

def join_class(request):
    if request.method == 'POST':
        class_code = request.POST.get('class_code')
        student = User.objects.get(id=request.session['user_id'])
        class_to_join = get_object_or_404(Class, class_code=class_code)
        ClassMembership.objects.create(student=student, class_joined=class_to_join)
        return JsonResponse({'status': 'success'})
    return render(request, 'classes/join_class.html')

def class_dashboard(request, class_code):
    class_obj = get_object_or_404(Class, class_code=class_code)
    students = class_obj.classmembership_set.all()
    return render(request, 'classes/class_dashboard.html', {'class': class_obj, 'students': students})

def remove_student(request, membership_id):
    membership = get_object_or_404(ClassMembership, id=membership_id)
    if membership.class_joined.teacher.id == request.session['user_id']:
        membership.delete()
    return redirect('class_dashboard', class_code=membership.class_joined.class_code)

def delete_class(request, class_code):
    class_obj = get_object_or_404(Class, class_code=class_code)
    if class_obj.teacher.id == request.session['user_id']:
        class_obj.delete()
    return redirect('teacher_dashboard')


# Assignment Creation (Teacher Only)
def create_assignment(request, class_code):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, class_code=class_code)

        # Ensure the user is the teacher of the class
        if class_obj.teacher.id != request.session['user_id']:
            return JsonResponse({'status': 'error', 'message': 'Only teachers can create assignments.'})

        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')

        assignment = Assignment.objects.create(
            class_obj=class_obj,
            title=title,
            description=description,
            due_date=due_date
        )

        # Handle file uploads
        files = request.FILES.getlist('files')
        for file in files:
            AssignmentFile.objects.create(assignment=assignment, file=file)

        # Notify students
        students = class_obj.classmembership_set.all()
        for student in students:
            Notification.objects.create(
                user=student.student,
                message=f"New Assignment: {assignment.title}",
                link=f"/classes/view_assignments/{class_code}/"
            )
        return JsonResponse({'status': 'success', 'message': 'Assignment created successfully'})
    return render(request, 'classes/create_assignment.html', {'class_code': class_code})

# Assignment Submission (Student Only)
def submit_assignment(request, assignment_id):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment, id=assignment_id)
        student = User.objects.get(id=request.session['user_id'])

        # Ensure the student is part of the class
        if not ClassMembership.objects.filter(class_joined=assignment.class_obj, student=student).exists():
            return JsonResponse({'status': 'error', 'message': 'You are not enrolled in this class.'})

        text = request.POST.get('text')
        files = request.FILES.getlist('files')

        # Validate that either text or files are provided
        if not text and not files:
            return JsonResponse({'status': 'error', 'message': 'Please provide text or upload at least one file.'})

        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student,
            text=text
        )

        # Handle file uploads
        for file in files:
            SubmissionFile.objects.create(submission=submission, file=file)

        # Notify teacher
        Notification.objects.create(
            user=assignment.class_obj.teacher,
            message=f"Assignment Submitted: {assignment.title} by {submission.student.username}",
            link=f"/classes/view_submissions/{assignment.id}/"
        )
        return JsonResponse({'status': 'success', 'message': 'Assignment submitted successfully'})
    
    # Pass the class_code to the template
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return render(request, 'classes/submit_assignment.html', {
        'assignment_id': assignment_id,
        'class_code': assignment.class_obj.class_code  # Pass the class_code
    })


# View Assignments (Teacher and Student)
def view_assignments(request, class_code):
    class_obj = get_object_or_404(Class, class_code=class_code)
    user = User.objects.get(id=request.session['user_id'])

    # Ensure the user is either the teacher or a student in the class
    if class_obj.teacher.id != user.id and not ClassMembership.objects.filter(class_joined=class_obj, student=user).exists():
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    assignments = class_obj.assignments.all()
    return render(request, 'classes/view_assignments.html', {'class': class_obj, 'assignments': assignments, 'user': user})

# View Submissions (Teacher Only)
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    user = User.objects.get(id=request.session['user_id'])

    # Ensure the user is the teacher of the class
    if assignment.class_obj.teacher.id != user.id:
        return JsonResponse({'status': 'error', 'message': 'Only teachers can view submissions.'})

    submissions = assignment.submissions.all()
    return render(request, 'classes/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

# View Student's Own Submissions (Student Only)
def view_student_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = User.objects.get(id=request.session['user_id'])

    # Ensure the student is part of the class
    if not ClassMembership.objects.filter(class_joined=assignment.class_obj, student=student).exists():
        return JsonResponse({'status': 'error', 'message': 'You are not enrolled in this class.'})

    submissions = assignment.submissions.filter(student=student)
    return render(request, 'classes/view_student_submissions.html', {'assignment': assignment, 'submissions': submissions})


def grade_submission(request, submission_id):
    if request.method == 'POST':
        submission = get_object_or_404(AssignmentSubmission, id=submission_id)
        teacher = User.objects.get(id=request.session['user_id'])

        # Ensure the user is the teacher of the class
        if submission.assignment.class_obj.teacher.id != teacher.id:
            return JsonResponse({'status': 'error', 'message': 'Only teachers can grade submissions.'})

        grade = request.POST.get('grade')
        if grade:
            submission.grade = grade
            submission.save()

            # Notify student
            Notification.objects.create(
                user=submission.student,
                message=f"Assignment Graded: {submission.assignment.title} - Grade: {grade}",
                link=f"/classes/view_student_submissions/{submission.assignment.id}/"
            )
            return JsonResponse({'status': 'success', 'message': 'Grade updated successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Please provide a valid grade.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# Post a new message
# def post_message(request, class_code):
#     if request.method == 'POST':
#         class_obj = get_object_or_404(Class, class_code=class_code)
#         user = User.objects.get(id=request.session['user_id'])
#
#         # Ensure the user is part of the class
#         if not (class_obj.teacher.id == user.id or ClassMembership.objects.filter(class_joined=class_obj, student=user).exists()):
#             return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
#
#         message = request.POST.get('message')
#         if not message:
#             return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'})
#
#         DiscussionPost.objects.create(class_obj=class_obj, author=user, message=message)
#         return JsonResponse({'status': 'success', 'message': 'Message posted successfully.'})
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def post_message(request, class_code):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, class_code=class_code)
        user = User.objects.get(id=request.session['user_id'])

        # Ensure the user is part of the class
        if not (class_obj.teacher.id == user.id or ClassMembership.objects.filter(class_joined=class_obj,
                                                                                  student=user).exists()):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

        message = request.POST.get('message')
        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'})

        # Create the discussion post
        post = DiscussionPost.objects.create(class_obj=class_obj, author=user, message=message)

        # Fetch all students in the class (excluding the teacher)
        students = class_obj.classmembership_set.exclude(student=user)  # Exclude the author from the notifications

        # Send notification to students
        students = class_obj.classmembership_set.all()
        for student in students:
            Notification.objects.create(
                user=student.student,
                message=f"New message posted in {class_obj.name}: {message[:50]}...",
                link=f"/classes/class_dashboard/{class_code}/"
            )

        # ✅ Send notification to the teacher also
        Notification.objects.create(
            user=class_obj.teacher,
            message=f"New message posted in {class_obj.name}: {message[:50]}...",
            link=f"/classes/class_dashboard/{class_code}/"
        )

        return JsonResponse({'status': 'success', 'message': 'Message posted successfully.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# Reply to a message
def reply_message(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(DiscussionPost, id=post_id)
        user = User.objects.get(id=request.session['user_id'])

        # Ensure the user is part of the class
        if not (post.class_obj.teacher.id == user.id or ClassMembership.objects.filter(class_joined=post.class_obj, student=user).exists()):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

        message = request.POST.get('message')
        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty.'})

        DiscussionReply.objects.create(post=post, author=user, message=message)
        return JsonResponse({'status': 'success', 'message': 'Reply posted successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# Delete a message or reply
def delete_message(request, message_id, message_type):
    user = User.objects.get(id=request.session['user_id'])

    if message_type == 'post':
        message = get_object_or_404(DiscussionPost, id=message_id)
    elif message_type == 'reply':
        message = get_object_or_404(DiscussionReply, id=message_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid message type.'})

    # Ensure the user is the author of the message
    if message.author.id != user.id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    message.delete()
    return JsonResponse({'status': 'success', 'message': 'Message deleted successfully.'})


# Create Quiz (Teacher Only)
def create_quiz(request, class_code):
    if request.method == 'POST':
        class_obj = get_object_or_404(Class, class_code=class_code)
        user = User.objects.get(id=request.session['user_id'])

        # Ensure the user is the teacher of the class
        if class_obj.teacher.id != user.id:
            return JsonResponse({'status': 'error', 'message': 'Only teachers can create quizzes.'})

        title = request.POST.get('title')
        time_limit = request.POST.get('time_limit', 0)  # Get time limit from form

        quiz = Quiz.objects.create(
            class_obj=class_obj,
            title=title,
            time_limit=time_limit
        )

        # Process questions and options
        question_texts = request.POST.getlist('question_text[]')
        question_points = request.POST.getlist('question_points[]')
        option_texts = request.POST.getlist('option_text[]')

        # Iterate over questions
        for i in range(len(question_texts)):
            question = Question.objects.create(
                quiz=quiz,
                text=question_texts[i],
                points=int(question_points[i])
            )

            # Get the correct option index for this question
            correct_option_index = int(request.POST.get(f'is_correct_{i}'))

            # Iterate over options for this question (4 options per question)
            for j in range(4):
                option_index = i * 4 + j  # Calculate the correct index for options
                is_correct = (j == correct_option_index)  # Mark the correct option
                Option.objects.create(
                    question=question,
                    text=option_texts[option_index],
                    is_correct=is_correct
                )

        # Notify students
        students = class_obj.classmembership_set.all()
        for student in students:
            Notification.objects.create(
                user=student.student,
                message=f"New Quiz: {quiz.title}",
                link=f"/classes/view_quizzes/{class_code}/"
            )
        return redirect('classes:view_quizzes', class_code=class_code)
    return render(request, 'classes/create_quiz.html', {'class_code': class_code})
        
# Take Quiz (Student Only)
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student = User.objects.get(id=request.session['user_id'])

    # Ensure the student is part of the class
    if not ClassMembership.objects.filter(class_joined=quiz.class_obj, student=student).exists():
        return JsonResponse({'status': 'error', 'message': 'You are not enrolled in this class.'})

    if request.method == 'POST':
        # Prevent duplicate submissions
        if QuizSubmission.objects.filter(quiz=quiz, student=student).exists():
            return redirect('classes:view_quiz_grades', quiz_id=quiz_id)

        submission = QuizSubmission.objects.create(student=student, quiz=quiz)
        total_score = 0

        # Process selected options
        for question in quiz.questions.all():
            selected_option_id = request.POST.get(f'question_{question.id}')
            if selected_option_id:
                option = get_object_or_404(Option, id=selected_option_id)
                SelectedOption.objects.create(submission=submission, option=option)
                if option.is_correct:
                    total_score += question.points  # Add points only if the selected option is correct

        submission.score = total_score
        submission.save()

        # Notify teacher
        Notification.objects.create(
            user=quiz.class_obj.teacher,
            message=f"Quiz Attempted: {quiz.title} by {submission.student.username}",
            link=f"/classes/view_quiz_grades/{quiz.id}/"
        )
        return redirect('classes:view_quiz_grades', quiz_id=quiz_id)

    return render(request, 'classes/take_quiz.html', {'quiz': quiz})
# View Quiz Grades
def view_quizzes(request, class_code):
    class_obj = get_object_or_404(Class, class_code=class_code)
    user = User.objects.get(id=request.session['user_id'])

    # Ensure the user is part of the class
    if not (class_obj.teacher.id == user.id or ClassMembership.objects.filter(class_joined=class_obj, student=user).exists()):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

    quizzes = class_obj.quizzes.all()
    return render(request, 'classes/view_quizzes.html', {'class': class_obj, 'quizzes': quizzes})

def view_quiz_grades(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = User.objects.get(id=request.session['user_id'])

    if user.role.name == 'Teacher':
        # Teacher: View all submissions
        submissions = quiz.submissions.all()
        return render(request, 'classes/view_quiz_grades_teacher.html', {'quiz': quiz, 'submissions': submissions})
    else:
        # Student: View their own submission
        submission = QuizSubmission.objects.filter(quiz=quiz, student=user).first()
        return render(request, 'classes/view_quiz_grades_student.html', {'submission': submission})
    
    
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = User.objects.get(id=request.session['user_id'])
    
    # Verify teacher owns the class
    if quiz.class_obj.teacher.id != user.id:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('classes:view_quizzes', class_code=quiz.class_obj.class_code)
    
    return redirect('classes:view_quizzes', class_code=quiz.class_obj.class_code)


def get_notifications(request):
    user = User.objects.get(id=request.session['user_id'])
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
    notifications_data = [{
        'id': notification.id,  # Include the notification ID
        'message': notification.message,
        'link': notification.link,
        'created_at': notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for notification in notifications]
    return JsonResponse({'notifications': notifications_data})

def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

