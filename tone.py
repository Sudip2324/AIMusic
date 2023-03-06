import os
import cv2
import numpy as np
import music21 as m21

def generate_part(switch, bw_image, instrument):
    '''
    Generate music part
    Args:
        switch: np.array-> Switch of tone matrix
        bw_image: np.array -> 16x16 black and white image
        instrument: str -> instrument for music part
    Return:
        Music21 stream object
    '''
    stream_algo = m21.stream.Stream()
    instrument_func = getattr(m21.instrument, instrument)()
    stream_algo.insert(0.0, instrument_func)
    offset = 0
    for y in range(16):
        add = ''
        for x in range(16):
            if (bw_image[x][y] == 255):
                temp = switch[x][y]
                add = add+' '+temp
        # if (add):
        stream_algo.insertIntoNoteOrChord(offset, m21.chord.Chord(add))
        if (len(add.split()) == 1):
            offset += 0.5
            # print('single',offset)
        else:
            offset += 1
    return stream_algo

def gen_music(filename, instrument1, instrument2="None"):
    '''Generate music using algorithmic approch
    Args:
        filename: Path-> path of image file to be used to generate music
        instrument1: str -> Default string used to generate music
        instrument2: str(default: "None") -> name of instrument used to add to music, additional instrument for music
    Return:
        stream_algo: music21.stream.Stream -> object of music21 after generating music
    '''
    static_path = 'static'
    img = cv2.imread(os.path.join(static_path, filename))

    # Convert the image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    try:
        # Resize the image to 16x16 pixels
        resized_img = cv2.resize(gray_img, (16, 16))
        print('RESIZING SUCCESSFUL')
    except Exception as err:
        print(f'{filename} is invalid: {str(err)}')
        return None

    # Get the intensity values of the resized image
    intensity_values = resized_img.flatten()

    # Transpose the intensity values to get the values column-wise
    intensity_values_column_wise = [intensity_values[i::16] for i in range(16)]

    column_index = []
    column_index_min = []
    # Print the index of the intensity values column-wise
    for i, col in enumerate(intensity_values_column_wise):
        indices = np.where(col == col.max())[0].tolist()
        indices_min = np.where(col == col.min())[0].tolist()
        column_index.append(indices)
        column_index_min.append(indices_min)
        # print(f'Column {i}: {col} and maxindex: {indices}')

    base = os.path.basename(filename)
    filename1 = os.path.splitext(base)[0]

    small_image_path =  os.path.join(static_path, 'upload_image',
                                    filename1 + '16x16.png')

    # make 16x16 tone matrix
    switch = np.zeros((16, 16), dtype='object')
    notes = ['C6', 'A5', 'G5', 'F5', 'D5', 'C5', 'A4', 'G4',
            'F4', 'D4', 'C4', 'A3', 'G3', 'F3', 'D3', 'C3']
    for i in range(16):
        switch[i, :] = notes[i]

    bw_image = np.zeros((16, 16), dtype='uint8')
    for i, index_col in enumerate(column_index):
        # print(index_col)
        if len(index_col) == 1:
            col = index_col[0]
            bw_image[i][col] = 255
        elif len(index_col) == 2:
            # print(index_col)
            col = index_col[0]
            col2 = index_col[1]
            bw_image[i][col] = 255
            bw_image[i][col2] = 255
        elif len(index_col) > 2:
            rand_index = sorted(np.random.randint(0, len(index_col), size=2))
            # print(rand_index)
            if i % 2 == 0:
                col1 = index_col[-1]
            else:
                col1 = index_col[-2]
            col2 = rand_index[-1]
            col3 = rand_index[-2]
            bw_image[i][col1] = 255
            bw_image[i][col2] = 255
            bw_image[i][col3] = 255
    bw_image = bw_image.T

    # save black and white image
    cv2.imwrite(small_image_path, bw_image)

    # switches control using minimum intensity
    bw_image_min = np.zeros((16, 16), dtype='uint8')
    for i, index_col in enumerate(column_index_min):
        if len(index_col) == 1:
            col = index_col[0]
            bw_image_min[i][col] = 255
        elif len(index_col) > 1:
            col = index_col[-1]
            bw_image_min[i][col] = 255

    bw_image_min = bw_image_min.T
    # generating midi file for instrument1
    stream1 = generate_part(switch, bw_image, instrument=instrument1)
    if instrument2 == "None":
        stream_algo = stream1
        stream1.show('text')
    else:
        stream2 = generate_part(switch, bw_image_min, instrument=instrument2)
        stream_algo = m21.stream.Stream()
        stream2.show('text')
        stream_algo.insert(0.0, stream1)
        stream_algo.insert(0.0, stream2)
    return stream_algo

import json
def get_tempo(file_name):
    '''
    Args:
        file_name: Path -> Path to midi file
    Return:
        time_sig: str -> return timesignature of midi event
        bpm: str -> return bpm of midi file
    '''
    notes_to_int = {"A3": 1,
                    "A4": 3,
                    "A5": 8,
                    "C3": 26,
                    "C4": 27,
                    "C5": 28,
                    "C6": 31,
                    "D3": 32,
                    "D4": 33,
                    "D5": 35,
                    "F3": 56,
                    "F4": 57,
                    "F5": 61,
                    "G3": 67,
                    "G4": 68,
                    "G5": 73,
                    "rest": 75}
    duration_to_int = {
        0.5: 5,
        1: 9,
        1.5: 13,
        2: 16
    }
    try:
        music_score = m21.converter.parse(file_name).chordify()
    except Exception as err:
        print('*'*10,'Error in loading file: ', err, '*'*10)
        return '4/4', '120'
    print('up')
    time_sig = music_score.getTimeSignatures()[0].ratioString
    print('down')
    bpm = music_score.metronomeMarkBoundaries()[0][2].number

    notes, note_list = [], []
    durations, duration_list = [], []
    for element in music_score.flat:
        if isinstance(element, m21.chord.Chord):
            notes.append('.'.join(n.nameWithOctave for n in element.pitches))
            durations.append(element.duration.quarterLength)
        elif isinstance(element, m21.note.Rest):
            if element.isRest:
                notes.append(str(element.name))
                durations.append(element.duration.quarterLength)
    for chord, duration in zip(notes, durations):
        note_int = notes_to_int[chord.split('.')[0]]
        # print(chord.split('.')[0], note_int)
        # print(duration)
        try:
            duration_int = duration_to_int[duration]
        except:
            duration_int = duration_to_int[1]
        note_list.append(note_int)
        duration_list.append(duration_int)
    print('*'*10, time_sig, bpm, '*'*10)
    return note_list, duration_list, time_sig, bpm
