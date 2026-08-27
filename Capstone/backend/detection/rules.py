import re
import urllib.parse

# RegEx signatures for SQL Injection
SQLI_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|EXEC|TRUNCATE)\b)",
    r"('|\"|%27|%22)?\s*(OR|AND)\s*('|\"|%27|%22)?\s*(\d+|\w+|'|\"|%27|%22)?\s*=\s*('|\"|\d+|\w+|%27|%22)?",
    r"('|\"|%27|%22)\s*(OR|AND)\s*('|\"|\d|\w)",
    r"('|\"|%27|%22)\s*=\s*('|\"|%27|%22)",
    r"(--|#|/\*)",
    r"(\bOR\b\s+\d+=\d+)",
    r"(\b1=1\b|\b1\s*=\s*1\b)"
]

# RegEx signatures for Cross-Site Scripting (XSS)
XSS_PATTERNS = [
    r"(<script[^>]*>|%3Cscript)",
    r"(javascript:)",
    r"(onerror\s*=)",
    r"(onload\s*=)",
    r"(alert\(|eval\()",
    r"(<iframe[^>]*>)"
]

# Path Traversal & Sensitive Endpoint Scanning
PATH_TRAVERSAL_PATTERNS = [
    r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/)",
    r"(/etc/passwd|/etc/shadow|boot\.ini|win\.ini)",
    r"(\.env|\.git/|\.config)",
    r"(/phpmyadmin|/admin/config|/wp-login)"
]

def check_sqli(input_string):
    if not input_string:
        return False, None
    decoded = urllib.parse.unquote(str(input_string))
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE) or re.search(pattern, decoded, re.IGNORECASE):
            return True, f"SQL Injection signature pattern detected: '{pattern}'"
    return False, None

def check_xss(input_string):
    if not input_string:
        return False, None
    decoded = urllib.parse.unquote(str(input_string))
    for pattern in XSS_PATTERNS:
        if re.search(pattern, input_string, re.IGNORECASE) or re.search(pattern, decoded, re.IGNORECASE):
            return True, f"Cross-Site Scripting (XSS) payload detected: '{pattern}'"
    return False, None

def check_path_traversal(path_string):
    if not path_string:
        return False, None
    decoded = urllib.parse.unquote(str(path_string))
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, path_string, re.IGNORECASE) or re.search(pattern, decoded, re.IGNORECASE):
            return True, f"Path Traversal / Sensitive scanner access: '{pattern}'"
    return False, None
