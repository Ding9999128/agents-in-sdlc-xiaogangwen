# filepath: server/models/base.py
from . import db

class BaseModel(db.Model):
    """
    Base model class providing common functionality for all database models.
    
    This abstract base class extends SQLAlchemy's Model class and provides
    common validation methods that can be used by all derived model classes.
    """
    __abstract__ = True
    
    @staticmethod
    def validate_string_length(field_name, value, min_length=2, allow_none=False):
        """
        Validate that a string field meets minimum length requirements.
        
        Args:
            field_name (str): The name of the field being validated (for error messages)
            value (str or None): The value to validate
            min_length (int, optional): Minimum required length. Defaults to 2.
            allow_none (bool, optional): Whether None values are allowed. Defaults to False.
            
        Returns:
            str or None: The validated value
            
        Raises:
            ValueError: If the value doesn't meet validation requirements
        """
        if value is None:
            if allow_none:
                return value
            else:
                raise ValueError(f"{field_name} cannot be empty")
        
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
            
        if len(value.strip()) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
            
        return value