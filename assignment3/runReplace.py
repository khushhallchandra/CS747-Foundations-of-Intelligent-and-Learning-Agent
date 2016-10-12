import agent
import numpy as np
import pickle

alpha = [i/10.0 for i in range(2,10)]

trials = 100
episodes = 15
lamb=0.9
gamma=0.9
epsilon=0.1

results = []
for i in alpha:
    result = []
    for j in xrange(trials):
        t = agent.sarsa(episodes, lamb, gamma, epsilon, alpha=i, replacingTrace=True)
        result.append(np.mean(t))
    results.append(np.mean(result))

with open("output/replace_trace.txt",'wb') as f:
	pickle.dump(results,f)