from flask import Flask, render_template, Response
import game
import io
import base64
from PIL import Image
import numpy as np

app = Flask(__name__)
game_instance = game.CarRacingGame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game_route():
    return Response(game_instance.run(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True) 