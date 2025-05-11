from django.contrib import admin

from .models import Post, Category, Location

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'pub_date', 'category', 'location', 'author', 'is_published'
    )
    search_fields = ('title', 'category__title', 'location__name')
    list_filter = ('pub_date', 'category', 'location', 'is_published')
    list_editable = ('is_published')
    ordering = ('-pub_date')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published')
    search_fields = ('title')
    list_filter = ('is_published')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name')
    list_filter = ('is_published')
