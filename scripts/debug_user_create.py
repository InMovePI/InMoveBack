"""Small script to test UserSerializer validation with minimal payload"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

import django
django.setup()

from core.serializers.user import UserSerializer, UserCreateSerializer
from core.models.user import User
from rest_framework.test import APIClient

# Minimal payload the frontend might submit
payload = {
    'email': 'testfrontend@example.com',
    'name': 'Test Frontend',
    'password': 'test1234',
}

serializer = UserCreateSerializer(data=payload)
print('Is valid:', serializer.is_valid())
print('Errors:', serializer.errors)

# Try with required fields
import uuid

payload_full = {
    'email': f'test_{uuid.uuid4()}@example.com',
    'name': 'Test Frontend',
    'password': 'test1234',
    'data_nascimento': '1990-01-01',
    'genero': 'M',
    'altura_cm': 170,
    'peso_kg': '80.00'
}

serializer2 = UserCreateSerializer(data=payload_full)
print('\nIs valid (full):', serializer2.is_valid())
print('Errors (full):', serializer2.errors)

# Try creating (this will not set password correctly because serializer is naive)
if serializer2.is_valid():
    user = serializer2.save()
    print('\nCreated user:', user.email)
    print('Password stored:', user.password)
    print('Check password (should be True if hashed):', user.check_password('test1234'))
else:
    print('\nCould not create user; fix errors first')

# Test manager create_user with minimal args (as TokenAuthentication does)
manager_user = User.objects.create_user(email=f'manager_{uuid.uuid4()}@example.com')
print('\nManager created user:', manager_user.email)
print('Manager user defaults - genero:', manager_user.genero, 'altura_cm:', manager_user.altura_cm, 'peso_kg:', manager_user.peso_kg)

# Test API endpoint /api/usuarios/ to ensure viewset registration works
client = APIClient()
resp = client.post('/api/usuarios/', {'email': f'api_{uuid.uuid4()}@example.com', 'name': 'API Create', 'password': 'apipass123'}, format='json')
print('\nAPI POST status:', resp.status_code)
print('API response:', resp.data)

# Try obtaining token using both username/email keys
new_email = f'token_{uuid.uuid4()}@example.com'
client.post('/api/usuarios/', {'email': new_email, 'name': 'Token Test', 'password': 'TokenPass123'}, format='json')
token1 = client.post('/api/token/', {'username': new_email, 'password': 'TokenPass123'}, format='json')
token2 = client.post('/api/token/', {'email': new_email, 'password': 'TokenPass123'}, format='json')
print('\nToken (username) status:', token1.status_code, token1.data)
print('Token (email) status:', token2.status_code, token2.data)
