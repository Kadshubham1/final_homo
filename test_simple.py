import requests
import datetime

email = f'working_test_{datetime.datetime.now().timestamp()}@example.com'

# Test 1: Signup  
resp = requests.post('http://localhost:8000/api/auth/signup-otp/', json={
    'email': email, 
    'password': 'Test123456!', 
    'password2': 'Test123456!', 
    'name': 'Test'
})

print(f'Signup Response Code: {resp.status_code}')

if resp.status_code != 201:
    print(f'Error: {resp.json()}')
else:
    data = resp.json()
    otp = data.get('otp_code')
    print(f'OTP Generated: {otp}')
    
    # Test 2: Verify OTP
    resp2 = requests.post('http://localhost:8000/api/auth/verify-otp/', json={
        'email': email, 
        'otp': otp
    })
    
    print(f'Verify Response Code: {resp2.status_code}')
    
    if resp2.status_code == 200:
        user_data = resp2.json().get('user', {})
        print(f'User Verified: {user_data.get("is_verified")}')
        print(f'Access Token Generated: {"YES" if resp2.json().get("access") else "NO"}')
        print('SUCCESS - OTP SYSTEM WORKING!')
    else:
        print(f'Verification Failed: {resp2.json()}')
