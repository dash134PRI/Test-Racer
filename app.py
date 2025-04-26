from flask import Flask, render_template, Response
import cv2
import numpy as np
import pygame
import io
from game import CarRacingGame

app = Flask(__name__)
game = CarRacingGame()

def generate_frames():
    while True:
        # Get the current game state
        frame = pygame.surfarray.array3d(game.screen)
        frame = frame.swapaxes(0, 1)
        
        # Convert to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control/<action>')
def control(action):
    if action == 'up':
        game.car_speed += game.acceleration
    elif action == 'down':
        game.car_speed -= game.acceleration
    elif action == 'left':
        game.car_angle -= game.turn_speed
    elif action == 'right':
        game.car_angle += game.turn_speed
    elif action == 'reset':
        game.reset()
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 