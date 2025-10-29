## FAKEDATA

### Instlação

#### Ambiente virtual (Virtual Environment)

```bash
python -m venv .venv
```

### Ativação do ambiente virtual python

```bash
source .venv/bin/activate
```

### Instalação das dependências

```bash
 pip3 install -r requirements.txt -U
```

### Execução

#### Ajunda online

```
usage: FakeData [-h] -f FIELD -t TABLE [-m MINIMUM_AGE] [-M MAXIMUM_AGE] [-n NUMBER_OF_REGISTERS] [-o OUTPUT] [-p]

Gera dados falsos para popular bancos de teste

options:
  -h, --help            show this help message and exit
  -f, --field FIELD     Lista de campos a serem populados (separados por vírgula).
  -t, --table TABLE     Tabela a ser populada.
  -m, --minimum-age MINIMUM_AGE
                        Idade mínima das pessoas geradas.
  -M, --maximum-age MAXIMUM_AGE
                        Idade máxima das pessoas geradas.
  -n, --number-of-registers NUMBER_OF_REGISTERS
                        Número de Registros a serem gerados.
  -o, --output OUTPUT   Nome do arquivo de saída a ser gerado.
  -p, --mask-cpf-cnpj   Gera os CPFs/CNPJs com máscara.
```

#### Execução básica

* Gerar 20 registros para a tabela pessoa para os campos nome, cpf, rg e telefone.

```bash
python3 main.py -t "pessoa" -f "nome,cpf,rg,telefone" -n 20
```

* Gerar 50 registros para a tabela pessoa para os campos nome, cpf, rg, nis, genero, telefone e profissao, determinando a idade mínima das pessoas como 18 e a idade máxima como 60.

```bash
python3 main.py -t "pessoa" -f "nome,cpf,rg,nis,genero,telefone,profissao" -m 18 -M 60 -n 50
```
