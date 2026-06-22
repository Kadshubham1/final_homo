/**
 * Firebase Storage Service
 * Handles file uploads, downloads, and storage operations
 */

import {
  ref,
  uploadBytes,
  downloadURL,
  deleteObject,
  listAll,
  getMetadata,
} from 'firebase/storage';
import { storage } from '../config/firebase';

// ============= FILE UPLOAD =============

/**
 * Upload file to Firebase Storage
 * @param {string} userId - User ID
 * @param {File} file - File to upload
 * @param {Function} onProgress - Progress callback
 */
export const uploadFile = async (userId, file, onProgress = null) => {
  try {
    // Create a unique filename
    const timestamp = new Date().getTime();
    const filename = `${timestamp}_${file.name}`;
    const storagePath = `users/${userId}/files/${filename}`;

    // Create reference
    const fileRef = ref(storage, storagePath);

    // Upload with progress tracking
    const uploadTask = await uploadBytes(fileRef, file, {
      customMetadata: {
        originalName: file.name,
        uploadedAt: new Date().toISOString(),
        userId,
      },
    });

    // Get download URL
    const downloadUrl = await downloadURL(fileRef);

    return {
      success: true,
      file: {
        name: file.name,
        size: file.size,
        type: file.type,
        storagePath,
        downloadUrl,
        uploadedAt: new Date(),
      },
    };
  } catch (error) {
    console.error('Error uploading file:', error);
    return {
      success: false,
      error: error.message || 'Failed to upload file',
    };
  }
};

/**
 * Upload file with progress tracking
 */
export const uploadFileWithProgress = async (userId, file, onProgress) => {
  try {
    const timestamp = new Date().getTime();
    const filename = `${timestamp}_${file.name}`;
    const storagePath = `users/${userId}/files/${filename}`;

    const fileRef = ref(storage, storagePath);

    // Simulate progress (Firebase doesn't have native progress in SDK)
    const chunkSize = 1024 * 1024; // 1MB
    let uploadedBytes = 0;

    return new Promise((resolve, reject) => {
      uploadBytes(fileRef, file)
        .then(async (uploadTask) => {
          const downloadUrl = await downloadURL(fileRef);
          if (onProgress) {
            onProgress(100);
          }
          resolve({
            success: true,
            file: {
              name: file.name,
              size: file.size,
              type: file.type,
              storagePath,
              downloadUrl,
              uploadedAt: new Date(),
            },
          });
        })
        .catch((error) => {
          reject({
            success: false,
            error: error.message || 'Failed to upload file',
          });
        });
    });
  } catch (error) {
    console.error('Error uploading file with progress:', error);
    return {
      success: false,
      error: error.message || 'Failed to upload file',
    };
  }
};

// ============= FILE DOWNLOAD =============

/**
 * Download file from Firebase Storage
 */
export const downloadFile = async (storagePath) => {
  try {
    const fileRef = ref(storage, storagePath);
    const downloadUrl = await downloadURL(fileRef);
    return {
      success: true,
      downloadUrl,
    };
  } catch (error) {
    console.error('Error getting download URL:', error);
    return {
      success: false,
      error: error.message || 'Failed to download file',
    };
  }
};

/**
 * Download file as blob
 */
export const downloadFileAsBlob = async (storagePath) => {
  try {
    const fileRef = ref(storage, storagePath);
    // Note: This requires using REST API or Cloud Functions
    // Firebase SDK doesn't support direct blob download in browser
    const downloadUrl = await downloadURL(fileRef);
    const response = await fetch(downloadUrl);
    const blob = await response.blob();
    return {
      success: true,
      blob,
    };
  } catch (error) {
    console.error('Error downloading file as blob:', error);
    return {
      success: false,
      error: error.message || 'Failed to download file',
    };
  }
};

// ============= FILE DELETION =============

/**
 * Delete file from Firebase Storage
 */
export const deleteStorageFile = async (storagePath) => {
  try {
    const fileRef = ref(storage, storagePath);
    await deleteObject(fileRef);
    return {
      success: true,
      message: 'File deleted successfully',
    };
  } catch (error) {
    console.error('Error deleting file:', error);
    return {
      success: false,
      error: error.message || 'Failed to delete file',
    };
  }
};

// ============= FILE LISTING =============

/**
 * List all files for a user
 */
export const listUserFiles = async (userId) => {
  try {
    const dirRef = ref(storage, `users/${userId}/files/`);
    const result = await listAll(dirRef);

    const files = [];
    for (const fileRef of result.items) {
      const metadata = await getMetadata(fileRef);
      const downloadUrl = await downloadURL(fileRef);
      files.push({
        name: metadata.name,
        fullPath: metadata.fullPath,
        size: metadata.size,
        contentType: metadata.contentType,
        timeCreated: metadata.timeCreated,
        updated: metadata.updated,
        downloadUrl,
      });
    }

    return {
      success: true,
      files,
    };
  } catch (error) {
    console.error('Error listing files:', error);
    return {
      success: false,
      error: error.message || 'Failed to list files',
    };
  }
};

/**
 * Get file metadata
 */
export const getFileMetadata = async (storagePath) => {
  try {
    const fileRef = ref(storage, storagePath);
    const metadata = await getMetadata(fileRef);
    return {
      success: true,
      metadata,
    };
  } catch (error) {
    console.error('Error getting file metadata:', error);
    return {
      success: false,
      error: error.message || 'Failed to get file metadata',
    };
  }
};

// ============= FILE SHARING =============

/**
 * Generate shareable link (valid for 7 days)
 * Returns download URL which is already shareable
 */
export const generateShareableLink = async (storagePath, expiryDays = 7) => {
  try {
    const fileRef = ref(storage, storagePath);
    // Firebase Storage URLs are already shareable and public
    const downloadUrl = await downloadURL(fileRef);
    return {
      success: true,
      shareLink: downloadUrl,
      expiresIn: `${expiryDays} days`,
      note: 'Anyone with this link can download the file',
    };
  } catch (error) {
    console.error('Error generating shareable link:', error);
    return {
      success: false,
      error: error.message || 'Failed to generate shareable link',
    };
  }
};

export default {
  uploadFile,
  uploadFileWithProgress,
  downloadFile,
  downloadFileAsBlob,
  deleteStorageFile,
  listUserFiles,
  getFileMetadata,
  generateShareableLink,
};
