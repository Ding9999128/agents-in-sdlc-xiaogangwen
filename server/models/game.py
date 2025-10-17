from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Game(BaseModel):
    """
    Game model representing a game in the crowdfunding platform.
    
    This model stores information about games including title, description,
    star rating, and relationships to publishers and categories.
    """
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    star_rating = db.Column(db.Float, nullable=True)
    
    # Foreign keys for one-to-many relationships
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'), nullable=False)
    
    # One-to-many relationships (many games belong to one category/publisher)
    category = relationship("Category", back_populates="games")
    publisher = relationship("Publisher", back_populates="games")
    
    @validates('title')
    def validate_name(self, key, name):
        """
        Validate the game title field.
        
        Args:
            key (str): The field name being validated
            name (str): The title value to validate
            
        Returns:
            str: The validated title
            
        Raises:
            ValueError: If the title doesn't meet validation requirements
        """
        return self.validate_string_length('Game title', name, min_length=2)
    
    @validates('description')
    def validate_description(self, key, description):
        """
        Validate the game description field.
        
        Args:
            key (str): The field name being validated
            description (str or None): The description value to validate
            
        Returns:
            str or None: The validated description
            
        Raises:
            ValueError: If the description doesn't meet validation requirements
        """
        if description is not None:
            return self.validate_string_length('Description', description, min_length=10, allow_none=True)
        return description
    
    def __repr__(self):
        """
        Return a string representation of the Game instance.
        
        Returns:
            str: A formatted string showing the game title and ID
        """
        return f'<Game {self.title}, ID: {self.id}>'

    def to_dict(self):
        """
        Convert the Game instance to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the game's data with publisher
                  and category information included
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'publisher': {'id': self.publisher.id, 'name': self.publisher.name} if self.publisher else None,
            'category': {'id': self.category.id, 'name': self.category.name} if self.category else None,
            'starRating': self.star_rating  # Changed from star_rating to starRating
        }