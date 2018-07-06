#!/usr/bin/python
# Matt Iadanza 2017-03-03
# vers 2.0 modified by matt 20180110 to deal with micrographs aquired faster then 1/min
# vers 3.0 20180620 added proper documentation, license and documentation.
# vers 4.0 20180705 now handles phase plate data or non phaseplate data

vers = '4.0'
import sys
import warnings
warnings.filterwarnings("ignore", module="matplotlib")
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit('ERROR: matplotlib is not installed ')
try:
    import numpy as np
except ImportError:
    sys.exit('ERROR: numpy is not installed ')
global dfa
dfa = 0
#------------------------------get arguments -----------------------------------------#
class Arg(object):
    _registry = []
    def __init__(self, flag, value, req):
        self._registry.append(self)
        self.flag = flag
        self.value = value
        self.req = req
def make_arg(flag, value, req):
    errmsg = '''\nUSAGE: micrograph_analysis.py --i <micrographs_gctf.star>
optional flags:
--f       filter the micrographs by resolution, defocus, and/or astigmatism and makes a new star file\n'''
    Argument = Arg(flag, value, req)
    if Argument.req == True:
        if Argument.flag not in sys.argv:
            print(errmsg)
            sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
    if Argument.value == True:
        try:
            test = sys.argv[sys.argv.index(Argument.flag)+1]
        except ValueError:
            if Argument.req == True:
                print(errmsg)
                sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
            elif Argument.req == False:
                return False
        except IndexError:
            print(errmsg)
            sys.exit("ERROR: argument '{0}' requires a value".format(Argument.flag))
        else:
            if Argument.value == True:
                Argument.value = sys.argv[sys.argv.index(Argument.flag)+1]
        
    if Argument.value == False:
        if Argument.flag in sys.argv:
            Argument.value = True
        else:
            Argument.value = False
    return Argument.value
#-----------------------------------------------------------------------------------#
###---------function: read the star file get the header, labels, and data -------------#######
def read_starfile(f):
    alldata = open(f,'r').readlines()
    labelsdic = {}
    data = []
    header = []
    for i in alldata:
        if '#' in i:
            labelsdic[i.split('#')[0]] = int(i.split('#')[1])-1
        if len(i.split()) > 3:
            data.append(i.split())
        if len(i.split()) < 3:
            header.append(i.strip("\n"))
    return(labelsdic,header,data)
#---------------------------------------------------------------------------------------------#
#---- get the stats of the files - make some pretty graphs
def get_stats_make_graphs(alldata,mresvals,mastigvals,pstimedata):
    global dfa
    global dpi
    data = []
    for i in alldata:
        if len(i.split()) > 3:
            data.append(i.split())
        if '_rlnDefocusU' in i:
            dfucol = int(i.split('#')[-1])-1
        if '_rlnDefocusV' in i:
            dfvcol = int(i.split('#')[-1])-1
        if '_rlnDefocusAngle' in i:
            dfacol = int(i.split('#')[-1])-1
        if '_rlnMicrographName' in i:
            namecol = int(i.split('#')[-1])-1
        if '_rlnCtfMaxResolution' in i:
            rescol = int(i.split('#')[-1])-1
        if '_rlnPhaseShift' in i:
            pscol = int(i.split('#')[-1])-1
    v,u,a,names,res,ps = [],[],[],[],[],[]
    for i in data:
        u.append(float(i[dfucol]))
        v.append(float(i[dfvcol]))
        a.append(float(i[dfacol]))
        names.append(i[namecol])
        res.append(float(i[rescol]))
        ps.append(float(i[pscol]))
    amin = min(a)
    amax = max(a)
    maxfactor = 1/amax
    
    #-- make microsgraphs dictionary
    micsdic = {}
    count = 0
    for i in names:
        micsdic[i] = (u[count],v[count],a[count],res[count],ps[count]) 
        count+=1
    #--- make defocus plot
    scaleda = []
    for i in a:
        scaleda.append(i*maxfactor)
    
    # -- make dfplot
    plt.subplot2grid((4,2), (0, 0), colspan=2)
    plt.scatter(u, v, s=1, c=scaleda)        
    plt.xlabel('DefocusU',fontsize=10)
    plt.ylabel('DefocusV',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)
    
    #-- make astig plots
    astig = []
    count = 0
    for i in u:
        astig.append(abs(i - v[count]))
        count +=1    
    plt.subplot2grid((4,2), (2, 0))
    n, bins, patches = plt.hist(astig, 100, facecolor='blue', alpha=0.75)
    plt.xlabel('Astigmatism',fontsize=10)
    plt.ylabel('Micrographs',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)
    
    dfumean = np.mean(u)
    dfvmean = np.mean(v)
    
    #-- make resolution plot
    plt.subplot2grid((4,2), (1, 0))
    n, bins, patches = plt.hist(res, 100, facecolor='green', alpha=0.75)
    plt.xlabel('Resolution',fontsize=10)
    plt.ylabel('Micrographs',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)
    plt.subplot2grid((4,2), (1, 1))
    plt.plot(mresvals)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.xticks([])
    
    nums = range(len(mresvals))
    fit = np.polyfit(nums,mresvals,1)
    x = np.arange(min(nums),max(nums))
    eq = '{0}*x+{1}'.format(fit[0],fit[1])
    y = eval(eq)
    plt.plot(x,y,color='Red')
    plt.xlabel('Res/Time {0}%'.format(round(fit[0]*100,7)),fontsize=10)
    plt.ylabel('Resolution % mean',fontsize=10)
    
    plt.subplot2grid((4,2), (2, 1))
    plt.plot(mastigvals)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.xticks([])
    fit = np.polyfit(nums,mastigvals,1)
    eq = '{0}*x+{1}'.format(fit[0],fit[1])
    y = eval(eq)
    plt.plot(x,y,color='Red')
    plt.xlabel('Astig/Time {0}%'.format(round(fit[0]*100,7)),fontsize=10)
    plt.ylabel('Astig % mean',fontsize=10)
    plt.subplot2grid((4,2), (3, 0))
    plt.hist(ps)
    plt.xlabel('Phase shift (degrees)',fontsize=10)
    plt.ylabel('micrographs',fontsize=10)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.subplot2grid((4,2), (3, 1))
    plt.plot(pstimedata)
    plt.xlabel('Phase shift / image #',fontsize=10)
    plt.ylabel('degrees',fontsize=10)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.tick_params(axis='x', which='major', labelsize=8)
    
    plt.tight_layout()
    plt.savefig('micrograph_analysis_{0}.png'.format(dfa))
    if filter == True:
        plt.show(block=False)
    dfa +=1 
    return (micsdic)
    
#------------------------------------------------------------------------
#---- do running total-------------------------------
def running_total(dic):
    dickeys = dic.keys()
    dickeys.sort()
    means = []
    running_total = 0
    n = 1
    for dicline in dickeys:
        for val in dic[dicline]:
            running_total = running_total + float(val)
            n+=1
    mean = running_total/n
    for dicline in dickeys:
        for val in dic[dicline]:
            means.append(float(val)/mean)    
    return(means)
#----------------------------------------------------
thefile = make_arg('--i',True,True)
alldata = open(thefile,'r').readlines()
filter = make_arg('--f',False,False)
about = make_arg('--about',False,False)
if about != False:
    print ("""
2018 Matt Iadanza - University of Leeds - Astbury Centre for Structural Molecular Biology
contact fbsmi@leeds.ac.uk for suggestions/bug reports

If you find this program useful in your research please cite:

Thompson RF, Iadanza MG, Rawson SD, Hesketh EL, Ranson NA. (2018) Collection, pre-processing, and on-the-fly analysis of data for high-resolution, single-particle cryo-electron microscopy.
Nature Protocols. xx:xx(xx-xx) doi: xxxxxxxxxxxxxxxxxxxxx

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.""")
    sys.exit()
print("**** Micropgraph Analysis v{0} ****".format(vers))

#-----get numbers for running calculations---------------
def get_time_stats(file):
    (star_labels,star_header,star_data) = read_starfile(file)
    if '_rlnCtfMaxResolution ' not in star_labels:
        sys.exit('ERROR: _rlnCtfMaxResolution column not in star file - need to perform eqiphase analysis when running GCTF')
    phaseshift = True
    if '_rlnPhaseShift ' not in star_labels:
        phaseshift = False
    astigdatesdic = {}
    resdatesdic = {}
    psdatesdic = {}
    for i in star_data:
        
        date = ''.join(i[star_labels['_rlnMicrographName ']].split('_')[-2:]).split('-')[0]
        daten=0        
        date='{0}.{1}'.format(date,daten)
        if date not in resdatesdic:
           resdatesdic[date] = [i[star_labels['_rlnCtfMaxResolution ']]]
        else:
            daten+=1
            date= '{0}.{1}'.format(date.split('.')[0],daten)
            resdatesdic[date]=[i[star_labels['_rlnCtfMaxResolution ']]]
        astig = abs(float(i[star_labels['_rlnDefocusU ']])-float(i[star_labels['_rlnDefocusV ']]))
        if date not in astigdatesdic:
           astigdatesdic[date] = [astig]
        else:
            astigdatesdic[date] = [astig]
        if phaseshift == True:
            if date not in psdatesdic:
               psdatesdic[date] = [i[star_labels['_rlnPhaseShift ']]]
            else:
                psdatesdic[date] = [i[star_labels['_rlnPhaseShift ']]]
        
    return(astigdatesdic,resdatesdic,psdatesdic)
#------------------------------------------------------------

#---- get the stats of the files - make some pretty graphs - no phase plate
def get_stats_make_graphs_noPP(alldata,mresvals,mastigvals):
    global dfa
    global dpi
    data = []
    for i in alldata:
        if len(i.split()) > 3:
            data.append(i.split())
        if '_rlnDefocusU' in i:
            dfucol = int(i.split('#')[-1])-1
        if '_rlnDefocusV' in i:
            dfvcol = int(i.split('#')[-1])-1
        if '_rlnDefocusAngle' in i:
            dfacol = int(i.split('#')[-1])-1
        if '_rlnMicrographName' in i:
            namecol = int(i.split('#')[-1])-1
        if 'rlnCtfMaxResolution' in i:
            rescol = int(i.split('#')[-1])-1
            
    v,u,a,names,res = [],[],[],[],[]
    for i in data:
        u.append(float(i[dfucol]))
        v.append(float(i[dfvcol]))
        a.append(float(i[dfacol]))
        names.append(i[namecol])
        res.append(float(i[rescol]))
    amin = min(a)
    amax = max(a)
    maxfactor = 1/amax
    
    #-- make microsgraphs dictionary
    micsdic = {}
    count = 0
    for i in names:
        micsdic[i] = (u[count],v[count],a[count],res[count]) 
        count+=1
    #--- make defocus plot
    scaleda = []
    for i in a:
        scaleda.append(i*maxfactor)
    
    # -- make dfplot
    plt.subplot2grid((3,2), (0, 0), colspan=2)
    plt.scatter(u, v, s=1, c=scaleda)        
    plt.xlabel('DefocusU',fontsize=10)
    plt.ylabel('DefocusV',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)
    
    #-- make astig plots
    astig = []
    count = 0
    for i in u:
        astig.append(abs(i - v[count]))
        count +=1    
    plt.subplot2grid((3,2), (1, 0))
    n, bins, patches = plt.hist(astig, 100, facecolor='blue', alpha=0.75)
    plt.xlabel('Astigmatism',fontsize=10)
    plt.ylabel('Micrographs',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)
    
    dfumean = np.mean(u)
    dfvmean = np.mean(v)
    #-- make resolution plot
    plt.subplot2grid((3,2), (2, 0))
    n, bins, patches = plt.hist(res, 100, facecolor='green', alpha=0.75)
    plt.xlabel('Resolution',fontsize=10)
    plt.ylabel('Micrographs',fontsize=10)
    plt.tick_params(axis='both', which='major', labelsize=8)

    plt.subplot2grid((3,2), (2, 1))
    plt.plot(mresvals)

    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.xticks([])
    
    nums = range(len(mresvals))
    fit = np.polyfit(nums,mresvals,1)
    x = np.arange(min(nums),max(nums))
    eq = '{0}*x+{1}'.format(fit[0],fit[1])
    y = eval(eq)
    plt.plot(x,y,color='Red')
    plt.xlabel('Res/Time {0}%'.format(round(fit[0]*100,7)),fontsize=10)
    plt.ylabel('Resolution % mean',fontsize=10)
    
    plt.subplot2grid((3,2), (1, 1))
    plt.plot(mastigvals)
    plt.tick_params(axis='y', which='major', labelsize=8)
    plt.xticks([])
    
    nums = range(len(mastigvals))
    fit = np.polyfit(nums,mastigvals,1)
    eq = '{0}*x+{1}'.format(fit[0],fit[1])
    y = eval(eq)
    plt.plot(x,y,color='Red')
    plt.xlabel('Astig/Time {0}%'.format(round(fit[0]*100,7)),fontsize=10)
    plt.ylabel('Astig % mean',fontsize=10)
    
    plt.tight_layout()
    plt.savefig('micrograph_analysis_{0}.png'.format(dfa))
    if filter == True:
        plt.show(block=False)
    dfa +=1 
    return (micsdic)
    

#------------------------------------------------------------------------

(astigdatesdic,resdatesdic,psdatesdic) = get_time_stats(thefile) 
astigmeans = running_total(astigdatesdic)
resmeans = running_total(resdatesdic)
pstimedata = []
phaseplate = True
if len(psdatesdic) < 1:
    phaseplate = False
if phaseplate == True:
    pskeys = psdatesdic.keys()
    pskeys.sort()
    for i in pskeys:
        pstimedata.append(psdatesdic[i])

# standard calculations - and making of graphs
if phaseplate == True:
    micrographs = get_stats_make_graphs(alldata,resmeans,astigmeans,pstimedata)
else:
    micrographs = get_stats_make_graphs_noPP(alldata,resmeans,astigmeans)

# filtering if necesary
if filter == False:
    sys.exit('FINISHED: wrote micrograph_analysis_0.png')
print('look at the graphs and decide on the cutoffs (graph is saved as micrograph_analysis_0.png)')
print('leave blank to ignore this parameter')
rescut = raw_input('Resolution cutoff: ')
acut = raw_input('Astigmatism cutoff: ')
dfcut = raw_input('Defocus Cutoff: ')
if phaseplate == True:
    pscut = raw_input('Phase shift cutoff: ')
try:
    rescut = float(rescut)
except ValueError:
    rescut = 'SKIP'
try:
    acut = float(acut)
except ValueError:
    acut = 'SKIP'
try:
    dfcut = float(dfcut)
except ValueError:
    dfcut = 'SKIP'
if phaseplate == True:
    try:
        pscut = float(pscut)
    except ValueError:
        pscut = 'SKIP'
else:
    pscut = 'SKIP'
plt.close()
# find the bad micrographs
badmicrographs_df = []
badmicrographs_as = []
badmicrographs_res = []
badmicrographs_ps = []
for i in micrographs:
    if micrographs[i][0] > dfcut or micrographs[i][1] > dfcut:
        badmicrographs_df.append(i)
    if abs(micrographs[i][0] - micrographs[i][1]) > acut:
        badmicrographs_as.append(i)
    if micrographs[i][3] > rescut:
        badmicrographs_res.append(i)
    if phaseplate == True:
        if micrographs[i][4] > pscut:
            badmicrographs_ps.append(i)
output = open('{0}_culled.star'.format(thefile.split('.')[0]),'w')
for i in alldata:
    if len(i.split()) < 3:
        output.write('{0}\n'.format(i.strip('\n')))
        if '_rlnMicrographName' in i:
            namecol = int(i.split('#')[-1])-1
    else:
        if i.split()[namecol] not in badmicrographs_as and i.split()[namecol] not in badmicrographs_df and i.split()[namecol] not in badmicrographs_res and i.split()[namecol] not in badmicrographs_ps:
            output.write('{0}\n'.format(i.strip('\n')))
output.close()
diagfile = open('bad_micrographs.txt','w')
if dfcut != 'SKIP':
    diagfile.write('## Micrographs thrown out for defocus > {0}\n'.format(dfcut))
    for i in badmicrographs_df:
        diagfile.write('{0}\n'.format(i))
if acut != 'SKIP':
    diagfile.write('## Micrographs thrown out for astigmatism > {0}\n'.format(acut))
    for i in badmicrographs_as:
        diagfile.write('{0}\n'.format(i))
if rescut != 'SKIP':
    diagfile.write('## Micrographs thrown out for resolution > {0}\n'.format(rescut))
    for i in badmicrographs_res:
        diagfile.write('{0}\n'.format(i))
if pscut != 'SKIP':
    diagfile.write('## Micrographs thrown out for phaseshift > {0}\n'.format(pscut))
    for i in badmicrographs_ps:
        diagfile.write('{0}\n'.format(i))
culledfile = '{0}_culled.star'.format(thefile.split('.')[0])
alldata = open(culledfile,'r').readlines()
(astigdatesdic,resdatesdic,psdatadic) = get_time_stats(culledfile) 
astigmeans = running_total(astigdatesdic)
resmeans = running_total(resdatesdic)
if phaseplate == True:
    pstimedata = []
    pskeys = psdatesdic.keys()
    pskeys.sort()
    for i in pskeys:
        pstimedata.append(psdatesdic[i])
    
# standard calculations
if phaseplate == True:
    micrographs = get_stats_make_graphs(alldata,resmeans,astigmeans,pstimedata)
else:
    micrographs = get_stats_make_graphs_noPP(alldata,resmeans,astigmeans)
print('Finished!\nNew graphs are in micrograph_analysis_1.png\nNew starfile is {0}_culled.star'.format(thefile.split('.')[0]))
plt.close()
