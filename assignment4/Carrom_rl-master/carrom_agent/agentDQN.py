# A Sample Carrom Agent to get you started. The logic for parsing a state
# is built in

from thread import *
import time
import socket
import sys
import argparse
import random
import ast

import tensorflow as tf
import numpy as np
from collections import deque
# Parse arguments

parser = argparse.ArgumentParser()

parser.add_argument('-np', '--num-players', dest="num_players", type=int,
                    default=1,
                    help='1 Player or 2 Player')
parser.add_argument('-p', '--port', dest="port", type=int,
                    default=12121,
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
    try:
        reward = float(s[1])
    except:
        reward = 0
    state = ast.literal_eval(s[0])
    return state, reward

ACTIONS = 3 # number of valid actions
GAMMA = 0.99 # decay rate of past observations
OBSERVE = 10. # timesteps to observe before training
EXPLORE = 10. # frames over which to anneal epsilon
FINAL_EPSILON = 0.05 # final value of epsilon
INITIAL_EPSILON = 1.0 # starting value of epsilon
REPLAY_MEMORY = 1000 # number of previous transitions to remember
BATCH = 3 # size of minibatch
K = 1 # only select an action every Kth frame, repeat prev for others

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev = 0.01)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.01, shape = shape)
    return tf.Variable(initial)

def conv2d(x, W, stride):
    return tf.nn.conv2d(x, W, strides = [1, stride, stride, 1], padding = "SAME")

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "SAME")

def createNetwork():
    # network weights
    W_conv1 = weight_variable([8, 8, 4, 32])
    b_conv1 = bias_variable([32])

    W_conv2 = weight_variable([4, 4, 32, 64])
    b_conv2 = bias_variable([64])

    W_conv3 = weight_variable([3, 3, 64, 64])
    b_conv3 = bias_variable([64])
    
    W_fc1 = weight_variable([1600, 512])
    b_fc1 = bias_variable([512])

    W_fc2 = weight_variable([512, ACTIONS])
    b_fc2 = bias_variable([ACTIONS])

    # input layer
    s1 = tf.placeholder("float", [None, 80, 80, 4])

    # hidden layers
    h_conv1 = tf.nn.relu(conv2d(s1, W_conv1, 4) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2, 2) + b_conv2)
    #h_pool2 = max_pool_2x2(h_conv2)

    h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3, 1) + b_conv3)
    #h_pool3 = max_pool_2x2(h_conv3)

    #h_pool3_flat = tf.reshape(h_pool3, [-1, 256])
    h_conv3_flat = tf.reshape(h_conv3, [-1, 1600])

    h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flat, W_fc1) + b_fc1)

    # readout layer
    readout = tf.matmul(h_fc1, W_fc2) + b_fc2

    return s1, readout, h_fc1

def agent_1player(state):

    flag = 1
    # print state
    try:
        state, reward = parse_state_message(state)  # Get the state and reward
    except:
        pass


    a = str(random.random()) + ',' + \
        str(random.randrange(-45, 225)) + ',' + str(random.random())

    try:
        s.send(a)
    except Exception as e:
        print "Error in sending:",  a, " : ", e
        print "Closing connection"
        flag = 0

    return flag

def agent_2player(state, color):

    flag = 1

   
    a = str(random.random()) + ',' + \
        str(random.randrange(-45, 225)) + ',' + str(random.random())

    try:
        s.send(a)
    except Exception as e:
        print "Error in sending:",  a, " : ", e
        print "Closing connection"
        flag = 0

    return flag
sess = tf.InteractiveSession()
s1, readout, h_fc1 = createNetwork()
a = tf.placeholder("float", [None, ACTIONS])
y = tf.placeholder("float", [None])
readout_action = tf.reduce_sum(tf.mul(readout, a), reduction_indices = 1)
cost = tf.reduce_mean(tf.square(y - readout_action))
train_step = tf.train.AdamOptimizer(1e-6).minimize(cost)

# store the previous observations in replay memory
D = deque()

z = np.zeros((80,80),dtype='uint8')
s_t = np.stack((z, z, z, z), axis = 2)

sess.run(tf.initialize_all_variables())
epsilon = INITIAL_EPSILON
t = 0

while 1:
    state = s.recv(1024)  # Receive state from server
    state_temp, reward_temp = parse_state_message(state)
    print "============================"

    readout_t = readout.eval(feed_dict = {s1 : [s_t]})[0]
    a_t = np.zeros([ACTIONS])
    action_index = 0
    if random.random() <= epsilon or t <= OBSERVE:
        # action_index = random.randrange(ACTIONS)
        # a_t[action_index] = 1
        a_t[0] = random.random()
        a_t[1] = random.randrange(-45, 225)
        a_t[2] = random.random()

    else:
        action_index = np.argmax(readout_t)
        a_t[action_index] = 1
    print a_t,"appended------------"
    print readout_t
    # scale down epsilon
    if epsilon > FINAL_EPSILON and t > OBSERVE:
        epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE

    r_t = reward_temp
    z = np.zeros((80,80),dtype='uint8')
    white = []
    black = []
    red = []

    if 'White_Locations' in state_temp:
        white = state_temp['White_Locations']
    if 'Black_Locations' in state_temp:
        black = state_temp['Black_Locations']
    if 'Red_Location' in state_temp:
        red = state_temp['Red_Location']
    print white
    print red
    print black
    z1 = np.zeros((80,80),dtype='uint8')
    z2 = np.zeros((80,80),dtype='uint8')
    z3 = np.zeros((80,80),dtype='uint8')
    z4 = np.zeros((80,80),dtype='uint8')    
    # for (x,y) in red:
    #      z1[1,1] = np.uint8(1)    
    if(color=='Black'):
        for (x,y) in black:
            z2[int(x/10.0),int(y/10.0)] = 255
            z3[int(x/10.0),int(y/10.0)] = 255
        for (x,y) in white:
            z4[int(x/10.0),int(y/10.0)] = 255
    s_t1 = np.stack((z1, z2, z3, z4), axis = 2)

    # store the transition in D
    D.append((s_t, a_t, r_t, s_t1))
    if len(D) > REPLAY_MEMORY:
        D.popleft()

    if t > OBSERVE:
        minibatch = random.sample(D, BATCH)

        # get the batch variables
        s_j_batch = [d[0] for d in minibatch]
        a_batch = [d[1] for d in minibatch]
        r_batch = [d[2] for d in minibatch]
        s_j1_batch = [d[3] for d in minibatch]

        y_batch = []
        readout_j1_batch = readout.eval(feed_dict = {s1 : s_j1_batch})
        for i in range(0, len(minibatch)):
            y_batch.append(r_batch[i] + GAMMA * np.max(readout_j1_batch[i]))

        # perform gradient step
        print type(s_j_batch)
        train_step.run(feed_dict = {y : y_batch,a : a_batch,s1 : s_j_batch})

    s_t = s_t1
    t += 1

    if num_players == 1:
        if agent_1player(state) == 0:
            break
    elif num_players == 2:
        if agent_2player(state, color) == 0:
            break
s.close()
