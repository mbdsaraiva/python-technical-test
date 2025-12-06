from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from .models import Aluno, Curso, Matricula
from .serializers import (
    AlunoSerializer,
    CursoSerializer,
    MatriculaSerializer,
    MatriculaCreateSerializer
)


class AlunoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Alunos.
    
    Fornece automaticamente:
    - GET /api/alunos/ (listar todos)
    - POST /api/alunos/ (criar)
    - GET /api/alunos/{id}/ (detalhe)
    - PUT /api/alunos/{id}/ (atualizar completo)
    - PATCH /api/alunos/{id}/ (atualizar parcial)
    - DELETE /api/alunos/{id}/ (deletar)
    """
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer

    def get_queryset(self):
        """
        Permite filtrar alunos pela URL.
        Ex: /api/alunos/?nome=João
        """
        queryset = Aluno.objects.all()
        
        # Filtro por nome (case-insensitive)
        nome = self.request.query_params.get('nome', None)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        
        # Filtro por CPF
        cpf = self.request.query_params.get('cpf', None)
        if cpf:
            queryset = queryset.filter(cpf=cpf)
        
        return queryset

    @action(detail=True, methods=['get'])
    def matriculas(self, request, pk=None):
        """
        Endpoint customizado: GET /api/alunos/{id}/matriculas/
        Retorna todas as matrículas de um aluno específico.
        """
        aluno = self.get_object()
        matriculas = aluno.matriculas.all()
        serializer = MatriculaSerializer(matriculas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def financeiro(self, request, pk=None):
        """
        Endpoint customizado: GET /api/alunos/{id}/financeiro/
        Retorna resumo financeiro do aluno.
        """
        aluno = self.get_object()
        data = {
            'aluno_id': aluno.id,
            'aluno_nome': aluno.nome,
            'total_devido': float(aluno.total_devido()),
            'total_pago': float(aluno.total_pago()),
            'total_geral': float(aluno.total_devido() + aluno.total_pago()),
            'total_matriculas': aluno.matriculas.count(),
            'matriculas_pagas': aluno.matriculas.filter(status='PAGO').count(),
            'matriculas_pendentes': aluno.matriculas.filter(status='PENDENTE').count(),
        }
        return Response(data)


# Views para Templates HTML
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count


def dashboard_view(request):
    """
    View para o dashboard principal.
    Renderiza o template com estatísticas gerais.
    """
    # Contadores básicos
    total_alunos = Aluno.objects.count()
    cursos_ativos = Curso.objects.filter(status='ATIVO').count()
    total_matriculas = Matricula.objects.count()
    matriculas_pagas = Matricula.objects.filter(status='PAGO').count()
    matriculas_pendentes = Matricula.objects.filter(status='PENDENTE').count()
    
    # Cálculos financeiros
    total_pago = Matricula.objects.filter(
        status='PAGO'
    ).aggregate(total=Sum('curso__valor_inscricao'))['total'] or 0
    
    total_pendente = Matricula.objects.filter(
        status='PENDENTE'
    ).aggregate(total=Sum('curso__valor_inscricao'))['total'] or 0
    
    total_geral = total_pago + total_pendente
    
    # Percentuais
    percentual_pagas = (matriculas_pagas / total_matriculas * 100) if total_matriculas > 0 else 0
    percentual_pendentes = (matriculas_pendentes / total_matriculas * 100) if total_matriculas > 0 else 0
    
    # Cursos mais populares (com count de matrículas)
    cursos_populares = Curso.objects.annotate(
        total_matriculas=Count('matriculas')
    ).order_by('-total_matriculas')[:5]
    
    context = {
        'total_alunos': total_alunos,
        'cursos_ativos': cursos_ativos,
        'total_matriculas': total_matriculas,
        'matriculas_pagas': matriculas_pagas,
        'matriculas_pendentes': matriculas_pendentes,
        'total_pago': total_pago,
        'total_pendente': total_pendente,
        'total_geral': total_geral,
        'percentual_pagas': percentual_pagas,
        'percentual_pendentes': percentual_pendentes,
        'cursos_populares': cursos_populares,
    }
    
    return render(request, 'core/dashboard.html', context)


def aluno_lista_view(request):
    """
    View para listar todos os alunos.
    """
    alunos = Aluno.objects.all()
    context = {'alunos': alunos}
    return render(request, 'core/aluno_lista.html', context)


def aluno_historico_view(request, pk):
    """
    View para exibir histórico de um aluno específico.
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    matriculas = aluno.matriculas.all()
    
    total_pago = aluno.total_pago()
    total_devido = aluno.total_devido()
    total_geral = total_pago + total_devido
    
    context = {
        'aluno': aluno,
        'matriculas': matriculas,
        'total_pago': total_pago,
        'total_devido': total_devido,
        'total_geral': total_geral,
    }
    
    return render(request, 'core/aluno_historico.html', context)


# ============================================
# ENDPOINT COM SQL RAW (OBRIGATÓRIO DESAFIO)
# ============================================
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def relatorio_sql_raw(request):
    """
    Endpoint que usa SQL RAW com JOIN e agregações.
    GET /api/relatorio-sql/
    
    Retorna relatório financeiro completo de todos os alunos
    usando consulta SQL pura com JOINS e agregações (SUM, COUNT, etc).
    """
    
    # SQL puro com JOIN e agregações
    sql_query = """
        SELECT 
            a.id as aluno_id,
            a.nome as aluno_nome,
            a.email as aluno_email,
            a.cpf as aluno_cpf,
            a.data_ingresso,
            COUNT(m.id) as total_matriculas,
            COUNT(CASE WHEN m.status = 'PAGO' THEN 1 END) as matriculas_pagas,
            COUNT(CASE WHEN m.status = 'PENDENTE' THEN 1 END) as matriculas_pendentes,
            COALESCE(SUM(CASE WHEN m.status = 'PAGO' THEN c.valor_inscricao ELSE 0 END), 0) as total_pago,
            COALESCE(SUM(CASE WHEN m.status = 'PENDENTE' THEN c.valor_inscricao ELSE 0 END), 0) as total_devido,
            COALESCE(SUM(c.valor_inscricao), 0) as total_geral
        FROM core_aluno a
        LEFT JOIN core_matricula m ON a.id = m.aluno_id
        LEFT JOIN core_curso c ON m.curso_id = c.id
        GROUP BY a.id, a.nome, a.email, a.cpf, a.data_ingresso
        ORDER BY total_geral DESC
    """
    
    # Executar SQL raw usando cursor
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    # Converter Decimal para float para JSON
    for result in results:
        result['total_pago'] = float(result['total_pago'])
        result['total_devido'] = float(result['total_devido'])
        result['total_geral'] = float(result['total_geral'])
        result['data_ingresso'] = result['data_ingresso'].strftime('%Y-%m-%d') if result['data_ingresso'] else None
    
    return Response({
        'mensagem': 'Relatório gerado usando SQL RAW com JOIN e agregações',
        'total_alunos': len(results),
        'alunos': results
    })


@api_view(['GET'])
def cursos_populares_sql_raw(request):
    """
    Endpoint alternativo com SQL RAW.
    GET /api/cursos-populares-sql/
    
    Lista cursos mais populares usando SQL puro.
    """
    
    sql_query = """
        SELECT 
            c.id as curso_id,
            c.nome as curso_nome,
            c.carga_horaria,
            c.valor_inscricao,
            c.status,
            COUNT(m.id) as total_matriculas,
            COUNT(CASE WHEN m.status = 'PAGO' THEN 1 END) as matriculas_pagas,
            COUNT(CASE WHEN m.status = 'PENDENTE' THEN 1 END) as matriculas_pendentes,
            COALESCE(SUM(CASE WHEN m.status = 'PAGO' THEN c.valor_inscricao ELSE 0 END), 0) as total_arrecadado
        FROM core_curso c
        LEFT JOIN core_matricula m ON c.id = m.curso_id
        GROUP BY c.id, c.nome, c.carga_horaria, c.valor_inscricao, c.status
        ORDER BY total_matriculas DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    # Converter Decimal para float
    for result in results:
        result['valor_inscricao'] = float(result['valor_inscricao'])
        result['total_arrecadado'] = float(result['total_arrecadado'])
    
    return Response({
        'mensagem': 'Cursos populares usando SQL RAW',
        'total_cursos': len(results),
        'cursos': results
    })


class CursoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Cursos.
    """
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    def get_queryset(self):
        """
        Permite filtrar cursos.
        Ex: /api/cursos/?status=ATIVO
        """
        queryset = Curso.objects.all()
        
        # Filtro por status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Filtro por nome
        nome = self.request.query_params.get('nome', None)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        
        return queryset

    @action(detail=True, methods=['get'])
    def matriculas(self, request, pk=None):
        """
        Endpoint customizado: GET /api/cursos/{id}/matriculas/
        Retorna todas as matrículas de um curso.
        """
        curso = self.get_object()
        matriculas = curso.matriculas.all()
        serializer = MatriculaSerializer(matriculas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def estatisticas(self, request, pk=None):
        """
        Endpoint customizado: GET /api/cursos/{id}/estatisticas/
        Retorna estatísticas do curso.
        """
        curso = self.get_object()
        data = {
            'curso_id': curso.id,
            'curso_nome': curso.nome,
            'carga_horaria': curso.carga_horaria,
            'valor_inscricao': float(curso.valor_inscricao),
            'status': curso.status,
            'total_matriculas': curso.matriculas.count(),
            'matriculas_pagas': curso.matriculas.filter(status='PAGO').count(),
            'matriculas_pendentes': curso.matriculas.filter(status='PENDENTE').count(),
            'total_arrecadado': float(curso.total_arrecadado()),
            'potencial_arrecadacao': float(
                curso.valor_inscricao * curso.matriculas.filter(status='PENDENTE').count()
            ),
        }
        return Response(data)


class MatriculaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Matrículas.
    """
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer

    def get_serializer_class(self):
        """
        Usa serializers diferentes para criar vs. listar.
        """
        if self.action == 'create':
            return MatriculaCreateSerializer
        return MatriculaSerializer

    def get_queryset(self):
        """
        Permite filtrar matrículas.
        Ex: /api/matriculas/?status=PAGO&aluno=1
        """
        queryset = Matricula.objects.all()
        
        # Filtro por status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Filtro por aluno
        aluno_id = self.request.query_params.get('aluno', None)
        if aluno_id:
            queryset = queryset.filter(aluno_id=aluno_id)
        
        # Filtro por curso
        curso_id = self.request.query_params.get('curso', None)
        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)
        
        return queryset

    @action(detail=True, methods=['post'])
    def marcar_pago(self, request, pk=None):
        """
        Endpoint customizado: POST /api/matriculas/{id}/marcar_pago/
        Marca uma matrícula como paga.
        """
        matricula = self.get_object()
        matricula.marcar_como_pago()
        serializer = self.get_serializer(matricula)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_pendente(self, request, pk=None):
        """
        Endpoint customizado: POST /api/matriculas/{id}/marcar_pendente/
        Marca uma matrícula como pendente.
        """
        matricula = self.get_object()
        matricula.status = 'PENDENTE'
        matricula.save()
        serializer = self.get_serializer(matricula)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resumo_financeiro(self, request):
        """
        Endpoint customizado: GET /api/matriculas/resumo_financeiro/
        Retorna resumo financeiro geral de todas as matrículas.
        """
        # Agregações usando ORM do Django
        total_matriculas = Matricula.objects.count()
        matriculas_pagas = Matricula.objects.filter(status='PAGO').count()
        matriculas_pendentes = Matricula.objects.filter(status='PENDENTE').count()
        
        # Soma total pago
        total_pago = Matricula.objects.filter(
            status='PAGO'
        ).aggregate(
            total=Sum('curso__valor_inscricao')
        )['total'] or 0
        
        # Soma total pendente
        total_pendente = Matricula.objects.filter(
            status='PENDENTE'
        ).aggregate(
            total=Sum('curso__valor_inscricao')
        )['total'] or 0
        
        data = {
            'total_matriculas': total_matriculas,
            'matriculas_pagas': matriculas_pagas,
            'matriculas_pendentes': matriculas_pendentes,
            'percentual_pagas': round(
                (matriculas_pagas / total_matriculas * 100) if total_matriculas > 0 else 0, 
                2
            ),
            'total_pago': float(total_pago),
            'total_pendente': float(total_pendente),
            'total_geral': float(total_pago + total_pendente),
        }
        return Response(data)