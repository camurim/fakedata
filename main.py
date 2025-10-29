#!/usr/bin/env python3

from faker import Faker
from rich.console import Console
from rich.panel import Panel
from datetime import date, datetime, timedelta, timezone
import pyfiglet
from typing import List
import argparse
import random
import re
import os


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
        field = str(args.field).replace("'", "")

    if args.number_of_registers:
        number = int(args.number_of_registers)

    print_header("FakeData Factory")

    ar_fields: List[str] = field.split(",")
    ar_fields = [i.replace("'", "") for i in ar_fields]
    ar_values: List[str] = []
    ar_line: List[str] = []

    for _ in range(number):
        ar_values: List[str] = []
        gender: str = get_random_genders()

        for f in ar_fields:
            match f.lower().strip():
                case "nome" | "nome_pessoa" | "nome_social":
                    if gender == "MASCULINO":
                        ar_values.append(f"'{fake.name_male()}'")
                    elif gender == "FEMININO":
                        ar_values.append(f"'{fake.name_female()}'")
                    elif gender == "NÃO BINÁRIO":
                        ar_values.append(f"'{fake.name_nonbinary()}'")
                    else:
                        ar_values.append(f"'{fake.name()}'")
                case "genero" | "gênero" | "identidade_genero":
                    ar_values.append(f"'{gender}'")
                case "cpf" | "cpf_pessoa":
                    cpf: str = fake.cpf()
                    if not args.mask_cpf_cnpj:
                        cpf = re.sub(r"\D", "", cpf)
                    ar_values.append(f"'{cpf}'")
                case "cnpj":
                    cnpj: str = fake.cnpj()
                    if not args.mask_cpf_cnpj:
                        cnpj = re.sub(r"\D", "", cnpj)
                    ar_values.append(f"'{cnpj}'")
                case "rg" | "rg_pessoa":
                    ar_values.append(f"'{fake.rg()}'")
                case "nis" | "nis_pessoa":
                    ar_values.append(f"'{fake.ssn()}'")
                case "endereco" | "endereço":
                    ar_values.append(f"'{fake.address()}'")
                case "telefone" | "fone" | "nr_telefone":
                    ar_values.append(f"'{fake.phone_number()}'")
                case "celular" | "cel" | "nr_celular":
                    ar_values.append(f"'{fake.cellphone_number()}'")
                case "nascimento" | "data_nascimento" | "dt_nascimento":
                    ar_values.append(
                        f"'{fake.date_of_birth(minimum_age=args.minimum_age, maximum_age=args.maximum_age)}'"
                    )
                case "cadastro" | "data_cadastro" | "dt_cadastro":
                    ar_values.append(f"'{fake.date_time_this_month()}'")
                case "email" | "endereco_email":
                    ar_values.append(f"'{fake.free_email()}'")
                case "ususario" | "username":
                    ar_values.append(f"'{fake.user_name()}'")
                case "profissao" | "trabalho" | "ocupacao":
                    if gender == "MASCULINO":
                        ar_values.append(f"'{fake.job_male()}'")
                    elif gender == "FEMININO":
                        ar_values.append(f"'{fake.job_female()}'")
                    else:
                        ar_values.append(f"'{fake.job()}'")

                case _:
                    ar_values.append("NULL")

        values: str = ",".join(ar_values)
        ar_line.append(f"INSERT INTO {table} ({field}) VALUES ({values});")

    console.print("\n".join(ar_line))

    if args.output:
        with open(os.path.expanduser(args.output), "w") as file:
            file.write("\n".join(ar_line))

        console.print(
            f"[bold blue]Arquivo de saída {args.output} gerado com sucesso![bold blue/]"
        )


if __name__ == "__main__":
    main()
