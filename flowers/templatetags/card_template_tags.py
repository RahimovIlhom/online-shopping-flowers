# card_template_tags
from django import template
from flowers.models import Order

register = template.Library()

@register.filter()
def card_flower_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs.last().products.count()
    return 0