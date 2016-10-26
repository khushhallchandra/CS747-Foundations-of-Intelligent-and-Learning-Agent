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


def parse_state_message(msg):
    s = msg.split(";REWARD")
    s[0] = s[0].replace("Vec2d", "")
    reward = float(s[1])
    state = ast.literal_eval(s[0])
    return state, reward

def get_dist_sq(x,y,x1,y1):
    return (x-x1)**2 + (y-y1)**2

def get_best_move(coins):
    min_dist = 1200*1200
    min_x = 1
    min_y = 1
    if(len(coins) != 0):
        min_x,min_y = coins[0]
    for(x,y) in coins:
        curr_dist = min(min(get_dist_sq(x,y,0,0),get_dist_sq(x,y,800,0)),min(get_dist_sq(x,y,800,800),get_dist_sq(x,y,0,800)))
        if(min_dist > curr_dist):
            min_x = x
            min_y = y
            min_dist = curr_dist

    return min_x,min_y



def get_dist_hole(x,y,angle):
    if(angle >= 0 and angle <90):
        dist = (800-45-x)**2 + (800-45-y)**2
    elif(angle >=90 and angle <180):
        dist = (0+45-x)**2 + (800-45-y)**2
    elif(angle >=180 and angle <270):
        dist = (0+45-x)**2 + (0+45-y)**2
    else:
        dist = (800-45-x)**2 + (0+45-y)**2
    return dist

def get_force(x,y,pos,angle):
    striker_x = 170.0 + pos*460.0
    striker_y = 145.0
    distance_sq = (striker_x - x)**2 + (striker_y - y)**2

    hole_distance_sq = get_dist_hole(x,y,angle)
    dist = math.sqrt(max(distance_sq, hole_distance_sq))
    max_force = 0.16 #0.2change later
    max_dist = math.sqrt((800 - 170)**2 + (800 - 145)**2)
    return dist*1.0*max_force/max_dist

def get_params(x,y):
    pos = random.random()
    angle = random.randrange(-45, 225)
    force = random.random()
    valid_pos = 1
    valid_angle = 1
    if(y<145):
        if(x<400):#pocket in lower left
            angle = 180 + math.degrees(math.atan((y*1.0)/x))
            pos = ((14.5*x/y)-17)/46.0
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else:#pocket in lower right
            angle = math.degrees(math.atan((y*1.0)/(x-800)))
            pos = (63.0 + ((14.5*(x-800))/y))/46.0
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
    else:
        if(x<400): #pocket in left-upper excluding blind-spot
            angle = 180 + math.degrees(math.atan(((y-800)*1.0)/x))
            pos = (((65.5*x)/(800-y))-17.0)/46.0
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0
        else: #pocket in right-upper excluding blind-spot
            angle = math.degrees(math.atan(((800-y)*1.0)/(800-x)))
            #pos = (800 + ((800-x)*(170-800)*1.0/(800-y)))/460.0
            pos = (63-(65.5*(800-x)/(800-y)))/46.0
            force = get_force(x, y, pos, angle)
            if(angle>225 or angle<-45):
                valid_angle=0
            if(pos<0 or pos>1):
                valid_pos=0

    if((y<=205 and y>=135) or valid_pos==0 or valid_angle==0):
        posprob = random.random()
        if(posprob<0.2):
            pos=0
            if(x==170):
                angle = 90
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x>170 and y>145):#first quadrant
                angle = math.degrees(math.atan((y-170)*1.0/(x-170)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x<170 and y>145):#2nd quadrant
                angle = 180-math.degrees(math.atan((y-170)*1.0/(170-x)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x<170 and y<145):#3rd quadrant
                angle = 180+math.degrees(math.atan((170-y)*1.0/(170-x)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x>170 and y<145):#4th quadrant
                angle = -math.degrees(math.atan((170-y)*1.0/(x-170)))
                prob = random.random()
                if(prob<=0.5):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
        elif(posprob>=0.2):
            pos=0.5
            if(x==400):
                angle = 90
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x>400 and y>145):#first quadrant
                angle = math.degrees(math.atan((y-170)*1.0/(x-400)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x<400 and y>145):#2nd quadrant
                angle = 180-math.degrees(math.atan((y-170)*1.0/(400-x)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x<400 and y<145):#3rd quadrant
                angle = 180+math.degrees(math.atan((170-y)*1.0/(400-x)))
                prob = random.random()
                if(prob<=0.3):
                    force = get_force(x, y, pos, angle)
                else:
                    force = 1
            elif(x>400 and y<145):#4th quadrant
                angle = -math.degrees(math.atan((170-y)*1.0/(x-400)))
                prob = random.random()
                if(prob<=0.5):
                    force = get_force(x, y, pos, angle)
                else:
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

    max_x = -1
    max_y = -1
    tmp = 0
    matrix = 4*[4*[0]]
    if len(red) == 0:
        for i in xrange(1,5):
            for j in xrange(1,5):
                for (a,b) in (white+black):
                    if(a <= i*200 and a>= (i-1)*200 and b <= j*200 and b >= (j-1)*200):
                        matrix[i-1][j-1] = matrix[i-1][j-1]+1
                if(matrix[i-1][j-1] > tmp):
                    tmp = matrix[i-1][j-1]
                    max_x = i-1
                    max_y = j-1
    else:
        max_x = red[0][0]/200
        max_y = red[0][1]/200

    if(max_x == -1 or max_y == -1):
        max_x = random.randrange(0,3)
        max_y = random.randrange(0,3)
        print "error : all cells have zero coins!"

    #TODOs
    #can play around later with force
    if len(red) == 1:
        max_x = red[0][0]
        max_y = red[0][1]
        pos,angle,force = get_params(max_x,max_y)
    # elif total_coin >= 10:
    #     max_x = (max_x+1)*200 - 100
    #     max_y = (max_y+1)*200 - 100
    #     print max_x,max_y,"checker"
    #     pos,angle,force = get_params(max_x,max_y)
    else:
        print len(white),len(black),len(red),"------------------"
        best_move = get_best_move(white+black)
        x = best_move[0]
        y = best_move[1]
        pos,angle,force = get_params(x,y)
    if(count<=2):
        pos = 0.5
        angle = 90
        force = 1
    elif(count<=3):
        pos = 0
        angle = 120
        force = 1
    elif(count<=4):
        pos = 1
        angle = 60
        force = 1
    #angle -= (random.choice([-1, 1]) * random.gauss(0, 1))
    # force = 0.5
    # pos = 0
    # angle = math.degrees(math.atan((800-170)*1.0/(800-170)))
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
