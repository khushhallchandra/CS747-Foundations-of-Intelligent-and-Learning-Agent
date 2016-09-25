# https://webdocs.cs.ualberta.ca/~sutton/book/4/node5.html

import sys
import readMDP

def valueIteration(S, A, R, T, gamma):

	#threshold
	theta = 0.00000001
	# Initialized V with 0 value
	V = [0.0 for i in range(S)]
	pi = [0.0 for i in range(S)]

	#loop until policy good enough
	while(1):
		delta = 0.0
		for s in xrange(S):
			v = V[s]

			value = 0.0
			action = 0.0
			for a in xrange(A):
				tempValue = 0.0
				for sp in xrange(S):
					tempValue  += T[s][a][sp]*(R[s][a][sp]+gamma*V[sp])
				if(tempValue > value):
					value = tempValue
					action = a

			V[s] = value
			pi[s] = action

			delta = max(delta,abs(v-V[s]))
		if(delta< theta):
			break

	return V,pi

if __name__ == '__main__':
	
	inputFile = sys.argv[1]
	S, A, R, T, gamma = readMDP.getParam(inputFile)	
	V,pi = valueIteration(S, A, R, T, gamma)
	
	for i in xrange(S):
		print "{0:.6f}".format(round(V[i],7)),pi[i]
		# print round(V[i],6), pi[i]