from flask import jsonify, Response, Blueprint
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query

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
