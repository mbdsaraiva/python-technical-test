from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlunoViewSet, 
    CursoViewSet, 
    MatriculaViewSet,
    dashboard_view,
    aluno_lista_view,
    aluno_historico_view,
    relatorio_sql_raw,
    cursos_populares_sql_raw
)

# Router do DRF - cria URLs 
router = DefaultRouter()
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'matriculas', MatriculaViewSet, basename='matricula')

urlpatterns = [
    # rota api
    path('api/', include(router.urls)),
    
    # api sql
    path('api/relatorio-sql/', relatorio_sql_raw, name='relatorio_sql_raw'),
    path('api/cursos-populares-sql/', cursos_populares_sql_raw, name='cursos_populares_sql'),
    
    # Templates HTML
    path('', dashboard_view, name='dashboard'),
    path('alunos/', aluno_lista_view, name='aluno_lista'),
    path('alunos/<int:pk>/', aluno_historico_view, name='aluno_historico'),
]