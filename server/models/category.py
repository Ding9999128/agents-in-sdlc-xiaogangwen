from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    """
    Category model representing a game category in the crowdfunding platform.
    
    This model stores information about game categories including name, description,
    and maintains relationships to the games within each category.
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        """
        Validate the category name field.
        
        Args:
            key (str): The field name being validated
            name (str): The category name to validate
            
        Returns:
            str: The validated name
            
        Raises:
            ValueError: If the name doesn't meet validation requirements
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        """
        Validate the category description field.
        
        Args:
            key (str): The field name being validated
            description (str or None): The description value to validate
            
        Returns:
            str or None: The validated description
            
        Raises:
            ValueError: If the description doesn't meet validation requirements
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self):
        """
        Return a string representation of the Category instance.
        
        Returns:
            str: A formatted string showing the category name
        """
        return f'<Category {self.name}>'
        
    def to_dict(self):
        """
        Convert the Category instance to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the category's data including
                  the count of associated games
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }