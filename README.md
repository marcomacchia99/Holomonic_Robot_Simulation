Assignment 1 - Research Track 1
================================

Introduction
------------

In this assignment we are asked to let the robot `constantly drive around the circuit in the counter-clockwise direction`, `avoiding all the gold boxes`. When a silver token in found along the path, the robot should also `grab it and move it behind himself.`

Installing and running
----------------------

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Pygame, unfortunately, can be tricky (though [not impossible](http://askubuntu.com/q/312767)) to install in virtual environments. If you are using `pip`, you might try `pip install hg+https://bitbucket.org/pygame/pygame`, or you could use your operating system's package manager. Windows users could use [Portable Python](http://portablepython.com/). PyPyBox2D and PyYAML are more forgiving, and should install just fine using `pip` or `easy_install`.

Key elements
------------
* `The holonomic Robot`

  ![alt text](https://github.com/marcomacchia99/ResearchTrack1/blob/main/sr/robot.png)
  
  The robot has distances sensor pointing in all direction, in such a way that he can see from -180 to 180 degrees.
 
* `Silver box`

  ![alt text](https://github.com/marcomacchia99/ResearchTrack1/blob/main/sr/token_silver.png)

* `Gold box`

  ![alt text](https://github.com/marcomacchia99/ResearchTrack1/blob/main/sr/token.png)


Run
-----------------------------

To run the assignment in the simulator, use `run.py`, passing it the file name `assignment1.py`, as the following:

```bash
$ python run.py assignment1.py
```

Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the motors, one might write the following:

```python
R.motors[0].m0.power = 10
R.motors[0].m1.power = -10
```
This simple snippet is used in two important functions, `drive(speed,seconds)` and `turn(speed,seconds)` to let the robot move straight or turn.

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.


### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has many attributes, included:

* `info`: a `MarkerInfo` object describing the marker itself. The program uses:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
* `dist`: the distance from the centre of the robot to the object (in metres).
* `rot_y`: rotation about the Y axis in degrees.

For example, the following code fitlter only the golden markers the robot can see:

```python
for token in R.see():
        if token.info.marker_type is MARKER_TOKEN_GOLD:
            ...
            ...
            ...
```

The code
--------

### Grabbing a silver token ###


[sr-api]: https://studentrobotics.org/docs/programming/sr/
