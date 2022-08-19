import gpiozero
import logging
# Setup logging Global for all modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("guestbook.log"),
        logging.StreamHandler()
    ]
)
import time
from statemachine.mixins import MachineMixin
from statemachine import StateMachine, State


from utils.Recorder import Recorder
from utils.Player import Player


logger = logging.getLogger(__name__)

class GuestBookState(StateMachine):
    waiting = State('Waiting for next user.', initial=True)
    recording = State("Recording mic")
    
    start = waiting.to(recording)
    stop = recording.to(waiting)

    # Recorder
    recorder = Recorder()
    recorder.disabled = False

    # Player
    player = Player()

    msg_count_total = 0
    msg_count_successfull = 0

    def on_start(self):
        self.msg_count_total += 1
        logger.info(f"Starting the {self.msg_count_total}. message this start.")
        time.sleep(1)

        logger.info("Request playback of greetings.")
        self.player.play_greetings()
        self.player.play_music()

        logger.info("Start to record.")
        self.recorder.start()

        # Wait for greetings to end
        # self.player.wait_for_greeting()
        # self.player.play_go_signal()

    def on_stop(self):
        logger.info("Going to stop.")
        # Stop playback
        self.player.stop_all()

        # Stop recorder
        self.recorder.stop()
        if self.recorder.save_2_file():
            self.msg_count_successfull += 1
            logger.info(f"{self.msg_count_successfull} successfull messenges so far!.")

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
        # spnning rate (hz)
        self.rate = 10

    def spin(self):
        warned_close2end = False
        while self.is_running:
            # Update telefone state
            if self.handset.is_pressed: # Picked
                if self.statemachine.is_waiting:
                    self.statemachine.start()
            else:
                if self.statemachine.is_recording:
                    self.statemachine.stop()
            # Check for special things to do
            if self.statemachine.recorder.recording_duration > 270 and not warned_close2end:
                self.statemachine.player.play_close2end()
                warned_close2end = True
            if self.statemachine.recorder.recording_duration > 300:
                self.statemachine.stop()

            time.sleep(1/self.rate)


if __name__ == '__main__':
    logger.info("--------------------------------------------------------------------------")
    logger.info("--------------------------------------------------------------------------")
    logger.info("--------------------------STARTING GUESTBOOK APP--------------------------")
    logger.info("--------------------------------------------------------------------------")
    logger.info("--------------------------------------------------------------------------")
    app = GuestBookApp()
    app.spin()
