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
import time
import socket

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check if we're running in a headless environment
if os.environ.get('DISPLAY') is None:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    logger.info("Running in headless mode")

app = Flask(__name__)

# Global variables
pygame_available = False
game_instance = None
last_error = None
initialization_attempted = False

def initialize_game():
    global pygame_available, game_instance, last_error, initialization_attempted
    if initialization_attempted:
        logger.info("Game initialization already attempted")
        return pygame_available
    
    initialization_attempted = True
    try:
        logger.info("Attempting to import pygame...")
        import pygame
        logger.info("Pygame imported successfully")
        
        # Initialize pygame with error handling
        logger.info("Initializing pygame...")
        pygame.mixer.quit()  # Disable sound
        pygame.init()
        if pygame.get_error():
            raise Exception(f"Pygame initialization error: {pygame.get_error()}")
        logger.info("Pygame initialized successfully")
        
        # Import game module
        logger.info("Attempting to import game module...")
        import game
        logger.info("Game module imported successfully")
        
        # Create game instance
        logger.info("Creating game instance...")
        game_instance = game.CarRacingGame()
        pygame_available = True
        last_error = None
        logger.info("Game instance created successfully")
        return True
    except Exception as e:
        last_error = str(e)
        logger.error(f"Error initializing game: {e}")
        logger.error(traceback.format_exc())
        pygame_available = False
        return False

# Initialize game on startup
initialize_game()

def generate_game_frames():
    global last_error
    try:
        while True:
            if not pygame_available:
                error_msg = last_error or "Pygame not available"
                logger.error(f"Pygame not available in frame generator: {error_msg}")
                yield "data: " + json.dumps({"error": error_msg}) + "\n\n"
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
        error_msg = last_error or "Pygame initialization failed"
        logger.error(f"Pygame not available in game route: {error_msg}")
        return Response(error_msg, status=500)
    return Response(generate_game_frames(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset_game():
    logger.info("Reset game requested")
    if not pygame_available:
        error_msg = last_error or "Pygame not available"
        logger.error(f"Pygame not available in reset route: {error_msg}")
        return Response(error_msg, status=500)
    try:
        game_instance.reset()
        logger.info("Game reset successfully")
        return Response("Game reset", status=200)
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        logger.error(traceback.format_exc())
        return Response(str(e), status=500)

@app.route('/status')
def status():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return {
        "pygame_available": pygame_available,
        "last_error": last_error,
        "game_instance": "initialized" if game_instance else "not initialized",
        "initialization_attempted": initialization_attempted,
        "server_info": {
            "hostname": hostname,
            "ip_address": ip_address,
            "port": int(os.environ.get('PORT', 5000))
        }
    }

@app.route('/health')
def health_check():
    return Response("OK", status=200)

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 