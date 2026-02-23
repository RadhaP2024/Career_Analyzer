from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('branches/', views.all_branches, name='all_branches'),
    path('placement/', views.placement_comparison, name='placement'),
    path('salary/', views.salary_analysis, name='salary'),
    path('branch/<int:branch_id>/', views.branch_detail, name='branch_detail'),
    path('compare/', views.compare_branches, name='compare'),
    path('suggestion/', views.career_suggestion, name='suggestion'),
    path('market/', views.market_analysis, name='market'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('courses/', views.courses, name='courses'),
    path('projects/', views.projects, name='projects'),
    path('about/', views.about, name='about'),
    path('load-data/', views.load_initial_data, name='load_data'),
]