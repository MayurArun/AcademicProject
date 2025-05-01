from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from accounts.models import User



class Class(models.Model):
    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='classes_taught')
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    description = models.TextField()
    class_code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.class_code:
            self.class_code = get_random_string(length=10)
        super().save(*args, **kwargs)

class ClassMembership(models.Model):
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='classes_joined')
    class_joined = models.ForeignKey(Class, on_delete=models.CASCADE)
    

class Assignment(models.Model):
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentFile(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='assignments/')  # Files will be stored in media/assignments/

    def __str__(self):
        return self.file.name

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Add this field

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class SubmissionFile(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='submissions/')  # Files will be stored in media/submissions/

    def __str__(self):
        return self.file.name


class DiscussionPost(models.Model):
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='discussion_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.message[:50]}"

class DiscussionReply(models.Model):
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.message[:50]}"
    
class Quiz(models.Model):
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.PositiveIntegerField(default=0)  # Time limit in minutes

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # Ensure this field exists

    def __str__(self):
        return self.text

class QuizSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class SelectedOption(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='selected_options')
    option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.submission.student.username} - {self.option.text}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)  # Optional link for the notification

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"