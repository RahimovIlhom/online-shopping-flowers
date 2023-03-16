from django.contrib import admin
from. models import Category, Product, OrderProduct, Order, BillingAddress, Payment, PromoCode


# Register your models here.4
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Payment)
admin.site.register(PromoCode)


