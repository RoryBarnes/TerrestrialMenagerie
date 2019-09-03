#!/usr/local/bin/python3.7

# Script to run all vspace runs
import sys
import string
import subprocess as subp
import matplotlib.pyplot as plt
try:
    import vplot as vpl
except:
    print('Cannot import vplot -- please install')

# Check correct number of arguments
if (len(sys.argv) != 2):
    print('ERROR: Incorrect number of arguments.')
    print('Usage: '+sys.argv[0]+' <pdf | png>')
    exit(1)
if (sys.argv[1] != 'pdf' and sys.argv[1] != 'png'):
    print('ERROR: Unknown file format: '+sys.argv[1])
    print('Options are: pdf, png')
    exit(1)

# Number of dimensions
necc=10
nsemi=10

# Write vspace.in
vspace = open('vspace.in','w')
vspace.write('srcfolder  .\n')
vspace.write('destfolder data\n')
vspace.write('trialname  TideMen\n')
vspace.write('\n')
vspace.write('file   vpl.in\n')
vspace.write('\n')
vspace.write('file   star.in\n')
vspace.write('\n')
vspace.write('file   planet.in\n')
vspace.write('dEcc  [0,0.5,n'+repr(necc)+'] e\n')
vspace.write('dSemi [1e-3,0.1,n'+repr(nsemi)+'] a\n')
vspace.close()

# Now build input files
sys.stdout.write('Building directories...')
sys.stdout.flush()
cmd = 'vspace vspace.in'
subp.call(cmd, shell=True)
print('done.')

# Now run, analyze output and store for plotting
ecc=[0 for j in range(necc)]
semi=[0 for j in range(nsemi)]
heat=[[0 for j in range(nsemi)] for k in range(necc)]

result = subp.run("ls -d data/TideMen*", shell=True, stdout=subp.PIPE).stdout.decode('utf-8')
dirs=result.split()

# Dirs contains array of directories to run

iEcc=0
iSemi=0

for dir in dirs:
    if dir != "0":  # WTF?
        cmd = "cd "+dir+"; vplanet vpl.in >& output"
        subp.call(cmd, shell=True)
        # At this point the log file has been generated

        logfile=dir+'/TideMen.log'
        log=open(logfile,"r")

        print(dir)
        sys.stdout.flush()
        sys.stderr.flush()
        # Now search for planet's parameters
        found=0
        for line in log:
            words=line.split()
            if len(words) > 2:
                if (words[1] == "BODY:") and (words[2] == "planet"):
                    found=1
                if (words[0] == "(Eccentricity)") and (found == 1):
                    ecc[iEcc] = float(words[4])
                if (words[0] == "(SemiMajorAxis)") and (found == 1):
                    semi[iSemi] = float(words[4])/1.49597870700e11
                if (words[0] == "(SurfEnFluxEqtide)") and (found == 1):
                    heat[iEcc][iSemi] = float(words[10])
        iSemi += 1
        if (iSemi == nsemi):
        # New line in ecc
            iEcc += 1
            iSemi = 0

# Arrays ecc,obl,heat now contain the data to make the figure

plt.ylabel('Eccentricity',fontsize=20)
plt.xlabel('Semi-Major AXis (AU)',fontsize=20)
plt.tick_params(axis='both', labelsize=20)

#plt.xscale('log')
#plt.yscale('log')
plt.xlim(1e-3,0.1)
plt.ylim(0,0.5)

ContSet = plt.contour(semi,ecc,heat,5,colors='black',linestyles='solid',
                      levels=[0.04,2,300],linewidths=3,origin='lower')
plt.clabel(ContSet,fmt="%d",inline=True,fontsize=18)

plt.tight_layout()

base="TidalMenagerie"

if (sys.argv[1] == 'pdf'):
    file = base+'.pdf'
if (sys.argv[1] == 'png'):
    file = base+'.png'

plt.savefig(file)
