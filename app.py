import os
import time
import music21 as m21
from flask import Flask, request, render_template, url_for
import auto_predict
import tone

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

@app.route('/ai_algo_sync')
def ai_algo_sync():
    '''
    Render page for ai algorithm sync generation
    '''
    return render_template('ai_algo_sync_index.html')

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
            return render_template('sorry.html', message=f'Please provide valid file: {err}')
        instrument1 = request.form['instrument1']
        instrument2 = request.form['instrument2']
        music_length = int(request.form['tone_length'])

        f.save(f'static/{f.filename}')
        print(f.filename)

    out_music = tone.gen_music(f.filename, instrument1, instrument2, SEQ_LEN=music_length)
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
                            length = music_length,
                            img_name=filename1)

@app.route('/ai_algo_sync_generate', methods=['GET', 'POST'])
def ai_algo_sync_generate():
    '''
    Return: file for ai generation of midi file with syncing 
            algorithmic generation of midi file
    '''
    static_path = 'static'
    if request.method == 'POST':
        instrument = request.form['instrument']
        instrument1 = request.form['algo_instrument']
        model_input = request.form['model_input']
        try:
            f = request.files['file']
        except Exception as err:
            print('*'*10, 'Error in Sending file:  ',err, '*'*10)
            return render_template('sorry.html', message='Please provide valid file')
        f.save(f'static/{f.filename}')
        print(f.filename)

    algo_music = tone.gen_music(f.filename,
                                instrument1=instrument1,
                                SEQ_LEN=128)
    if algo_music is None:
        return render_template('sorry.html')

    base = os.path.basename(f.filename)
    filename1 = os.path.splitext(base)[0]
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

    new_file = os.path.join(static_path, 'midi_generation', 
                            filename1 + timestr + '.mid')
    print(f'new file: {new_file}')
    algo_music.write('midi', new_file)

    notes, durations, timesig, bpm = tone.get_tempo(new_file)

    ai_music = auto_predict.music_stream(instrument, model_input,
                                                     timesig, bpm, 
                                                     notes_seed=notes, 
                                                     durations_seed=durations)

    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    ai_filename = f'static/ai_generation/{instrument}_' + timestr + '.mid'
    ai_music.write('midi', ai_filename)
    stream_algo = m21.stream.Stream()
    stream_algo.insert(0.0, algo_music)
    stream_algo.insert(0.0, ai_music)
    output_filename = f'static/ai_generation/ai_algo_generation/ai_{instrument}_algo_{instrument1}' + timestr + '.mid'
    stream_algo.write('midi', output_filename)
    
    return render_template('ai_algo_sync_generate.html',
                            file_path = new_file,
                            ori_image = f.filename,
                            img_name = filename1,
                            instrument = instrument,
                            algo_instrument = instrument1,
                            timesig = timesig,
                            bpm = bpm,
                            length = 128,
                            algo_ai_music = output_filename)

if __name__ == '__main__':
    app.run(debug=True)
