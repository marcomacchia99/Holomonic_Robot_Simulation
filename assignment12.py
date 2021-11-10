from __future__ import print_function


import time
from sr.robot import *



a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

g_th = 1
"""float: Threshold for golden markers"""

g_border_th = 0.8
""" float: Threshold for the control of the borders (golden markers)"""

vTurning = 38
"""int: Velocity for turning the robot during the grab movement"""

silver = True
""" boolean: variable for letting the robot know if it has to look for a silver marker"""

R = Robot()
""" instance of the class Robot"""

def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token():
    """
    Function to find the closest silver token in front of the robot

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER and -30<token.rot_y<30:
            print("qui ci entro")
            if check_golden_between_silver(token.dist, token.rot_y) == False:
                dist=token.dist
                rot_y=token.rot_y
    if dist==100:
        return -1, -1
    else:
        return dist, rot_y

def find_golden_token():
    """
    Function to find the closest golden token in front of the robot

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD and -30<token.rot_y<30:
            dist=token.dist
            rot_y=token.rot_y
    if dist==100:
	    return -1, -1
    else:
   	    return dist, rot_y

def check_golden_between_silver(dist, rot_y):
    """
    Function to check if there is a golden token between a silver one detected from the robot

    Args:
        dist (float): distance of the closest silver token
        rot_y (float): angle between the robot and the token
    """
    distG=100
    for token in R.see():
        if token.dist < distG and token.info.marker_type is MARKER_TOKEN_GOLD and abs(token.rot_y) < abs(rot_y): 
            distG = token.dist
   	if distG == 100 or dist < distG: return False
    else: return True


def turn_decision():
    """
    Function to decide where to turn
    Returns:
	    1: if the closest golden token is on the right, so the robot should turn on its left (counter clockwise),
        -1: if the closest golden token is on the left, so the robot should turn on its right (clockwise).
    """
    dist=100
    g_sx = 50
    g_dx = 50
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            if 70<token.rot_y<110 and token.dist < g_dx:
                g_dx = token.dist
            elif -110<token.rot_y<-80 and token.dist < g_sx:
                g_sx = token.dist
            if ((dist ==100) | (g_sx == g_dx)):
                return -1
            else:
                if g_sx < g_dx:
                # the robot turns right in proximity of a wall on the left
                    return 1 
                # otherwise the robot turns left
                else: return -1 

def align_to_next_silver_token(turn_direction): 
    
    dist, rot_y = find_silver_token()
    if dist >100 : return
    else:
        silv_tok=None
        unreachable = []
        dist=100
        for token1 in R.see():
                if token1.info.marker_type is MARKER_TOKEN_SILVER:
                    for token in R.see():
                        if -token1.rot_y-0.5<=token.rot_y<=token1.rot_y+0.5 and token.dist<token1.dist and token.info.marker_type is MARKER_TOKEN_GOLD:
                            unreachable.append(token.info.code)
                            break
        lower_angle_limit = -35 - 20 if turn_direction==1 else 0
        upper_angle_limit = 35 + 20 if turn_direction==-1 else 0
        for token in R.see():
                if lower_angle_limit<=token.rot_y<=upper_angle_limit and token.dist<dist and not token.info.code in unreachable and token.info.marker_type is MARKER_TOKEN_SILVER:
                    dist=token.dist
                    silv_tok=token
                    break                
        if silv_tok==None: return
        print("Aligning with next token...")
        print(dist)
        print(silv_tok.rot_y)            
        while silv_tok.rot_y < -0.5 or silv_tok.rot_y > 0.5: 
                if silv_tok.rot_y < -0.5: # if the robot is not well aligned with the token, we move it on the left or on the right
                    turn(-2, 0.1)
                elif silv_tok.rot_y > 0.5:
                    turn(+2, 0.1)
                for token in R.see():
                    if -35<=token.rot_y<=35 and token.dist<dist and token.info.marker_type is MARKER_TOKEN_SILVER:
                     silv_tok=token
    print("Alignment complete!")                              
    return

def grab_silver_token(dist, rot_y):
    """
    Function to make the robot grab the closest silver token
    
    Args:
        dist (float): distance of the closest silver token
        rot_y (float): angle between the robot and the token
    """

    # if the robot is close to the token, it tries to grab it
    if dist <d_th: 
        print("Found it!")

        # if the robot grab the token, we make the robot turn around (clockwise), we release the token, and we go back to the initial position
        if R.grab(): 
            print("Gotcha!")
            turn(vTurning, 2)
            R.release()
            drive(-10,1)
            turn(-vTurning, 2)

        # if the robot can't grab it, it has to move nearer to it
        else:
            print("I'm not close enough.")

    # if the robot is well aligned with the token, we go forward in order to reach it
    elif -a_th<= rot_y <= a_th: 
        print("Ah, that'll do.")
        drive(50, 0.1)

    # if the robot is not well aligned with the token, it manage to adjust the trajectory
    elif rot_y < -a_th: 
        print("Left a bit...")
        turn(-15, 0.5)
    elif rot_y > a_th:
        print("Right a bit...")
        turn(+15, 0.5)


def main():

    while 1:
         # collision avoidance
        dist, rot_y = find_golden_token()
        if dist < g_border_th:
            if 10<rot_y<150:
                print("I'm close to the wall, left a bit...")
                turn(-10,0.5)
            elif -150<rot_y<-10:
                print("I'm close to the wall, right a bit...")
                turn(-10,0.5)
         # go on the path
        if dist < g_th and -20<rot_y<20:
            print("There's a wall in front of me, I have to turn...")
            if turn_decision() == 1: 
                turn(17,2)
            else: 
                turn(-17,2)
        else: 
            dist, rot_y = find_silver_token()
            print(dist)
            if dist != -1:
                grab_silver_token(dist, rot_y)
                print("Silver token just grabbed")
            else:
                drive(80,0.1)
            

main()