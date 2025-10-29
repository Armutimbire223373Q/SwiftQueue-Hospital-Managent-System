"""
Input Sanitization Utilities - Prevent injection attacks and XSS
"""
import re
import html
from typing import Any, Dict, List, Union
from bleach import clean
import bleach


class InputSanitizer:
    """
    Sanitize user input to prevent security vulnerabilities
    """
    
    # Allowed HTML tags for rich text fields (very restrictive)
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'a', 'span'
    ]
    
    # Allowed HTML attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'span': ['class'],
    }
    
    # Allowed URL protocols
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @staticmethod
    def sanitize_string(value: str, allow_html: bool = False) -> str:
        """
        Sanitize a string input
        
        Args:
            value: Input string
            allow_html: If True, allow safe HTML tags
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        if allow_html:
            # Use bleach to clean HTML
            return clean(
                value,
                tags=InputSanitizer.ALLOWED_TAGS,
                attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
                protocols=InputSanitizer.ALLOWED_PROTOCOLS,
                strip=True
            )
        else:
            # Escape all HTML
            return html.escape(value)
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Sanitize and validate email address
        
        Args:
            email: Email address
        
        Returns:
            Sanitized email or raises ValueError
        """
        email = email.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Check for suspicious patterns
        if '..' in email or email.startswith('.') or email.endswith('.'):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Sanitize phone number
        
        Args:
            phone: Phone number
        
        Returns:
            Sanitized phone number (digits only)
        """
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Validate length (adjust based on your country)
        if len(phone) < 10 or len(phone) > 15:
            raise ValueError("Invalid phone number length")
        
        return phone
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        
        Args:
            filename: Original filename
        
        Returns:
            Safe filename
        """
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitize URL
        
        Args:
            url: URL to sanitize
        
        Returns:
            Safe URL or raises ValueError
        """
        url = url.strip()
        
        # Check protocol
        if not url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL protocol")
        
        # Check for suspicious patterns
        if any(pattern in url.lower() for pattern in ['javascript:', 'data:', 'vbscript:']):
            raise ValueError("Invalid URL content")
        
        return url
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allow_html: bool = False) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values
        
        Args:
            data: Dictionary to sanitize
            allow_html: Allow HTML in string values
        
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = InputSanitizer.sanitize_string(str(key), allow_html=False)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = InputSanitizer.sanitize_string(value, allow_html=allow_html)
            elif isinstance(value, dict):
                sanitized[safe_key] = InputSanitizer.sanitize_dict(value, allow_html=allow_html)
            elif isinstance(value, list):
                sanitized[safe_key] = InputSanitizer.sanitize_list(value, allow_html=allow_html)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any], allow_html: bool = False) -> List[Any]:
        """
        Sanitize list elements
        
        Args:
            data: List to sanitize
            allow_html: Allow HTML in string values
        
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for value in data:
            if isinstance(value, str):
                sanitized.append(InputSanitizer.sanitize_string(value, allow_html=allow_html))
            elif isinstance(value, dict):
                sanitized.append(InputSanitizer.sanitize_dict(value, allow_html=allow_html))
            elif isinstance(value, list):
                sanitized.append(InputSanitizer.sanitize_list(value, allow_html=allow_html))
            else:
                sanitized.append(value)
        
        return sanitized
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        Sanitize SQL identifier (table name, column name)
        Use only when absolutely necessary - prefer parameterized queries
        
        Args:
            identifier: SQL identifier
        
        Returns:
            Safe identifier
        """
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValueError("Invalid SQL identifier")
        
        # Prevent SQL keywords (basic list)
        sql_keywords = {
            'select', 'insert', 'update', 'delete', 'drop', 'create',
            'alter', 'table', 'from', 'where', 'union', 'exec'
        }
        
        if identifier.lower() in sql_keywords:
            raise ValueError("SQL keyword not allowed as identifier")
        
        return identifier
    
    @staticmethod
    def validate_json(data: Any, max_depth: int = 10, current_depth: int = 0) -> bool:
        """
        Validate JSON data structure to prevent deeply nested attacks
        
        Args:
            data: Data to validate
            max_depth: Maximum nesting depth
            current_depth: Current depth (internal)
        
        Returns:
            True if valid
        
        Raises:
            ValueError if invalid
        """
        if current_depth > max_depth:
            raise ValueError(f"JSON nesting too deep (max {max_depth})")
        
        if isinstance(data, dict):
            for value in data.values():
                InputSanitizer.validate_json(value, max_depth, current_depth + 1)
        elif isinstance(data, list):
            for item in data:
                InputSanitizer.validate_json(item, max_depth, current_depth + 1)
        
        return True


# Convenience function
def sanitize(value: Any, allow_html: bool = False) -> Any:
    """
    Sanitize any input value
    
    Args:
        value: Value to sanitize
        allow_html: Allow HTML in strings
    
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        return InputSanitizer.sanitize_string(value, allow_html=allow_html)
    elif isinstance(value, dict):
        return InputSanitizer.sanitize_dict(value, allow_html=allow_html)
    elif isinstance(value, list):
        return InputSanitizer.sanitize_list(value, allow_html=allow_html)
    else:
        return value


# Export main classes and functions
__all__ = ['InputSanitizer', 'sanitize']
