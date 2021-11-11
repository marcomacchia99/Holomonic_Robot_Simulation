from __future__ import print_function

import time
from sr.robot import *

a_th = 4.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

g_th = 1
""" float: Threshold for the control of the linear distance from gold boxes that are in front of the robot"""

border_th = 0.55
""" float: Threshold for the control of the linear distance from the lateral border of the arena"""

drive_v = 40
""" int: Linear velocity of the robot"""

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

def find_golden_token():
    """
    Function to find the closest golden token

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	    return -1, -1
    else:
   	    return dist, rot_y
    

def see_forward():
    """
    Function to look in front of the robot

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and  -10<=token.rot_y<=10 and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	    return -1, -1
    else:
   	    return dist, rot_y
    
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

def align_to_next_silver_token(turn_direction): 
    """
    Function to align to the next silver token after a turn
    """    
    
    if not look_for_silver_token(35): return
    else:
        silv_tok=None
        unreachable = []
        dist=100
        
        # creates a list of unreachable silver tokens, that must be ignored
        for token1 in R.see():
                if token1.info.marker_type is MARKER_TOKEN_SILVER:
                    for token in R.see():
                        if -token1.rot_y-0.5<=token.rot_y<=token1.rot_y+0.5 and token.dist<token1.dist and token.info.marker_type is MARKER_TOKEN_GOLD:
                            unreachable.append(token.info.code)
                            break
                        
        # extra vision to one side or another according to the turn direction
        # in order to manage unexpected turn behavior              
        lower_angle_limit = -35 - 20 if turn_direction==1 else 0
        upper_angle_limit = 35 + 20 if turn_direction==-1 else 0
        
        
        # look for the nearest reachable silver token
        for token in R.see():
                if lower_angle_limit<=token.rot_y<=upper_angle_limit and token.dist<dist and not token.info.code in unreachable and token.info.marker_type is MARKER_TOKEN_SILVER:
                    dist=token.dist
                    silv_tok=token
                    break 
                               
        if silv_tok==None: return
        
        
        print("Aligning with next token...")        
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
   	

def detect_angle():
    """
    Function to understand how an angle is made and how the robot should turn

    Returns:
	direction (int): 1 if it has to turn clockwise, -1 if counterclockwise 
    """
    distCcw=100 #distance counterclockwise
    distCw=100 #distance clockwise
    for token in R.see():
        if  70<=token.rot_y<=110  and token.dist < distCw and token.info.marker_type is MARKER_TOKEN_GOLD:
            distCw=token.dist
        elif -110<=token.rot_y<=-90  and token.dist < distCcw and token.info.marker_type is MARKER_TOKEN_GOLD:
            distCcw=token.dist         
    if distCw==100:
	    return -1
    else:
        if distCw>distCcw:
            return 1
        else:
            return -1
        
while 1:
    
    #avoid collisin with lateral border
    dist,rot_y = find_golden_token()         
    if dist <border_th:
        if 0<rot_y<150:
            print(rot_y)
            print("Danger! Left a bit...")
            turn(-45, 0.2)
            drive(20,0.5)
        elif -150<rot_y<0:
            print(rot_y)
            print("Danger! Right a bit...")
            turn(45, 0.2)
            drive(20,0.5)
            
    #turn when there's an angle  
    dist,rot_y = see_forward()
    if dist <g_th and -20<rot_y<20:
        print("Angle! I'm turning...")
        direction = detect_angle()
    	if direction==1:
            turn(17,2)
    	else:
            turn(-17,2)
        align_to_next_silver_token(direction)
        
    else:	           
        #if no silver token found just go straight
        if not look_for_silver_token(20):
            drive(drive_v , 0.1)
        else:
            dist, rot_y = find_silver_token() 
            
            if dist <d_th and -a_th<= rot_y <= a_th : # if we are close to the token, we try grab it.
                print("Found it!")
                if R.grab(): # if we grab the token, we move the robot forward and on the right, we release the token, and we go back to the initial position
                    print("Gotcha!")
                    turn(30, 2)
                    R.release()
                    drive(-20,1)
                    turn(-30,2)
            
                else:
                    print("Aww, I'm not close enough.")
                    drive(drive_v , 0.1)
            elif rot_y<-30 or rot_y>30 or-a_th<= rot_y <= a_th: #if a silver token is found behind or if the robot is well aligned with the next silver token we let it move straight
                drive(drive_v , 0.1)
            elif rot_y < -a_th: # if the robot is not well aligned with the token, we slightly move it on the left or on the right
                print("Left a bit...")
                turn(-2, 0.1)
            elif rot_y > a_th:
                print("Right a bit...")
                turn(+2, 0.1)