from django.contrib import admin
from .models import Phone, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email")
    search_fields = ("username", "email")


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ("brand", "model", "price", "ram", "rom", "battery")
    list_filter = ("brand",)
    search_fields = ("brand", "model")
    ordering = ("price",)
