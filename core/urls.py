from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlunoViewSet, CursoViewSet, MatriculaViewSet

# Router do DRF - cria URLs automaticamente
router = DefaultRouter()
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'matriculas', MatriculaViewSet, basename='matricula')

urlpatterns = [
    path('', include(router.urls)),
]