import csv


def celula(valor):
    """Mantém texto com aparência de fórmula como texto em planilhas."""
    if not isinstance(valor, str):
        return valor
    prefixos = ("=", "+", "-", "@", "＝", "＋", "－", "＠")
    if valor.lstrip().startswith(prefixos) or valor.startswith(("\t", "\r", "\n")):
        return "'" + valor
    return valor


def linhas(relatorio):
    for item in relatorio['opcoes']:
        yield (item['nome'], item['total_minutos'], item['custo'], item['mapa_carro'], item['mapa_caminhada'],)


def escrever_csv(relatorio, destino):
    escritor = csv.writer(destino, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\n")
    escritor.writerow(('nome', 'total_minutos', 'custo', 'mapa_carro', 'mapa_caminhada'))
    for linha in linhas(relatorio):
        escritor.writerow([celula(valor) for valor in linha])
