# A Sample Carrom Agent to get you started. The logic for parsing a state
# is built in

from thread import *
import time
import socket
import sys
import argparse
import random
import ast
import math

# Parse arguments

parser = argparse.ArgumentParser()

parser.add_argument('-np', '--num-players', dest="num_players", type=int,
                    default=1,
                    help='1 Player or 2 Player')
parser.add_argument('-p', '--port', dest="port", type=int,
                    default=123,
                    help='port')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int,
                    default=0,
                    help='Random Seed')
parser.add_argument('-c', '--color', dest="color", type=str,
                    default="Black",
                    help='Legal color to pocket')
args = parser.parse_args()


host = '127.0.0.1'
port = args.port
num_players = args.num_players
random.seed(args.rng)  # Important
color = args.color

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect((host, port))


# Given a message from the server, parses it and returns state and action

X1 = 44.1
Y1 = 44.1
X2 = 755.9
Y2 = 44.1
X3 = 755.9
Y3 = 755.9
X4 = 44.1
Y4 = 755.9
X  = 170.0
Y  = 145.0
width = 460.0
STRIKER_RADIUS = 20.6

def parse_state_message(msg):
    s = msg.split(";REWARD")
    s[0] = s[0].replace("Vec2d", "")
    reward = float(s[1])
    state = ast.literal_eval(s[0])
    return state, reward

# function to compute square of distance btw 2 points
def d_sq(x,y,x1,y1):
    return (x-x1)**2 + (y-y1)**2

#adds noise to the angle when hitting a coin in blind spot
def add_noise(angle):
    new_angle = angle
    if(angle>=0 and angle <= 90): #1st quadrant
        ref_angle = math.degrees(math.atan(((Y3-Y)*1.0)/(X3-X)))
        if(ref_angle > angle):
            new_angle = angle + 2.0
        else:
            new_angle = angle - 2.0
    elif(angle > 90 and angle < 180): #2nd quadrant
        ref_angle = 180 + math.degrees(math.atan(((Y4-Y)*1.0)/(X4-(X+width))))
        if(ref_angle > angle):
            new_angle = angle - 2.0
        else:
            new_angle = angle + 2.0
    elif(angle >= 180 and angle <= 225):
        new_angle = angle - 2.0
    elif(angle <0):
        new_angle = angle + 2.0
    return new_angle


# function to get the best move for the current state
def get_best_move(coins):
    min_dist = 1200*1200
    min_x = 400
    min_y = 400
    found = 0
    if(len(coins) != 0):
        min_x,min_y = coins[0]
    for(x,y) in coins:
        curr_dist = min(min(d_sq(x,y,X1,Y1),d_sq(x,y,X2,Y2)),min(d_sq(x,y,X3,Y3),d_sq(x,y,X4,Y4)))
        res = valid_move(x,y,coins)
        if(res[0]==1 and min_dist > curr_dist):
            found = 1
            min_x = x
            min_y = y
            min_dist = curr_dist
            pos = res[1]
            angle = res[2]
            force = res[3]
    #print "in get_best_move"
    if(found==1):
        print "GOOD"
        return min_x,min_y,pos,angle,force
    else:
        print "BAD"
        ret = get_params(min_x,min_y)
        pos = ret[0]
        angle = add_noise(ret[1])
        dist = get_dist_hole_sq(min_x,min_y,angle)
        if(dist < 3000):
            force = 0.2
        else:
            force = 0.5
        return min_x,min_y,pos,angle,force

#checks if striker can be placed at desired location or not->(when a coin already exists in that pos)
def can_strike(pos,coins):
    x_c = X + pos*width
    y_c = Y
    x_left = x_c - 2*STRIKER_RADIUS
    x_right = x_c + 2*STRIKER_RADIUS
    y_top = y_c + 2*STRIKER_RADIUS
    y_bottom = y_c - 2*STRIKER_RADIUS
    valid = 1
    for(x,y) in coins:
        if(x >= x_left and x <= x_right and y <= y_top and y >= y_bottom):
            valid = 0
            break
    return valid
# computes distance of coin from nearest hole
def get_dist_hole_sq(x,y,angle):
    if(angle >= 0 and angle <90):
        dist = d_sq(x,y,X3,Y3)
    elif(angle >=90 and angle <180):
        dist = d_sq(x,y,X4,Y4)
    elif(angle >=180 and angle <270):
        dist = d_sq(x,y,X1,Y1)
    else:
        dist = d_sq(x,y,X2,Y2)
    return dist

# computes the force required for hitting
def get_force(x,y,pos,angle):
    striker_x = X + pos*width
    striker_y = Y
    striker_distance_sq = d_sq(x,y,striker_x,striker_y)
    hole_distance_sq = get_dist_hole_sq(x,y,angle)
    dist = math.sqrt(max(striker_distance_sq, hole_distance_sq))
    if(angle >=0 and angle <=180):
        max_force = 0.12
        max_dist = math.sqrt(d_sq(X,Y,X3,Y3))
    else:
        max_force = 0.12
        max_dist = math.sqrt(d_sq(X,Y,X2,Y2))
    return (dist*1.0*max_force)/max_dist

# checks if the move is valid or not, if it is valid, then also return (pos,force,angle) to hit
def valid_move(x,y,coins):
    pos = random.random()
    angle = random.randrange(-45, 225)
    force = random.random()
    valid_pos = 1
    valid_angle = 1
    if(y<145):
        if(x<400):#pocket in lower left
            angle = 180 + math.degrees(math.atan(((y-Y1)*1.0)/(x-X1)))
            x_pos =  x + ((145.0-y)*(x-X1)*1.0)/(y-Y1)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else:#pocket in lower right
            angle = math.degrees(math.atan(((Y2-y)*1.0)/(X2-x)))
            x_pos = x + ((145.0-y)*(X2-x)*1.0)/(Y2-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
    else:
        if(x<400): #pocket in left-upper excluding blind-spot
            angle = 180 + math.degrees(math.atan(((Y4-y)*1.0)/(X4-x)))
            x_pos = x + ((145.0-y)*(X4-x)*1.0)/(Y4-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else: #pocket in right-upper excluding blind-spot
            angle = math.degrees(math.atan(((Y3-y)*1.0)/(X3-x)))
            x_pos = x + ((145.0-y)*(X3-x)*1.0)/(Y3-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
    if((y<=170 and y>=110) or valid_pos==0 or valid_angle==0):
        valid = 0
    elif can_strike(pos,coins) == 0:
        valid = 0
    else:
        valid = 1
        print "valid move", (x,y)
    return valid,pos,angle,force

# gets pos,angle,force for hitting coin at x,y. called when hitting queen and when a valid move couldn't
# be found
def get_params(x,y):
    pos = random.random()
    angle = random.randrange(-45, 225)
    force = random.random()
    valid_pos = 1
    valid_angle = 1
    if(y<145):
        if(x<400):#pocket in lower left
            angle = 180 + math.degrees(math.atan(((y-Y1)*1.0)/(x-X1)))
            x_pos =  x + ((145.0-y)*(x-X1)*1.0)/(y-Y1)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else:#pocket in lower right
            angle = math.degrees(math.atan(((Y2-y)*1.0)/(X2-x)))
            x_pos = x + ((145.0-y)*(X2-x)*1.0)/(Y2-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
    else:
        if(x<400): #pocket in left-upper excluding blind-spot
            angle = 180 + math.degrees(math.atan(((Y4-y)*1.0)/(X4-x)))
            x_pos = x + ((145.0-y)*(X4-x)*1.0)/(Y4-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else: #pocket in right-upper excluding blind-spot
            angle = math.degrees(math.atan(((Y3-y)*1.0)/(X3-x)))
            x_pos = x + ((145.0-y)*(X3-x)*1.0)/(Y3-y)
            pos = ((x_pos - X)*1.0)/width
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0


    if((y<=170 and y>=110) or valid_pos==0 or valid_angle==0):
        posprob = random.random()
        if(posprob<0.2):
            pos=0
            if(x==170):
                angle = 90
                force = 1
            elif(x>170 and y>145):#first quadrant
                angle = math.degrees(math.atan((y-145)*1.0/(x-170)))
                force = 1
            elif(x<170 and y>145):#2nd quadrant
                angle = 180-math.degrees(math.atan((y-145)*1.0/(170-x)))
                force = 1
            elif(x<170 and y<145):#3rd quadrant
                angle = 180+math.degrees(math.atan((145-y)*1.0/(170-x)))
                force = 1
            elif(x>170 and y<145):#4th quadrant
                angle = -math.degrees(math.atan((145-y)*1.0/(x-170)))
                force = 1
        elif(posprob>=0.2):
            pos=0.5
            if(x==400):
                angle = 90
                force = 1
            elif(x>400 and y>145):#first quadrant
                angle = math.degrees(math.atan((y-145)*1.0/(x-400)))
                force = 1
            elif(x<400 and y>145):#2nd quadrant
                angle = 180-math.degrees(math.atan((y-145)*1.0/(400-x)))
                prob = random.random()
                force = 1
            elif(x<400 and y<145):#3rd quadrant
                angle = 180+math.degrees(math.atan((145-y)*1.0/(400-x)))
                prob = random.random()
                force = 1
            elif(x>400 and y<145):#4th quadrant
                angle = -math.degrees(math.atan((145-y)*1.0/(x-400)))
                prob = random.random()
                force = 1
        if(angle>225 or angle<-45):
            if(posprob<0.2):
                pos=0.5
                if(x==400):
                    angle = 90
                    force = 1
                elif(x>400 and y>145):#first quadrant
                    angle = math.degrees(math.atan((y-145)*1.0/(x-400)))
                    force = 1
                elif(x<400 and y>145):#2nd quadrant
                    angle = 180-math.degrees(math.atan((y-145)*1.0/(400-x)))
                    prob = random.random()
                    force = 1
                elif(x<400 and y<145):#3rd quadrant
                    angle = 180+math.degrees(math.atan((145-y)*1.0/(400-x)))
                    prob = random.random()
                    force = 1
                elif(x>400 and y<145):#4th quadrant
                    angle = -math.degrees(math.atan((145-y)*1.0/(x-400)))
                    prob = random.random()
                    force = 1
            elif(posprob>=0.2):
                pos=0
                if(x==170):
                    angle = 90
                    force = 1
                elif(x>170 and y>145):#first quadrant
                    angle = math.degrees(math.atan((y-145)*1.0/(x-170)))
                    force = 1
                elif(x<170 and y>145):#2nd quadrant
                    angle = 180-math.degrees(math.atan((y-145)*1.0/(170-x)))
                    force = 1
                elif(x<170 and y<145):#3rd quadrant
                    angle = 180+math.degrees(math.atan((145-y)*1.0/(170-x)))
                    force = 1
                elif(x>170 and y<145):#4th quadrant
                    angle = -math.degrees(math.atan((145-y)*1.0/(x-170)))
                    force = 1

    return pos,angle,force


def agent_1player(state):

    flag = 1
    # print state
    print "******************"
    try:
        state, reward = parse_state_message(state)  # Get the state and reward
        print state
        print reward
    except:
        pass
    # Assignment 4: your agent's logic should be coded here
    white = []
    black = []
    red = []
    if 'White_Locations' in state:
        white = state['White_Locations']
    if 'Black_Locations' in state:
        black = state['Black_Locations']
    if 'Red_Location' in state:
        red = state['Red_Location']
    global count

    pos = random.random()
    angle = random.randrange(-45, 225)
    force = random.random()
    total_coin = len(white) + len(black) + len(red)

    # max_x = -1
    # max_y = -1
    # tmp = 0
    # matrix = 4*[4*[0]]
    # if len(red) == 0:
    #     for i in xrange(1,5):
    #         for j in xrange(1,5):
    #             for (a,b) in (white+black):
    #                 if(a <= i*200 and a>= (i-1)*200 and b <= j*200 and b >= (j-1)*200):
    #                     matrix[i-1][j-1] = matrix[i-1][j-1]+1
    #             if(matrix[i-1][j-1] > tmp):
    #                 tmp = matrix[i-1][j-1]
    #                 max_x = i-1
    #                 max_y = j-1
    # else:
    #     max_x = red[0][0]/200
    #     max_y = red[0][1]/200

    #TODOs
    #can play around later with force
    if len(red) == 1:
        x = red[0][0]
        y = red[0][1]
        pos,angle,force = get_params(x,y)
    else:
        best_move = get_best_move(white+black)
        x = best_move[0]
        y = best_move[1]
        pos = best_move[2]
        angle = best_move[3]
        force = best_move[4]
    if(count<=1):
        pos = 0.5
        angle = 90
        force = 1
    elif(count<=2):
        pos = 0
        angle = 120
        force = 1
    elif(count<=3):
        pos = 1
        angle = 60
        force = 1
    # pos = 1
    # force = 0.04
    # angle = 180 + math.degrees(math.atan((Y1-Y)*1.0/(X1-(X+width)))) + 2
    a = str(pos) + ',' + str(angle) + ',' + str(force)
    try:
        s.send(a)
    except Exception as e:
        print "Error in sending:",  a, " : ", e
        print "Closing connection"
        flag = 0
    count = count +1
    return flag


def agent_2player(state, color):

    flag = 1

    # Can be ignored for now
    a = str(random.random()) + ',' + \
        str(random.randrange(-45, 225)) + ',' + str(random.random())

    try:
        s.send(a)
    except Exception as e:
        print "Error in sending:",  a, " : ", e
        print "Closing connection"
        flag = 0

    return flag

count=1
while 1:
    state = s.recv(1024)  # Receive state from server
    if num_players == 1:
        if agent_1player(state) == 0:
            break
    elif num_players == 2:
        if agent_2player(state, color) == 0:
            break
s.close()
