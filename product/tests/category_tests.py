import json

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from django.test import TestCase

from product.models import Category
from product.serializers.category_serializer import CategorySerializer
from product.factories import CategoryFactory


class CategoryModelTest(TestCase):
    def setUp(self):
        # Cria uma categoria de teste
        self.category = CategoryFactory(
            title="Tecnologia", slug="tecnologia", description="Livros de TI"
        )

    def test_category_creation(self):
        """Testa a criação da categoria no banco de dados"""
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(self.category.title, "Tecnologia")
        self.assertEqual(self.category.slug, "tecnologia")
        self.assertTrue(self.category.active)  # Por padrão é True no seu modelo


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


class CategoryViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="books")

    def test_get_all_category(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category_data = json.loads(response.content)

        self.assertEqual(category_data[0]["title"], self.category.title)

    def test_create_category(self):
        data = json.dumps({"title": "technology"})

        response = self.client.post(
            reverse("category-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_category = Category.objects.get(title="technology")

        self.assertEqual(created_category.title, "technology")
