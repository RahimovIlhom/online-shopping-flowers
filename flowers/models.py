from django.db import models
from django.shortcuts import reverse
from ckeditor.fields import RichTextField

from django.conf import settings
from django_countries.fields import CountryField


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"

    def get_absolute_url(self):
        return reverse('categories')

    def get_id_url(self):
        return reverse('flowers-list', kwargs={
            'id': self.id,
            'page': 1,
        })

    def get_page_url(self):
        return reverse('flowers-list', kwargs={
            'id': self.id,
        })

    def __str__(self):
        return self.name

LABEL_CHOICES = (
    ('BestSeller', 'primary'),
    ('Action', 'success'),
    ('New', 'danger'),
)

class Product(models.Model):
    name = models.CharField(max_length=50)
    description = RichTextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/')
    price = models.IntegerField()
    discount_price = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=10, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def get_absolute_url(self):
        return reverse('products')

    def get_add_to_card_url(self):
        return reverse('add-to-card', kwargs={
            'id': self.id
        })

    def get_remove_from_card_url(self):
        return reverse('remove-from-card', kwargs={
            'id': self.id
        })

    def __str__(self):
        return self.name

class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} ta {self.product.name}"

    def get_total_product_price(self):
        return self.quantity * self.product.price

    def get_total_product_discount_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_total_product_discount_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_product_discount_price()
        return self.get_total_product_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    order_completed = models.BooleanField(default=False)
    order_completed_date = models.DateTimeField(null=True, blank=True)
    billingAddress = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    promo_code_text = models.CharField(max_length=20, blank=True, null=True)
    promocode = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.user}'

    def get_total_price(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        promo_code = self.promocode
        if promo_code:
            if promo_code.discount_cash:
                total -= promo_code.discount_cash
            elif promo_code.discount_interest:
                total *= (100-promo_code.discount_interest) / 100
        return total

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    apartment_address = models.CharField(max_length=255)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class PromoCode(models.Model):
    promocode = models.CharField(max_length=20)
    min_price = models.IntegerField(blank=True, null=True)
    discount_cash = models.IntegerField(null=True, blank=True)
    discount_interest = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.promocode
