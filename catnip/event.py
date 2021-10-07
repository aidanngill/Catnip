""" Functions to use when motion is detected. """

import os
import time
from datetime import datetime

from . import config, util
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

    path : str
        unique path to save frames to.

    path_index : int
        current amount of frames. each file will be saved sequentially with this
        index number as its file name.
    """

    def __init__(self, trigger: Frame):
        """
        Parameters
        ----------
        trigger : catnip.Frame
            initial frame that triggered the motion event.
        """
        self.trigger: Frame = trigger
        self.updated: float = time.time()

        self.path: str = util.generate_unique_folder(config.CAPTURE_PATH)
        self.path_index: int = 0

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
        Save a frame to the event's unique path and update the file index.

        Parameters
        ----------
        frame : catnip.Frame
            frame to save to get the image from.
        """
        file = os.path.join(self.path, f"{self.path_index}.png")
        frame.write(file, [datetime.now().strftime("%d %B %Y at %H:%M:%S")])

        self.path_index += 1

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
