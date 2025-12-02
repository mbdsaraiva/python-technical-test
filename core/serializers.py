from rest_framework import serializers
from .models import Aluno, Curso, Matricula


class AlunoSerializer(serializers.ModelSerializer):
    """
    serializer para o model Aluno.
    converte objetos Python (Model) em JSON e vice-versa.
    e alem disso faz validacoes dos dados.
    """
    # Campos calculados
    total_devido = serializers.SerializerMethodField()
    total_pago = serializers.SerializerMethodField()
    total_matriculas = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = [
            'id',
            'nome',
            'email',
            'cpf',
            'data_ingresso',
            'total_devido',
            'total_pago',
            'total_matriculas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_devido(self, obj):
        """metodo para calcular total devido"""
        return float(obj.total_devido())

    def get_total_pago(self, obj):
        """metodo para calcular total pago"""
        return float(obj.total_pago())

    def get_total_matriculas(self, obj):
        """metodo para contar matrículas"""
        return obj.matriculas.count()

    def validate_cpf(self, value):
        """validacao customizada do CPF"""
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, value))
        
        # Valida se tem 11 dígitos
        if len(cpf) != 11:
            raise serializers.ValidationError("CPF deve ter 11 digitos.")
        
        # Valida se não é sequência repetida (11111111111)
        if cpf == cpf[0] * 11:
            raise serializers.ValidationError("CPF invalido.")
        
        return cpf


class CursoSerializer(serializers.ModelSerializer):
    """
    serializer para o model Curso.
    """
    # campo calculado
    total_matriculas = serializers.SerializerMethodField()
    total_arrecadado = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = [
            'id',
            'nome',
            'carga_horaria',
            'valor_inscricao',
            'status',
            'total_matriculas',
            'total_arrecadado',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_matriculas(self, obj):
        """conta total de matriculas"""
        return obj.matriculas.count()

    def get_total_arrecadado(self, obj):
        """calcula total arrecadado (apenas matriculas pagas)"""
        return float(obj.total_arrecadado())

    def validate_carga_horaria(self, value):
        """validacao para carga horaria"""
        if value <= 0:
            raise serializers.ValidationError("Carga horaria deve ser maior que zero.")
        return value

    def validate_valor_inscricao(self, value):
        """validação para valor"""
        if value <= 0:
            raise serializers.ValidationError("Valor deve ser maior que zero.")
        return value


class MatriculaSerializer(serializers.ModelSerializer):
    """
    serializer para o model Matricula.
    """
    # campos aninhados para exibir dados completos do aluno e curso
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)
    valor_curso = serializers.DecimalField(
        source='curso.valor_inscricao',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Matricula
        fields = [
            'id',
            'aluno',
            'aluno_nome',
            'curso',
            'curso_nome',
            'valor_curso',
            'data_matricula',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        validacao customizada ao criar matricula.
        verifica se o aluno ja esta matriculado no curso.
        """
        aluno = data.get('aluno')
        curso = data.get('curso')

        # verifica se ja existe matricula (apenas ao criar, nao ao editar)
        if self.instance is None:  # Se instance é None, cria
            if Matricula.objects.filter(aluno=aluno, curso=curso).exists():
                raise serializers.ValidationError(
                    "Este aluno ja esta matriculado neste curso."
                )

        # verifica se o curso esta ativo
        if curso.status == 'INATIVO':
            raise serializers.ValidationError(
                "Nao eh possivel matricular em curso inativo."
            )

        return data


class MatriculaCreateSerializer(serializers.ModelSerializer):
    """
    serializer simplificado para criar matriculas.
    aceita apenas IDs de aluno e curso.
    """
    class Meta:
        model = Matricula
        fields = ['aluno', 'curso', 'data_matricula', 'status']

    def validate(self, data):
        """mesmas validacoes do serializer anterior"""
        aluno = data.get('aluno')
        curso = data.get('curso')

        if Matricula.objects.filter(aluno=aluno, curso=curso).exists():
            raise serializers.ValidationError(
                "este aluno ja esta matriculado neste curso."
            )

        if curso.status == 'INATIVO':
            raise serializers.ValidationError(
                "Nao eh possivel matricular em curso inativo."
            )

        return data