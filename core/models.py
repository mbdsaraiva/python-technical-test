from django.db import models
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Aluno(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name="E-mail"
    )
    cpf = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="CPF",
        help_text="Apenas números"
    )
    data_ingresso = models.DateField(
        default=timezone.now,
        verbose_name="Data de Ingresso"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['-data_ingresso']

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

    def total_devido(self):
        matriculas_pendentes = self.matriculas.filter(status='PENDENTE')
        return sum(m.curso.valor_inscricao for m in matriculas_pendentes)

    def total_pago(self):
        matriculas_pagas = self.matriculas.filter(status='PAGO')
        return sum(m.curso.valor_inscricao for m in matriculas_pagas)


class Curso(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
    ]

    nome = models.CharField(max_length=200, verbose_name="Nome do Curso")
    carga_horaria = models.IntegerField(
        verbose_name="Carga Horária",
        help_text="Em horas"
    )
    valor_inscricao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor da Inscrição"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"

    def total_matriculas(self):
        return self.matriculas.count()

    def total_arrecadado(self):
        matriculas_pagas = self.matriculas.filter(status='PAGO')
        return matriculas_pagas.count() * self.valor_inscricao


class Matricula(models.Model):
    STATUS_CHOICES = [
        ('PAGO', 'Pago'),
        ('PENDENTE', 'Pendente'),
    ]

    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name="Aluno"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name="Curso"
    )
    data_matricula = models.DateField(
        default=timezone.now,
        verbose_name="Data da Matrícula"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status de Pagamento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ['-data_matricula']
        unique_together = ['aluno', 'curso']

    def __str__(self):
        return f"{self.aluno.nome} - {self.curso.nome} ({self.get_status_display()})"

    def marcar_como_pago(self):
        self.status = 'PAGO'
        self.save()