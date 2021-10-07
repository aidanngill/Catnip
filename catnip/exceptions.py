""" Exceptions for the library. """


class CatnipException(Exception):
    """ Base exception class. """


class NoFrame(CatnipException):
    """ Failed to receive a new frame. """
