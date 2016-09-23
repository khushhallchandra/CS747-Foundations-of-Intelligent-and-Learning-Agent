import sys
import readMDP

def valueIteration(S, A, R, T, gamma):

	# Initialized V with 0 value
	V = [0 for i in range(S)]
	pi = [0 for i in range(S)]

	#loop until policy good enough
	# while(1):


	return V,pi

if __name__ == '__main__':
	
	inputFile = sys.argv[1]
	S, A, R, T, gamma = readMDP.getParam(inputFile)	
	V,pi = valueIteration(S, A, R, T, gamma)
	
	for i in range(S):
		print V[i], pi[i]