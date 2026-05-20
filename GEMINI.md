# GEMINI.md - Fakedata

Este projeto é uma ferramenta de linha de comando (CLI) escrita em Python projetada para gerar dados fictícios (fake data) em formato de comandos SQL `INSERT`, facilitando o povoamento de bancos de dados de teste.

## Visão Geral do Projeto

- **Propósito:** Gerar registros aleatórios e realistas para tabelas de banco de dados.
- **Tecnologias Principais:**
  - [Python 3](https://www.python.org/)
  - [Faker](https://faker.readthedocs.io/): Para geração dos dados (configurado para `pt_BR`).
  - [Rich](https://rich.readthedocs.io/): Para formatação visual no terminal.
  - [Pyfiglet](https://github.com/pwaller/pyfiglet): Para exibição do cabeçalho em ASCII art.
- **Arquitetura:** Script único (`main.py`) que processa argumentos via `argparse` e gera strings SQL.

## Comandos de Instalação e Execução

### Configuração do Ambiente

1. **Criar Ambiente Virtual:**
   ```bash
   python -m venv .venv
   ```

2. **Ativar Ambiente Virtual:**
   ```bash
   source .venv/bin/activate
   ```

3. **Instalar Dependências:**
   ```bash
   pip install -r requirements.txt -U
   ```

### Execução da Ferramenta

O script principal é o `main.py`. Abaixo estão os parâmetros fundamentais:

- `-t`, `--table`: Nome da tabela SQL.
- `-f`, `--field`: Lista de campos separados por vírgula (ex: `nome,cpf,telefone`).
- `-n`, `--number-of-registers`: Quantidade de registros a gerar (padrão: 1).
- `-m`, `--minimum-age` / `-M`, `--maximum-age`: Faixa etária para campos de data de nascimento.
- `-o`, `--output`: Caminho para salvar o resultado em um arquivo.
- `-p`, `--mask-cpf-cnpj`: Aplicar máscara em CPFs e CNPJs.

**Exemplo de uso:**
```bash
python3 main.py -t "usuarios" -f "nome,cpf,email,telefone" -n 50 -o "popula_usuarios.sql"
```

## Convenções de Desenvolvimento

- **Localidade:** O gerador está fixado para a localidade `pt_BR`.
- **Campos Suportados:**
  - `nome`, `nome_pessoa`, `nome_social` (sensível ao gênero gerado).
  - `genero`, `gênero`, `identidade_genero`.
  - `cpf`, `cnpj`, `rg`, `nis`.
  - `endereco`, `telefone`, `celular`, `email`.
  - `nascimento`, `cadastro`, `profissao`.
- **Saída:** O padrão é imprimir os comandos `INSERT INTO ...` diretamente no terminal (stdout).
- **Estilo de Código:** Segue padrões idiomáticos de Python com tipagem básica (`typing.List`).
