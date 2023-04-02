from contextlib import redirect_stderr
from email import message
from itertools import product
from unicodedata import category
from django.shortcuts import render, redirect
from django.urls import is_valid_path
from django.views import View
from .models import Customer,Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.db.models import Q
from django.http import JsonResponse

class ProductView(View):
    def get(self, request):
        coffee = Product.objects.filter(category= 'C')
        snacks = Product.objects.filter(category= 'SN')
        shakes = Product.objects.filter(category= 'S')
        return render(request, 'app/home.html', {'coffee':coffee,'snacks':snacks, 'shakes':shakes})

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html',{'product':product})
        

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user= user, product= product).save()
    return redirect('/cart')

def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        delivary_charge = 40.00
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user ==user]
        if cart_product:
            for p in cart_product:
                tempamount =(p.quantity * p.product.price)
                amount += tempamount
                totalamount = amount + delivary_charge
            return render(request, 'app/addtocart.html',{'carts':cart, 'totalamount':totalamount, 'amount':amount})
        else:
            return render(request, 'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET' :
        prod_id =request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        delivary_charge = 40.00
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount =(p.quantity * p.product.price)
            amount += tempamount

        data ={
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : amount + delivary_charge
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET' :
        prod_id =request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        delivary_charge = 40.00
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount =(p.quantity * p.product.price)
            amount += tempamount

        data ={
            'quantity' : c.quantity,
            'amount' : amount,
            'totalamount' : amount + delivary_charge
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET' :
        prod_id =request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.delete()
        amount = 0.0
        delivary_charge = 40.00
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount =(p.quantity * p.product.price)
            amount += tempamount

        data ={
            'amount' : amount,
            'totalamount' : amount + delivary_charge
        }
        return JsonResponse(data)


def buy_now(request):
 return render(request, 'app/buynow.html')

class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            mobileno = form.cleaned_data['mobileno']
            reg = Customer(user= user,name= name, address= address,mobileno = mobileno)
            reg.save()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

        

def address(request):
    add = Customer.objects.filter(user = request.user)
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})

def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'odrer_placed': op})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})
        

def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_item = Cart.objects.filter(user=user)
    amount = 0.0
    delivary_charge = 40.00
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount =(p.quantity * p.product.price)
            amount += tempamount
        totalamount = amount + delivary_charge
    return render(request, 'app/checkout.html', {'add':add, 'totalamount': totalamount, 'cart_item':cart_item})


def order_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

