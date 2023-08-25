from django.contrib import admin
from .models import Project, Technology

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)
    filter_horizontal = ('technologies',)

    fieldsets = (
        ('General', {
            'fields': ('title', 'description', 'image', 'url', 'created_at', 'slug')
        }),
        ('Technologies', {
            'fields': ('technologies',)
        })
    )

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
