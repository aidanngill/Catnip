""" A manager for the camera device to process the frames for motion events. """

import logging
import os
import signal
import threading
import time
from datetime import datetime

import cv2

from . import util
from .camera import Camera, Frame
from .event import Event

log = logging.getLogger(__name__)


class Manager:
    """
    Manages any motion events or devices.

    Attributes
    ----------
    device_id : int
        the id number of the device to capture from, defaulting to zero (0).

    recording_length : float
        how long recordings will be after movement.

    detection_wait : float
        how long to wait between detection cycles.

    camera : catnip.Camera
        the camera object.

    exit_event : threading.Event
        when the function's loops should be stopped.

    latest_frame : catnip.Frame
        the latest frame from the camera.

    latest_frame_lock : threading.Lock
        thread lock to activate when `latest_frame` is activated.

    average_frame : catnip.Frame
        the average to base comparisons with newer frames on.

    event : catnip.Event
        current motion event.
    """

    def __init__(self,
                 device_id: int = 0,
                 output_path: os.PathLike = None,
                 recording_length: float = 5.0,
                 detection_wait: float = 1.0
                 ):
        """
        Parameters
        ----------
        device_id : int
            the id number of the device to capture from, defaulting to zero (0).

        recording_length : float
            how long recordings will be after movement.

        detection_wait : float
            how long to wait between detection cycles.
        """
        self.device_id = device_id
        self.path = output_path if output_path else util.get_default_directory()
        self.recording_length = recording_length
        self.detection_wait = detection_wait

        self.camera = Camera(device_id)

        self.exit_event = threading.Event()

        self.latest_frame: Frame = None
        self.latest_frame_lock = threading.Lock()

        self.average_frame: Frame = None
        self.average_frame_lock = threading.Lock()

        self.event: Event = None
        self.callback_functions: dict = {}

    def _update_average_frame(self, frame: Frame) -> None:
        """
        Update the average frame.

        Parameters
        ----------
        frame : catnip.Frame
            the _blurred_ frame to set the average frame to.
        """
        with self.average_frame_lock:
            self.average_frame = frame

        log.debug("Updated the average frame.")
    
    def _create_event(self, frame: Frame) -> Event:
        """
        Start a new motion event.

        Parameters
        ----------
        frame : catnip.Frame
            the frame that set off the motion event.
        
        Returns
        -------
        catnip.Event
            newly created event.
        """
        now = datetime.now()
        path = os.path.join(self.path, str(now.year), str(now.month), str(now.day))

        return Event(frame, path, self.camera.width, self.camera.height, self.camera.fps)
    
    def _do_callback(self, name: str, *args, **kwargs):
        """
        Call the function given by the callback name with its parameters.
        
        Parameters
        ----------
        name : str
            the name of the callback.
        """
        func = self.callback_functions.get(name)

        if func is None:
            return
        
        func(*args, **kwargs)
    
    def on(self, name: str) -> None:
        """
        Register a callback function.
        
        Parameters
        ----------
        name : str
            the name of the callback.
        """
        def _on(func, *_, **__):
            self.callback_functions[name] = func

        return _on

    def detect(self) -> None:
        """ Process the latest frame to check for any movement. """
        while self.latest_frame is None:
            time.sleep(0.1)

        while not self.exit_event.is_set():
            start = time.time()

            if self.average_frame is None:
                continue

            with self.latest_frame_lock:
                frame: Frame = self.latest_frame.copy()

            resized: Frame = frame.resize(frame.width // 4)
            grey: Frame = resized.recolor(cv2.COLOR_BGR2GRAY)
            blur: Frame = grey.blur()

            contours = blur.contours(self.average_frame)

            if self.event:
                if self.event.should_update_trigger(self.recording_length):
                    if not self.event.trigger.is_similar(blur):
                        self.event.update_trigger(blur)
                        continue

                    self.event.writer.release()

                    self._do_callback("event_end", self.event)
                    self._update_average_frame(blur)

                    log.info("Finished recording a motion event.")
                    self.event = None

            elif len(contours) > 0:
                self.event = self._create_event(blur)
                self._do_callback("event_start", self.event)

                log.info("Started recording a motion event.")

            end = time.time()
            dur = end - start

            time.sleep(
                (self.detection_wait - dur)
                if dur <= self.detection_wait
                else self.detection_wait
            )

    def record(self) -> None:
        """
        Record footage from the camera constantly, saving the latest frame to
        the `latest_frame` value. Before accessing it, the `latest_frame_lock`
        lock should be acquired.
        """
        while not self.exit_event.is_set():
            frame: Frame = self.camera.capture()

            with self.latest_frame_lock:
                self.latest_frame = frame

            if self.average_frame is None:
                resized: Frame = frame.resize(frame.width // 4)
                grey: Frame = resized.recolor(cv2.COLOR_BGR2GRAY)
                blur: Frame = grey.blur()

                self._update_average_frame(blur)

                continue

            if self.event is None:
                continue

            self.event.add_frame(frame)

    def run(self) -> None:
        """
        Start all of the manager's required functions as threads.
        """
        targets = [self.record, self.detect]

        def signal_handler(*_, **__):
            log.warning("Received a keyboard interrupt, shutting down...")
            self.exit_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        threads = [threading.Thread(target=t, args=()) for t in targets]

        for thread in threads:
            thread.start()

        log.info("Started the manager.")

        for thread in threads:
            while thread.is_alive():
                thread.join(1)

        self.shutdown()

    def shutdown(self) -> None:
        """
        Graceful shutdown.
        """
        self.camera.release()
        log.debug("Shut down gracefully.")
