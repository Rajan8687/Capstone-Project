from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ReaderProfile, WriterProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('role', 'bio', 'profile_picture', 'website', 'twitter', 'linkedin')}),
    )


@admin.register(ReaderProfile)
class ReaderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_articles_read', 'total_reading_time', 'last_active')
    list_filter = ('last_active',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)


@admin.register(WriterProfile)
class WriterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_articles_published', 'total_views', 'total_likes', 'writer_score', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('writer_score',)
    
    actions = ['calculate_writer_scores']
    
    def calculate_writer_scores(self, request, queryset):
        for profile in queryset:
            profile.calculate_writer_score()
        self.message_user(request, f'Writer scores calculated for {queryset.count()} writers.')
    calculate_writer_scores.short_description = 'Calculate writer scores'
