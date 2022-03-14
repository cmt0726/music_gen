from music21 import *
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import BatchNormalization as BatchNorm
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import numpy
import os
import pickle


notes = []

#opening all the midis takes forever. analyze_notes.py saves the notes list in a pickle file to be loaded here
with open("notes.pickle", "rb") as f:
    notes = pickle.load(f)

n_vocab = float(len(set(notes)))
pitch_names = sorted(set(item for item in notes))

def setup_data():
    seq_len = 100

    

    note_to_int : dict[note, int] = dict((note, number) for number, note in enumerate(pitch_names))

    net_input = []
    net_output = []

    for i in range(0, len(notes) - seq_len, 1):
        seq_in = notes[i:i + seq_len]
        seq_out = notes[i + seq_len]
        net_input.append([note_to_int[char] for char in seq_in])
        net_output.append(note_to_int[seq_out])

    n_patterns = len(net_input)

    net_input = numpy.reshape(net_input, (n_patterns, seq_len, 1))

    net_input = net_input / n_vocab #normalizes to 0 - 1

    net_output = np_utils.to_categorical(net_output)

    return net_input, net_output

net_input, net_output = setup_data()

def create_model():

    model = Sequential()

    model.add(LSTM(
        256,
        input_shape = (net_input.shape[1], net_input.shape[2]),
        return_sequences= True
    ))

    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(256))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    return model



def run_model(model):
    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"    
    checkpoint = ModelCheckpoint(
        filepath, monitor='loss', 
        verbose=0,        
        save_best_only=True,        
        mode='min'
    )
    callbacks_list = [checkpoint]     
    model.fit(net_input, net_output, epochs=200, batch_size=64, callbacks=callbacks_list)

def generate_notes(model, int_to_note):
    prediction_output = []
    for note_index in range(500):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)
        prediction = model.predict(prediction_input, verbose=0)
        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)
        pattern = numpy.append(pattern, index)
        
        pattern = pattern[1:len(pattern)]
    
    return prediction_output

def get_notes_and_chords(prediction_output):
    start = numpy.random.randint(0, len(net_input)-1)
    
    pattern = net_input[start]
    offset = 0
    output_notes = []
    # create note and chord objects based on the values generated by the model
    for pattern in prediction_output:
        # pattern is a chord
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        # pattern is a note
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)
        # increase offset each iteration so that notes do not stack
        offset += 0.5
    return output_notes

def generate_music(path_to_weights):
    model = create_model()
    int_to_note = dict((number, note) for number, note in enumerate(pitch_names))
    # Load the weights to each node
    model.load_weights(path_to_weights)

    # generate 500 notes
    prediction_output = generate_notes(model, int_to_note)
    
    output_notes = get_notes_and_chords(prediction_output)
    
    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp='test_output.mid')

if __name__ == "__main__":
    model = create_model()
    run_model(model)
    generate_music("weights.hdf5") ##temp path to weights. When all epochs are done, rename the best model to this file name