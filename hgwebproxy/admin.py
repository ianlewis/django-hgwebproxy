from django.contrib import admin
from hgwebproxy.models import Repository

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    prepopulated_fields = {
        'slug': ('name',)
    }

admin.site.register(Repository, RepositoryAdmin)
