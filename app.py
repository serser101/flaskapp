from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from random import sample
import os 
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure MongoDB settings
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')

# Initialize PyMongo
mongo = PyMongo(app)

@app.route('/randomMatchup', methods=['GET'])
def randomMatchup():
    players = list(mongo.db.Players.find({}))
    if len(players) < 2:
        return jsonify({"error": "Not enough players for a matchup"}), 400
    
    # Create a new matchup with random players
    player_one, player_two = sample(players, 2)
    
    # Generate a unique matchup ID
    matchup_id = str(ObjectId())
    
    new_matchup = {
        '_id': ObjectId(matchup_id),  # Assign the generated ID as the matchup ID
        'player_one_id': ObjectId(player_one['_id']),
        'player_two_id': ObjectId(player_two['_id']),
        'votes_for_player_one': 0,
        'votes_for_player_two': 0
    }
    mongo.db.Matchups.insert_one(new_matchup)
    
    return jsonify({
        "matchup_id": matchup_id,  # Return the generated matchup ID
        "player_one": {
            "id": str(player_one['_id']),
            "name": player_one['name'],
            "photo_url": player_one['photo_url'],
            "team": player_one['team'],
            "team_logo_url": player_one['team_logo_url'],
        },
        "player_two": {
            "id": str(player_two['_id']),
            "name": player_two['name'],
            "photo_url": player_two['photo_url'],
            "team": player_two['team'],
            "team_logo_url": player_two['team_logo_url'],
        },
        "votes_for_player_one": 0,
        "votes_for_player_two": 0
    })
