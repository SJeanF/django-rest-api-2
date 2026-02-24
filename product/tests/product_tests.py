import json

from django.test import TestCase

from product.models import Product
from product.serializers.product_serializer import ProductSerializer
from order.factories import UserFactory
from product.factories import ProductFactory, CategoryFactory


from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory(title="Educação")
        # Cria o produto e já associa a categoria (graças ao post_generation da factory)
        self.product = ProductFactory(
            title="Clean Code", price=150, category=(self.category,)
        )

    def test_product_creation(self):
        """Testa se o produto é criado e a relação ManyToMany com Category funciona"""
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.title, "Clean Code")
        self.assertEqual(self.product.price, 150)

        # Verifica se a categoria foi associada corretamente
        self.assertEqual(self.product.category.count(), 1)
        self.assertIn(self.category, self.product.category.all())


class ProductSerializerTest(TestCase):
    def setUp(self):
        # Cria duas categorias para testar a lista (many=True)
        self.category1 = CategoryFactory(title="Programação")
        self.category2 = CategoryFactory(title="Arquitetura de Software")

        self.product = ProductFactory(
            title="Padrões de Projeto",
            description="Livro sobre GoF",
            price=200,
            active=True,
            category=(self.category1, self.category2),
        )

    def test_product_serialization(self):
        """Testa se o produto serializa seus campos e aninha as categorias"""
        serializer = ProductSerializer(self.product)
        data = serializer.data

        # Testa os campos básicos do produto
        self.assertEqual(data["title"], "Padrões de Projeto")
        self.assertEqual(data["price"], 200)

        # Testa o aninhamento (nested serializer) da categoria
        self.assertIn("category", data)
        self.assertEqual(len(data["category"]), 2)

        # Verifica se os dados de dentro da categoria aninhada estão corretos
        self.assertEqual(data["category"][0]["title"], "Programação")
        self.assertEqual(data["category"][1]["title"], "Arquitetura de Software")


class TestProductViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        token = Token.objects.create(user=self.user)  # added
        token.save()  # added

        self.product = ProductFactory(
            title="pro controller",
            price=200.00,
        )

    def test_get_all_product(self):
        token = Token.objects.get(user__username=self.user.username)  # added
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)  # added
        response = self.client.get(reverse("product-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_data = json.loads(response.content)

        self.assertEqual(product_data[0]["title"], self.product.title)
        self.assertEqual(product_data[0]["price"], self.product.price)
        self.assertEqual(product_data[0]["active"], self.product.active)

    def test_create_product(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        category = CategoryFactory()
        data = {
            "title": "notebook",
            "price": "800.00",
            "categories_id": [category.id],
            "description": "Um notebook potente",
            "active": True,
        }

        response = self.client.post(
            reverse("product-list", kwargs={"version": "v1"}),
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_product = Product.objects.get(title="notebook")

        self.assertEqual(created_product.title, "notebook")
        self.assertEqual(created_product.price, 800.00)
