import json

from django.test import TestCase
from order.models import Order
from order.serializers import OrderSerializer
from order.factories import OrderFactory, UserFactory
from product.factories import ProductFactory, CategoryFactory

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class OrderModelTest(TestCase):
    def setUp(self):
        # Cria o usuário e os produtos que usaremos nos testes
        self.user = UserFactory()
        self.product1 = ProductFactory(price=15.00)
        self.product2 = ProductFactory(price=25.00)

    def test_order_creation(self):
        """Testa se o pedido é criado corretamente com seus relacionamentos."""

        # Cria a ordem passando a tupla/lista de produtos para acionar o @factory.post_generation
        order = OrderFactory(user=self.user, product=(self.product1, self.product2))

        # Verifica se o pedido foi salvo no banco
        self.assertEqual(Order.objects.count(), 1)

        # Verifica se o usuário associado é o correto
        self.assertEqual(order.user, self.user)

        # Verifica se os produtos foram adicionados corretamente na relação M2M
        self.assertEqual(order.product.count(), 2)
        self.assertIn(self.product1, order.product.all())
        self.assertIn(self.product2, order.product.all())


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


class TestOrderViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="technology")
        self.product = ProductFactory(
            title="mouse", price=100, category=[self.category]
        )
        self.order = OrderFactory(product=[self.product])

    def test_order(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order_data = json.loads(response.content)
        self.assertEqual(order_data[0]["product"][0]["title"], self.product.title)
        self.assertEqual(order_data[0]["product"][0]["price"], self.product.price)
        self.assertEqual(order_data[0]["product"][0]["active"], self.product.active)
        self.assertEqual(
            order_data[0]["product"][0]["category"][0]["title"],
            self.category.title,
        )

    def test_create_order(self):
        user = UserFactory()
        product = ProductFactory()
        data = json.dumps({"products_id": [product.id], "user": user.id})

        response = self.client.post(
            reverse("order-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(user=user)
