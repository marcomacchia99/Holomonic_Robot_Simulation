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

### Finding and grabbing a silver token ###

While the robot moves along the path, it also look for all the silver tokens, and tries to grab them and move them behind him. First he sees if there is a token in front of him, using this function:


```python
def look_for_silver_token(angle):  
    """
    Function to see if there is a silver token in front of the robot

    Returns:
	silverTokenForward (bool): presence of a silver token
    """
    silverTokenForward = False
    for token in R.see():
        if -angle<=token.rot_y<=angle and token.info.marker_type is MARKER_TOKEN_SILVER:
            silverTokenForward = True
    return silverTokenForward
```

Then, if something is found, he gets the how far the token is and how much he should turn in order to reach it, using the return values of this function:


```python
def find_silver_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	    return -1, -1
    else:
   	    return dist, rot_y
```
After that, the robot goes towards the token, avoiding all the golden token.

The following code is used to approach the silver token:

```python
a_th = 4.0
""" float: Threshold for the control of the linear distance"""

if rot_y < -a_th: # if the robot is not well aligned with the token, we slightly move it on the left or on the right
  turn(-2, 0.1)
elif rot_y > a_th:
  turn(+2, 0.1)
```


[sr-api]: https://studentrobotics.org/docs/programming/sr/
