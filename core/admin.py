from django.contrib import admin
from .models import Aluno, Curso, Matricula


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'cpf', 'data_ingresso', 'total_devido', 'total_pago']
    list_filter = ['data_ingresso']
    search_fields = ['nome', 'email', 'cpf']
    date_hierarchy = 'data_ingresso'
    ordering = ['-data_ingresso']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'cpf')
        }),
        ('Dados Acadêmicos', {
            'fields': ('data_ingresso',)
        }),
    )

    readonly_fields = []

    def total_devido(self, obj):
        valor = obj.total_devido()
        return f"R$ {valor:.2f}"
    total_devido.short_description = "Total Devido"

    def total_pago(self, obj):
        valor = obj.total_pago()
        return f"R$ {valor:.2f}"
    total_pago.short_description = "Total Pago"


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'carga_horaria', 'valor_inscricao', 'status', 'total_matriculas']
    list_filter = ['status']
    search_fields = ['nome']
    ordering = ['nome']
    
    fieldsets = (
        ('Informações do Curso', {
            'fields': ('nome', 'carga_horaria', 'valor_inscricao')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )

    def total_matriculas(self, obj):
        return obj.total_matriculas()
    total_matriculas.short_description = "Total de Matrículas"


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'curso', 'data_matricula', 'status', 'valor_curso']
    list_filter = ['status', 'data_matricula', 'curso']
    search_fields = ['aluno__nome', 'aluno__cpf', 'curso__nome']
    date_hierarchy = 'data_matricula'
    ordering = ['-data_matricula']
    
    fieldsets = (
        ('Matrícula', {
            'fields': ('aluno', 'curso', 'data_matricula')
        }),
        ('Financeiro', {
            'fields': ('status',)
        }),
    )

    actions = ['marcar_como_pago', 'marcar_como_pendente']

    def valor_curso(self, obj):
        return f"R$ {obj.curso.valor_inscricao:.2f}"
    valor_curso.short_description = "Valor"

    def marcar_como_pago(self, request, queryset):
        updated = queryset.update(status='PAGO')
        self.message_user(request, f'{updated} matrícula(s) marcada(s) como PAGO.')
    marcar_como_pago.short_description = "Marcar selecionadas como PAGO"

    def marcar_como_pendente(self, request, queryset):
        updated = queryset.update(status='PENDENTE')
        self.message_user(request, f'{updated} matrícula(s) marcada(s) como PENDENTE.')
    marcar_como_pendente.short_description = "Marcar selecionadas como PENDENTE"