from flask import Flask, render_template, Response, request
import io
import base64
from PIL import Image
import numpy as np
import os
import sys
import logging
import json
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if we're running in a headless environment
if os.environ.get('DISPLAY') is None:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    logger.info("Running in headless mode")

app = Flask(__name__)

try:
    import pygame
    logger.info("Pygame imported successfully")
    pygame.mixer.quit()  # Disable sound
    pygame.init()
    logger.info("Pygame initialized successfully")
    import game
    logger.info("Game module imported successfully")
    game_instance = game.CarRacingGame()
    pygame_available = True
    logger.info("Game instance created successfully")
except Exception as e:
    logger.error(f"Error initializing game: {e}")
    logger.error(traceback.format_exc())
    pygame_available = False

def generate_game_frames():
    try:
        while True:
            if not pygame_available:
                logger.error("Pygame not available in frame generator")
                yield "data: " + json.dumps({"error": "Pygame not available"}) + "\n\n"
                break

            try:
                # Get the game frame
                frame = game_instance.get_frame()
                if frame is None:
                    logger.warning("Received None frame from game")
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
                logger.error(traceback.format_exc())
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
                break
    except GeneratorExit:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error in game stream: {e}")
        logger.error(traceback.format_exc())
        yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/game')
def game_route():
    logger.info("Game route accessed")
    if not pygame_available:
        logger.error("Pygame not available in game route")
        return Response("Pygame initialization failed", status=500)
    return Response(generate_game_frames(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset_game():
    logger.info("Reset game requested")
    if not pygame_available:
        logger.error("Pygame not available in reset route")
        return Response("Pygame not available", status=500)
    try:
        game_instance.reset()
        logger.info("Game reset successfully")
        return Response("Game reset", status=200)
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        logger.error(traceback.format_exc())
        return Response(str(e), status=500)

@app.route('/health')
def health_check():
    logger.info("Health check accessed")
    return Response("OK", status=200)

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 