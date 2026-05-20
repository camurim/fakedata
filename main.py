#!/usr/bin/env python3

from faker import Faker
from rich.console import Console
from rich.panel import Panel
from datetime import datetime, timedelta, timezone
import pyfiglet
from typing import List
import argparse
import random
import re
import os
import ast
from decimal import Decimal




def parseargs():
    parser = argparse.ArgumentParser(
        prog="FakeData", description="Gera dados falsos para popular bancos de teste"
    )

    parser.add_argument(
        "-f",
        "--field",
        help="Lista de campos a serem populados (separados por vírgula).",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-t",
        "--table",
        help="Tabela a ser populada.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-m",
        "--minimum-age",
        help="Idade mínima das pessoas geradas.",
        type=int,
        required=False,
        default=1,
    )

    parser.add_argument(
        "-M",
        "--maximum-age",
        help="Idade máxima das pessoas geradas.",
        type=int,
        required=False,
        default=60,
    )

    parser.add_argument(
        "-n",
        "--number-of-registers",
        help="Número de Registros a serem gerados.",
        type=int,
        required=False,
        default=1,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Nome do arquivo de saída a ser gerado.",
        type=str,
        required=False,
    )

    parser.add_argument(
        "-p",
        "--mask-cpf-cnpj",
        help="Gera os CPFs/CNPJs com máscara.",
        action="store_true",
        required=False,
        default=False,
    )

    return parser.parse_args()


def current_datetime():
    weekdays = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    months = [
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]
    now = datetime.now()

    year = now.astimezone(timezone(timedelta(hours=-3))).strftime("%Y")
    month = int(now.astimezone(timezone(timedelta(hours=-3))).strftime("%-m")) - 1
    weekday = int(now.astimezone(timezone(timedelta(hours=-3))).strftime("%w"))
    day = now.astimezone(timezone(timedelta(hours=-3))).strftime("%d")
    time = now.astimezone(timezone(timedelta(hours=-3))).strftime("%H:%M:%S")

    return f"{weekdays[weekday]}, {day} de {months[month]} de {year} às {time}"


def print_header(p_msg: str):
    console = Console()
    title = pyfiglet.figlet_format(
        p_msg,
        font="big",
    )
    console.print(f"[yellow bold]{title}[yellow bold/]")
    console.print(
        Panel.fit(f"[bold white]{current_datetime()}[bold white/]", style="blue")
    )
    console.print("\n")


def get_random_genders():
    """
    Retorna pseudo-randomicamente um dos três valores:
    "MASCULINO", "FEMININO", ou "NÃO BINÁRIO".
    """
    # Lista dos valores possíveis
    valores = ["MASCULINO", "FEMININO", "NÃO BINÁRIO"]

    # Seleciona e retorna um valor aleatório da lista
    return random.choice(valores)


def split_fields(field_str: str) -> List[str]:
    """
    Divide a string de campos por vírgula, ignorando vírgulas dentro de parênteses ou aspas.
    """
    parts = []
    current = []
    paren_depth = 0
    in_single_quote = False
    in_double_quote = False
    
    for char in field_str:
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current.append(char)
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)
        elif in_single_quote or in_double_quote:
            current.append(char)
        elif char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            if paren_depth > 0:
                paren_depth -= 1
            current.append(char)
        elif char == ',' and paren_depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
            
    if current:
        parts.append("".join(current).strip())
        
    return parts


def parse_field(field_str: str):
    """
    Analisa um campo no formato 'coluna:provedor(args)' e extrai:
    - O nome da coluna.
    - O nome do provedor Faker (se houver).
    - Os argumentos posicionais e nomeados (se houver).
    """
    field_str = field_str.strip()
    if ":" not in field_str:
        col_name = field_str.replace("'", "")
        return col_name, None, [], {}
    
    col_name, provider_expr = field_str.split(":", 1)
    col_name = col_name.strip().replace("'", "")
    provider_expr = provider_expr.strip()
    
    expr = provider_expr
    if "(" not in expr:
        expr = f"{expr}()"
        
    try:
        tree = ast.parse(expr, mode='eval')
        if isinstance(tree.body, ast.Call):
            if isinstance(tree.body.func, ast.Name):
                provider_name = tree.body.func.id
            elif isinstance(tree.body.func, ast.Attribute):
                parts = []
                func = tree.body.func
                while isinstance(func, ast.Attribute):
                    parts.append(func.attr)
                    func = func.value
                if isinstance(func, ast.Name):
                    parts.append(func.id)
                parts.reverse()
                provider_name = ".".join(parts)
            else:
                provider_name = provider_expr.split("(")[0].strip()

            args = []
            for arg in tree.body.args:
                args.append(ast.literal_eval(arg))
                
            kwargs = {}
            for kw in tree.body.keywords:
                kwargs[kw.arg] = ast.literal_eval(kw.value)
                
            return col_name, provider_name, args, kwargs
    except Exception:
        pass
    
    provider_name = provider_expr.split("(")[0].strip()
    return col_name, provider_name, [], {}


def resolve_field_value(
    fake: Faker,
    col_name: str,
    provider_name: str | None,
    args: list,
    kwargs: dict,
    gender: str,
    mask_cpf_cnpj: bool,
    minimum_age: int,
    maximum_age: int,
    console: Console
):
    """
    Resolve o valor dinâmico ou estático baseado nas regras especificadas.
    """
    if provider_name:
        if provider_name.startswith("fake."):
            provider_name = provider_name[5:]
        elif provider_name.startswith("faker."):
            provider_name = provider_name[6:]

        method = getattr(fake, provider_name, None)
        if method and callable(method):
            try:
                val = method(*args, **kwargs)
                if provider_name in ["cpf", "cnpj"] and not mask_cpf_cnpj:
                    if isinstance(val, str):
                        val = re.sub(r"\D", "", val)
                return val
            except Exception as e:
                console.print(f"[yellow]Aviso: Falha ao executar o gerador '{provider_name}' para o campo '{col_name}': {e}. Valor preenchido com NULL.[/yellow]")
                return None
        else:
            console.print(f"[yellow]Aviso: O gerador '{provider_name}' não é um método válido do Faker. O campo '{col_name}' será preenchido com NULL.[/yellow]")
            return None
            
    col_lower = col_name.lower().strip()
    
    match col_lower:
        case "nome" | "nome_pessoa" | "nome_social":
            if gender == "MASCULINO":
                return fake.name_male()
            elif gender == "FEMININO":
                return fake.name_female()
            elif gender == "NÃO BINÁRIO":
                return fake.name_nonbinary()
            else:
                return fake.name()
        case "genero" | "gênero" | "identidade_genero":
            return gender
        case "cpf" | "cpf_pessoa":
            cpf: str = fake.cpf()
            if not mask_cpf_cnpj:
                cpf = re.sub(r"\D", "", cpf)
            return cpf
        case "cnpj":
            cnpj: str = fake.cnpj()
            if not mask_cpf_cnpj:
                cnpj = re.sub(r"\D", "", cnpj)
            return cnpj
        case "rg" | "rg_pessoa":
            return fake.rg()
        case "nis" | "nis_pessoa":
            return fake.ssn()
        case "endereco" | "endereço":
            return fake.address().replace('\n', ' ')
        case "telefone" | "fone" | "nr_telefone":
            return fake.phone_number()
        case "celular" | "cel" | "nr_celular":
            return fake.cellphone_number()
        case "nascimento" | "data_nascimento" | "dt_nascimento":
            return fake.date_of_birth(minimum_age=minimum_age, maximum_age=maximum_age)
        case "cadastro" | "data_cadastro" | "dt_cadastro":
            return fake.date_time_this_month()
        case "email" | "endereco_email":
            return fake.free_email()
        case "usuario" | "username" | "ususario":
            return fake.user_name()
        case "profissao" | "trabalho" | "ocupacao":
            if gender == "MASCULINO":
                return fake.job_male()
            elif gender == "FEMININO":
                return fake.job_female()
            else:
                return fake.job()
                
    method = getattr(fake, col_lower, None)
    if method and callable(method):
        try:
            return method()
        except Exception:
            pass
            
    return None


def format_sql_value(val) -> str:
    """
    Formata o valor gerado para uma representação válida em SQL INSERT, 
    de acordo com seu tipo primitivo.
    """
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float, Decimal)):
        return str(val)
    if hasattr(val, "strftime"):
        val_str = val.strftime("%Y-%m-%d %H:%M:%S") if hasattr(val, "hour") else val.strftime("%Y-%m-%d")
    else:
        val_str = str(val)
        
    val_str_escaped = val_str.replace("'", "''")
    return f"'{val_str_escaped}'"


def main():
    console = Console()
    fake = Faker("pt_BR")
    args = parseargs()

    table: str = ""
    field: str = ""
    number: int = 1

    if args.table:
        table = str(args.table).replace("'", "")

    if args.field:
        field = str(args.field)

    if args.number_of_registers:
        number = int(args.number_of_registers)

    print_header("FakeData Factory")

    raw_fields = split_fields(field)
    
    parsed_fields = []
    for rf in raw_fields:
        col_name, provider_name, p_args, p_kwargs = parse_field(rf)
        parsed_fields.append((col_name, provider_name, p_args, p_kwargs))
        
    col_names = [item[0] for item in parsed_fields]
    sql_fields_clause = ", ".join(col_names)
    
    ar_line: List[str] = []

    for _ in range(number):
        ar_values: List[str] = []
        gender: str = get_random_genders()

        for col_name, provider_name, p_args, p_kwargs in parsed_fields:
            val = resolve_field_value(
                fake=fake,
                col_name=col_name,
                provider_name=provider_name,
                args=p_args,
                kwargs=p_kwargs,
                gender=gender,
                mask_cpf_cnpj=args.mask_cpf_cnpj,
                minimum_age=args.minimum_age,
                maximum_age=args.maximum_age,
                console=console
            )
            ar_values.append(format_sql_value(val))

        values: str = ",".join(ar_values)
        ar_line.append(f"INSERT INTO {table} ({sql_fields_clause}) VALUES ({values});")

    console.print("\n".join(ar_line))

    if args.output:
        with open(os.path.expanduser(args.output), "w") as file:
            file.write("\n".join(ar_line))

        console.print(
            f"[bold blue]Arquivo de saída {args.output} gerado com sucesso![bold blue/]"
        )


if __name__ == "__main__":
    main()
