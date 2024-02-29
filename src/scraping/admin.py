from django.contrib import admin
from .models import (
    City, 
    Language, 
    Vacancy, 
    Error, 
    Url
)


class MyCityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    list_display_links = ['name']
    fields = ('name', 'slug')


class MyLanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    list_display_links = ['name']
    fields = ('name', 'slug')


class MyVacancyAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'company', 'city', 'language', 'url' ,'timestamp']
    readonly_fields = ['timestamp']
    list_display_links = ['id', 'title']
    fields = ('title', 'company', 'city', 'language', 'url', 'description', 'timestamp')


class MyUrlAdmin(admin.ModelAdmin):
    list_display = ['city', 'language']
    fields = ('city', 'language', 'url_data')


class MyErrorAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'data']
    list_display_links = ['data']
    readonly_fields = ['timestamp']
    fields = ['data']


admin.site.register(City, MyCityAdmin)
admin.site.register(Language, MyLanguageAdmin)
admin.site.register(Vacancy, MyVacancyAdmin)
admin.site.register(Url, MyUrlAdmin)
admin.site.register(Error, MyErrorAdmin)
# admin.site.register(City)
# admin.site.register(Language)
# admin.site.register(Vacancy)
# admin.site.register(Error)
# admin.site.register(Url)