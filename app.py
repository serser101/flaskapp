from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from random import sample
import os

app = Flask(__name__)

# Configure MongoDB settings
app.config["MONGO_URI"] = os.environ.get(
    'MONGO_URI', 'mongodb+srv://sergeiganz:Franklin1948!@soccergame.jam2il0.mongodb.net/soccergame')

# Initialize PyMongo
mongo = PyMongo(app)

@app.route('/')
def home():
    return "Welcome to the Soccer Game Voting App"

@app.route('/test_connection')
def test_connection():
    try:
        player = mongo.db.Players.find_one({})
        if player:
            return jsonify({"success": True, "player": str(player)})
        else:
            return jsonify({"success": False, "message": "No data found in Players collection."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/randomMatchup', methods=['GET'])
def random_matchup():
    players = list(mongo.db.Players.find({}))
    if len(players) < 2:
        return jsonify({"error": "Not enough players for a matchup"}), 400
    player_one, player_two = sample(players, 2)
    return jsonify({
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
        }
    })

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    player_one_id = data['player_one_id']
    player_two_id = data['player_two_id']
    voted_for_player_one = data['voted_for_player_one']
    matchup_query = {
        'player_one_id': ObjectId(player_one_id),
        'player_two_id': ObjectId(player_two_id)
    }
    matchup = mongo.db.Matchups.find_one(matchup_query)
    if matchup:
        update_field = 'votes_for_player_one' if voted_for_player_one else 'votes_for_player_two'
        mongo.db.Matchups.update_one(matchup_query, {'$inc': {update_field: 1}})
    else:
        new_matchup = {
            'player_one_id': ObjectId(player_one_id),
            'player_two_id': ObjectId(player_two_id),
            'votes_for_player_one': 1 if voted_for_player_one else 0,
            'votes_for_player_two': 0 if voted_for_player_one else 1
        }
        mongo.db.Matchups.insert_one(new_matchup)
    return jsonify({"message": "Vote recorded successfully"})

if __name__ == '__main__':
    app.run()
