from django.contrib import admin
from . import models
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']
    prepopulated_fields={'slug':    ('title',)}


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title']
    
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']
    # prepopulated_fields = {'unit_price': ['menuitem'], 'price': ('quantity', 'unit_price')}
    readonly_fields = ['price', 'unit_price']

    
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user']
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order']
    readonly_fields = ['price', 'unit_price']
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.MenuItem, MenuItemAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem,OrderItemAdmin)
