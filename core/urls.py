from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlunoViewSet, 
    CursoViewSet, 
    MatriculaViewSet,
    dashboard_view,
    aluno_lista_view,
    aluno_historico_view
)

# Router do DRF - cria URLs automaticamente
router = DefaultRouter()
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'matriculas', MatriculaViewSet, basename='matricula')

urlpatterns = [
    # APIs
    path('api/', include(router.urls)),
    
    # Templates HTML
    path('', dashboard_view, name='dashboard'),
    path('alunos/', aluno_lista_view, name='aluno_lista'),
    path('alunos/<int:pk>/', aluno_historico_view, name='aluno_historico'),
]