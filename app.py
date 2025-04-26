from flask import Flask, render_template, Response
import io
import base64
from PIL import Image
import numpy as np
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're running in a headless environment
if os.environ.get('DISPLAY') is None:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

app = Flask(__name__)

try:
    import pygame
    pygame.init()
    import game
    game_instance = game.CarRacingGame()
    pygame_available = True
    logger.info("Pygame initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Pygame: {e}")
    pygame_available = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game_route():
    if not pygame_available:
        return Response("Pygame initialization failed", status=500)
    try:
        return Response(game_instance.run(), mimetype='text/event-stream')
    except Exception as e:
        logger.error(f"Error in game route: {e}")
        return Response(f"Error running game: {str(e)}", status=500)

@app.route('/health')
def health_check():
    return Response("OK", status=200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 