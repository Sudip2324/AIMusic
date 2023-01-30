from flask import Flask, request, render_template, url_for
import time
import tone
import os

app = Flask(__name__)

@app.route('/')
def home():
    # Render the home page template
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():

    if request.method == 'POST':
        try:
            f = request.files['file']
        except:
            return render_template('sorry.html')
        f.save(f'static/{f.filename}')
        print(f.filename)

    out_music = tone.gen_music(f.filename)
    if out_music is None:
        return render_template('sorry.html')

    base = os.path.basename(f.filename)
    filename1 = os.path.splitext(base)[0]
    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    new_file = f'static/{filename1}' + timestr + '.mid'
    print(f'new file: {new_file}')
    out_music.write('midi', new_file)
    return render_template('result.html', file_path=new_file, ori_image=f.filename, img_name=filename1)

if __name__ == '__main__':
    app.run(debug=True)
