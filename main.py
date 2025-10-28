#!/usr/bin/env python3

from faker import Faker
from rich.console import Console
from typing import List
import argparse

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

    return parser.parse_args()


def main():
    console = Console()
    fake = Faker("pt_BR")
    args = parseargs()

    table:str = ""
    field:str = ""
    number:int = 1

    if args.table:
        table = str(args.table)

    if args.field:
        field = str(args.field)

    if args.number_of_registers:
        number = int(args.number_of_registers)

    ar_fields: list[str] = field.split(",")
    
    for i in range(number):
        ar_linha: list[str] = [] 
        for f in ar_fields:
            match f.lower():
                case "nome":
                    ar_linha.append(fake.name())
                case "cpf":
                    ar_linha.append(fake.cpf())
                case "rg":
                    ar_linha.append(fake.rg())
                case "endereco" | "endereço":
                    pass
                case "telefone" | "fone" | "celular":
                    pass
        pass

if __name__ == "__main__":
    main()
