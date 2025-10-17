from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    """
    Create a base query for retrieving games with joined publisher and category data.
    
    This function creates a SQLAlchemy query that joins the Game table with
    Publisher and Category tables using outer joins to ensure games are
    returned even if they don't have associated publishers or categories.
    
    Returns:
        Query: A SQLAlchemy Query object for games with joined related data
    """
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    """
    Retrieve all games from the database.
    
    This endpoint returns a JSON array containing all games in the database
    with their associated publisher and category information.
    
    Returns:
        Response: A Flask Response object containing JSON array of games
    """
    # Use the base query for all games
    games_query = get_games_base_query().all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    return jsonify(games_list)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    """
    Retrieve a specific game by its ID.
    
    This endpoint returns a single game with the specified ID, including
    its associated publisher and category information.
    
    Args:
        id (int): The unique identifier of the game to retrieve
        
    Returns:
        Response: A Flask Response object containing JSON data for the game,
                 or a 404 error response if the game is not found
    """
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int] | Response:
    """
    Create a new game.
    
    Expects JSON payload with title, description, category_id, publisher_id,
    and optional star_rating.
    
    Returns:
        Response: A Flask Response object containing JSON data for the created game,
                 or error responses for validation failures or missing data
    """
    try:
        # Parse JSON data from request
        data = request.get_json(force=True, silent=True)
        if data is None or not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'category_id', 'publisher_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate that publisher and category exist
        publisher = Publisher.query.get(data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 404
            
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 404
        
        # Create new game
        new_game = Game(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            publisher_id=data['publisher_id'],
            star_rating=data.get('star_rating')
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        # Return the created game with related data
        created_game = get_games_base_query().filter(Game.id == new_game.id).first()
        return jsonify(created_game.to_dict()), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int] | Response:
    """
    Update an existing game by ID.
    
    Expects JSON payload with optional fields: title, description, category_id,
    publisher_id, star_rating.
    
    Args:
        id (int): The unique identifier of the game to update
        
    Returns:
        Response: A Flask Response object containing JSON data for the updated game,
                 or error responses for validation failures or if game not found
    """
    try:
        # Get the existing game
        game = Game.query.get(id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Parse JSON data from request  
        data = request.get_json(force=True, silent=True)
        if data is None or not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
            
        # Validate and update publisher_id if provided
        if 'publisher_id' in data:
            publisher = Publisher.query.get(data['publisher_id'])
            if not publisher:
                return jsonify({"error": "Publisher not found"}), 404
            game.publisher_id = data['publisher_id']
            
        # Validate and update category_id if provided
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({"error": "Category not found"}), 404
            game.category_id = data['category_id']
        
        db.session.commit()
        
        # Return the updated game with related data
        updated_game = get_games_base_query().filter(Game.id == id).first()
        return jsonify(updated_game.to_dict())
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int]:
    """
    Delete a game by ID.
    
    Args:
        id (int): The unique identifier of the game to delete
        
    Returns:
        Response: A Flask Response object with success message or error if game not found
    """
    try:
        # Get the existing game
        game = Game.query.get(id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({"message": "Game deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
