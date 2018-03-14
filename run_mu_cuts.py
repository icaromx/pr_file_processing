import ROOT, math, sys, os
from ROOT import *
#import numpy as np
import glob, os, sys, subprocess
from subprocess import call
#os.getenv('$DYLD_LIBRARY_PATH')
#os.getenv('ROOTSYS')

pr_files = glob.glob('../pr_files/pr_*.root')
####################################################################
#########################PARAMETERS#################################

t0 = -3200 #ticks
result_folder = '../mu_candidates/'
file_name = 'Stop_mu_'

####################################################################
if(os.path.exists(result_folder) == True):
	os.system('rm -r ' + result_folder)
	os.system('mkdir ' + result_folder)
else:
	os.system('mkdir ' + result_folder)

n = 0
print('Applying cuts to pr_files')
for x in pr_files:
	print('Cutting file ' + x + ' ' + str(n/len(pr_files))*100)
	os.system('python mu_cuts.py ' + x) #Applies cuts on events resulting from wirecell chain.
	n += 1
#####################################################################
############################TO BEE###################################
#####################################################################
print('Starting Bee file making process')

if(os.path.exists('data/') == True):
	os.system('rm -r data/')
	os.system('mkdir data/')
else:
	os.system('mkdir data/')

if(os.path.exists('to_upload.zip') == True):
	os.system('rm to_upload.zip')


folder = 0
for i in xrange(len(pr_files)):
	if folder == 1:
		break
	root_pr_file = ROOT.TFile.Open(pr_files[i])	
	for row in root_pr_file.Trun:
		ev_num = row.eventNo
		run_num = row.runNo 

	mu_file = result_folder + file_name + 'run_' + str(run_num) + '_ev_' + str(ev_num) + '.root'
	print('Looking at file: ' + mu_file + ' ' + str(folder/len(pr_files)*100))	
	label_nc = 'No_Cuts'
	os.system('mkdir data/' + str(folder))
	os.system('python TTree_to_JSON.py ' + pr_files[i] + ' T_charge_cluster > ' + str(folder) + '-' + label_nc + '.json')
	os.system('mv ' + str(folder) + '-' + label_nc + '.json data/' + str(folder))
	folder += 1

	label_tcuts = 'Topological_cuts'
	os.system('mkdir data/' + str(folder))
	os.system('python TTree_to_JSON.py ' + mu_file + ' T_charge_cluster_nfc > ' + str(folder) + '-' + label_tcuts + '.json')
	os.system('mv ' + str(folder) + '-' + label_tcuts + '.json data/' + str(folder))
	folder += 1

	label_tfcuts = 'Topological_plus_Flash_cuts'
	os.system('mkdir data/' + str(folder))
	os.system('python TTree_to_JSON.py ' + mu_file + ' T_charge_cluster > ' + str(folder) + '-' + label_tfcuts + '.json')
	os.system('mv ' + str(folder) + '-' + label_tfcuts + '.json data/' + str(folder))
	folder += 1

os.system('zip -r ../to_upload.zip data')
os.system('rm -r data/')
print("DONE")
