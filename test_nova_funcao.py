import unittest
from app import run
class TempoTotal(unittest.TestCase):
    def test_limite(self):
        data={"origem":"Natal","destino":"Alecrim","teto_reais":10,"teto_caminhada_min":10,"teto_total_min":20,"opcoes":[{"nome":"A","local":"Rua A","carro":15,"caminhada":5,"preco":5},{"nome":"B","local":"Rua B","carro":16,"caminhada":5,"preco":5}]}
        self.assertEqual([x["nome"] for x in run(data)["opcoes"]],["A"])
        del data["teto_total_min"]
        self.assertEqual(run(data)["dentro_do_limite"],2)
