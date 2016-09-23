def getParam(inputFile):

	f = open(inputFile,'r')

	S  = int(f.readline().strip())
	A = int(f.readline().strip())
	
	R = []
	for s in range(S):
		R.append([])
		for a in range(A):
			temp = f.readline().strip().split()
			R[s].append([float(i) for i in temp])

	T = []
	for s in range(S):
		T.append([])
		for a in range(A):
			temp = f.readline().strip().split()
			T[s].append([float(i) for i in temp])

	gamma = float(f.readline().strip())

	return S, A, R, T, gamma