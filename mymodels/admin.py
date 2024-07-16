from django.contrib import admin
import models


@admin.register(models.Person)
class Person(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    list_display_links = ('first_name',)


@admin.register(models.Address)
class Address(admin.ModelAdmin):
    list_display = ('person', 'city')
    list_display_links = ('person', 'city')


@admin.register(models.Project)
class Project(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_display_links = ('name',)


@admin.register(models.Document)
class Document(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('title',)
