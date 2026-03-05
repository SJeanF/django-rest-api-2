

from django.test import TestCase

from product.models import Category
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

