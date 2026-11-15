import unittest
from app import run

class ParkingTests(unittest.TestCase):
    def test_filters_by_price_and_walking_time(self):
        data={"origem":"Natal","destino":"Praia","teto_reais":10,"teto_caminhada_min":15,"opcoes":[{"nome":"A","local":"Rua A","carro":10,"caminhada":5,"preco":8},{"nome":"B","local":"Rua B","carro":3,"caminhada":20,"preco":2},{"nome":"C","local":"Rua C","carro":8,"caminhada":3,"preco":10}]}
        result=run(data)
        self.assertEqual([x["nome"] for x in result["opcoes"]],["C","A"])
        self.assertIn("travelmode=walking",result["opcoes"][0]["mapa_caminhada"])

    def test_negative_budget_rejected(self):
        with self.assertRaises(ValueError):
            run({"origem":"Natal","destino":"Praia","teto_reais":-1,"teto_caminhada_min":10,"opcoes":[]})

if __name__=="__main__": unittest.main()
