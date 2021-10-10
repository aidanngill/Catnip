""" Anything related to OpenCV's camera device. """

from typing import Any, List

import cv2
import imutils
import numpy

from .exceptions import NoFrame


class Frame:
    """ Singular frame from the camera. """

    def __init__(self, frame: Any):
        self._frame_data = frame

    @property
    def data(self) -> numpy.ndarray:
        """
        The raw frame data.

        Returns
        -------
        numpy.ndarray
            the raw frame data as a numpy array.
        """
        return self._frame_data

    @property
    def height(self) -> int:
        """
        Height of the frame.

        Returns
        -------
        int
            height of the frame.
        """
        return self._frame_data.shape[0]

    @property
    def width(self) -> int:
        """
        Width of the frame.

        Returns
        -------
        int
            width of the frame.
        """
        return self._frame_data.shape[1]

    def copy(self) -> Any:
        """
        Make a copy of the frame.

        Returns
        -------
        catnip.Frame
            a copy of the frame.
        """
        return Frame(self.data.copy())

    def resize(self, new_size: int) -> Any:
        """
        Resize the frame to a given width.

        Parameters
        ----------
        new_size : int
            width to resize the image to. height will be adjusted automatically.

        Returns
        -------
        catnip.Frame
            the resized image.
        """
        return Frame(imutils.resize(self.data, width=new_size))

    def recolor(self, new_color: int) -> Any:
        """
        Recolour the frame into a given colour space. Use the following code
        example to list all available colour spaces.

        ```python3
        import cv2

        for item in dir(cv2):
            if item.startswith("COLOR_"):
                print(item)
        ```

        Parameters
        ----------
        new_color : int
            OpenCV colour space, not a standard hex colour.

        Return
        ------
        catnip.Frame
            the recoloured frame.
        """
        return Frame(cv2.cvtColor(self.data, new_color))

    def blur(self) -> Any:
        """
        Blur the image.

        Returns
        -------
        catnip.Frame
            the blurred image.
        """
        return Frame(cv2.GaussianBlur(self.data, (21, 21), 0))

    def delta(self, other_frame) -> Any:
        """
        Get the difference between two frames.

        Parameters
        ----------
        other_frame : catnip.Frame
            the frame to create the delta with.

        Returns
        -------
        catnip.Frame
            frame with the difference between the frames.
        """
        return Frame(cv2.absdiff(self.data, other_frame.data))

    def threshold(
        self,
        other_frame: Any,
        threshold: int = 30,
        max_amount: int = 255,
        function: int = cv2.THRESH_BINARY
    ) -> Any:
        """
        Calculate the thresholded value of the frame deltas.

        Parameters
        ----------
        other_frame : catnip.Frame
            the frame to create the delta with.

        threshold : int
            at what number the threshold should be activated.

        max_amount:
            the maximum value of the threshold, default is 255 due to RGB
            colouring.

        function:
            the thresholding function to use.

        Returns
        -------
        catnip.Frame
            the thresholded frame.
        """
        delta: Frame = self.delta(other_frame)

        _, threshold = cv2.threshold(
            delta.data,
            threshold,
            max_amount,
            function
        )

        return Frame(threshold)

    def dilate(self, other_frame: Any, iterations: int = 2) -> Any:
        """
        Diminish the features of the frame.
        * https://docs.opencv.org/3.4.15/db/df6/tutorial_erosion_dilatation.html

        Parameters
        ----------
        other_frame : catnip.Frame
            the frame to create the delta with.

        iterations : int
            how many times the dilation should be done.

        Returns
        -------
        catnip.Frame
            the dilated frame.
        """
        threshold: Frame = self.threshold(other_frame)

        return Frame(cv2.dilate(threshold.data, None, iterations=iterations))

    def contours(self, other_frame: Any, minimum_area: int = 2500) -> List[Any]:
        """
        Generate the contours between the given frames.

        Parameters
        ----------
        other_frame : catnip.Frame
            the frame to create the delta with.

        minimum_area : int
            minimum amount of pixels to have within a contour for it to count
            towards the count.

        Returns
        -------
        List[Any]
            list of any contours that match the parameters.
        """
        frame: Frame = self.dilate(other_frame)

        contours = cv2.findContours(
            frame.data,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        return [
            contour
            for contour
            in imutils.grab_contours(contours)
            if cv2.contourArea(contour) >= minimum_area
        ]

    def is_similar(self, other_frame: Any) -> bool:
        """
        Whether or not one frame is similar to another.

        Parameters
        ----------
        other_frame : catnip.Frame
            the frame to compare contours with.

        Returns
        -------
        bool
            whether or not the other frame is similar to the current one.
        """
        return len(self.contours(other_frame)) == 0

    def write(self, file_name: str, draw_text: List[str] = None) -> None:
        """
        Save the frame to an output file.

        Parameters
        ----------
        file_name : str
            the path to save the image to.
        draw_text : List[str]
            a list of strings to print on the frame.
        """
        frame = self._frame_data.copy()

        if draw_text is not None:
            for idx, item in enumerate(draw_text, start=1):
                cv2.putText(
                    img=frame,
                    text=item,
                    org=(10, 10 + (10 * idx)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.5,
                    color=(255, 255, 255),
                    thickness=1,
                )

        cv2.imwrite(file_name, frame)


class Camera(cv2.VideoCapture):
    """ Helpers for OpenCV's `VideoCapture` class, from which it inherits. """

    @property
    def is_opened(self) -> bool:
        """
        Whether or not the device is open currently.
        """
        return super().isOpened()

    @property
    def fps(self) -> bool:
        """
        How many (f)rames the device outputs (p)er (s)econd.
        """
        return super().get(cv2.CAP_PROP_FPS)
    
    @property
    def width(self) -> int:
        """
        Width of the frame in pixels.
        """
        return int(super().get(cv2.CAP_PROP_FRAME_WIDTH))
    
    @property
    def height(self) -> int:
        """
        Height of the frame in pixels.
        """
        return int(super().get(cv2.CAP_PROP_FRAME_HEIGHT))

    def exposure(self, enable: bool) -> None:
        """
        Enable or disable automatic exposure, which can create false positives.

        Parameters
        ----------
        enable : bool
            whether to enable or disable the camera's automatic exposure
            adjustment settings.
        """
        super().set(cv2.CAP_PROP_AUTO_EXPOSURE, 0 if enable else 1)
        super().set(cv2.CAP_PROP_EXPOSURE, -7 if enable else 0)

    def capture(self) -> Frame:
        """
        Capture the current frame from the device.

        Returns
        -------
        catnip.Frame
            the current frame.
        """
        received, frame = super().read()

        if not received:
            raise NoFrame(
                f"Could not receive a new frame from device {self.device_id}."
            )

        return Frame(frame)

    def release(self) -> None:
        """
        Release the device and destroy any windows held by OpenCV.
        """
        super().release()
        cv2.destroyAllWindows()
