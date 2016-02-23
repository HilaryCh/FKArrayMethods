import numpy as np


def average_anti_diag(A):
	"""
	Given a Hankel matrix A,  this program retrieves
	the signal that was used to make the Hankel matrix
	by averaging along the antidiagonals of A.

	M.D.Sacchi
	2008
	SAIG - Physics - UofA
	msacchi@ualberta.ca


	In    A: A hankel matrix

	Out   s: signal (column vector)
	"""

	"""
	MATLAB
	[m,n] = size(A);
	N = m+n-1;

	 s = zeros(N,1);

	 for i = 1 : N

	  a = max(1,i-m+1);
	  b = min(n,i);

	   for k = a : b
	    s(i,1) = s(i,1) + A(i-k+1,k);
	   end

	 s(i,1) = s(i,1)/(b-a+1);

	 end;
 	"""

 	m,n = A.shape

 	N = m+n-1

 	s = np.zeros(N)

 	for i in range(N):
		a = max(1,(i+1)-m+1)
		b = min(n,(i+1))
		
		if a == b:
			k = a
			s[i] = s[i] + A[i-k+1,k-1]
		else:
	 		for k in range(a,b+1):
	 			s[i] = s[i] + A[i-k+1,k-1]

		s[i]= s[i]/(b-a+1)
 		
	return(s)







