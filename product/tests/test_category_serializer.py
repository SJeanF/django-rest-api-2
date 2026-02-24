from django.test import TestCase

from product.serializers.category_serializer import CategorySerializer
from product.factories import CategoryFactory


class CategorySerializerTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory(
            title="Ficção", description="Livros de ficção científica", active=True
        )

    def test_category_serialization(self):
        """Testa se o serializer gera o dicionário correto e omite o slug"""
        serializer = CategorySerializer(self.category)
        data = serializer.data

        self.assertEqual(data["title"], "Ficção")
        self.assertEqual(data["description"], "Livros de ficção científica")
        self.assertEqual(data["active"], True)

        # Garante que o slug não vazou no serializer, pois não está na classe Meta
        self.assertNotIn("slug", data)
