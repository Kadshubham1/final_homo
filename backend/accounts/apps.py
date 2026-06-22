from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = '🔐 User Accounts'

    def ready(self):
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_email = 'admin@central.com'
            if not User.objects.filter(email=admin_email).exists():
                User.objects.create_superuser(
                    username='admin',
                    email=admin_email,
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    role='admin'
                )
                print("[+] Auto-created admin user: admin@central.com / admin123")
        except Exception:
            pass

