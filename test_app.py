from tempfile import TemporaryDirectory
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['dentro_do_limite'], 1)

    def test_cli_com_exemplo(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), str(ROOT / "exemplo.json")],
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        self.assertEqual(json.loads(result.stdout)['dentro_do_limite'], 1)

    def test_rejeita_dados_incompletos(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            run({})

    def test_limites_inclusivos(self):
        item = dict(nome="A", local="Natal", carro=10, caminhada=5, preco=20)
        result = run(dict(origem="A", destino="B", teto_reais=20, teto_caminhada_min=5, opcoes=[item, dict(item, preco=21), dict(item, caminhada=6)]))
        self.assertEqual(result["dentro_do_limite"], 1)
        self.assertEqual(result["opcoes"][0]["total_minutos"], 15)

    def test_soma_de_duracoes_deve_ser_finita(self):
        data = {
            "origem": "Natal", "destino": "Praia",
            "teto_reais": 20, "teto_caminhada_min": 1e308,
            "opcoes": [{"nome": "A", "local": "Rua A", "carro": 1e308, "caminhada": 1e308, "preco": 10}],
        }
        with self.assertRaisesRegex(ValueError, "duração total"):
            run(data)

    def test_duracoes_inteiras_sao_somadas_sem_conversao(self):
        tempo = 10 ** 400
        data = {
            "origem": "Natal", "destino": "Praia",
            "teto_reais": 20, "teto_caminhada_min": 10,
            "opcoes": [{"nome": "A", "local": "Rua A", "carro": tempo, "caminhada": 5, "preco": 10}],
        }
        self.assertEqual(run(data)["opcoes"][0]["total_minutos"], tempo + 5)

    def test_rejeita_custo_negativo(self):
        with self.assertRaises(ValueError):
            run(dict(origem="A", destino="B", teto_reais=-1, teto_caminhada_min=5, opcoes=[]))

    def test_cli_aceita_json_com_bom(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-bom.json"
            arquivo.write_text(exemplo, encoding="utf-8-sig")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
        self.assertEqual(json.loads(result.stdout), run(json.loads(exemplo)))

    def test_cli_rejeita_chave_json_repetida(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8").lstrip()
        chave = next(iter(json.loads(exemplo)))
        conteudo = "{" + json.dumps(chave) + ": null," + exemplo[1:]
        with tempfile.TemporaryDirectory() as diretorio:
            arquivo = Path(diretorio) / "exemplo-repetido.json"
            arquivo.write_text(conteudo, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(arquivo)],
                capture_output=True, text=True, encoding="utf-8",
            )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("Campo JSON repetido", result.stderr)


class JsonEstritoCliTest(unittest.TestCase):
    def test_cli_rejeita_constantes_numericas_nao_padronizadas(self):
        exemplo = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.json"
            for constante in ("NaN", "Infinity", "-Infinity"):
                with self.subTest(constante=constante):
                    exemplo["metadados"] = {"observacao": "CONSTANTE_TESTE"}
                    entrada.write_text(
                        json.dumps(exemplo).replace('"CONSTANTE_TESTE"', constante),
                        encoding="utf-8",
                    )
                    resultado = subprocess.run(
                        [sys.executable, str(ROOT / "app.py"), str(entrada)],
                        capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(resultado.returncode, 2)
                    self.assertIn(constante, resultado.stderr)
                    self.assertEqual(resultado.stdout, "")


class CriterioEstacionamentoTest(unittest.TestCase):
    def dados(self):
        return dict(origem="A", destino="B", teto_reais=20, teto_caminhada_min=10,
                    opcoes=[dict(nome="Rapido", local="C", carro=1, caminhada=5, preco=10),
                            dict(nome="Barato", local="D", carro=9, caminhada=3, preco=5),
                            dict(nome="Perto", local="E", carro=15, caminhada=1, preco=8)])

    def test_criterios(self):
        from app import run
        for criterio, primeiro in (("tempo", "Rapido"), ("preco", "Barato"), ("caminhada", "Perto")):
            with self.subTest(criterio=criterio):
                result = run(dict(self.dados(), ordenar_por=criterio))
                self.assertEqual(result["opcoes"][0]["nome"], primeiro)

    def test_padrao_compativel(self):
        from app import run
        self.assertNotIn("minutos_caminhada", run(self.dados())["opcoes"][0])

    def test_limites_continuam_validos(self):
        from app import run
        result = run(dict(self.dados(), ordenar_por="preco", teto_reais=4))
        self.assertEqual(result["opcoes"], [])

    def test_rejeita_criterio(self):
        from app import run
        with self.assertRaises(ValueError):
            run(dict(self.dados(), ordenar_por="desconhecido"))
