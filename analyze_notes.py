
from music21 import *
import os
import pickle5 as pickle

notes = []
path = "music_gen/midi_files/"
for dir in os.listdir(path):
    num_midis = len(os.listdir(path + "/" + dir))
    progress = 0
    for file in os.listdir(path + "/" + dir)[0:5]: #if we use more than this, each epoch becomes HUGE
        parsed_midi = converter.parse(path + dir + "/" + file)
        notes_to_parse = None
        parts = instrument.partitionByInstrument(parsed_midi)
        try:
            if parts: # file has instrument parts
                notes_to_parse = parts.parts[1].recurse()
                
            else: # file has notes in a flat structure
                notes_to_parse = parsed_midi.flat.notes
            for element in notes_to_parse:
                if isinstance(element, note.Note):     
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))
        except:
            if parts: # file has instrument parts
                notes_to_parse = parts.parts[0].recurse()
                
            else: # file has notes in a flat structure
                notes_to_parse = parsed_midi.flat.notes
            for element in notes_to_parse:
                if isinstance(element, note.Note):     
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))
        progress += 1
        if progress % 5 == 0:
            print("Analyzed: ", progress, "/", num_midis)
        

print("Done analyzing Midis!")

with open("music_gen/notes.pickle", "wb") as f:
    pickle.dump(notes, f, protocol=pickle.HIGHEST_PROTOCOL)