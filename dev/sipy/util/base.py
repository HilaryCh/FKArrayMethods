from __future__ import absolute_import
import numpy as np
import scipy as sp
import obspy
from obspy import UTCDateTime, Stream, Inventory
from obspy.core.inventory.network import Network
import warnings


"""
Basic collection of fundamental functions for the SiPy lib
Author: S. Schneider 2016
"""
def stream2array(stream, normalize=False):
	sx = stream.copy()
	x = np.zeros((len(sx), len(sx[0].data)))
	for i, traces in enumerate(sx):
		for j, data in enumerate(traces):
			x[i,j]=data

	if normalize:
		if x.max()==0:
			print('Maximum value is 0')
			return(x)
		else:
			x = x / x.max()
	return(x)

def array2stream(ArrayData, st_original=None, network=None):
	"""
	param network: Network, of with all the station information
	type network: obspy.core.inventory.network.Network
	"""		
	traces = []
	
	for i, trace in enumerate(ArrayData):
		newtrace = obspy.core.trace.Trace(trace)
		traces.append(newtrace)
		
	stream = Stream(traces)
	
	# Just writes the network information, if possible input original stream
	
	if isinstance(st_original, Stream):
		st_tmp = st_original.copy()
		# Checks length of ArrayData and st_original, if needed,
		# corrects trace.stats.npts value of new generated Stream-object.
		if ArrayData.shape[1] == len(st_tmp[0]):

			for i, trace in enumerate(stream):
				trace.stats = st_tmp[i].stats

		else:

			for i, trace in enumerate(stream):
				trace.stats = st_tmp[i].stats
				trace.stats.npts = ArrayData.shape[1]
			

	elif isinstance(network, Network) and not isinstance(st_tmp, Stream):

		for trace in stream:
			trace.meta.network = network.code
			trace.meta.station = network[0].code


	return(stream)
def read_file(stream, inventory, catalog, array=False):
	"""
	function to read data files, such as MSEED, station-xml and quakeml, in a way of obspy.read
	if need, pushes stream in an array for further processing
	"""
	st=obspy.read(stream)
	inv=obspy.read_inventory(inventory)
	cat=obspy.readEvents(catalog)

	#pushing the trace data in an array
	if array:
		ArrayData=stream2array(st)
		return(st, inv, cat, ArrayData)
	else:
		return(st, inv, cat)

def create_sine( no_of_traces=10, len_of_traces=30000, samplingrate = 30000,
                 no_of_periods=1):
    
    deltax = 2*np.pi/len_of_traces
    signal_len = len_of_traces * no_of_periods
    period_time = 1 / samplingrate
    data_temp = np.array([np.zeros(signal_len)])
    t = []
    
    # first trace
    for i in range(signal_len):
        data_temp[0][i] = np.sin(i*deltax)
        t.append((float(i) + float(i)/signal_len)*2*np.pi/signal_len)
        data = data_temp
	
    # other traces
    for i in range(no_of_traces)[1:]:
       #np.array([np.zeros(len_of_traces)])
       #new_trace[0] = data[0]
       data = np.append(data, data_temp, axis=0)
       
       
    return(data, t)

def create_ricker(nofs, noft, slope, shift, width=2.):
	"""
	Creates noft Traces with a Ricker wavelet
	:param nofs: No of samples
	:type  nofs: int
	
	:param noft: No of traces
	:type  noft: int

	:param slope: Indexshift of the traces
	:type  slope: int

	:param width: Width parameter of Ricker-wavelet, default 2
	:type  width: float
	"""
	data = np.zeros((noft, nofs))	

	delta = int(1. / (slope * float(noft)/float(nofs)))
	
	trace = sp.signal.ricker(2*nofs, width)
	trace = np.roll(trace, trace.argmax() * (int(0.9 * nofs)-shift))/trace.max()
	if slope > 0:
		for i in range(data.shape[0]):
			data[i] = np.roll(trace, i * delta)[:nofs]	
	elif slope < 0:
		for i in range(data.shape[0])[::-1]:
			data[i] = np.roll(trace, -(data.shape[0]-1-i) * delta)[:nofs]	
	

	return data

def create_deltasignal(no_of_traces=10, len_of_traces=30000,
                       multiple=False, multipdist=2, no_of_multip=1, slowness=None,
                       zero_traces=False, no_of_zeros=0,
                       noise_level=0,
                       non_equi=False):
	"""
	function that creates a delta peak signal
	slowness = 0 corresponds to shift of 1 to each trace
	"""
	if slowness:
		slowness = slowness-1
	data = np.array([noise_level * np.random.rand(len_of_traces)])
	
	if multiple:
		dist = multipdist
		data[0][0] = 1
		for i in range(no_of_multip):
			data[0][dist+i*dist] = 1
	else:
		data[0][0] = 1
  
	data_temp = data
	for i in range(no_of_traces)[1:]:
		if slowness:
			new_trace = np.roll(data_temp, slowness*i)
		else:
			new_trace = np.roll(data_temp,i)
		data = np.append(data, new_trace, axis=0)

	if zero_traces:
		first_zero=len(data)/no_of_zeros
		while first_zero <= len(data):
			data[first_zero-1] = 0
			first_zero = first_zero+len(data)/no_of_zeros
	
	if non_equi:
		for i in [5, 50, 120]:
			data = line_set_zero(data, i, 10)
		data, indices= extract_nonzero(data)
	else:
		indices = []

	return(data, indices)

def standard_test_signal(snes1=1, snes2=3, noise=0, nonequi=False):
        y, yindices = create_deltasignal(no_of_traces=200, len_of_traces=200, 
        						multiple=True, multipdist=5, no_of_multip=1, 
        						slowness=snes1, noise_level=noise,
        						non_equi=nonequi)

        x, xindices = create_deltasignal(no_of_traces=200, len_of_traces=200, 
        						multiple=True, multipdist=5, no_of_multip=5, 
        						slowness=snes2, noise_level=noise,
        						non_equi=nonequi)
        a = x + y
        y_index = np.sort(np.unique(np.append(yindices, xindices)))
        return(a, y_index)

def maxrow(array):
	rowsum=0
	for i in range(len(array)):
		if array[i].sum() > rowsum:
			rowsum = array[i].sum()
			max_row_index = i
	return(max_row_index)

def nextpow2(i):
	#See Matlab documentary
	n = 1
	count = 0
	while n < abs(i):
		n *= 2
		count+=1
	return count

def LCM(a,b):
	"""
	Calculates the least common multiple of two values
	"""
	import fractions
	return abs(a * b) / fractions.gcd(a,b) if a and b else 0
