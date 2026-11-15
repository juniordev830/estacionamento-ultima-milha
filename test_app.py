import json
from pathlib import Path
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

    def test_rejeita_custo_negativo(self):
        with self.assertRaises(ValueError):
            run(dict(origem="A", destino="B", teto_reais=-1, teto_caminhada_min=5, opcoes=[]))
