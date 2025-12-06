
-- Tabela: Aluno
-- Armazena informações dos alunos cadastrados
CREATE TABLE core_aluno (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    data_ingresso DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar performance de busca
CREATE INDEX idx_aluno_nome ON core_aluno(nome);
CREATE INDEX idx_aluno_cpf ON core_aluno(cpf);
CREATE INDEX idx_aluno_email ON core_aluno(email);

-- Comentários explicativos
COMMENT ON TABLE core_aluno IS 'Tabela de cadastro de alunos da academia';
COMMENT ON COLUMN core_aluno.cpf IS 'CPF do aluno (apenas números, 11 dígitos)';
COMMENT ON COLUMN core_aluno.data_ingresso IS 'Data de entrada do aluno na academia';


-- Tabela: Curso
-- Armazena informações dos cursos disponíveis
CREATE TABLE core_curso (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    carga_horaria INTEGER NOT NULL CHECK (carga_horaria > 0),
    valor_inscricao NUMERIC(10, 2) NOT NULL CHECK (valor_inscricao > 0),
    status VARCHAR(10) NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'INATIVO')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_curso_nome ON core_curso(nome);
CREATE INDEX idx_curso_status ON core_curso(status);

-- Comentários
COMMENT ON TABLE core_curso IS 'Tabela de cursos oferecidos pela academia';
COMMENT ON COLUMN core_curso.carga_horaria IS 'Carga horária total do curso em horas';
COMMENT ON COLUMN core_curso.valor_inscricao IS 'Valor da inscrição no curso';
COMMENT ON COLUMN core_curso.status IS 'Status do curso: ATIVO ou INATIVO';


-- Tabela: Matrícula
-- Relaciona alunos com cursos
CREATE TABLE core_matricula (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    data_matricula DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(10) NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('PAGO', 'PENDENTE')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves estrangeiras
    CONSTRAINT fk_matricula_aluno 
        FOREIGN KEY (aluno_id) 
        REFERENCES core_aluno(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_matricula_curso 
        FOREIGN KEY (curso_id) 
        REFERENCES core_curso(id) 
        ON DELETE CASCADE,
    
    -- Constraint única: um aluno não pode se matricular 2x no mesmo curso
    CONSTRAINT unique_aluno_curso 
        UNIQUE(aluno_id, curso_id)
);

-- Índices para otimizar consultas
CREATE INDEX idx_matricula_aluno ON core_matricula(aluno_id);
CREATE INDEX idx_matricula_curso ON core_matricula(curso_id);
CREATE INDEX idx_matricula_status ON core_matricula(status);
CREATE INDEX idx_matricula_data ON core_matricula(data_matricula);

-- Comentários
COMMENT ON TABLE core_matricula IS 'Tabela de matrículas (relacionamento entre alunos e cursos)';
COMMENT ON COLUMN core_matricula.status IS 'Status do pagamento: PAGO ou PENDENTE';
COMMENT ON CONSTRAINT unique_aluno_curso ON core_matricula IS 'Impede matrícula duplicada';


-- Consultas

-- 1. Listar todos os alunos com total de matrículas
SELECT 
    a.id,
    a.nome,
    a.email,
    a.cpf,
    COUNT(m.id) as total_matriculas
FROM core_aluno a
LEFT JOIN core_matricula m ON a.id = m.aluno_id
GROUP BY a.id, a.nome, a.email, a.cpf
ORDER BY total_matriculas DESC;


-- 2. Relatório financeiro por aluno
SELECT 
    a.id,
    a.nome,
    a.cpf,
    COUNT(m.id) as total_matriculas,
    SUM(CASE WHEN m.status = 'PAGO' THEN c.valor_inscricao ELSE 0 END) as total_pago,
    SUM(CASE WHEN m.status = 'PENDENTE' THEN c.valor_inscricao ELSE 0 END) as total_devido,
    SUM(c.valor_inscricao) as total_geral
FROM core_aluno a
LEFT JOIN core_matricula m ON a.id = m.aluno_id
LEFT JOIN core_curso c ON m.curso_id = c.id
GROUP BY a.id, a.nome, a.cpf
ORDER BY total_geral DESC;


-- 3. Cursos mais populares
SELECT 
    c.id,
    c.nome,
    c.carga_horaria,
    c.valor_inscricao,
    c.status,
    COUNT(m.id) as total_matriculas,
    SUM(CASE WHEN m.status = 'PAGO' THEN 1 ELSE 0 END) as matriculas_pagas,
    SUM(CASE WHEN m.status = 'PAGO' THEN c.valor_inscricao ELSE 0 END) as total_arrecadado
FROM core_curso c
LEFT JOIN core_matricula m ON c.id = m.curso_id
GROUP BY c.id, c.nome, c.carga_horaria, c.valor_inscricao, c.status
ORDER BY total_matriculas DESC;


-- 4. Matrículas pendentes de pagamento
SELECT 
    a.nome as aluno_nome,
    a.email,
    c.nome as curso_nome,
    c.valor_inscricao,
    m.data_matricula,
    CURRENT_DATE - m.data_matricula as dias_pendente
FROM core_matricula m
INNER JOIN core_aluno a ON m.aluno_id = a.id
INNER JOIN core_curso c ON m.curso_id = c.id
WHERE m.status = 'PENDENTE'
ORDER BY m.data_matricula ASC;


-- 5. Dashboard
SELECT 
    (SELECT COUNT(*) FROM core_aluno) as total_alunos,
    (SELECT COUNT(*) FROM core_curso WHERE status = 'ATIVO') as cursos_ativos,
    (SELECT COUNT(*) FROM core_matricula) as total_matriculas,
    (SELECT COUNT(*) FROM core_matricula WHERE status = 'PAGO') as matriculas_pagas,
    (SELECT COUNT(*) FROM core_matricula WHERE status = 'PENDENTE') as matriculas_pendentes,
    (SELECT COALESCE(SUM(c.valor_inscricao), 0) 
     FROM core_matricula m 
     INNER JOIN core_curso c ON m.curso_id = c.id 
     WHERE m.status = 'PAGO') as total_pago,
    (SELECT COALESCE(SUM(c.valor_inscricao), 0) 
     FROM core_matricula m 
     INNER JOIN core_curso c ON m.curso_id = c.id 
     WHERE m.status = 'PENDENTE') as total_pendente;


-- exemplos para testes

INSERT INTO core_aluno (nome, email, cpf, data_ingresso) VALUES
('João Silva', 'joao@email.com', '12345678901', '2024-01-15'),
('Maria Santos', 'maria@email.com', '98765432109', '2024-02-20'),
('Pedro Oliveira', 'pedro@email.com', '45678912345', '2024-03-10');

INSERT INTO core_curso (nome, carga_horaria, valor_inscricao, status) VALUES
('Python Avançado', 80, 1500.00, 'ATIVO'),
('Django Web Development', 120, 2000.00, 'ATIVO'),
('Data Science com Python', 100, 1800.00, 'ATIVO'),
('Machine Learning Básico', 60, 1200.00, 'INATIVO');

INSERT INTO core_matricula (aluno_id, curso_id, data_matricula, status) VALUES
(1, 1, '2024-01-20', 'PAGO'),
(1, 2, '2024-02-15', 'PENDENTE'),
(2, 1, '2024-02-25', 'PAGO'),
(2, 3, '2024-03-01', 'PAGO'),
(3, 2, '2024-03-15', 'PENDENTE');