from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import json

from .models import Quiz, Question, Option
from .forms import NameForm


def home(request):
    """Home page displaying all available quizzes"""
    quizzes = Quiz.objects.filter(is_active=True)
    context = {
        'quizzes': quizzes
    }
    return render(request, 'core/home.html', context)


def start_quiz(request, quiz_id):
    """Page where user confirms details before starting the quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    if request.method == 'POST':
        # Static values - no form validation needed
        # Store quiz info in session with static name
        request.session['quiz_id'] = quiz_id
        request.session['user_name'] = 'MD'  # Static name value
        request.session['answers'] = {}
        # Don't start timer yet - wait for instructions page
        return redirect('core:instructions', quiz_id=quiz_id)
    
    context = {
        'quiz': quiz
    }
    return render(request, 'core/start_quiz.html', context)


def instructions(request, quiz_id):
    """Instruction page before starting the quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has entered their name
    if 'user_name' not in request.session or request.session.get('quiz_id') != quiz_id:
        messages.warning(request, 'Please enter your name to start the quiz.')
        return redirect('core:start_quiz', quiz_id=quiz_id)
    
    if request.method == 'POST':
        # Start the timer when user clicks "Start the exam"
        request.session['start_time'] = timezone.now().isoformat()
        return redirect('core:quiz', quiz_id=quiz_id)
    
    context = {
        'quiz': quiz,
        'user_name': request.session['user_name'],
        'time_limit': quiz.time_limit,
        'total_questions': quiz.get_total_questions(),
    }
    return render(request, 'core/instructions.html', context)


def quiz(request, quiz_id):
    """Display the quiz with questions and timer"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has started the quiz (has name in session)
    if 'user_name' not in request.session or request.session.get('quiz_id') != quiz_id:
        messages.warning(request, 'Please enter your name to start the quiz.')
        return redirect('core:start_quiz', quiz_id=quiz_id)
    
    # Get all questions with their options
    questions = quiz.questions.all().prefetch_related('options')
    
    if not questions.exists():
        messages.error(request, 'This quiz has no questions.')
        return redirect('core:home')
    
    # Calculate end time
    start_time_str = request.session['start_time']
    try:
        start_time = datetime.fromisoformat(start_time_str)
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
    except (ValueError, AttributeError):
        # Fallback: use current time if parsing fails
        start_time = timezone.now()
    end_time = start_time + timedelta(minutes=quiz.time_limit)
    time_remaining_seconds = int((end_time - timezone.now()).total_seconds())
    
    # If time has expired, redirect to results
    if time_remaining_seconds <= 0:
        return redirect('core:submit_quiz', quiz_id=quiz_id)
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'user_name': request.session['user_name'],
        'time_limit_minutes': quiz.time_limit,
        'time_remaining_seconds': time_remaining_seconds,
    }
    return render(request, 'core/quiz.html', context)


@require_http_methods(["POST"])
def submit_quiz(request, quiz_id):
    """Handle quiz submission and calculate score"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has started the quiz
    if 'user_name' not in request.session or request.session.get('quiz_id') != quiz_id:
        messages.warning(request, 'Please start the quiz first.')
        return redirect('core:start_quiz', quiz_id=quiz_id)
    
    # Get user answers from POST data
    user_answers = {}
    for key, value in request.POST.items():
        if key.startswith('question_'):
            question_id = int(key.replace('question_', ''))
            try:
                option_id = int(value)
                user_answers[question_id] = option_id
            except (ValueError, TypeError):
                pass
    
    # Calculate score
    questions = quiz.questions.all().prefetch_related('options')
    total_questions = questions.count()
    correct_answers = 0
    
    for question in questions:
        user_option_id = user_answers.get(question.id)
        if user_option_id:
            try:
                selected_option = Option.objects.get(id=user_option_id, question=question)
                if selected_option.is_correct:
                    correct_answers += 1
            except Option.DoesNotExist:
                pass
    
    score = correct_answers
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Store results in session
    request.session['quiz_results'] = {
        'score': score,
        'total_questions': total_questions,
        'percentage': round(percentage, 2),
        'user_name': request.session.get('user_name', 'Guest')
    }
    
    # Clear quiz session data
    request.session.pop('quiz_id', None)
    request.session.pop('start_time', None)
    request.session.pop('answers', None)
    
    return redirect('core:completion', quiz_id=quiz_id)


def completion(request, quiz_id):
    """Display completion message after exam ends"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if results exist
    if 'quiz_results' not in request.session:
        messages.warning(request, 'No results found. Please complete a quiz first.')
        return redirect('core:home')
    
    context = {
        'quiz': quiz,
    }
    
    return render(request, 'core/completion.html', context)


def results(request, quiz_id):
    """Display quiz results"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Get results from session
    results_data = request.session.get('quiz_results')
    
    if not results_data:
        messages.warning(request, 'No results found. Please complete a quiz first.')
        return redirect('core:home')
    
    context = {
        'quiz': quiz,
        'user_name': results_data.get('user_name', 'Guest'),
        'score': results_data.get('score', 0),
        'total_questions': results_data.get('total_questions', 0),
        'percentage': results_data.get('percentage', 0),
    }
    
    # Clear results from session after displaying
    request.session.pop('quiz_results', None)
    request.session.pop('user_name', None)
    
    return render(request, 'core/results.html', context)


def check_time(request, quiz_id):
    """API endpoint to check remaining time"""
    if 'start_time' not in request.session:
        return JsonResponse({'error': 'Quiz not started'}, status=400)
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    start_time_str = request.session['start_time']
    try:
        start_time = datetime.fromisoformat(start_time_str)
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)
    except (ValueError, AttributeError):
        # Fallback: use current time if parsing fails
        start_time = timezone.now()
    end_time = start_time + timedelta(minutes=quiz.time_limit)
    time_remaining = int((end_time - timezone.now()).total_seconds())
    
    return JsonResponse({
        'time_remaining': max(0, time_remaining),
        'expired': time_remaining <= 0
    })
