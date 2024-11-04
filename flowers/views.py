from random import sample
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, View

from .forms import CheckOutForm, PromoCodeForm
from .models import Product, Category, OrderProduct, Order, BillingAddress, Payment, PromoCode

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

# Create your views here.

def redirect_login(request):
    response = redirect('/category/0/page/1/')
    return response


def flowers_list(request, id, page):
    if id == 0:
        flowers = Product.objects.all().order_by('-id')
        paginator = Paginator(flowers, per_page=8)
        page_object = paginator.get_page(page)
        page_max_number = paginator.num_pages
        context = {"page_obj": page_object,
                   'categories': Category.objects.all(),
                   'category': 0,
                   'max_number': page_max_number,
                   }
    else:
        category = get_object_or_404(Category, id=id)
        flowers = Product.objects.filter(category=category)
        paginator = Paginator(flowers, per_page=8)
        page_object = paginator.get_page(page)
        page_max_number = paginator.num_pages
        context = {
            "page_obj": page_object,
            'categories': Category.objects.all(),
            'category': category.id,
            'max_number': page_max_number,
        }
    return render(request, 'home-page.html', context)


def flower_page(request, id):
    flower = get_object_or_404(Product, id=id)
    category = flower.category
    three_objects = Product.objects.order_by('?')[:4]
    # three = sample(three_objects, 3)
    context = {
        'flower': flower,
        'three_objects': three_objects,
    }

    return render(request, 'product-page.html', context)

@login_required
def add_to_card(request, id):
    flower = get_object_or_404(Product, id=id)
    order_flower, created = OrderProduct.objects.get_or_create(
        user=request.user,
        product=flower,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.last()
        if order.products.filter(product__id=flower.id).exists():
            order_flower.quantity += 1
            order_flower.save()
            messages.success(request, "Mahsulot yana bittaga oshirildi!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            order.products.add(order_flower)
            messages.success(request, "Mahsulot savatga qo'shildi!")
            return redirect('product', id=id)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date,
        )
        order.products.add(order_flower)
        messages.success(request, "Mahsulot savatga qo'shildi!")
        return redirect('product', id=id)

@login_required
def remove_from_card(request, id):
    product = get_object_or_404(Product, id=id)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False,
    )
    if order_qs.exists():
        order = order_qs.last()
        if order.products.filter(product__id=product.id).exists():
            order_product = OrderProduct.objects.filter(
                user=request.user,
                product=product,
                ordered=False,
            )[0]
            order.products.remove(order_product)
            order_product.delete()
            order.save()
            messages.success(request, "Bu mahsulot olib tashlandi!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            messages.info(request, "Bu mahsulot savatda mavjud emas!")
            return redirect('product', id=id)
    else:
        messages.info(request, "Savatingiz bo'sh, hali hech qanday mahsulot qo'shmagansiz!")
        return redirect('product', id=id)

@login_required
def remove_single_flower_from_card(request, id):
    product = get_object_or_404(Product, id=id)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False,
    )
    if order_qs.exists():
        order = order_qs.last()
        if order.products.filter(product__id=product.id).exists():
            order_product = OrderProduct.objects.filter(
                user=request.user,
                product=product,
                ordered=False,
            )[0]
            order_product.quantity -= 1
            order_product.save()
            if order_product.quantity <= 0:
                order_product.delete()
            messages.success(request, "Bu mahsulot soni o'zgartirildi!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, "Bu mahsulot savatda mavjud emas!")
            return redirect('product', id=id)
    else:
        messages.info(request, "Savatingiz bo'sh, hali hech qanday mahsulot qo'shmagansiz!")
        return redirect('product', id=id)

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'order_summary.html', context={
                'object': order,
            })
        except ObjectDoesNotExist:
            messages.error(self.request, "Savatingiz bo'sh, mahsulot tanlab uni qo'shing!", extra_tags='danger')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))



class CheckOutView(View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        form_promocode = PromoCodeForm()
        order = get_object_or_404(Order, user=self.request.user, ordered=False)
        order_product = order.products.all()
        n = len(order_product)
        context = {
            "form": form,
            'form_promocode': form_promocode,
            'order': order,
            'n': n,
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        form_promocode = PromoCodeForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billingAddress = billing_address
                order.save()
                if payment_option == "S":
                    return redirect("payment", payment_option='stripe')
                elif payment_option == "P":
                    return redirect("payment", payment_option='paypal')
                else:
                    messages.warning(self.request, 'Invalid payment option selected')
                    return redirect("checkout")

            elif form_promocode.is_valid():
                promo_code = form_promocode.cleaned_data.get('promocode')
                order.promo_code_text = promo_code
                order.save()
                promocode = PromoCode.objects.all()[:]
                if promocode:
                    available = False
                    for promo in promocode:
                        if promo_code == promo.promocode:
                            promocode_get = PromoCode.objects.get(promocode=self.request.POST['promocode'])
                            order.promocode = promocode_get
                            if order.get_total_price() >= promo.min_price:
                                order.save()
                                messages.warning(self.request, "Siz promokodni to'g'ri kiritdingiz!")
                                return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
                            else:
                                messages.warning(self.request, f"Xaridingiz ${promo.min_price} dan ko'p bo'lishi kerak!")
                                return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
                    messages.warning(self.request, "Siz noto'g'ri promokod kiritdingiz!")
                    return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
                else:
                    messages.warning(self.request, "Hozirda hech qanday promo code mavjud emas!")
                    return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


            messages.warning(self.request, "Failed Checkout")
            return redirect("checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "Savatingiz bo'sh, mahsulot tanlab uni qo'shing!", extra_tags='danger')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))



# def add_promo_code(request):
#     form_promocode = PromoCodeForm(request.POST or None)
#     order = get_object_or_404(Order, user=request.user)
#     promo_code = ''
#     if form_promocode.is_valid():
#         promo_code = form_promocode.cleaned_data.get('promocode')
#         order.promo_code_text = promo_code
#     try:
#         promocode = get_object_or_404(PromoCode)[:]
#         for promo in promocode:
#             if promo_code == promo.promocode:
#                 order.promocode = promocode
#         order.save()
#         messages.warning(request, "Siz promocode kiritdingiz!")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#     except:
#         messages.warning(request, "Siz promocode kiritdingiz!")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = order.get_total()
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = charge['amount']
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "You order was successful!")
            return redirect(self.request, 'payment.html')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect(self.request, 'payment.html')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, f"Rate limit error")
            return redirect(self.request, 'payment.html')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, f"Invalid parameters")
            return redirect(self.request, 'payment.html')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, f"Not authenticated")
            return redirect(self.request, 'payment.html')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, f"Network error")
            return redirect(self.request, 'payment.html')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, f"Something went wrong. You where not charged. Please try again!")
            return redirect(self.request, 'payment.html')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, f"A serious error occurred. We have been notifed.")
            return redirect(self.request, 'payment.html')


