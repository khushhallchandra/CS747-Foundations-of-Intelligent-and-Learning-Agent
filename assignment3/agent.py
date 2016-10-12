# http://webdocs.cs.ualberta.ca/~sutton/book/ebook/node80.html
# Solution for the Exercise 7.7 , given in the book

# Note: all the name of variables are taken as given in the book
import numpy as np
import random

def epsilonGreedyAction(epsilon, p):
    # epsilon
    if random.random() <= epsilon:
        action = random.randint(0, len(p) - 1)
        return action
    # greedy
    action = np.where(p == np.amax(p))[0][0]
    return action

# i=5, is terminal state, others are non-terminal state(0,1,2,3,4)
term_state = 5
states = [i for i in range(term_state+1)]
actions = [0,1]
    
def sarsa(episodes, lamb, gamma, epsilon, alpha, replacingTrace):     
    # https://webdocs.cs.ualberta.ca/~sutton/book/ebook/node77.html
    # ^ Link for sarsa algorithm   
    timer = []    
    state_actions = []
    for j in states:
        for k in actions:
            state_actions.append((j,k))

    # initialize Q(s,a) arbitrarily and e(s,a) = 0, for all s,a
    Q = np.random.random([len(states), len(actions)])
    e = np.zeros([len(states), len(actions)])
    # Repeat for each episode
    for i in xrange(episodes):
        count_time = 0
        e = e * 0
        # initialize s, a
        s = 0
        a = 0
        # Repeat for each state of episode until s is terminal
        while (s!=term_state):
            # take action a, observe r, s'
            s_temp = s
            if a == 1:
                s_temp += 1
            # We are required to give reward 1 only if we are in terminal state
            if s_temp == term_state:
                r = 1
            else:
                r = 0
            s_prime = s_temp

            # Choose a' from s' using epsilon_greedy
            a_prime = epsilonGreedyAction(epsilon, Q[s_prime, :])

            delta = r + gamma * Q[s_prime, a_prime] - Q[s, a]
            if replacingTrace:
                e[s,a] = 1
            else:
                e[s,a] = e[s,a] + 1
            # for all s,a                
            for s, a in state_actions:
                Q[s,a] = Q[s,a] + alpha * delta * e[s,a]
                e[s,a] = gamma * lamb * e[s,a]
                
            s = s_prime
            a = a_prime
            count_time += 1
        # to measure the performance of the agent we are measuring the time taken to reach
        # the terminal state
        timer.append(count_time)
    return timer    
