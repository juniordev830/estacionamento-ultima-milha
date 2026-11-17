import json
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

from app import run

ROOT = Path(__file__).resolve().parent


class ProjetoTest(unittest.TestCase):
    def test_exemplo_documentado(self):
        data = json.loads((ROOT / "exemplo.json").read_text(encoding="utf-8"))
        result = run(data)
        self.assertEqual(result['dentro_do_limite'], 1)

    def test_cli_aceita_json_utf8_com_bom(self):
        exemplo = (ROOT / "exemplo.json").read_text(encoding="utf-8")
        with TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "entrada.json"
            entrada.write_text(exemplo, encoding="utf-8-sig")
            resultado = subprocess.run(
                [sys.executable, str(ROOT / "app.py"), str(entrada)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
        self.assertEqual(json.loads(resultado.stdout), run(json.loads(exemplo)))

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
