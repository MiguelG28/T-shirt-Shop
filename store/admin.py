from .models import Category, Product, Streamer, Cart, Order, OrderProduct, Address
from django.contrib import admin

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
class OrderAdmin(admin.ModelAdmin):
    filter_horizontal = ('orderProduct',)

admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(OrderProduct)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Streamer, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)


