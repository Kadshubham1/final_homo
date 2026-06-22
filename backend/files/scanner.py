import os
import re
from io import BytesIO

class MalwareScanner:
    """
    Malware Scanning Utility for File Uploads
    Detects:
    - Suspicious extensions
    - Known malicious strings/patterns
    - Corrupted PDF files
    """

    SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.js', '.vbs', '.scr', '.pif', '.cmd', '.msi', '.ps1']
    
    # Simple signature-based detection for demonstration
    # In production, use ClamAV or a real threat intel feed
    MALICIOUS_PATTERNS = [
        rb'eval\(base64_decode',
        rb'powershell\.exe -ExecutionPolicy Bypass',
        rb'Invoke-WebRequest',
        rb'cmd\.exe /c',
        rb'<script>.*location\.href.*</script>',
        rb'WScript\.Shell',
        rb'document\.write\(unescape\(',
    ]

    @classmethod
    def scan_file(cls, uploaded_file):
        """
        Main entry point for scanning a file.
        Returns (is_safe, error_message)
        """
        filename = uploaded_file.name.lower()
        _, extension = os.path.splitext(filename)

        # 1. Check extension
        if extension in cls.SUSPICIOUS_EXTENSIONS:
            return False, f"⚠️ SECURITY ALERT: The extension '{extension}' is blocked for security reasons. Dangerous scripts (.exe, .bat, .js, etc.) are not allowed."

        # 2. Check for PDF corruption/validity specifically
        if extension == '.pdf':
            is_valid_pdf, pdf_error = cls.validate_pdf(uploaded_file)
            if not is_valid_pdf:
                return False, pdf_error

        # 3. Scan for malicious signatures/patterns
        is_safe, sign_error = cls.scan_signatures(uploaded_file)
        if not is_safe:
            return False, sign_error

        return True, "File is safe"

    @classmethod
    def validate_pdf(cls, uploaded_file):
        """Checks if PDF file header is valid and doesn't look corrupted"""
        uploaded_file.seek(0)
        header = uploaded_file.read(10)
        uploaded_file.seek(0)

        # PDF magic number is %PDF-
        if not header.startswith(rb'%PDF-'):
            return False, "❌ CORRUPTED FILE: This PDF is invalid or corrupted (missing standard PDF header). Please check your file and try again."

        # Check for matching EOF marker (%%EOF) in the last few hundred bytes
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        
        if file_size < 20:
            return False, "❌ INVALID UPLOAD: This PDF file is too small to be a valid document."

        # Check tail for %%EOF
        seek_back = min(file_size, 1024)
        uploaded_file.seek(-seek_back, os.SEEK_END)
        tail = uploaded_file.read()
        uploaded_file.seek(0)

        if rb'%%EOF' not in tail:
            return False, "⚠️ PDF CORRUPTION: This file is missing the required %%EOF marker. It may be incomplete, corrupted, or used to spoof a malicious payload."

        return True, None

    @classmethod
    def scan_signatures(cls, uploaded_file):
        """Scans for known malicious code patterns within the file"""
        uploaded_file.seek(0)
        content = uploaded_file.read(1024 * 1024) # Scan first 1MB for performance
        uploaded_file.seek(0)

        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return False, "🚨 MALWARE DETECTED: This file contains suspicious code signatures (scripts or shell commands) and has been blocked for your protection."

        return True, None

    @classmethod
    def log_attempt(cls, user, filename, reason):
        """Logs a malicious upload attempt (Optional Requirement)"""
        # Normally integrate with a SecurityLog model
        from security_logs.models import SystemLog
        SystemLog.objects.create(
            user=user,
            log_type='security_event',
            action='Malicious File Blocked',
            details={
                'filename': filename,
                'reason': reason,
                'status': 'Blocked'
            },
            is_success=False,
            error_message=reason
        )
