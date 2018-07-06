#!/usr/bin/env python

# **************************************************************************
# *
# * Replace the resolution estimates in a micrographs_ctf.star files with 
# * new values estimated using a custom CCC cutoff.
# *
# * Rado Danev
# *
# * 14/02/2017
# *
# **************************************************************************

# modified - Matt Iadanza 2018/06/23
# Astbury Biostructure Laboratory - University of Leeds
# contact fbscem@leeds.ac.uk with bugs and suggestions


import optparse
from sys import *
import os,sys,re
import linecache
import random
import shutil
import numpy as np

if len(sys.argv) ==1:
	sys.exit('''
USAGE: Gctf_custom_res_limit_micrographs_ctf_test.py <ctf star file >

Optional arguments:

--cc_cutoff <n>		EPA cross correlation value to use for max resolution determination - default is 0.5\n''')

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()

        parser.set_usage("%prog [options] <micrographs star file>")
        
        parser.add_option("--cc_cutoff", dest="cc_cutoff", type="float", default=0.5, metavar=0.5,
                help="CC cutoff value for resolution estimation")
        
        options,args = parser.parse_args()

        if len(args) > 1:
                parser.error("Unknown commandline options: " + str(args[1:]))

        if len(sys.argv) < 2:
                parser.print_help()
                sys.exit()

        params={}

        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)

        return params, args

#==============================
def checkConflicts(params, args):

        if not os.path.exists(args[0]):
            print 'Error: File %s does not exist' %(args[0])
            sys.exit()

        if params['cc_cutoff'] < 0:
            print 'Error: cc_cutoff < 0. Exiting'
            sys.exit()

        if params['cc_cutoff'] > 1.0:
            print 'Error: cc_cutoff > 1.0. Exiting'
            sys.exit()


#===============================
def getRelionColumnIndex(star,rlnvariable):

    counter=50
    i=1

    while i<=50:

        line=linecache.getline(star,i)

        if len(line)>0:
            if len(line.split())>1:
                if line.split()[0] == rlnvariable:
                    return line.split()[1][1:]

        i=i+1

#==============================
def getNumberofLinesRelionHeader(star):

    f1=open(star,'r')
    tot=0

    for line in f1:
        if len(line) < 50:
            tot=tot+1
    f1.close()

    tot=tot-1

    return tot

#==============================
def getNumberMicrographsRelion(star):

    f1=open(star,'r')
    tot=0

    for line in f1:
        if len(line) > 50:
            tot=tot+1

    f1.close()

    return tot

#==============================
def reweight_starfile(euler,particle,rotlim1,rotlim2,tiltlim1,tiltlim2,psilim1,psilim2,debug,tot,remove):

  

        #Find number of particles that need to be removed & write into temp file



#####TO DO
#create random list without replacement containing the number of entries in tmpfile
#then, read each line of tmpfile, asking if it is in teh random array
#If in random array, write to new text file
#Now, loop over all particles, and check if given particle is in the 'bad list', if so, do not write to output file .



	while 1:
	    line=linecache.getline(euler,counter)

	    if len(line) < 50:
	        counter=counter+1
	        continue

            l=line.split()

            rot=float(l[int(colrot)-1])
            tilt=float(l[int(coltilt)-1])
            psi=float(l[int(colpsi)-1])

            flag=0
            if debug is True:
                print rot
                print tilt
                print psi

            if rotlim1 > -180:
                if rotlim2 < 180:
                    if rot>rotlim1 and rot<rotlim2:
                        flag=1
                        if debug is True:
                            print 'flagged b/c of rot'

            if tiltlim1 >0:
                if tiltlim2<180:
                    if tilt>tiltlim1 and tilt<tiltlim2:
                        flag=1
                        if debug is True:
                            print 'flagged b/c of tilt'

            if psilim1 > -180:
                if psilim2 < 180:
                    if psi>psilim1 and ps<psilim2:
                        flag=1
                        if debug is True:
                            print 'flagged b/c of psi'
            if flag == 1:
                out.write('%i\n'%(particlecounter))
            counter=counter+1
            particlecounter=particlecounter+1



        #Get number of lines in tmpfile
        numLinesTemptFile=len(open(tmp,'r').readlines())

        #Throw error if number to be removed is greater than number in group
        if remove>numLinesTemptFile:
            print 'Error: Number of particles to removed from euler angle range is greater than the number of particles in given group. Check tmpfile122.txt for number of particles that are in euler angle group.Exiting'
            sys.exit()

        #Create numpy list of random numbers withOUT replacement to be removed
        toberemoved=np.random.choice(numLinesTemptFile,remove,replace=False)

        #Create new text file from which actual bad particle numbers will be stored
        tmp2='tmpfile122_sel.txt'
        if os.path.exists(tmp2):
            os.remove(tmp2)
        tmpread=open(tmp,'r')
        tmp2out=open(tmp2,'w')
        counter=1

        for line in tmpread:

            if counter in toberemoved:
                tmp2out.write(line)

            counter=counter+1

        tmp2out.close()
        tmpread.close()

        badparticlelist=np.loadtxt(tmp2)

        #Write header lines from edited file into new file header
        particleopen=open(particle,'r')
        particlewrite=open('%s_reweight.star' %(particle[:-5]),'w')
        counter=1
        counter=1
        for line in particleopen:
            if counter<80:
                if len(line)<50:
                    particlewrite.write(line)
            counter=counter+1

        #Get number of lines in header for edited file
        header_particle=getNumberofLinesRelionHeader(particle)-1
        if debug is True:
            outtemp=open('tmpout_flaggedtoberemoved.txt','w')
            print 'Number of lines in header: %i' %(header_particle)

        #Go through each line, decide if it should/shouldn't be included and write into new file
        euler_open=open(euler,'r')
        counter=1

        #Particlesremoved
        outtmp=open('%s_linesRemoved.txt'%(tmp[:-4]),'w')

        for line in euler_open:

            if len(line) < 50:
                counter=counter+1
                continue

            #Debug print
            #if debug is True:
                #print 'Working on particle %i in euler file' %(counter)
                #print 'Euler line: %s' %(line)

            #Check if this particle is to be removed
            #remove_flag=checkInList('tmpfile122_222.txt',counter)
            remove_flag=0

            if (counter-header_particle) in badparticlelist:
                remove_flag=1

            if not (counter-header_particle) in badparticlelist:
                remove_flag=0

            #Determine corresponding line number in edited file for this particle
            particle_num=counter

            #Get line from file
            particle_line=linecache.getline(particle,particle_num)

            #if debug is True:
                #print 'Particle %i is on line %i in %s' %(counter,particle_num,particle)
                #print 'Particle line: %s' %(particle_line)

            if remove_flag == 0:
                particlewrite.write(particle_line)
                #if debug is True:
                    #'Writing particle %i to new file' %(counter)

                if debug is True:
                    outtemp.write('%s\n' %(str(remove_flag)))

            counter=counter+1
        return badparticlelist

#==============================
def checkInList(badlist,checknum):

    readingfile=open(badlist,'r')

    flag=0

    for line in readingfile:
        #print float(line.split()[0])
        #print float(checknum)
        if float(line.split()[0]) == float(checknum):
            flag=1

    readingfile.close()
    return flag

#==============================
if __name__ == "__main__":

        #Get input options
        params,args =setupParserOptions()

	cc_cutoff = params['cc_cutoff']
	print 'cc_cutoff: ', cc_cutoff

	micrographs_star = args[0]
	print 'micrographs star file: ', micrographs_star    

        #Parameters check
        checkConflicts(params, args)

        #Number of micrographs
        num_micrographs=getNumberMicrographsRelion(micrographs_star)
	print 'Number of micrographs: ', num_micrographs

	#Number of header lines
	star_header=getNumberofLinesRelionHeader(micrographs_star)
	print 'Header lines: ', star_header

	#Res limit column
	res_column = int(getRelionColumnIndex( micrographs_star, '_rlnCtfMaxResolution'))
	print 'CTF resolution column: ', res_column
        if not res_column:
            print 'Could not find _rlnCtfMaxResolution in header of %s. Exiting' %(micrographs_star)
            sys.exit()

	#Micrograph name column
	micrograph_column = int(getRelionColumnIndex( micrographs_star, '_rlnMicrographName'))
	print 'Micrograph name column: ', micrograph_column
        if not micrograph_column:
            print 'Could not find _rlnMicrographName in header of %s. Exiting' %(micrographs_star)
            sys.exit()

        #Create output star file
        out_file=micrographs_star[:-5]+'_CC'+str(cc_cutoff)+'.star'
        if os.path.exists(out_file):
            os.remove(out_file)

        out=open(out_file,'w')

        counter=1
	
	#Transplant the header as it is
        while counter <= star_header:
	    line=linecache.getline(micrographs_star,counter)
	    out.write(line)
	    counter+=1

        counter=1

	#Transfer the micrographs
        while counter <= num_micrographs:

	    line=linecache.getline(micrographs_star,(star_header+counter))
	    
	    l=line.split()
	    
	    EPA_logfile=l[2][:-8]+'_EPA.log'
	    
	    
	    res_file_line=2
	    res_measured=False
	    
	    #Measure the resolution of the current micrograph	    
	    while not res_measured:
		res_line=linecache.getline(EPA_logfile, res_file_line)
		res_split = res_line.split()
		#If the end of file is reached before a measurement can be performed
		if len(res_split) < 5:
		    resolution = 100.0
		    res_measured = True
		    continue
		if float(res_split[4]) < cc_cutoff:
		    resolution = float(res_split[0])
		    res_measured = True
		res_file_line+=1
		
	    column=1

	    while column <= len(l):
		if column == res_column:
	    	    out.write('%.2f\t' % (resolution))
		else:
		    out.write(l[column-1] + '\t')

		column+=1
	    
	    out.write('\n');

	    counter=counter+1

	out.close()

	print 'Done! The results were written to: ' + out_file
