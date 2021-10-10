""" Functions to use when motion is detected. """

import os
import time
from datetime import datetime

import cv2

from .camera import Frame


class Event:
    """
    Class for a motion event, from when the motion is first detected to a given
    period afterwards (which can be extended as needed).

    As frames are fed to the event from the camera thread, they will be
    processed (timestamp and other text the user wants).

    Attributes
    ----------
    trigger : catnip.Frame
        initial frame that triggered the motion event.

    updated : float
        when the trigger frame was last updated.

    file : str
        the file to save the video to.
    
    writer : cv2.VideoWriter
        cv2 video writer object to process frames into video.
    """

    def __init__(self, trigger: Frame, path: str, width: int, height: int, fps: int):
        """
        Parameters
        ----------
        trigger : catnip.Frame
            initial frame that triggered the motion event.
        """
        self.trigger: Frame = trigger

        self.start: datetime = datetime.now()
        self.updated: float = time.time()

        self.file = os.path.join(path, self.start.strftime("%H%M%S_%f.avi"))

        if not os.path.isfile(path):
            os.makedirs(path, exist_ok=True)

        cc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(self.file, cc, fps, (width, height))

    def should_update_trigger(self, delta: int = 10) -> bool:
        """
        Whether or not the trigger frame should be updated yet.

        Parameters
        ----------
        delta : int
            amount of time til a frae comparison is made again.

        Returns
        -------
        bool
            whether or not the trigger frame should be updated.
        """
        return self.updated <= time.time() - delta

    def add_frame(self, frame: Frame) -> None:
        """
        Save a frame to the event's video writer.

        Parameters
        ----------
        frame : catnip.Frame
            frame to save to get the image from.
        """
        self.writer.write(frame.data)

    def update_trigger(self, frame: Frame) -> None:
        """
        Update the trigger frame.

        Parameters
        ----------
        frame : catnip.Frame
            frame to set the trigger to.
        """
        self.trigger = frame
        self.updated = time.time()
