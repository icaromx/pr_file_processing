import ROOT, math, sys, os
from ROOT import *
import numpy as np
import glob, os, sys

def order(track):
	order_trk = sorted(track, key = lambda x: x[2], reverse = True)
	return order_trk

filename = sys.argv[1]
f = ROOT.TFile.Open(filename)

for row in f.Trun:
		ev_num = row.eventNo
		run_num = row.runNo

##################################################################

vdrift = 0.1101 #cm/us CONSTANT
pe_threshold = 10
x_anode = 0.0
x_cathode = 256.4

x_anode_th = 3.0
x_cathode_th = 4.0 

file_name = 'Stop_mu_'
result_folder = '../mu_candidates/'
mu_file = result_folder + file_name + 'run_' + str(run_num) + '_ev_' + str(ev_num) + '.root'
##################################################################
clusters = []
ev_points = []
xp = []
yp = []
zp = []
qp = []

num = 0
prev_cval = 0

########################EXTRACT CLUSTER###########################
for e in f.T_charge_cluster:
	a = []
	x, y, z, q, cl = e.qx, e.qy, e.qz, e.qc, e.cluster_id
	a = [cl, x, y, z, q] ### cl, x, y, z, q
	ev_points.append(a)

	if num == 0:
		clusters.append(e.cluster_id)
		prev_cval = e.cluster_id
	elif prev_cval != e.cluster_id:
		prev_cval = e.cluster_id
		clusters.append(e.cluster_id)
	num += 1

####################################################################
temp_of_t = []
pe = []
of_t = []
flash_tree = ROOT.gROOT.FindObject("T_op")
for entry in flash_tree:
	for i in entry.of_t:
		temp_of_t.append(i)
	index = 0
	for j in entry.of_peTotal:
		if j > pe_threshold:
			of_t.append(temp_of_t[index])
		index += 1

##########################################################
##############Making Track Array##########################
cnum = 0
track = []
All_tracks = []
for p in ev_points:
	if p[0] == clusters[cnum]:
		track.append(p)
	else:
		track = order(track)
		All_tracks.append(track)
		cnum += 1
		track = []
		track.append(p)
####################################################################
#############################CUTS###################################
####################################################################

kept_tracks = []
kept_tracks_noflscut = []
kept_clusters =[]
for track in All_tracks:
	cl = []
	x  = []
	y  = []
	z  = []
	q  = []
	flash_found = False
	piercing = False
	for point in track:#	if point[0] == 14:	#	print "%f, %f, %f"%(point[1],point[2],point[3])
		cl.append(point[0])
		x.append(point[1])
		y.append(point[2])
		z.append(point[3])
		q.append(point[4])
#		y[-1] == min(y) the last y value is the minimum y value
	if(x[-1] > x_cathode - x_cathode_th/2.0 and x[-1] < x_cathode + x_cathode_th/2.0):
		continue
	if(x[-1] > x_anode - x_anode_th/2.0 and x[-1] < x_anode + x_anode_th/2.0):
		continue
	if(y[-1] < -85 or y[0] < 95):
		continue
	if(z[-1] < 20 or z[0] > 1015):
		continue
	if(abs(x[-1]-x[0]) > 230):
		continue
	if(math.sqrt((x[-1] - x[0])**2.0 + (y[-1] - y[0])**2.0 + (z[-1] - z[0])**2.0) < 20):
		continue
	if(x[-1] < -165 or x[-1] > 340):
		continue

	kept_tracks_noflscut.append(track)
	#x = v(t - t0)
	ta = x[-1]/vdrift# + 3200*0.5
	for t0 in of_t:
		xactual = vdrift*(ta - t0)
		#if track[0][0] == 14 and ev_num == '762':
		#	print (xactual)
		if x[-1] > x[0]: #Cathode-piercing track
			if xactual > x_cathode - x_cathode_th/2.0 and xactual < x_cathode + x_cathode_th/2.0:
				piercing = True
				break
		if x[-1] < x[0]: #Anode-piercing track
			if xactual > x_anode - x_anode_th/2.0 and xactual < x_anode + x_anode_th/2.0: 
				piercing = True
				break
	if piercing:
		continue
	kept_tracks.append(track)
	kept_clusters.append(track[0][0])
"""
	########x = v(t - t0) => t = x/v + t0
	for i in x:
		ta = i/0.1101 + (-3200)*0.5
		for t in of_t:
			if ta >= t - 4 and ta <= t + 4: #ta in (t-1,t+1)
				flash_found = True
				break
		if flash_found:
			break
	if flash_found != True:
		continue
		#print(i/0.1101 + (-3200)*0.5)

    ###################################
	piercing = False
	if(x[-1] > x[0]): #Anode-piercing like track
		for t in of_t:
			if (x[-1] + t * 0.1101) > 250:
			xa = t*0.1101

				piercing = True
				break
	else:  #Cathode-piercing
		for t in of_t:
			if (x[-1] - t * 0.1101) < 0:
				piercing = True
				break
	if piercing:
		continue
"""
#####################################################################
######################SAVING HISTOGRAMS##############################
#####################################################################

output = ROOT.TFile(mu_file,"recreate")

tcl = ROOT.TTree("T_cluster_id", "Cluster IDs")

t = ROOT.TTree("T_charge_cluster", "Charge clusters")

tr = ROOT.TTree("Trun", "Run Metadata")
tr = ROOT.TTree.CloneTree(f.Trun)

cl = np.zeros(1, dtype=float)
x  = np.zeros(1, dtype=float)
y  = np.zeros(1, dtype=float)
z  = np.zeros(1, dtype=float)
q  = np.zeros(1, dtype=float)
cl_id = np.zeros(1, dtype=float)

cl_nfc = np.zeros(1, dtype=float)
x_nfc  = np.zeros(1, dtype=float)
y_nfc  = np.zeros(1, dtype=float)
z_nfc  = np.zeros(1, dtype=float)
q_nfc  = np.zeros(1, dtype=float)

cl_id = np.zeros(1, dtype=float)


t.Branch('cluster_id', cl, 'cluster_id/D')
t.Branch('qx', x, 'qx/D')
t.Branch('qy', y, 'qy/D')
t.Branch('qz', z, 'qz/D')
t.Branch('qc', q, 'qc/D')

tcl.Branch('cluster_id', cl_id, 'cluster_id/D')

t_nfc = ROOT.TTree("T_charge_cluster_nfc", "Charge clusters - No Flash Cut")
t_nfc.Branch('cluster_id', cl_nfc, 'cluster_id/D')
t_nfc.Branch('qx', x_nfc, 'qx/D')
t_nfc.Branch('qy', y_nfc, 'qy/D')
t_nfc.Branch('qz', z_nfc, 'qz/D')
t_nfc.Branch('qc', q_nfc, 'qc/D')
for track in kept_tracks_noflscut:
	for points in track:
		cl_nfc[0] = points[0]
		x_nfc[0]  = points[1]
		y_nfc[0]  = points[2]
		z_nfc[0]  = points[3]
		q_nfc[0]  = points[4]
		t_nfc.Fill()

for cid in kept_clusters:
	cl_id[0] = float(cid)
	tcl.Fill()

for track in kept_tracks:
	for points in track:
		cl[0] = points[0]
		x[0]  = points[1]
		y[0]  = points[2]
		z[0]  = points[3]
		q[0]  = points[4]
		t.Fill()


output.Write()
output.Close()
