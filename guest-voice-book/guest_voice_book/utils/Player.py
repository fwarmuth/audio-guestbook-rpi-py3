
from pygame import mixer
import glob
import random
import time
import logging
logger = logging.getLogger(__name__)

# Init pygame mixer
mixer.init()

class Player:
    def __init__(self) -> None:
        pass
        
        self.greetings = glob.glob("data/greetings/*.mp3")
        self.go_signals = glob.glob("data/sounds/go_signal*.mp3")
        self.close2end = glob.glob("data/sounds/close2end*.mp3")
        self.music = glob.glob("data/music/*.mp3")


    def play_go_signal(self):
        choice =  random.choice(self.go_signals)
        mixer.Channel(1).play(mixer.Sound(choice))
        return choice

    def play_close2end(self):
        choice =  random.choice(self.close2end)
        mixer.Channel(0).play(mixer.Sound(choice))
        return choice

    def play_greetings(self, with_go_signal=True):
        choice =  random.choice(self.greetings)
        mixer.Channel(0).play(mixer.Sound(choice))
        if with_go_signal:
            choice =  random.choice(self.go_signals)
            mixer.Channel(0).queue(mixer.Sound(choice))

        return choice
    
    def play_music(self):
        choice =  random.choice(self.music)
        mixer.music.load(choice)
        mixer.music.set_volume(0.5)
        mixer.music.play() 
    
    def stop_all(self):
        # Stop music
        mixer.music.stop()
        # Stop greeting
        mixer.Channel(0).stop()
    
    def wait_for_greeting(self):
        while mixer.Channel(0).get_busy():
            time.sleep(0.1)
