""" Any utility functions for paths, images, etc. """

import os
import uuid

import cv2


def combine_images_to_video(
    input_path: str,
    output_path: str,
    frames_per_second: int,
    frame_extension: str = "png",
) -> None:
    """
    Combine all images from a given path into one video. Files should be named
    sequentially, e.g., `["1.png", "2.png", ...]`.

    Parameters
    ----------
    input_path : str
        the _path_ to find frame images from.

    output_path : str
        the _file_ to save the resulting video to.

    frames_per_second : int
        how many frames should be used per second.

    frame_extension : str
        the file extension of the frame images.
    """
    path = os.path.join(os.getcwd(), input_path)

    numbers = []

    for item in os.listdir(path):
        numbers.append(int(item.split(".")[0]))

    if len(numbers) == 0:
        return

    # Re-order the file list to be sequential.
    files = [f"{d}.{frame_extension}" for d in sorted(numbers)]

    frame = cv2.imread(os.path.join(path, files[0]))
    height, width, _ = frame.shape

    four_cc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(output_path, four_cc,
                            frames_per_second, (width, height))

    for file in files:
        video.write(cv2.imread(os.path.join(path, file)))

    video.release()


def generate_unique_folder(capture_path: str) -> str:
    """
    Generate a randomly named unique folder using a UUID.

    Parameters
    ----------
    capture_path : str
        base path/capture folder.

    Returns
    -------
    str
        generated folder name.
    """
    path = os.path.join(capture_path, str(uuid.uuid4()))

    if os.path.isdir(path):
        return generate_unique_folder(capture_path)

    os.mkdir(path)

    return path
