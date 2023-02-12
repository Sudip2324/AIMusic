import os
import time
import auto_predict
import tone
from flask import Flask, request, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    '''
    Render the home page template
    '''
    return render_template('index.html')

@app.route('/algorithm')
def algorithm_home():
    '''
    Render page for algorithm generation
    '''
    return render_template('algo_index.html')

@app.route('/ai_generate', methods=['GET', 'POST'])
def ai_generate():
    '''
    Generate AI music from model
    '''
    
    if request.method == 'POST':
        instrument = request.form['instrument']
        model_input = request.form['model_input']
        timesig = request.form['timesig']
        bpm = request.form['bpm']

    out_music = auto_predict.music_stream(
        instrument, model_input, timesig, bpm)

    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    new_file = f'static/ai_generation/{instrument}_{bpm}bpm_' + timestr + '.mid'
    out_music.write('midi', new_file)
    return render_template('result.html',
                            file_path=new_file,
                            instrument=instrument,
                            timesig=timesig,
                            bpm=bpm)


@app.route('/algo_generate', methods=['GET', 'POST'])
def algo_generate():
    '''
    Return: file for algorithmic generation of midi file
    '''
    static_path = 'static'
    if request.method == 'POST':
        try:
            f = request.files['file']
        except Exception as err:
            return render_template('sorry.html', message='No file was attached to the request')

        f.save(f'static/{f.filename}')
        print(f.filename)

    out_music = tone.gen_music(f.filename)
    if out_music is None:
        return render_template('sorry.html')

    base = os.path.basename(f.filename)
    filename1 = os.path.splitext(base)[0]
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

    new_file = os.path.join(static_path, 'midi_generation', 
                            filename1 + timestr + '.mid')
    print(f'new file: {new_file}')
    out_music.write('midi', new_file)
    return render_template('algo_result.html',
                            file_path=new_file,
                            ori_image=f.filename,
                            img_name=filename1)

if __name__ == '__main__':
    app.run(debug=True)
