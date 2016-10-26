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
port =17500
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
    left_coins = 0
    right_coins = 0
    matrix = 4*[4*[0]]
    if len(red) == 0:
        for i in xrange(1,5):
            for j in xrange(1,5):
                for (a,b) in (white+black+red):
                    if a<400:
                        left_coins = left_coins + 1
                    else:
                        right_coins = right_coins + 1
                    if(a <= i*200 and a>= (i-1)*200 and b <= j*200 and b >= (j-1)*200):
                        matrix[j-1][i-1] = matrix[j-1][i-1]+1
                        if(matrix[j-1][i-1] > tmp):
                            tmp = matrix[j-1][i-1]
                            max_x = i-1
                            max_y = j-1
    else:
        max_x = red[0][0]/200
        max_y = red[0][1]/200
        if red[0][0] <= 400:
            left_coins = 1
        else:
            right_coins = 1

    if(max_x == -1 or max_y == -1):
        max_x = random.randrange(0,3)
        max_y = random.randrange(0,3)
        print "error : all cells have zero coins!"

    #TODOs
    #can play around later with force
    if total_coin >= 10:
        force = 1 
        if left_coins >= right_coins:
            pos = 0
        else:
            pos = 1
        max_x = (max_x+1)*200 - 100
        max_y = (max_y+1)*200 - 100
        angle = math.degrees(math.atan((max_y-170)*1.0/(max_x-200)))
        if(max_x<400): #2nd and 3rd quadrant
            angle = 180 + angle
    else:
        print len(white),len(black),len(red),"------------------"
        valid_angle = 1
        valid_pos = 1
        for (x,y) in (white+black+red):
            if(y<170):
                if(x<400):#pocket in lower left
                    angle = 180 + math.degrees(math.atan((y-0)*1.0/(x-0)))
                    pos = 17*(x-y)/(y*46.0)
                    force = 0.2
                    if(angle>225 or angle<-45):
                        valid_angle=0
                    if(pos<0 or pos>1):
                        valid_pos=0
                    # blind_choosen = 0
                else:#pocket in lower right
                    angle = - math.degrees(math.atan((y-0)*1.0/(x-0)))
                    pos = ((170-y)*(800-x)/(y*1.0) + x - 170)/460.0
                    force = 0.2
                    if(angle>225 or angle<-45):
                        valid_angle=0
                    if(pos<0 or pos>1):
                        valid_pos=0
                    # blind_choosen = 0
            else:
                if(x<400): #pocket in left-upper excluding blind-spot
                    angle = 180-math.degrees(math.atan((y-800)*1.0/x))
                    #pos = ((800-170)*x*1.0/(800-y))/460.0
                    pos = (x-170+((y-170)*x*1.0/(800-y)))/460.0
                    force = 0.4
                    if(angle>225 or angle<-45):
                        valid_angle=0
                    if(pos<0 or pos>1):
                        valid_pos=0
                    # blind_choosen = 0
                else: #pocket in right-upper excluding blind-spot
                    angle = math.degrees(math.atan((800-y)*1.0/(800-x)))
                    #pos = (800 + ((800-x)*(170-800)*1.0/(800-y)))/460.0
                    pos = (630-630*(800-x)*1.0/(800-y))/460.0
                    force = 0.4
                    if(angle>225 or angle<-45):
                        valid_angle=0
                    if(pos<0 or pos>1):
                        valid_pos=0
                    # blind_choosen = 0
        #        else: #blind-spot
        #            blind_choosen = 1
            if(valid_pos==1 and valid_angle==1):
                break
            # if blind_choosen == 0:
                # break
        # if blind_choosen == 1:
            # angle =45
            # pos = 1
        if(valid_pos==0 or valid_angle==0):
            pos=0
            if(x>=170 and y>=170):#first quadrant
                angle = math.degrees(math.atan((y-170)*1.0/(x-170)))
                force = 0.4
            elif(x<170 and y>170):#2nd quadrant
                angle = 180-math.degrees(math.atan((y-170)*1.0/(170-x)))
                force = 0.4
            elif(x<170 and y<170):#3rd quadrant
                angle = 180+math.degrees(math.atan((170-y)*1.0/(170-x)))
                force = 0.4
            elif(x>170 and y<170):#4th quadrant
                angle = -math.degrees(math.atan((170-y)*1.0/(x-170)))
                force = 0.4
            #angle= 180+math.degrees(math.atan((y-170)/(x-170)))
    force = 0.5
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
