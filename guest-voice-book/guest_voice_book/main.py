import gpiozero
import logging
import time
from statemachine.mixins import MachineMixin
from statemachine import StateMachine, State

from pygame import mixer
# Init pygame mixer
mixer.init()

from utils.Recorder import Recorder


class GuestBookState(StateMachine):
    waiting = State('Waiting for next user.', initial=True)
    recording = State("Recording mic")
    
    start = waiting.to(recording)
    stop = recording.to(waiting)

    # Recorder
    recorder = Recorder()
    recorder.disabled = True

    def on_start(self):
        time.sleep(1)
        print("playing greetings")
        mixer.music.load('data/music/happy-day.mp3')
        mixer.music.play() 
        mixer.Channel(0).play(mixer.Sound('data/greetings/test_loud.mp3'))
        print("Start to record")
        self.recorder.start()
        
    def on_stop(self):
        print("Stopping")
        # Stop background music
        mixer.music.stop()
        # Stop recorder
        self.recorder.stop()
        self.recorder.save_2_file()

        

            
    
class GuestBookApp(MachineMixin):
    state_machine_name = 'GuestBookState'

    def __init__(self,  **kwargs):
        # Setup state machines
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(GuestBookApp, self).__init__()

        # Phone headset
        self.handset = gpiozero.Button(2) 

        # Flag to stop the main spin loop
        self.is_running = True
        # Sample rate (hz)
        self.rate = 10




    def spin(self):
        while self.is_running:
            # Update telefone state
            if self.handset.is_pressed: # Picked
                if self.statemachine.is_waiting:
                    self.statemachine.start()
            else:
                if self.statemachine.is_recording:
                    self.statemachine.stop()
        
            time.sleep(1/self.rate)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = GuestBookApp()
    app.spin()
