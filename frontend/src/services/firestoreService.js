/**
 * Firestore Database Service
 * Handles all Firestore operations for files, sharing, and security logs
 */

import {
  collection,
  doc,
  addDoc,
  getDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  limit,
  serverTimestamp,
  arrayUnion,
  arrayRemove,
  writeBatch,
} from 'firebase/firestore';
import { db } from '../config/firebase';

// ============= FILE OPERATIONS =============

/**
 * Upload file metadata to Firestore
 */
export const createFileRecord = async (userId, fileData) => {
  try {
    const docRef = await addDoc(collection(db, 'files'), {
      ...fileData,
      userId,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp(),
      accessCount: 0,
    });
    return {
      success: true,
      fileId: docRef.id,
    };
  } catch (error) {
    console.error('Error creating file record:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get all files for a user
 */
export const getUserFiles = async (userId) => {
  try {
    const filesQuery = query(
      collection(db, 'files'),
      where('userId', '==', userId),
      orderBy('createdAt', 'desc')
    );
    const snapshot = await getDocs(filesQuery);
    const files = [];
    snapshot.forEach((doc) => {
      files.push({ id: doc.id, ...doc.data() });
    });
    return {
      success: true,
      files,
    };
  } catch (error) {
    console.error('Error fetching user files:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get file details
 */
export const getFileDetails = async (fileId) => {
  try {
    const docSnapshot = await getDoc(doc(db, 'files', fileId));
    if (!docSnapshot.exists()) {
      return {
        success: false,
        error: 'File not found',
      };
    }
    return {
      success: true,
      file: { id: docSnapshot.id, ...docSnapshot.data() },
    };
  } catch (error) {
    console.error('Error fetching file details:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Update file
 */
export const updateFile = async (fileId, updates) => {
  try {
    await updateDoc(doc(db, 'files', fileId), {
      ...updates,
      updatedAt: serverTimestamp(),
    });
    return {
      success: true,
      message: 'File updated successfully',
    };
  } catch (error) {
    console.error('Error updating file:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Delete file
 */
export const deleteFile = async (fileId) => {
  try {
    await deleteDoc(doc(db, 'files', fileId));
    return {
      success: true,
      message: 'File deleted successfully',
    };
  } catch (error) {
    console.error('Error deleting file:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

// ============= FILE SHARING OPERATIONS =============

/**
 * Share file with another user
 */
export const shareFile = async (fileId, recipientEmail, expiresInHours = 24) => {
  try {
    const batch = writeBatch(db);

    // Create share record
    const shareRef = doc(collection(db, 'shares'));
    batch.set(shareRef, {
      fileId,
      recipientEmail,
      sharedAt: serverTimestamp(),
      expiresAt: new Date(Date.now() + expiresInHours * 60 * 60 * 1000),
      accessCount: 0,
      maxAccess: 1,
    });

    // Update file with share info
    const fileRef = doc(db, 'files', fileId);
    batch.update(fileRef, {
      sharedWith: arrayUnion({
        email: recipientEmail,
        sharedAt: new Date(),
      }),
    });

    await batch.commit();

    return {
      success: true,
      shareId: shareRef.id,
      message: 'File shared successfully',
    };
  } catch (error) {
    console.error('Error sharing file:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get shared files for a user
 */
export const getSharedFilesForUser = async (email) => {
  try {
    const sharesQuery = query(
      collection(db, 'shares'),
      where('recipientEmail', '==', email),
      where('expiresAt', '>', new Date())
    );
    const snapshot = await getDocs(sharesQuery);
    const shares = [];
    
    for (const shareDoc of snapshot.docs) {
      const shareData = shareDoc.data();
      const fileSnapshot = await getDoc(doc(db, 'files', shareData.fileId));
      if (fileSnapshot.exists()) {
        shares.push({
          shareId: shareDoc.id,
          ...shareData,
          file: fileSnapshot.data(),
        });
      }
    }

    return {
      success: true,
      shares,
    };
  } catch (error) {
    console.error('Error fetching shared files:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Revoke file share
 */
export const revokeShare = async (shareId) => {
  try {
    await deleteDoc(doc(db, 'shares', shareId));
    return {
      success: true,
      message: 'Share revoked successfully',
    };
  } catch (error) {
    console.error('Error revoking share:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

// ============= SECURITY LOG OPERATIONS =============

/**
 * Log security event
 */
export const logSecurityEvent = async (eventData) => {
  try {
    const docRef = await addDoc(collection(db, 'security_logs'), {
      ...eventData,
      timestamp: serverTimestamp(),
      userAgent: navigator.userAgent,
    });
    return {
      success: true,
      logId: docRef.id,
    };
  } catch (error) {
    console.error('Error logging security event:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get security logs
 */
export const getSecurityLogs = async (userId, limitCount = 50) => {
  try {
    const logsQuery = query(
      collection(db, 'security_logs'),
      where('userId', '==', userId),
      orderBy('timestamp', 'desc'),
      limit(limitCount)
    );
    const snapshot = await getDocs(logsQuery);
    const logs = [];
    snapshot.forEach((doc) => {
      logs.push({ id: doc.id, ...doc.data() });
    });
    return {
      success: true,
      logs,
    };
  } catch (error) {
    console.error('Error fetching security logs:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

// ============= USER OPERATIONS =============

/**
 * Search users by email
 */
export const searchUsers = async (email) => {
  try {
    const usersQuery = query(
      collection(db, 'users'),
      where('email', '==', email),
      where('verified', '==', true)
    );
    const snapshot = await getDocs(usersQuery);
    const users = [];
    snapshot.forEach((doc) => {
      users.push({ id: doc.id, ...doc.data() });
    });
    return {
      success: true,
      users,
    };
  } catch (error) {
    console.error('Error searching users:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get user by ID
 */
export const getUserById = async (userId) => {
  try {
    const docSnapshot = await getDoc(doc(db, 'users', userId));
    if (!docSnapshot.exists()) {
      return {
        success: false,
        error: 'User not found',
      };
    }
    return {
      success: true,
      user: { id: docSnapshot.id, ...docSnapshot.data() },
    };
  } catch (error) {
    console.error('Error fetching user:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

export default {
  createFileRecord,
  getUserFiles,
  getFileDetails,
  updateFile,
  deleteFile,
  shareFile,
  getSharedFilesForUser,
  revokeShare,
  logSecurityEvent,
  getSecurityLogs,
  searchUsers,
  getUserById,
};
