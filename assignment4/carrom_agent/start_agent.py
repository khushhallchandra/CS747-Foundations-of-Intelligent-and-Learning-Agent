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
    if(count<4):
        a = str(0.5) + ',' + str(90) + ',' + str(1)
    elif(count<11):
        a = str(0) + ',' + str(135) + ',' + str(1)
    else:
        print len(white),len(black),len(red),"------------------"

        #for (x,y) in (white+black):
        #    if(y<170):
        #        if(x<400):#pocket in lower left
        #            angle = 180 + math.atan((y-0)/(x-0))
        #            pos = (x-y)/(y*1.0)
        #        else:#pocket in lower right
        #            angle = - math.atan((y-0)/(x-0))
        #            pos = ((170-y)*(x-800)/(y*1.0) + x - 170)/170.0
        #    else:
        #        angle=45
        #        pos = 1
        #    break
        angle =45
        pos = 1
    	a = str(pos) + ',' + str(angle) + ',' + str(1)
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
