from flask import Flask, request, jsonify, render_template, send_file
import os
import time
import auto_predict

app = Flask(__name__)


@app.route('/')
def home():
    # Render the home page template
    return render_template('index.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():

    if request.method == 'POST':
        instrument = request.form['instrument']
        model_input = request.form['model_input']
        timesig = request.form['timesig']
        bpm = request.form['bpm']

    out_music = auto_predict.music_stream(
        instrument, model_input, timesig, bpm)

    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    new_file = f'static/{instrument}_{bpm}bpm_' + timestr + '.mid'
    out_music.write('midi', new_file)
    return render_template('result.html', file_path=new_file, instrument=instrument, timesig=timesig, bpm=bpm)


if __name__ == '__main__':
    app.run(debug=True)
