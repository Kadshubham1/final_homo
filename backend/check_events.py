import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from security_logs.models import SecurityEvent
for e in SecurityEvent.objects.order_by('-timestamp')[:5]:
    print(f'ID: {e.id}, Action: {e.action}, Device: {e.device_name}, Image: {e.image}')
