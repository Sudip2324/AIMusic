import os
import cv2
import numpy as np
import music21 as m21
from music21.chord import Chord
from music21.stream import Stream

def gen_music(filename):
    ''' converting image to b&w 16x16 px'''
    static_path = 'static'
    im = cv2.imread(os.path.join(static_path, filename))
    try:
        image = cv2.resize(im, (16, 16))
        print('RESIZING SUCCESSFUL')
    except Exception as err:
        print(f'{filename} is invalid: {str(err)}')
        return None
    image[np.all(image < (128, 128, 128), axis=-1)] = (0, 0, 0)
    image[np.all(image >= (128, 128, 128), axis=-1)] = (255, 255, 255)
    black = np.all(image == (0, 0, 0),  axis=-1)
    white = np.all(image == (255, 255, 255), axis=-1)
    image[~black & ~white] = (0, 0, 0)
    base = os.path.basename(filename)
    filename1 = os.path.splitext(base)[0]

    small_image_path =  os.path.join(static_path, 'upload_image',
                                    filename1 + '16x16.png')
    cv2.imwrite(small_image_path, image)

    # extracting parameters for tone matrix from image
    img = cv2.imread(small_image_path)
    new = np.zeros((16, 16), dtype=object)
    for x in range(16):
        for y in range(16):
            if (img[x][y] == [255, 255, 255]).all():
                new[x][y] = 1
            else:
                new[x][y] = 0

    # make 16x16 tone matrix
    a = np.zeros((16, 16), dtype=object)

    # create a list of notes
    notes = ['C7', 'A6', 'G6', 'F6', 'D6', 'C6', 'A5', 'G5',
             'F5', 'D5', 'C5', 'A4', 'G4', 'F4', 'D4', 'C4']

    # loop through the rows and set the values
    for i in range(16):
        a[i, :] = notes[i]

    # pass image parameters to tone matrix
    for x in range(16):
        for y in range(16):
            if (new[x][y] == 1):
                new[x][y] = a[x][y]

    # generating midi file
    stream_algo = Stream()
    for y in range(16):
        add = ''
        for x in range(16):
            if (new[x][y] != 0):
                temp = new[x][y]
                add = add+' '+temp
        if (add):
            stream_algo.insertIntoNoteOrChord(y, Chord(add))

    return stream_algo

def get_tempo(file_name):
    '''
    Args:
        file_name: Path -> Path to midi file
    Return:
        time_sig: str -> return timesignature of midi event
        bpm: str -> return bpm of midi file
    '''
    try:
        music_score = m21.converter.parse(file_name)
    except Exception as err:
        print('*'*10,'Error in loading file: ', err, '*'*10)
        return '4/4', '120'
    time_sig = music_score.recurse().getElementsByClass(m21.meter.TimeSignature)[0].ratioString
    bpm = music_score.recurse().getElementsByClass(m21.tempo.MetronomeMark)[0].number
    print('*'*10, time_sig, bpm, '*'*10)
    return time_sig, bpm
