from flask import Flask, render_template, Response
import game
import io
import base64
from PIL import Image
import numpy as np
from car_racing_env import CarRacingEnv
from dqn_agent import DQNAgent
import json
import os
import threading
import time

app = Flask(__name__)
game_instance = game.CarRacingGame()
env = CarRacingEnv()
state_size = 8
action_size = 4
agent = DQNAgent(state_size, action_size)

# Try to load the trained model if it exists
model_path = "models/car_racing_dqn_990.h5"
if os.path.exists(model_path):
    agent.load(model_path)
else:
    print("No pre-trained model found. AI will use random actions.")

# Global state for the game
game_state = None
game_lock = threading.Lock()

def game_loop():
    global game_state
    while True:
        with game_lock:
            if game_state is not None:
                env.render()
        time.sleep(1/60)  # 60 FPS

# Start the game loop in a separate thread
game_thread = threading.Thread(target=game_loop, daemon=True)
game_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game_route():
    return Response(game_instance.run(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset():
    global game_state
    with game_lock:
        state = env.reset()
        game_state = state.tolist()
    return jsonify({'state': game_state})

@app.route('/step', methods=['POST'])
def step():
    global game_state
    data = request.json
    action = data['action']
    
    # Convert keyboard input to action values
    action_values = [0, 0]  # [acceleration, steering]
    if action == 'ArrowUp':
        action_values = [1, 0]
    elif action == 'ArrowDown':
        action_values = [-1, 0]
    elif action == 'ArrowLeft':
        action_values = [0, -1]
    elif action == 'ArrowRight':
        action_values = [0, 1]
    
    with game_lock:
        next_state, reward, done = env.step(action_values)
        game_state = next_state.tolist()
    
    return jsonify({
        'state': game_state,
        'reward': reward,
        'done': done
    })

if __name__ == '__main__':
    app.run(debug=True) 