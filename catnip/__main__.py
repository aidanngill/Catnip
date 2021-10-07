""" Basic script to start the manager. """

import argparse
import logging
import sys

from . import Manager

log = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


def parse_arguments():
    """ Parse arguments from argv. """
    parser = argparse.ArgumentParser(description="Motion detection software.")

    # Standard arguments.
    parser.add_argument(
        "-d",
        "--device-id",
        type=int,
        default=0,
        help="Device ID of the camera."
    )

    parser.add_argument(
        "-m",
        "--minimum-area",
        type=int,
        default=1000,
        help="Minimum area for change before motion is detected.",
    )

    parser.add_argument(
        "-r",
        "--recording-length",
        type=float,
        default=5.0,
        help="Length to record after motion has been detected.",
    )

    parser.add_argument(
        "-w",
        "--detection-wait",
        type=float,
        default=1.0,
        help="Time to wait between processing frames.",
    )

    # Boolean values.
    parser.add_argument(
        "--disable-exposure",
        action="store_true",
        default=False,
        help="Disable automatic exposure adjustment."
    )

    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()

    manager = Manager(
        device_id=opts.device_id,
        recording_length=opts.recording_length,
        detection_wait=opts.detection_wait
    )

    manager.camera.exposure(enable=(not opts.disable_exposure))

    if not manager.camera.is_opened:
        log.fatal("Could not open the camera device.")
        sys.exit(1)

    manager.run()

    sys.exit(0)
