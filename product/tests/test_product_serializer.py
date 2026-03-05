from django.test import TestCase

from product.serializers.product_serializer import ProductSerializer
from product.factories import ProductFactory, CategoryFactory


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
