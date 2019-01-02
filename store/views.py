import stripe
from django.views import generic
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from store.models import Product, Category, Streamer, Cart, Order, OrderProduct , Address
from store.forms import CartForm, OrderForm, AddressForm, EditProfileForm, RegistrationForm, AddProduct
from store.utils import send_simple_message

stripe.api_key = settings.STRIPE_SECRET_KEY


class Payment(TemplateView):
    template_name = 'store/payment.html'
    model = Cart

    def get_queryset(self):
        return Cart.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = Cart.objects.filter(user__id=self.request.user.id, paid=False)
        sum = 0
        for item in cart_items:
            sum = sum + item.line_total()
        context['total_price'] = sum
        return context


class IndexView(generic.ListView):
    template_name = 'store/index.html'
    model = Product

    def get_queryset(self):
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        return context


class OrdersView(generic.ListView):
    template_name = 'store/my_orders.html'
    model = Order

    def get_queryset(self):
        return Order.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        # .filter(user__id=self.request.user.id)
        teste = Order.objects.values('orderProduct__price', 'orderProduct__quantity', 'id', 'billing_address__address', 'delivery_address__address', 'status', 'created_at')
        ordered=[]
        for order in teste:
            prod = {
                'price': order['orderProduct__price'].real * order['orderProduct__quantity'],
                'id': order['id'],
                'billing_address': order['billing_address__address'],
                'delivery_address': order['delivery_address__address'],
                'status': order['status'],
                'created_at': order['created_at']
            }
            ordered.append(prod)

        # validar se existem vais produtos na mesma order e somar os preços
        for index, orders in enumerate(ordered):
            for index_2, orders_2 in enumerate(ordered):
                if orders != orders_2 and orders['id'] == orders_2['id']:
                    ordered[index]= {
                        'price': orders['price'] + orders_2['price'],
                        'id': orders['id'],
                        'billing_address': orders['billing_address'],
                        'delivery_address': orders['delivery_address'],
                        'status': orders['status'],
                        'created_at': orders['created_at']
                    }
                    del ordered[index_2]

        context['order_list'] = ordered
        return context


class DetailView(generic.ListView):
    template_name = 'store/detail.html'
    model = Product
    context_object_name = 'product_list'

    def post(self, request, **kwargs):
        form = CartForm(request.POST)
        if form.is_valid():
            cart = form.save(commit=False)
            cart.user = request.user
            product_stock = Product.objects.get(id=cart.product_id)
            cart_item = Cart.objects.filter(user_id=cart.user.id, product_id=cart.product_id, ordered=False).first()
            if product_stock.stock == 0:
                product_stock.available = False
                product_stock.save()
            else:
                product_stock.available = True
                if cart_item:
                    if cart.quantity > product_stock.stock:
                        return redirect('store:cart')
                    else:
                        cart_item.quantity += cart.quantity
                        cart_item.save()
                        product_stock.stock -= cart.quantity
                        if product_stock.stock == 0:
                            product_stock.available = False
                            product_stock.save()
                        product_stock.save()
                else:
                    if cart.quantity > product_stock.stock:
                        return redirect('store:cart')
                    else:
                        product_stock.stock -= cart.quantity
                        if product_stock.stock == 0:
                            product_stock.available = False
                            product_stock.save()
                        product_stock.save()
                        cart.save()
            return redirect('store:cart')
        context = {'form': form}
        return context

    def get_queryset(self):
        return Product.objects.filter(slug=self.kwargs['product_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        form = CartForm()
        form.initial["product"] = Product.objects.filter(slug=self.kwargs['product_slug']).first().id
        context['form'] = form
        return context


class CategoryView(generic.DetailView):
    template_name = 'store/index.html'
    model = Category
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['product_list'] = Product.objects.filter(category__slug=self.kwargs['slug'])
        return context


class StreamerView(generic.DetailView):
    template_name = 'store/index.html'
    model = Streamer
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['product_list'] = Product.objects.filter(streamer__slug=self.kwargs['slug'])
        return context


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('store:login')
    template_name = 'store/signup.html'


class CartView(generic.ListView):
    template_name = 'store/cart.html'
    context_object_name = 'product_list'
    model = Cart

    def get_queryset(self):
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['product_list'] = Product.objects.all()
        context['cart_list'] = Cart.objects.filter(ordered=False)
        context['address_list'] = Address.objects.filter(user__id=self.request.user.id)
        cart_list = Cart.objects.filter(user__id=self.request.user.id, ordered=False)
        product_total = 0
        for item in cart_list:
            product_total = product_total + item.line_total()

        context['total_price'] = product_total
        return context


class DeleteFromCart(generic.DeleteView):
    model = Cart
    template_name = 'store/cart.html'

    def get_queryset(self):
        return Cart.objects.all()

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return redirect('store:cart')


class IncreaseCartQuantity (generic.UpdateView):
    model = Cart
    template_name = 'store/cart.html'
    fields = ['quantity']

    def get_queryset(self):
        return Cart.objects.all()

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.quantity += 1
        product.save()
        return redirect('store:cart')


class DecreaseCartQuantity (generic.UpdateView):
    model = Cart
    template_name = 'store/cart.html'
    fields = ['quantity']

    def get_queryset(self):
        return Cart.objects.all()

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        if product.quantity > 1:
            product.quantity -= 1
            product.save()
        return redirect('store:cart')


class InsertOrder (generic.CreateView):
    template_name = 'store/order.html'
    model = Order
    form_class = OrderForm

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST, user=self.request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            order_products = dict()
            cart_items = Cart.objects.filter(user_id=order.user.id, ordered=False)
            for cart_item in cart_items:
                product = cart_item.product
                order_products[product.id] = OrderProduct(
                    product=product,
                    quantity=cart_item.quantity,
                    size=product.size,
                    color=product.color,
                    price=product.price,
                    img=product.img
                )
            for item in order_products.values():
                item.save()
            order.orderProduct.add(*list(order_products.values()))
            cart_items.update(ordered=True)
            return redirect('store:payment')
        else:
            return redirect('store:error')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class InsertUserData (generic.CreateView):
    template_name = 'store/user_data.html'
    model = Address
    fields = ['address', 'phone', 'nif']

    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        if form.is_valid():
            user_data = form.save(commit=False)
            user_data.user = request.user
            user_data.save()
            return redirect('store:order')
        else:
            return redirect('store:error')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        return context


class OrderProductsList(generic.ListView):
    template_name = 'store/my_order_products.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['order_products'] = Order.objects.get(pk=self.kwargs['pk'])
        return context


class Profile(generic.ListView):
    template_name = 'store/profile.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        context['user_detail'] = User.objects.get(pk=self.request.user.id)
        return context


class EditProfile(generic.UpdateView):
    model = User
    queryset = User.objects.all()
    fields = ['username', 'first_name', 'last_name', 'email',]
    template_name = 'store/edit_profile.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = EditProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('store:profile')
        else:
            form = EditProfileForm(instance=request.user)
            args = {'form': form}
            return render(request, self.template_name, args)

# def edit_profile(request):
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('store:profile')
#     else:
#         form=EditProfileForm(instance=request.user)
#         args= {'form':form}
#         return render(request, 'store/edit_profile.html', args)


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('store:profile')
        else:
            return redirect('store/change_password.html')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'store/change_password.html', args)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('store:index')
    else:
        form = RegistrationForm()
    return render(request, 'store/reg_form.html', {'form': form})


def charge(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user__id=request.user.id, paid=False)
        order_status = Order.objects.filter(user__id=request.user.id).last()
        product_total = 0
        for item in cart_items:
            product_total = product_total + item.line_total()
        cart_items.update(paid=True)
        order_status.status = 'Completed'
        order_status.save()
        send_simple_message(request)
        stripe.Charge.create(
            amount=int(product_total)*100,
            currency='EUR',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'store/charge.html')


class InsertProducts (generic.CreateView):
    template_name = 'store/insert_products.html'
    model = Product
    fields = ['category', 'name', 'description', 'streamer', 'size', 'color', 'price', 'available', 'stock', 'img']

    def post(self, request, *args, **kwargs):
        form = AddProduct(request.POST, request.FILES)
        if form.is_valid():
            user_data = form.save(commit=False)
            # user_data.user = request.user
            user_data.save()
            return redirect('store:index')
        else:
            return redirect('store:error')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['streamer_list'] = Streamer.objects.all()
        return context

