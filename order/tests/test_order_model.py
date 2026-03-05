import json
from django.test import TestCase
from order.models import Order
from order.factories import OrderFactory, UserFactory
from product.factories import ProductFactory


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.product1 = ProductFactory(price=15.00)
        self.product2 = ProductFactory(price=25.00)

    def test_order_creation(self):

        order = OrderFactory(user=self.user, product=(self.product1, self.product2))

        self.assertEqual(Order.objects.count(), 1)

        self.assertEqual(order.user, self.user)

        self.assertEqual(order.product.count(), 2)
        self.assertIn(self.product1, order.product.all())
        self.assertIn(self.product2, order.product.all())
