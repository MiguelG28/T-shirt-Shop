from django.db import models
from django.utils.datetime_safe import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name='slug', max_length=100, unique=True, db_index=True, default='')
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    updated_at = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return "Category Name= %s" % self.name


class Streamer(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name='slug', max_length=100, unique=True, db_index=True)

    def __str__(self):
        return "%s" % self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(verbose_name='slug', max_length=100, unique=True, db_index=True, default='')
    description = models.TextField(blank=True)
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE)
    size = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(default=datetime.now, blank=True)
    updated_at = models.DateTimeField(default=datetime.now, blank=True)
    img = models.ImageField(verbose_name='imagem apresentacao', upload_to='media/', default='')

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return "Product Name= %s" % self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    ordered = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def line_total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return "Product=%s" % self.product.name


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=200, default='')
    color = models.CharField(max_length=200, default='')
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    img = models.ImageField(verbose_name='imagem apresentacao', upload_to='media/', default='')

    def __str__(self):
        return "%s-Quantidade=%s" % (self.product.name, self.quantity)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=12)
    nif = models.CharField(max_length=12)

    def __str__(self):
        return self.address


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='user_billing_address',
        default=''
    )
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='user_delivery_address',
        default=''
    )
    orderProduct = models.ManyToManyField(OrderProduct)

    created_at = models.DateTimeField(default=datetime.now, blank=True)
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return "User=%s, Order ID=%s" % (str(self.user), self.id)
