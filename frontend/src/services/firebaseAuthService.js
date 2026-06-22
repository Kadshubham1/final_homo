/**
 * Firebase Authentication Service
 * Handles user signup, login, logout, and OTP verification using Firebase
 */

import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  updateProfile,
  setPersistence,
  browserLocalPersistence,
} from 'firebase/auth';
import {
  doc,
  setDoc,
  getDoc,
  updateDoc,
  query,
  where,
  collection,
  getDocs,
  serverTimestamp,
} from 'firebase/firestore';
import { auth, db } from '../config/firebase';

// Enable persistent authentication
setPersistence(auth, browserLocalPersistence);

/**
 * Generate a 6-digit OTP
 */
const generateOTP = () => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

/**
 * Store OTP in Firestore (temporary collection)
 */
const storeOTP = async (email, otp) => {
  try {
    const otpDoc = doc(db, 'otp_codes', email);
    await setDoc(otpDoc, {
      code: otp,
      email,
      createdAt: serverTimestamp(),
      expiresAt: new Date(Date.now() + 5 * 60 * 1000), // 5 minutes
      verified: false,
    });
    return true;
  } catch (error) {
    console.error('Error storing OTP:', error);
    return false;
  }
};

/**
 * Send OTP to email (in real app, use Firebase Cloud Functions)
 * For now, we'll log it to console
 */
const sendOTPEmail = (email, otp) => {
  console.log(`========================================`);
  console.log(`OTP for ${email}: ${otp}`);
  console.log(`Expires in 5 minutes`);
  console.log(`========================================`);
  // In production, call a Cloud Function to send the email
};

/**
 * Signup with email, password, and name
 * Creates user and sends OTP
 */
export const signupWithOTP = async (email, password, name) => {
  try {
    // Check if user already exists
    const userQuery = query(collection(db, 'users'), where('email', '==', email));
    const snapshot = await getDocs(userQuery);
    
    if (!snapshot.empty) {
      return {
        success: false,
        error: 'Email already registered',
      };
    }

    // Create user in Firebase Auth (but don't sign in yet)
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    
    // Update profile with name
    await updateProfile(userCredential.user, {
      displayName: name,
    });

    // Generate and store OTP
    const otp = generateOTP();
    await storeOTP(email, otp);
    sendOTPEmail(email, otp);

    // Store user profile in Firestore (unverified)
    await setDoc(doc(db, 'users', userCredential.user.uid), {
      uid: userCredential.user.uid,
      email,
      name,
      verified: false,
      createdAt: serverTimestamp(),
      role: 'user',
    });

    // Sign out temporarily (user must verify OTP first)
    await signOut(auth);

    return {
      success: true,
      message: 'Signup successful. Please verify your email with OTP.',
      email,
    };
  } catch (error) {
    console.error('Signup error:', error);
    return {
      success: false,
      error: error.message || 'Signup failed',
    };
  }
};

/**
 * Verify OTP
 */
export const verifyOTP = async (email, otp) => {
  try {
    const otpDoc = await getDoc(doc(db, 'otp_codes', email));

    if (!otpDoc.exists()) {
      return {
        success: false,
        error: 'OTP not found. Please request a new one.',
      };
    }

    const otpData = otpDoc.data();

    // Check if OTP is expired
    if (new Date() > otpData.expiresAt.toDate()) {
      return {
        success: false,
        error: 'OTP expired. Please request a new one.',
      };
    }

    // Check if OTP matches
    if (otpData.code !== otp) {
      return {
        success: false,
        error: 'Invalid OTP. Please try again.',
      };
    }

    // Find user by email
    const userQuery = query(collection(db, 'users'), where('email', '==', email));
    const snapshot = await getDocs(userQuery);

    if (snapshot.empty) {
      return {
        success: false,
        error: 'User not found',
      };
    }

    const userDoc = snapshot.docs[0];
    const userId = userDoc.id;

    // Mark user as verified
    await updateDoc(doc(db, 'users', userId), {
      verified: true,
      verifiedAt: serverTimestamp(),
    });

    // Delete OTP code
    await updateDoc(otpDoc.ref, {
      verified: true,
    });

    return {
      success: true,
      message: 'Email verified successfully. You can now login.',
    };
  } catch (error) {
    console.error('OTP verification error:', error);
    return {
      success: false,
      error: error.message || 'OTP verification failed',
    };
  }
};

/**
 * Resend OTP
 */
export const resendOTP = async (email) => {
  try {
    // Check if user exists
    const userQuery = query(collection(db, 'users'), where('email', '==', email));
    const snapshot = await getDocs(userQuery);

    if (snapshot.empty) {
      return {
        success: false,
        error: 'User not found',
      };
    }

    // Generate new OTP
    const otp = generateOTP();
    await storeOTP(email, otp);
    sendOTPEmail(email, otp);

    return {
      success: true,
      message: 'OTP resent successfully',
    };
  } catch (error) {
    console.error('Resend OTP error:', error);
    return {
      success: false,
      error: error.message || 'Failed to resend OTP',
    };
  }
};

/**
 * Login with email and password
 */
export const loginWithEmail = async (email, password) => {
  try {
    // Check if user is verified
    const userQuery = query(collection(db, 'users'), where('email', '==', email));
    const snapshot = await getDocs(userQuery);

    if (snapshot.empty) {
      return {
        success: false,
        error: 'User not found',
      };
    }

    const userDoc = snapshot.docs[0].data();

    if (!userDoc.verified) {
      return {
        success: false,
        error: 'Email not verified. Please check your inbox for OTP.',
      };
    }

    // Sign in with Firebase Auth
    const userCredential = await signInWithEmailAndPassword(auth, email, password);

    // Get user token
    const token = await userCredential.user.getIdToken();

    return {
      success: true,
      message: 'Login successful',
      user: {
        uid: userCredential.user.uid,
        email: userCredential.user.email,
        name: userCredential.user.displayName,
      },
      token,
    };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: error.message === 'Firebase: Error (auth/user-not-found).'
        ? 'Email not registered'
        : error.message === 'Firebase: Error (auth/wrong-password).'
        ? 'Incorrect password'
        : error.message || 'Login failed',
    };
  }
};

/**
 * Logout
 */
export const logout = async () => {
  try {
    await signOut(auth);
    return {
      success: true,
      message: 'Logged out successfully',
    };
  } catch (error) {
    console.error('Logout error:', error);
    return {
      success: false,
      error: error.message || 'Logout failed',
    };
  }
};

/**
 * Get current user info
 */
export const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      unsubscribe();
      if (user) {
        // Fetch user document from Firestore
        try {
          const userDoc = await getDoc(doc(db, 'users', user.uid));
          resolve({
            uid: user.uid,
            email: user.email,
            name: user.displayName,
            ...userDoc.data(),
          });
        } catch (error) {
          resolve({
            uid: user.uid,
            email: user.email,
            name: user.displayName,
          });
        }
      } else {
        resolve(null);
      }
    });
  });
};

/**
 * Update user profile
 */
export const updateUserProfile = async (userId, updates) => {
  try {
    await updateDoc(doc(db, 'users', userId), {
      ...updates,
      updatedAt: serverTimestamp(),
    });
    return {
      success: true,
      message: 'Profile updated successfully',
    };
  } catch (error) {
    console.error('Update profile error:', error);
    return {
      success: false,
      error: error.message || 'Failed to update profile',
    };
  }
};

/**
 * Request password reset
 */
export const requestPasswordReset = async (email) => {
  try {
    await sendPasswordResetEmail(auth, email);
    return {
      success: true,
      message: 'Password reset email sent',
    };
  } catch (error) {
    console.error('Password reset error:', error);
    return {
      success: false,
      error: error.message || 'Failed to send password reset email',
    };
  }
};

export default {
  signupWithOTP,
  verifyOTP,
  resendOTP,
  loginWithEmail,
  logout,
  getCurrentUser,
  updateUserProfile,
  requestPasswordReset,
};
