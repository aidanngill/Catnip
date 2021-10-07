# Catnip

Motion detection project. Aims to minimise resource usage whilst providing accurate reports with minimal false positives.

## Requirements

* Python <sup>v3.8</sup>
* USB Webcam or Camera Device

## Usage

```python
py -m catnip --help
```

## Process

* In one thread, record footage constantly and save the latest frame to a variable.

* On another thread, process the very latest frame and check for movement every _x_ (1) seconds.

* If we detect movement, start recording frames to a _new_ folder (or memory perhaps?) for _x_ (15) seconds.

* If the average is still the _exact_ same at the end of a certain period of _x_ (15) seconds, update the average.

## Issues

* Automatic exposure settings may create false positives, especially in places with harsh light differences such as a lamp on a brightly coloured surface at night.
  * Added a "fix" with the `--disable-exposure` argument.
