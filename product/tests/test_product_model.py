from django.test import TestCase

from product.models import Product
from product.factories import ProductFactory, CategoryFactory


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
