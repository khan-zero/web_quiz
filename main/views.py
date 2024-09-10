from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from . import models

from random import choice, sample
from colorama import Fore, init
import openpyxl

#def index(request):
    #return render(request, 'index.html')

init(autoreset=True)


def quizList(request):
    images = [
        'https://st2.depositphotos.com/2769299/7314/i/450/depositphotos_73146775-stock-photo-a-stack-of-books-on.jpg',
        'https://img.freepik.com/free-photo/creative-composition-world-book-day_23-2148883765.jpg',
        'https://profit.pakistantoday.com.pk/wp-content/uploads/2018/04/Stack-of-books-great-education.jpg',
        'https://live-production.wcms.abc-cdn.net.au/73419a11ea13b52c6bd9c0a69c10964e?impolicy=wcms_crop_resize&cropH=1080&cropW=1918&xPos=1&yPos=0&width=862&height=485',
        'https://live-production.wcms.abc-cdn.net.au/398836216839841241467590824c5cf1?impolicy=wcms_crop_resize&cropH=2813&cropW=5000&xPos=0&yPos=0&width=862&height=485',
        'https://images.theconversation.com/files/45159/original/rptgtpxd-1396254731.jpg?ixlib=rb-4.1.0&q=45&auto=format&w=1356&h=668&fit=crop'
    ]
    
    quizes = models.Quiz.objects.filter(author=request.user)
    # images = sample(len(quizes), images)

    quizes_list = []

    for quiz in quizes:
        quiz.img = choice(images)
        quizes_list.append(quiz)

    return render(request, 'quiz-list.html', {'quizes':quizes_list})

@login_required(login_url='login')
def quizDetail(request, id):
    quiz = models.Quiz.objects.get(id=id)
    return render(request, 'quiz-detail.html', {'quiz':quiz})

@login_required(login_url='login')
def questionDelete(request, id, pk):
    models.Question.objects.get(id=id).delete()
    return redirect('quizDetail', id=pk)


@login_required(login_url='login')
def createQuiz(request):
    if request.method == 'POST':
        quiz = models.Quiz.objects.create(
            name = request.POST['name'],
            amount = request.POST['amount'],
            author = request.user
        )
        return redirect('quizDetail', quiz.id)
    return render(request, 'quiz-create.html')


@login_required(login_url='login')
def questionCreate(request, id):
    quiz = models.Quiz.objects.get(id=id)
    if request.method == 'POST':
        question_text = request.POST['name']
        true = request.POST['true']
        false_list = request.POST.getlist('false-list')

        question = models.Question.objects.create(
            name = question_text,
            quiz = quiz,
        )
        question.save()
        models.Option.objects.create(
            question = question,
            name = true,
            correct = True,
        )

        for false in false_list:
            models.Option.objects.create(
                name = false,
                question = question,
            )
        return redirect('quizList')

    return render(request, 'question-create.html', {'quiz':quiz})


@login_required(login_url='login')
def questionDetail(request, id):
    question = models.Question.objects.get(id=id)
    return render(request, 'question-detail.html', {'question':question})


@login_required(login_url='login')
def deleteOption(request, ques, option):
    question = models.Question.objects.get(id=ques)
    models.Option.objects.get(question=question, id=option).delete()
    return redirect('questionDetail', id=ques)



@login_required(login_url='login')
def detail(request):
    quizzes = models.Quiz.objects.all()
    results = []

    for quiz in quizzes:
        total_questions = quiz.questions_count

        answer_details = models.AnswerDetail.objects.filter(answer__quiz=quiz)

        correct_answers = answer_details.filter(
            user_choice__correct=True
        ).count()
        incorrect_answers = answer_details.filter(
            user_choice__correct=False
        ).count()

        results.append({
            'quiz': quiz,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers
        })
        
    print(Fore.RED + str(f"{results}"))

    return render(request, 'detail.html', {'results': results})
    
   
@login_required(login_url='login')
def results_detail(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, id=quiz_id)
    answers = models.Answer.objects.filter(quiz=quiz)
    
    details = []

    for answer in answers:
        answer_details = models.AnswerDetail.objects.filter(answer=answer)
        
        correct_answers = 0
        incorrect_answers = 0

        for detail in answer_details:
            if detail.is_correct:
                correct_answers += 1
            else:
                incorrect_answers += 1

        total_questions = correct_answers + incorrect_answers
        correct_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        details.append({
            'user': answer.author,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'correct_percentage': correct_percentage
        })

    return render(request, 'results_detail.html', {
        'quiz': quiz,
        'details': details
    })
    

@login_required(login_url='login')  
def participant_results(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, id=quiz_id)
    participants = models.Answer.objects.filter(quiz=quiz).values('author').distinct()

    participant_details = []

    for participant in participants:
        user = User.objects.get(id=participant['author'])
        
        total_answers = models.AnswerDetail.objects.filter(
            answer__author=user,
            answer__quiz=quiz
        ).count()
        
        correct_answers = models.AnswerDetail.objects.filter(
            answer__author=user,
            answer__quiz=quiz,
            user_choice__correct=True
        ).count()
        
        incorrect_answers = models.AnswerDetail.objects.filter(
            answer__author=user,
            answer__quiz=quiz,
            user_choice__correct=False
        ).count()
        
        correct_percentage = (correct_answers / total_answers) * 100 if total_answers > 0 else 0
        
        participant_details.append({
            'user': user,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'correct_percentage': correct_percentage
        })

    return render(request, 'participant_results.html', {'quiz': quiz, 'participant_details': participant_details})
    
    
@login_required(login_url='login')  
def participant_detail(request, quiz_id, user_id):
    quiz = get_object_or_404(models.Quiz, id=quiz_id)
    user = get_object_or_404(User, id=user_id)
    details = models.AnswerDetail.objects.filter(answer__author=user, answer__quiz=quiz)
    
    return render(request, 'participant_detail.html', {
        'quiz': quiz,
        'user': user,
        'details': details
    })
    
    
@login_required(login_url='login') 
def export_to_excel(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, id=quiz_id)
    answers = models.Answer.objects.filter(quiz=quiz)
    data = []

    for answer in answers:
        answer_details = models.AnswerDetail.objects.filter(answer=answer)
        correct_answers = answer_details.filter(user_choice__correct=True).count()
        incorrect_answers = answer_details.filter(user_choice__correct=False).count()
        correct_percentage = (correct_answers / quiz.questions_count) * 100 if quiz.questions_count > 0 else 0

        data.append([
            answer.author.username,
            correct_answers,
            incorrect_answers,
            correct_percentage,
        ])

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Quiz Results"

    headers = ['Username', 'Correct Answers', 'Incorrect Answers', 'Correct Percentage']
    ws.append(headers)

    for row in data:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=quiz_results_{quiz_id}.xlsx'
    
    return response


@login_required(login_url='login')
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('frist_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')

        if password == password_confirm:
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()

                login(request, user)
                return redirect('quizList') 
        #else:
        #    return h(request, 'Passwords do not match')

    return render(request, 'auth-register.html')
    


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('quizList'))
            else:
                # Handle invalid login
                pass
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
    
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')
    

def my_view(request):
    context = {
        'user': request.user
    }
    return render(request, 'base.html', context)


def error_handler(request, exception=None):
    
    
    error_list = ['error1.html', 'error2.html', 'error3.html']
    current_error = error_list.choice(error_list)
    
    
    return render(request, current_error, status=status_code)
