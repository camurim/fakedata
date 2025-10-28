#!/usr/bin/env python3

from faker import Faker
from rich.console import Console
from rich.panel import Panel
from datetime import date, datetime, timedelta, timezone
import pyfiglet
from typing import List
import argparse
import re

def parseargs():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--field",
        help="Lista de campos a serem populados (separados por vírgula).",
        type=ascii,
        required=True,
    )

    parser.add_argument(
        "-t",
        "--table",
        help="Tabela a ser populada.",
        type=ascii,
        required=True,
    )

    parser.add_argument(
        "-n",
        "--number-of-registers",
        help="Número de Registros a serem gerados.",
        type=int,
        required=False,
        default=1
    )

    parser.add_argument(
        "-m",
        "--mask-cpf",
        help="Gera os CPFs com máscara.",
        action="store_true",
        required=False,
        default=False
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

def main():
    console = Console()
    fake = Faker("pt_BR")
    args = parseargs()

    table:str = ""
    field:str = ""
    number:int = 1

    if args.table:
        table = str(args.table).replace("'","")

    if args.field:
        field = str(args.field).replace("'","")

    if args.number_of_registers:
        number = int(args.number_of_registers)

    print_header("FakeData Factory")

    ar_fields: list[str] = field.split(',')
    ar_fields = [i.replace("'","") for i in ar_fields]
    ar_values: list[str] = [] 
    ar_line: list[str] = [] 

    for _ in range(number):
        ar_values: list[str] = [] 
        for f in ar_fields:
            match f.lower().strip():
                case "nome" | "nome_pessoa":
                    ar_values.append(f"'{fake.name()}'")
                case "cpf" | "cpf_pessoa":
                    cpf: str = fake.cpf()
                    if not args.mask_cpf:
                        cpf = re.sub(r'\D', '', cpf)
                    ar_values.append(f"'{cpf}'")
                case "rg" | "rg_pessoa":
                    ar_values.append(f"'{fake.rg()}'")
                case "endereco" | "endereço":
                    ar_values.append(f"'{fake.address()}'")
                case "telefone" | "fone" | "nr_telefone" :
                    ar_values.append(f"'{fake.phone_number()}'")
                case "celular" | "cel" | "nr_celular" :
                    ar_values.append(f"'{fake.cellphone_number()}'")
                case _:
                    ar_values.append("NULL")

        values: str = ','.join(ar_values)
        ar_line.append(f"INSERT INTO {table} ({field}) VALUES ({values});")
        console.print("\n".join(ar_line))


if __name__ == "__main__":
    main()
