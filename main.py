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
import csv
import io
from decimal import Decimal
import urllib.request
import json
import gzip

VALID_UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

UF_TO_ESTADO = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}


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

    parser.add_argument(
        "--format",
        help="Formato de saída: 'sql' (padrão) ou 'csv'.",
        type=str,
        required=False,
        default="sql",
        choices=["sql", "csv"],
    )

    parser.add_argument(
        "--csv-delimiter",
        help="Delimitador do CSV (padrão: ',').",
        type=str,
        required=False,
        default=",",
    )

    parser.add_argument(
        "-u",
        "--uf",
        help="Sigla do estado (UF) para filtrar os municípios gerados (ex: SP, RJ).",
        type=str,
        required=False,
    )

    args = parser.parse_args()
    if args.uf:
        uf_upper = args.uf.upper().strip()
        if uf_upper not in VALID_UFS:
            parser.error(
                f"UF inválida: '{args.uf}'. UFs válidas: {', '.join(sorted(VALID_UFS))}"
            )
    return args


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
        elif char == "(":
            paren_depth += 1
            current.append(char)
        elif char == ")":
            if paren_depth > 0:
                paren_depth -= 1
            current.append(char)
        elif char == "," and paren_depth == 0:
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
        tree = ast.parse(expr, mode="eval")
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


def fetch_municipios(uf: str | None, console: Console) -> List[List[str]]:
    """
    Busca a lista de municípios do IBGE (com cache local).
    Retorna uma lista de pares [nome_municipio, sigla_uf].
    """
    cache_path = os.path.expanduser("~/.fakedata_ibge_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception as e:
            console.print(f"[yellow]Aviso: Falha ao ler cache do IBGE: {e}[/yellow]")

    key = uf.upper().strip() if uf else "ALL"
    if key in cache:
        cached_data = cache[key]
        if (
            cached_data
            and isinstance(cached_data[0], list)
            and len(cached_data[0]) == 2
        ):
            return cached_data
        else:
            del cache[key]

    if uf:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{key}/municipios"
        target_name = f"municípios do estado {key}"
    else:
        url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
        target_name = "municípios de todo o Brasil"

    console.print(f"[blue]Buscando {target_name} na API pública do IBGE...[/blue]")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read()
            if response.info().get("Content-Encoding") == "gzip":
                content = gzip.decompress(content)
            data = json.loads(content.decode("utf-8"))

            municipios = []
            for item in data:
                nome = item.get("nome")
                sigla = None
                if uf:
                    sigla = key
                else:
                    microrregiao = item.get("microrregiao")
                    if microrregiao:
                        mesorregiao = microrregiao.get("mesorregiao")
                        if mesorregiao:
                            uf_data = mesorregiao.get("UF")
                            if uf_data:
                                sigla = uf_data.get("sigla")

                    if not sigla:
                        regiao_imediata = item.get("regiao-imediata")
                        if regiao_imediata:
                            regiao_intermediaria = regiao_imediata.get(
                                "regiao-intermediaria"
                            )
                            if regiao_intermediaria:
                                uf_data = regiao_intermediaria.get("UF")
                                if uf_data:
                                    sigla = uf_data.get("sigla")

                    if not sigla:
                        sigla = "SP"
                if nome and sigla:
                    municipios.append([nome, sigla.upper()])

            if not municipios:
                console.print(
                    f"[yellow]Aviso: Nenhum município retornado pela API do IBGE para a chave '{key}'.[/yellow]"
                )
                return []

            cache[key] = municipios
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception as e:
                console.print(
                    f"[yellow]Aviso: Falha ao salvar cache do IBGE: {e}[/yellow]"
                )

            return municipios
    except Exception as e:
        console.print(f"[red]Erro ao buscar dados do IBGE na API pública: {e}.[/red]")
        return []


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
    console: Console,
    municipio_nome: str | None = None,
    uf_sigla: str | None = None,
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
                console.print(
                    f"[yellow]Aviso: Falha ao executar o gerador '{provider_name}' para o campo '{col_name}': {e}. Valor preenchido com NULL.[/yellow]"
                )
                return None
        else:
            console.print(
                f"[yellow]Aviso: O gerador '{provider_name}' não é um método válido do Faker. O campo '{col_name}' será preenchido com NULL.[/yellow]"
            )
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
        case "nome_mae" | "nomemae" | "nm_mae":
            return fake.name_female()
        case "nome_pai" | "nomepai" | "nm_pai":
            return fake.name_male()
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
            if municipio_nome and uf_sigla:
                logradouro_completo = f"{fake.street_prefix()} {fake.street_name()}, {random.randint(1, 9999)}"
                bairro = fake.neighborhood()
                cep = fake.postcode()
                return f"{logradouro_completo} {bairro} {cep}"
            return fake.address().replace("\n", " ")
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
        case (
            "numero"
            | "numero_logradouro"
            | "nr_logradouro"
            | "numero_endereco"
            | "nr_endereco"
            | "numero_residencia"
        ):
            return random.randint(1, 9999)
        case "complemento_numero" | "apartamento" | "apto" | "nr_apartamento":
            return random.randint(1, 999)
        case "andar" | "nr_andar":
            return random.randint(1, 30)
        case "bloco" | "nr_bloco":
            return random.randint(1, 20)
        case "quantidade" | "qtd" | "qtde":
            return random.randint(1, 100)
        case "idade":
            return random.randint(minimum_age, maximum_age)
        case "municipio" | "município" | "cidade":
            if municipio_nome:
                return municipio_nome
            return fake.city()
        case "uf" | "sigla_uf" | "estado_sigla":
            if uf_sigla:
                return uf_sigla
            return fake.state_abbr()
        case "estado":
            if uf_sigla and uf_sigla in UF_TO_ESTADO:
                return UF_TO_ESTADO[uf_sigla]
            return fake.state()

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
        val_str = (
            val.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(val, "hour")
            else val.strftime("%Y-%m-%d")
        )
    else:
        val_str = str(val)

    val_str_escaped = val_str.replace("'", "''")
    return f"'{val_str_escaped}'"


def format_csv_value(val) -> str:
    """
    Formata o valor gerado para uma representação válida em CSV.
    Valores None se tornam string vazia.
    Datas são formatadas como string ISO.
    """
    if val is None:
        return ""
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    if isinstance(val, (int, float, Decimal)):
        return str(val)
    if hasattr(val, "strftime"):
        return (
            val.strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(val, "hour")
            else val.strftime("%Y-%m-%d")
        )
    return str(val)


def main():
    console = Console()
    fake = Faker("pt_BR")
    args = parseargs()

    table: str = ""
    field: str = ""
    number: int = 1
    output_format: str = "sql"

    if args.table:
        table = str(args.table).replace("'", "")

    if args.field:
        field = str(args.field)

    if args.number_of_registers:
        number = int(args.number_of_registers)

    if args.format:
        output_format = str(args.format).lower()

    print_header("FakeData Factory")

    raw_fields = split_fields(field)

    parsed_fields = []
    for rf in raw_fields:
        col_name, provider_name, p_args, p_kwargs = parse_field(rf)
        parsed_fields.append((col_name, provider_name, p_args, p_kwargs))

    col_names = [item[0] for item in parsed_fields]

    # Verifica se há necessidade de carregar municípios
    needs_municipios = False
    for col_name, provider_name, _, _ in parsed_fields:
        if not provider_name:
            col_lower = col_name.lower().strip()
            if col_lower in [
                "municipio",
                "município",
                "cidade",
                "endereco",
                "endereço",
                "uf",
                "sigla_uf",
                "estado_sigla",
                "estado",
            ]:
                needs_municipios = True
                break

    municipios_list = None
    if needs_municipios:
        uf = args.uf.upper().strip() if args.uf else None
        municipios_list = fetch_municipios(uf, console)

    if output_format == "csv":
        delimiter = args.csv_delimiter
        # Gera os dados em formato CSV
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)

        # Cabeçalho com os nomes das colunas
        writer.writerow(col_names)

        for _ in range(number):
            row_values = []
            gender: str = get_random_genders()

            municipio_nome = None
            uf_sigla = None
            if municipios_list:
                item_muni = random.choice(municipios_list)
                municipio_nome = item_muni[0]
                uf_sigla = item_muni[1]
            else:
                if args.uf:
                    uf_sigla = args.uf.upper().strip()
                else:
                    uf_sigla = random.choice(list(VALID_UFS))
                municipio_nome = fake.city()

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
                    console=console,
                    municipio_nome=municipio_nome,
                    uf_sigla=uf_sigla,
                )
                row_values.append(format_csv_value(val))

            writer.writerow(row_values)

        output_content = csv_buffer.getvalue().rstrip("\r\n")
        csv_buffer.close()

        console.print(output_content)

        if args.output:
            output_path = args.output
            # Se o usuário não especificou extensão .csv, ajustar
            if not output_path.lower().endswith(".csv"):
                output_path = os.path.splitext(output_path)[0] + ".csv"

            with open(os.path.expanduser(output_path), "w", newline="") as file:
                file.write(output_content + "\n")

            console.print(
                f"[bold blue]Arquivo de saída {output_path} gerado com sucesso![bold blue/]"
            )
    else:
        # Formato SQL (comportamento original)
        sql_fields_clause = ", ".join(col_names)
        ar_line: List[str] = []

        for _ in range(number):
            ar_values: List[str] = []
            gender: str = get_random_genders()

            municipio_nome = None
            uf_sigla = None
            if municipios_list:
                item_muni = random.choice(municipios_list)
                municipio_nome = item_muni[0]
                uf_sigla = item_muni[1]
            else:
                if args.uf:
                    uf_sigla = args.uf.upper().strip()
                else:
                    uf_sigla = random.choice(list(VALID_UFS))
                municipio_nome = fake.city()

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
                    console=console,
                    municipio_nome=municipio_nome,
                    uf_sigla=uf_sigla,
                )
                ar_values.append(format_sql_value(val))

            values: str = ",".join(ar_values)
            ar_line.append(
                f"INSERT INTO {table} ({sql_fields_clause}) VALUES ({values});"
            )

        console.print("\n".join(ar_line))

        if args.output:
            with open(os.path.expanduser(args.output), "w") as file:
                file.write("\n".join(ar_line))

            console.print(
                f"[bold blue]Arquivo de saída {args.output} gerado com sucesso![bold blue/]"
            )


if __name__ == "__main__":
    main()
