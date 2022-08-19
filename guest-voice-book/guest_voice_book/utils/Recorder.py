from datetime import datetime
import pygame
import time
import logging
from pydub import AudioSegment
# sound = AudioSegment.from_wav('myfile.wav')

# sound.export('myfile.mp3', format='mp3')


logger = logging.getLogger(__name__)

from pygame._sdl2 import (
    get_audio_device_names,
    AudioDevice,
    AUDIO_F32,
    AUDIO_U16,
    AUDIO_U8,
    AUDIO_ALLOW_FORMAT_CHANGE,
)

class Recorder:
    def __init__(self) -> None:
        logger.debug(f'Found following audio input devices: {get_audio_device_names(True)}')
        self.audio_device_name = get_audio_device_names(True)[0]
        logger.info(f'Using: {self.audio_device_name} as recording mice')

        # Current audio device
        self.audio_device = AudioDevice(
            devicename=self.audio_device_name,
            iscapture=True,
            frequency=44100,
            audioformat=AUDIO_U16, # https://wiki.libsdl.org/SDL_AudioFormat
            numchannels=1,
            chunksize=512,
            allowed_changes=AUDIO_ALLOW_FORMAT_CHANGE,
            callback=self._record_callback,
        )

        # Start audio device
        self.audio_device.pause(0)

        # Buffer holding the recordings not written to disk yet.
        self.record = None

        # Buffer of current recording bytes
        self._buffer = []

        # State of recording.
        self.recording = False

        # disable recording
        self.disaled = False

        # Duration of current recording:
        self.recording_duration = 0

        # Minimum recording time so that the recording gets saved to disk.
        self.min_recording_time = 15
    

    def _record_callback(self, audiodevice, audiomemoryview):
        """This is called in the sound thread.
        Note, that the frequency and such you request may not be what you get.
        """
        # Add recording to current buffer
        if self.recording:
            self._buffer.append(bytes(audiomemoryview))
            now = time.time()
            self.recording_duration = now - self.start_time
            if (now - self.start_time) % 5 < 0.009:
                logger.info(f'recording since {self.recording_duration:.2f}')

    def start(self):
        if not self.disabled:
            logger.debug('Start recording')
            self.start_time = time.time()
            self.recording = True
    
    def stop(self):
        if not self.disabled:
            if not self.recording:
                logger.error("You can not stop a not recording recording.")
                return
            self.recording = False
            now = time.time()
            self.recording_duration = now - self.start_time
            logger.info(f'Stopped current recording. It is {self.recording_duration:.2f}s long.')


            logger.info("Turning data into a pygame.mixer.Sound")
            self.record = pygame.mixer.Sound(buffer=b"".join(self._buffer))
            self._buffer = []

    
    def save_2_file(self):
        if not self.disabled and self.recording_duration > self.min_recording_time:
            logger.info("Saving record to file.")
            filename = "recordings/" + datetime.utcnow().strftime('%Y%m%d-%H%M%S.%f')[:-3] + f'-{self.recording_duration:.2f}.mp3'
            self.record.set_volume(1)
            audio_segment = AudioSegment(self.record.get_raw(), sample_width=2, frame_rate=44100, channels=1)
            # Save MP3
            audio_segment.export(filename, format='mp3')

            logger.info(f"Done saving {filename}")
            # Reset duration
            self.recording_duration = 0
            return True
        else:
            logger.info("Not saving record to file. Recording was to short or is disabled.")
            return False