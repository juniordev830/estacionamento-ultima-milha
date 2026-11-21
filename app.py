'Compare pontos de estacionamento, com links para dirigir até lá e caminhar ao destino.'


from math import isfinite


def texto(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Use texto não vazio.")
    return value.strip()


def numero(value, minimo=0):
    if type(value) not in (int, float) or value < minimo or (
        type(value) is float and not isfinite(value)
    ):
        raise ValueError(f"Use um número finito a partir de {minimo}.")
    return value


from urllib.parse import urlencode


MODOS = {"carro": "driving", "a-pe": "walking", "bicicleta": "bicycling", "onibus": "transit"}


def _url(acao, parametros):
    url = "https://www.google.com/maps/" + acao + "?" + urlencode({"api": 1, **parametros})
    if len(url) > 2048:
        raise ValueError("O endereço gerado ultrapassa o limite do Google Maps.")
    return url


def rota(origem, destino, modo="carro", paradas=(), evitar_pedagios=False):
    pontos = [texto(parada) for parada in paradas]
    if len(pontos) > 3 or any("|" in parada for parada in pontos):
        raise ValueError("Use até 3 paradas por link e evite o caractere |.")
    if modo not in MODOS:
        raise ValueError(f"Modo desconhecido: {modo}")
    params = {"origin": texto(origem), "destination": texto(destino), "travelmode": MODOS[modo]}
    if pontos:
        params["waypoints"] = "|".join(pontos)
    if evitar_pedagios:
        params["avoid"] = "tolls"
    return _url("dir/", params)


def run(data):
    if not isinstance(data, dict):
        raise ValueError("A entrada deve ser um objeto JSON.")
    pontos = data.get("opcoes")
    if not isinstance(pontos, list) or len(pontos) > 100 or any(
        not isinstance(item, dict) for item in pontos
    ):
        raise ValueError("Informe até 100 opções de estacionamento como objetos.")
    origem, destino = texto(data["origem"]), texto(data["destino"])
    reais = numero(data["teto_reais"])
    caminhada = numero(data["teto_caminhada_min"])
    opcoes = []
    for item in pontos:
        dirigir, andar, custo = (numero(item[campo]) for campo in ("carro", "caminhada", "preco"))
        if custo > reais or andar > caminhada:
            continue
        try:
            total_minutos = dirigir + andar
        except OverflowError as exc:
            raise ValueError("A duração total não pode ser representada.") from exc
        if type(total_minutos) is float and not isfinite(total_minutos):
            raise ValueError("A duração total não pode ser representada.")

        local = texto(item["local"])
        opcoes.append({"nome": texto(item["nome"]), "total_minutos": total_minutos,
                       "custo": custo, "mapa_carro": rota(origem, local),
                       "mapa_caminhada": rota(local, destino, "a-pe")})
    opcoes.sort(key=lambda item: (item["total_minutos"], item["custo"], item["nome"].casefold()))
    return {"opcoes": opcoes, "dentro_do_limite": len(opcoes)}


import argparse
from contextlib import nullcontext
import sys
from relatorio_csv import escrever_csv
import json
from pathlib import Path


def objeto_sem_campos_repetidos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo JSON repetido: {chave!r}.")
        objeto[chave] = valor
    return objeto


def rejeitar_constante_json(constante):
    raise ValueError(f"Constante numérica inválida em JSON: {constante}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help="Arquivo JSON com os dados ou - para a entrada padrão")
    parser.add_argument("--csv", action="store_true", help="Exportar as opções de estacionamento e seus percursos em CSV")
    args = parser.parse_args()

    try:
        entrada = nullcontext(sys.stdin.buffer) if args.entrada == "-" else Path(args.entrada).open(encoding="utf-8-sig")
        with entrada as source:
            data = json.load(
                source,
                object_pairs_hook=objeto_sem_campos_repetidos,
                parse_constant=rejeitar_constante_json,
            )
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except RecursionError:
        parser.exit(2, "O JSON tem níveis de aninhamento demais.\n")
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if args.csv:
        escrever_csv(result, sys.stdout)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
