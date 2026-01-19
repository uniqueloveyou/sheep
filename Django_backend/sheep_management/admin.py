from django.contrib import admin
from .models import Sheep, Breeder, GrowthRecord, FeedingRecord, VaccinationHistory, User, CartItem


@admin.register(Sheep)
class SheepAdmin(admin.ModelAdmin):
    list_display = ['id', 'gender', 'weight', 'height', 'length', 'breeder']
    list_filter = ['gender', 'breeder']
    search_fields = ['id', 'gender', 'breeder__name']
    list_per_page = 20


@admin.register(Breeder)
class BreederAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender', 'phone', 'get_actual_sheep_count', 'sheep_count', 'sheep_id', 'female_count', 'male_count']
    list_filter = ['gender']
    search_fields = ['name', 'phone', 'sheep_id']
    list_per_page = 20
    readonly_fields = ['get_actual_sheep_count']
    
    def get_actual_sheep_count(self, obj):
        """显示实际关联的羊只数量"""
        count = obj.sheep_list.count()  # 使用related_name
        if count > 0:
            return f"{count}只 (点击查看)"
        return "0只"
    get_actual_sheep_count.short_description = '实际羊只数'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'gender', 'phone')
        }),
        ('羊只信息', {
            'fields': ('sheep_id', 'sheep_count', 'female_count', 'male_count', 'get_actual_sheep_count')
        }),
    )


@admin.register(GrowthRecord)
class GrowthRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'sheep', 'record_date', 'weight', 'height', 'length']
    list_filter = ['record_date', 'sheep']
    search_fields = ['sheep__id']
    date_hierarchy = 'record_date'
    list_per_page = 20


@admin.register(FeedingRecord)
class FeedingRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'sheep', 'feed_type', 'start_date', 'end_date', 'amount', 'unit']
    list_filter = ['feed_type', 'start_date']
    search_fields = ['sheep__id', 'feed_type']
    date_hierarchy = 'start_date'
    list_per_page = 20


@admin.register(VaccinationHistory)
class VaccinationHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'sheep', 'get_vaccination_id_display', 'vaccination_date', 'expiry_date', 'dosage', 'administered_by']
    list_filter = ['vaccination_id', 'vaccination_date', 'administered_by']
    search_fields = ['sheep__id', 'administered_by', 'vaccine_type']
    date_hierarchy = 'vaccination_date'
    list_per_page = 20


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'nickname', 'openid', 'mobile', 'get_gender_display', 'created_at', 'last_login_at']
    list_filter = ['gender', 'created_at', 'last_login_at']
    search_fields = ['username', 'nickname', 'openid', 'mobile']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'nickname', 'mobile', 'gender')
        }),
        ('微信信息', {
            'fields': ('openid', 'unionid', 'avatar_url')
        }),
        ('地址信息', {
            'fields': ('country', 'province', 'city')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'last_login_at')
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sheep', 'quantity', 'price', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'user__nickname', 'sheep__id']
    date_hierarchy = 'created_at'
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']

