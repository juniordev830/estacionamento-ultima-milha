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
    origem, destino = texto(data["origem"]), texto(data["destino"])
    reais = numero(data["teto_reais"])
    caminhada = numero(data["teto_caminhada_min"])
    opcoes = []
    for item in data["opcoes"]:
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
    opcoes.sort(key=lambda item: (item["total_minutos"], item["custo"]))
    return {"opcoes": opcoes, "dentro_do_limite": len(opcoes)}


import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="Arquivo JSON com os dados")
    args = parser.parse_args()

    try:
        with args.entrada.open(encoding="utf-8-sig") as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError("A entrada deve ser um objeto JSON.")
        result = run(data)
    except (KeyError, TypeError, ValueError, OSError) as exc:
        parser.exit(2, f"Erro nos dados ou na execução: {exc}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
