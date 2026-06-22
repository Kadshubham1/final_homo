# API Testing Examples - OTP Signup System

This file contains complete examples for testing the OTP signup system using various tools.

---

## 1. Testing with cURL

### Signup Request
```bash
curl -X POST http://localhost:8000/api/auth/signup-otp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass@123",
    "password2": "SecurePass@123",
    "name": "John Doe"
  }'
```

**Response (201 Created):**
```json
{
  "message": "Signup successful! Check your email for OTP verification code.",
  "email": "john@example.com",
  "user": {
    "id": 5,
    "username": "john@example.com",
    "name": "John Doe",
    "email": "john@example.com",
    "mobile": "",
    "role": "user",
    "avatar": null,
    "created_at": "2026-04-04T14:30:45.123456Z"
  }
}
```

### Verify OTP Request
```bash
# First, fetch the OTP from the Django console output
# Look for the 6-digit code in the email output

curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "john@example.com",
    "otp": "123456"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully! Your account is now active.",
  "user": {
    "id": 5,
    "username": "john@example.com",
    "name": "John Doe",
    "email": "john@example.com",
    "mobile": "",
    "role": "user",
    "avatar": null,
    "bio": "",
    "is_verified": true,
    "created_at": "2026-04-04T14:30:45.123456Z",
    "last_login_ip": null
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Resend OTP Request
```bash
curl -X POST http://localhost:8000/api/auth/resend-otp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

**Response (200 OK):**
```json
{
  "message": "New OTP sent to your email. It will expire in 5 minutes.",
  "expires_in": 300,
  "email": "john@example.com"
}
```

### Error Response - Invalid Email
```bash
curl -X POST http://localhost:8000/api/auth/signup-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "password": "Password123",
    "password2": "Password123"
  }'
```

**Response (400 Bad Request):**
```json
{
  "email": ["Enter a valid email address."]
}
```

### Error Response - Passwords Don't Match
```bash
curl -X POST http://localhost:8000/api/auth/signup-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "Password123",
    "password2": "DifferentPassword"
  }'
```

**Response (400 Bad Request):**
```json
{
  "password": ["Passwords do not match."]
}
```

### Error Response - Email Already Registered
```bash
curl -X POST http://localhost:8000/api/auth/signup-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "Password123",
    "password2": "Password123"
  }'
```

**Response (400 Bad Request):**
```json
{
  "email": ["This email is already registered."]
}
```

### Error Response - Invalid OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp": "999999"
  }'
```

**Response (400 Bad Request):**
```json
{
  "otp": ["Invalid OTP. Please try again."]
}
```

### Error Response - Rate Limit Exceeded
```bash
# Try to resend OTP within 30 seconds of last request
curl -X POST http://localhost:8000/api/auth/resend-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "Please wait 30 seconds before requesting a new OTP."
}
```

---

## 2. Testing with Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/auth"

# 1. Signup
print("=== SIGNUP ===")
signup_data = {
    "email": "alice@example.com",
    "password": "AlicePassword123",
    "password2": "AlicePassword123",
    "name": "Alice Smith"
}

response = requests.post(f"{BASE_URL}/signup-otp/", json=signup_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Get the user email for next step
email = response.json()["email"]

# 2. Get OTP (from Django console - manually copy)
print("\n=== GET OTP FROM CONSOLE ===")
otp_code = input("Enter OTP from console: ")

# 3. Verify OTP
print("\n=== VERIFY OTP ===")
verify_data = {
    "email": email,
    "otp": otp_code
}

response = requests.post(f"{BASE_URL}/verify-otp/", json=verify_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# 4. Extract tokens
if response.status_code == 200:
    tokens = {
        "access": response.json()["access"],
        "refresh": response.json()["refresh"]
    }
    print(f"\nAccess Token: {tokens['access'][:50]}...")
    print(f"Refresh Token: {tokens['refresh'][:50]}...")

# 5. Test authenticated request
print("\n=== AUTHENTICATED REQUEST ===")
headers = {
    "Authorization": f"Bearer {tokens['access']}"
}

response = requests.get(f"{BASE_URL}/me/", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"User Profile: {json.dumps(response.json(), indent=2)}")

# 6. Test resend OTP
print("\n=== RESEND OTP ===")
resend_data = {"email": email}

response = requests.post(f"{BASE_URL}/resend-otp/", json=resend_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
```

---

## 3. Testing with Postman

### Collection Setup

1. **Create new Collection**: "OTP Signup System"
2. **Set Base URL**: `{{base_url}}/auth` 
3. **Set Variable**: `base_url = http://localhost:8000/api`

### Request 1: Signup

**URL**: `{{base_url}}/signup-otp/`
**Method**: POST
**Headers**:
```
Content-Type: application/json
Accept: application/json
```

**Body (raw JSON)**:
```json
{
  "email": "bob@example.com",
  "password": "BobPassword123",
  "password2": "BobPassword123",
  "name": "Bob Wilson"
}
```

**Tests**:
```javascript
pm.test("Status is 201", function() {
    pm.response.to.have.status(201);
});

pm.test("Response has email", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("email");
});

// Save email for next request
pm.environment.set("signup_email", pm.response.json().email);
```

### Request 2: Verify OTP

**URL**: `{{base_url}}/verify-otp/`
**Method**: POST
**Headers**:
```
Content-Type: application/json
Accept: application/json
```

**Body (raw JSON)**:
```json
{
  "email": "{{signup_email}}",
  "otp": "123456"
}
```

**Note**: Copy the OTP from Django console output

**Tests**:
```javascript
pm.test("Status is 200", function() {
    pm.response.to.have.status(200);
});

pm.test("Response has access token", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("access");
});

pm.test("User is verified", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.user.is_verified).to.equal(true);
});

// Save token for authenticated requests
pm.environment.set("access_token", pm.response.json().access);
```

### Request 3: Get User Profile (Authenticated)

**URL**: `{{base_url}}/me/`
**Method**: GET
**Headers**:
```
Authorization: Bearer {{access_token}}
Accept: application/json
```

**Tests**:
```javascript
pm.test("Status is 200", function() {
    pm.response.to.have.status(200);
});

pm.test("User is verified", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.is_verified).to.equal(true);
});
```

### Request 4: Resend OTP

**URL**: `{{base_url}}/resend-otp/`
**Method**: POST
**Headers**:
```
Content-Type: application/json
Accept: application/json
```

**Body (raw JSON)**:
```json
{
  "email": "{{signup_email}}"
}
```

---

## 4. Testing with JavaScript/Fetch

```javascript
// 1. Signup
async function testSignup() {
  const response = await fetch('http://localhost:8000/api/auth/signup-otp/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: 'charlie@example.com',
      password: 'CharliePass123',
      password2: 'CharliePass123',
      name: 'Charlie Brown'
    })
  });
  
  const data = await response.json();
  console.log('Signup Response:', data);
  return data.email;
}

// 2. Verify OTP
async function testVerifyOTP(email, otp) {
  const response = await fetch('http://localhost:8000/api/auth/verify-otp/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      otp: otp
    })
  });
  
  const data = await response.json();
  console.log('Verify OTP Response:', data);
  return data.access;
}

// 3. Get authenticated user
async function testGetUser(token) {
  const response = await fetch('http://localhost:8000/api/auth/me/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    }
  });
  
  const data = await response.json();
  console.log('User Profile:', data);
}

// 4. Resend OTP
async function testResendOTP(email) {
  const response = await fetch('http://localhost:8000/api/auth/resend-otp/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email
    })
  });
  
  const data = await response.json();
  console.log('Resend OTP Response:', data);
}

// Run tests
(async () => {
  try {
    const email = await testSignup();
    console.log('Check Django console for OTP code');
    
    // Manually enter OTP in browser console:
    // const token = await testVerifyOTP(email, '123456');
    // await testGetUser(token);
  } catch (error) {
    console.error('Test failed:', error);
  }
})();
```

---

## 5. Response Status Codes

| Code | Scenario |
|------|----------|
| 201 | Signup successful |
| 200 | OTP verified successfully |
| 200 | Resend OTP successful |
| 400 | Invalid input (email, password, OTP) |
| 400 | Email already registered |
| 400 | OTP expired or invalid |
| 400 | Rate limit exceeded |
| 401 | Unauthorized (invalid token) |
| 500 | Server error |

---

## 6. Common Test Scenarios

### Scenario 1: Happy Path (Complete Signup)
```
1. POST /signup-otp/ → 201
2. Check console for OTP
3. POST /verify-otp/ → 200
4. GET /me/ (with token) → 200
```

### Scenario 2: Invalid Input
```
1. POST /signup-otp/ with invalid email → 400
2. POST /signup-otp/ with short password → 400
3. POST /signup-otp/ with mismatched passwords → 400
```

### Scenario 3: Duplicate Email
```
1. POST /signup-otp/ with new email → 201
2. POST /signup-otp/ with same email → 400
```

### Scenario 4: Rate Limiting
```
1. POST /resend-otp/ → 200
2. POST /resend-otp/ immediately → 400 (too soon)
3. Wait 30 seconds
4. POST /resend-otp/ → 200
```

### Scenario 5: OTP Expiration
```
1. POST /signup-otp/ → 201
2. Note OTP creation time
3. Wait 5+ minutes
4. POST /verify-otp/ → 400 (expired)
```

---

## 7. Debugging Tips

### Check Django Console
When using console email backend, OTP appears as:
```
------------- start of email -----------
From: noreply@secure-file-sharing.com
To: user@example.com
Subject: Your Email Verification OTP

Your OTP code is: 123456

This code is valid for 5 minutes.
------------ end of email -----------
```

### Check Response Headers
```bash
curl -i http://localhost:8000/api/auth/signup-otp/
```

### View Raw Request/Response
In Postman: Click "Code" → Select language for equivalent code

---

## 8. Performance Testing

### Load Testing with Apache Bench
```bash
# Test signup endpoint with 100 requests, 10 concurrent
ab -n 100 -c 10 -p signup.json -T application/json http://localhost:8000/api/auth/signup-otp/
```

---

## Notes

- All timestamps are in UTC (add to settings if needed)
- JWT tokens expire after 24 hours (configurable)
- OTP expires after 5 minutes (configurable)
- Email backend for development prints to console
- Use SMTP backend for production email

---

Generated: April 4, 2026
