#!/usr/bin/env python
"""Quick script to test email configuration"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"Sending test email to: {settings.EMAIL_HOST_USER}")

try:
    send_mail(
        subject="Test Email from Django",
        message="If you're reading this, your SMTP configuration is working!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print("\n✅ SUCCESS! Check your inbox for the test email.")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nCommon issues:")
    print("1. Wrong app password (must be 16 characters, no spaces)")
    print("2. 2-Factor authentication not enabled on Gmail")
    print("3. App password not generated correctly")
    print("4. Firewall blocking SMTP connections")
