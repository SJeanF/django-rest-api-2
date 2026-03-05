import json

from django.test import TestCase
from order.serializers import OrderSerializer
from order.factories import OrderFactory
from product.factories import ProductFactory


class OrderSerializerTest(TestCase):
    def setUp(self):
        # Prepara os dados
        self.product1 = ProductFactory(price=10)
        self.product2 = ProductFactory(price=20)
        self.product3 = ProductFactory(price=5)

        # Cria um pedido com 3 produtos
        self.order = OrderFactory(product=(self.product1, self.product2, self.product3))

    def test_order_serialization(self):
        """Testa se os dados lidos do banco são transformados corretamente em JSON/Dict."""

        # Passa a instância do modelo para o serializer
        serializer = OrderSerializer(self.order)
        data = serializer.data

        # 1. Testa o campo 'total' calculado no get_total()
        # 10.50 + 20.00 + 5.00 = 35.50
        self.assertEqual(data["total"], 35)

        # 2. Testa se os produtos aninhados estão presentes
        self.assertEqual(len(data["product"]), 3)

        # 3. Verifica se as chaves corretas estão presentes no dicionário final
        self.assertIn("product", data)
        self.assertIn("total", data)
