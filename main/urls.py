from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.quizList, name='quizList'),
    path('quiz-detail/<int:id>/', views.quizDetail, name='quizDetail'),
    path('questionDelete/<int:id>/<int:pk>/', views.questionDelete, name='questionDelete'),
    path('optionDelete/<int:ques>/<int:option>/', views.deleteOption, name='optionDelete'),
    path('question-detail/<int:id>/', views.questionDetail, name='questionDetail'),
    path('create-quiz', views.createQuiz, name='createQuiz'),
    path('create-question/<int:id>/', views.questionCreate, name='questionCreate'),
    path('detail/', views.detail, name='detail'),
    path('results-detail/<int:quiz_id>/', views.results_detail, name='results-detail'),
    path('participant-results/<int:quiz_id>/', views.participant_results, name='participant-results'),
    path('participant-detail/<int:quiz_id>/<int:user_id>/', views.participant_detail, name='participant_detail'),
    path('export-to-excel/<int:quiz_id>/', views.export_to_excel, name='export_to_excel'),
    
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('force-404/', views.error_handler, name='force_404'),
    path('force-500/', views.error_handler, name='force_500'),

]


handler404 = 'main.views.error_handler'
handler500 = 'main.views.error_handler'
