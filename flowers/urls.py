from django.urls import path
from .views import (
    flowers_list, CheckOutView, flower_page,
    redirect_login, add_to_card, remove_from_card,
    OrderSummaryView, remove_single_flower_from_card,
    PaymentView,
)

urlpatterns = [
    path('', redirect_login, name='home'),
    path('category/<int:id>/page/<int:page>/', flowers_list, name='flowers-list'),
    path('flower/<int:id>/', flower_page, name='product'),
    path('flower/add-to-card/<int:id>/', add_to_card, name='add-to-card'),
    path('flower/remove-from-card/<int:id>/', remove_from_card, name='remove-from-card'),
    path('flower/remove-flower-from-card/<int:id>/', remove_single_flower_from_card, name='remove-flower-from-card'),
    path('order-summary', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckOutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
]