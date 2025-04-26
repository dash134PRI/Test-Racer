from flask import Flask, render_template, Response, request
import io
import base64
from PIL import Image
import numpy as np
import os
import sys
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're running in a headless environment
if os.environ.get('DISPLAY') is None:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'

app = Flask(__name__)

try:
    import pygame
    pygame.mixer.quit()  # Disable sound
    pygame.init()
    logger.info("Pygame initialized successfully")
    import game
    game_instance = game.CarRacingGame()
    pygame_available = True
    logger.info("Game instance created successfully")
except Exception as e:
    logger.error(f"Error initializing Pygame: {e}")
    pygame_available = False

def generate_game_frames():
    try:
        while True:
            if not pygame_available:
                yield "data: " + json.dumps({"error": "Pygame not available"}) + "\n\n"
                break

            try:
                # Get the game frame
                frame = game_instance.get_frame()
                if frame is None:
                    continue

                # Convert the frame to base64
                img = Image.fromarray(frame)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

                # Send the frame
                yield f"data: {json.dumps({'image': img_str})}\n\n"
            except Exception as e:
                logger.error(f"Error generating frame: {e}")
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
                break
    except GeneratorExit:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error in game stream: {e}")
        yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game_route():
    if not pygame_available:
        return Response("Pygame initialization failed", status=500)
    return Response(generate_game_frames(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset_game():
    if not pygame_available:
        return Response("Pygame not available", status=500)
    try:
        game_instance.reset()
        return Response("Game reset", status=200)
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        return Response(str(e), status=500)

@app.route('/health')
def health_check():
    return Response("OK", status=200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 