import pickle
import matplotlib.pyplot as plt

with open("output/replace_trace.txt",'rb') as f:
	y1 = pickle.load(f)
with open("output/regular_trace.txt",'rb') as f:
	y2 = pickle.load(f)
with open("output/alpha.txt",'rb') as f:
	x = pickle.load(f)

plt.plot(x, y1, label='Replace trace')
plt.plot(x, y2, label='Regular trace')

plt.legend()
plt.title('No. of episodes =  %d, No. of trials =  %d' %(15, 100))
plt.xlabel('alpha')
plt.ylabel('Time-steps')
plt.show()
