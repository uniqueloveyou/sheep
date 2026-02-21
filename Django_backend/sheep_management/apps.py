from django.apps import AppConfig


class SheepManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sheep_management'
    verbose_name = '羊只管理系统'

    def ready(self):
        import sheep_management.signals  # noqa: F401 注册信号
