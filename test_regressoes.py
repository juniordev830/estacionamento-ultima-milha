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

    def test_reject_unexpected_input_shapes(self):
        base = {"origem": "Natal", "destino": "Centro", "teto_reais": 20,
                "teto_caminhada_min": 20}
        for options in ("texto", [None], [1], [{}] * 101):
            with self.subTest(options=str(options)[:20]), self.assertRaisesRegex(ValueError, "100"):
                run({**base, "opcoes": options})
        with self.assertRaisesRegex(ValueError, "objeto JSON"):
            run([])

    def test_equal_cost_and_duration_are_sorted_by_name(self):
        base = {"origem": "Natal", "destino": "Centro", "teto_reais": 20,
                "teto_caminhada_min": 20,
                "opcoes": [{"nome": name, "local": "Natal", "carro": 10,
                            "caminhada": 5, "preco": 8}
                           for name in ("Zona B", "Zona A")]}
        result = run(base)
        self.assertEqual([item["nome"] for item in result["opcoes"]], ["Zona A", "Zona B"])


if __name__=="__main__": unittest.main()
