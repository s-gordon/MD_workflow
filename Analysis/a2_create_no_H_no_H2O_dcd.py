#!/usr/bin/env python
# AUTHOR:   Shane Gordon
# FILE:     a1_other_analyses.py
# ROLE:     TODO (some explanation)
# CREATED:  2015-06-16 21:46:32
# MODIFIED: 2015-06-21 17:07:44

import os
import sys
import logging
import argparse
import subprocess
import shutil
import time
import shlex
import glob

# Argparse
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser=MyParser(description='Run CDPro automatically.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-v', '--verbose',  action="store_true",
        help="Increase verbosity")

result = parser.parse_args()

"""
If verbosity set, change logging to debug.
Else leave at info
"""
if result.verbose:
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.INFO)

def check_dir(dir):
    """
    Check whether directory dir exists.
    If true continue. Else exit.
    """
    if not os.path.isdir(dir):
        logging.error('Path %s not found', dir)
        logging.error('Aborting')
        sys.exit()

def check_file(file):
    """
    Check whether directory dir exists.
    If true continue. Else exit.
    """
    if not os.path.isfile(file):
        logging.error('Path %s not found', file)
        logging.error('Aborting')
        sys.exit()

def delete_dir(dir):
    """
    Check whether directory dir exists.
    If true delete and remake.
    """
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def delete_file(file):
    """
    Check whether file exists.
    If true delete.
    """
    if os.path.isfile(file):
    	os.remove(file)

def check_cmd(cmd):
    try:
        subprocess.check_call(['%s' % cmd], shell=True)
    except subprocess.CalledProcessError:
        pass # handle errors in the called executable
    except OSError:
        logging.error('Command %s not found' % cmd)
        sys.exit()

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

dcdfile_list = glob.glob('dcdfile_list_*.txt')
catdcd = "../Scripts/Tools/catdcd"

dir_list = []
with open('../.dir_list.txt') as dir:
	for line in dir:
		dir_list.append(line)

for l in dcdfile_list:
	dir = l.rstrip('\n')
	i = subprocess.check_output(
			"echo {0} | sed 's/.*_//' | sed 's/\.*//' | sed 's/\.[^.]*$//'".format(dir),
			shell=True
			)
	i = i.replace('\n', '')
	iter = 0
	with open(l) as f:
		for dcd in f:
			dcd = dcd.replace('\n', '')
			try:
				r = subprocess.Popen([
					catdcd,
					'-otype',
					'dcd',
					'-stride',
					'100',
					'-o',
					'{0}_temp_{1:04d}.dcd'.format(i, iter),
					dcd
					], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				r.wait()
				stdout, stderr = r.communicate()
			except OSError as e:
				logging.error(e)
				logging.error("failed")
				sys.exit()
			iter = iter+1
	try:
		r = subprocess.Popen('{0} -otype dcd -o no_water_{1}.dcd -dcd {1}_temp_*.dcd'.format(catdcd, i), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		r.wait()
		stdout, stderr = r.communicate()
		if glob.glob('{0}_temp_*.dcd'.format(i)):
			for idcd in glob.glob('{0}_temp_*.dcd'.format(i)):
				delete_file(idcd)
		try:
			num_frames = subprocess.check_output('{0} -num no_water_{1}.dcd | grep "Total frames:"| awk \'{{print $3}}\''.format(catdcd, i), shell=True)
			num_frames = num_frames.replace('\n', '')
			delete_file('number_frames_{0}.txt'.format(i))
			f = open('number_frames_{0}.txt'.format(i), 'w')
			f.write(num_frames)
			f.close()
		except OSError as e:
			logging.error(e)
			logging.error("failed")
			sys.exit()
	except OSError as e:
		logging.error(e)
		logging.error("failed")
		sys.exit()
