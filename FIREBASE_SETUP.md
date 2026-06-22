# Firebase Setup Guide

This guide explains how to set up Firebase and integrate it with the Homomorphic Secure File Sharing System.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add project"**
3. Enter project name: `secure-file-sharing`
4. Continue through the setup process
5. Click **"Create project"**

## Step 2: Get Firebase Credentials

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Under **"General"** tab, scroll down to find your app
3. If no app exists, click **"Add app"** → select **Web**
4. Copy the configuration object
5. Extract these values:
   - `apiKey`
   - `authDomain`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

## Step 3: Add Credentials to .env

Update your `.env` file:

```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef123456
```

## Step 4: Enable Authentication

1. In Firebase Console, go to **Authentication**
2. Click **"Get Started"**
3. Enable **Email/Password** provider:
   - Click **"Email/Password"**
   - Toggle **"Enabled"**
   - Click **"Save"**

## Step 5: Create Firestore Database

1. Go to **Firestore Database**
2. Click **"Create database"**
3. Choose **"Start in test mode"** (for development)
4. Select your region and click **"Enable"**

## Step 6: Set Up Firebase Storage

1. Go to **Storage**
2. Click **"Get Started"**
3. Review security rules and click **"Next"**
4. Choose a region and click **"Done"**

## Step 7: Configure Security Rules

### Firestore Rules

In Firestore, go to **Rules** and paste:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    
    // Files collection
    match /files/{fileId} {
      allow read: if request.auth.uid == resource.data.userId || 
                     resource.data.scope == 'public';
      allow write: if request.auth.uid == resource.data.userId;
      allow delete: if request.auth.uid == resource.data.userId;
    }
    
    // Shares collection
    match /shares/{shareId} {
      allow read: if request.auth.token.email == resource.data.recipientEmail;
      allow write: if false;
      allow delete: if false;
    }
    
    // Security logs
    match /security_logs/{logId} {
      allow read: if request.auth.uid == resource.data.userId;
      allow write: if request.auth.uid == resource.data.userId;
    }
    
    // OTP codes
    match /otp_codes/{email} {
      allow read, write: if true; // Allow OTP creation
    }
  }
}
```

### Storage Rules

In Storage, go to **Rules** and paste:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow user to upload to their own folder
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

## Step 8: Update Environment Variables

Copy `.env.example` to `.env` and fill in your Firebase credentials:

```bash
cp .env.example .env
```

## Step 9: Using Firebase Services

### Import and Use in Your Components

```javascript
// Import auth service
import { 
  signupWithOTP, 
  loginWithEmail, 
  logout 
} from '@/services/firebaseAuthService';

// Import database service
import { 
  getUserFiles, 
  shareFile 
} from '@/services/firestoreService';

// Import storage service
import { 
  uploadFile, 
  downloadFile 
} from '@/services/firebaseStorageService';

// Example signup
const result = await signupWithOTP(email, password, name);
if (result.success) {
  console.log('Signup successful! Check email for OTP.');
}

// Example upload file
const upload = await uploadFile(userId, file);
if (upload.success) {
  console.log('File uploaded:', upload.file.downloadUrl);
}
```

## Step 10: Hybrid Setup (Firebase + Django)

If you want to use both Firebase and Django:

1. **Frontend**: Use Firebase for authentication and file storage
2. **Backend**: Keep Django for additional logic, admin panel, security monitoring

Update your API configuration:

```javascript
// Use Django API only for admin/monitoring endpoints
const adminAPI = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Authorization': `Bearer ${firebaseToken}`,
  },
});
```

## Troubleshooting

### Issue: "apiKey is not a valid API key"
- Verify you copied the correct credentials from Firebase Console
- Restart the dev server: `npm run dev`

### Issue: "Permission denied" errors in Firestore
- Check that your security rules are properly configured
- Verify `request.auth.uid` matches the document owner

### Issue: Files not uploading to Storage
- Ensure Storage rules allow your user ID
- Check that bucket name matches your Firebase project

### Issue: OTP not sending
- Currently, OTP is logged to console for development
- To send real emails, set up Firebase Cloud Functions

## Next Steps

1. **Create Cloud Functions** for sending emails:
   ```javascript
   // functions/sendOtp.js
   const functions = require('firebase-functions');
   const nodemailer = require('nodemailer');
   
   exports.sendOtp = functions.https.onCall(async (data, context) => {
     // Send OTP via email
   });
   ```

2. **Set up backup** for important data

3. **Enable Analytics** to track user behavior

4. **Create custom claims** for role-based access control

## References

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firestore Database](https://firebase.google.com/docs/firestore)
- [Firebase Storage](https://firebase.google.com/docs/storage)
- [Security Rules](https://firebase.google.com/docs/rules)
