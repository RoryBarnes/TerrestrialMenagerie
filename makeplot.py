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

# Number of dimensions
necc=100
nsemi=100
minecc=0
maxecc=0.1
minsemi=1e-3
maxsemi=0.05

# Category limits
vlim = 300         # Tidal Venus, W/^2
iolim = 2           # Super-Io
telim = 0.04        # Tidal Earth

# Check correct number of arguments
if (len(sys.argv) != 2):
    print('ERROR: Incorrect number of arguments.')
    print('Usage: '+sys.argv[0]+' <pdf | png>')
    exit(1)
if (sys.argv[1] != 'pdf' and sys.argv[1] != 'png'):
    print('ERROR: Unknown file format: '+sys.argv[1])
    print('Options are: pdf, png')
    exit(1)

AUM = 1.49597870700e11

# Write vspace.in
# Note the plotting expects eccentricity to be first parameter in the data
# directory. Make sure the dimensions work for the plot.
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
vspace.write('dEcc  ['+repr(minecc)+','+repr(maxecc)+',n'+repr(necc)+'] e\n')
vspace.write('dSemi ['+repr(minsemi)+','+repr(maxsemi)+',n'+repr(nsemi)+'] a\n')
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
hzem=[0 for j in range(necc)]
hzmoistg=[0 for j in range(necc)]
hzmaxg=[0 for j in range(necc)]
hzrv=[0 for j in range(necc)]
heat=[[0 for j in range(nsemi)] for k in range(necc)]
instell=[[0 for j in range(nsemi)] for k in range(necc)]
totflux = [[0 for j in range(nsemi)] for k in range(necc)]

# Category boundaries
tv=[-1 for j in range(necc)]
venus=[-1 for j in range(necc)]
io=[-1 for j in range(necc)]
te=[-1 for j in range(necc)]
snow=[0 for j in range(necc)]
se=[0 for j in range(necc)]
venus=[0 for j in range(necc)]
xmax=[maxsemi for j in range(necc)]

#result = subp.run("ls -d data/TideMen*", shell=True, stdout=subp.PIPE).stdout.decode('utf-8')
#dirs=result.split()

dirs = ['data/TideMene' for j in range(necc*nsemi)]

# Dirs contains array of directories to run

iEcc=0
iSemi=0

for dir in dirs:
    if dir != "0":  # WTF?
        if (iEcc < 10):
            epad = "0"
        else:
            epad = ""
        if (iSemi < 10):
            apad = "0"
        else:
            apad = ""
        dir = dir + epad+ repr(iEcc)+'_a'+apad+repr(iSemi)

        cmd = "cd "+dir+"; vplanet vpl.in >& output"
        subp.call(cmd, shell=True)
        # At this point the log file has been generated

        logfile=dir+'/TideMen.log'
        log=open(logfile,"r")

        print(dir)
        sys.stdout.flush()
        # Now search for planet's parameters
        found1=0
        found2=0
        for line in log:
            words=line.split()
            if len(words) > 2:
                if (words[1] == "BODY:") and (words[2] == "star"):
                    found1=1
                if (words[0] == "(HZLimRecVenus)") and (found1 == 1):
                    hzrv[iEcc] = float(words[7])/AUM
                if (words[0] == "(HZLimMoistGreenhouse)") and (found1 == 1):
                    hzmoistg[iEcc] = float(words[7])/AUM
                if (words[0] == "(HZLimMaxGreenhouse)") and (found1 == 1):
                    hzmaxg[iEcc] = float(words[7])/AUM
                if (words[0] == "(HZLimEarlyMars)") and (found1 == 1):
                    hzem[iEcc] = float(words[7])/AUM

                if (words[1] == "BODY:") and (words[2] == "planet"):
                    found2=1
                if (words[0] == "(Eccentricity)") and (found2 == 1):
                    ecc[iEcc] = float(words[4])
                if (words[0] == "(SemiMajorAxis)") and (found2 == 1):
                    semi[iSemi] = float(words[4])/AUM
                if (words[0] == "(SurfEnFluxEqtide)") and (found2 == 1):
                    heat[iEcc][iSemi] = float(words[10])
                if (words[0] == "(Instellation)") and (found2 == 1):
                    instell[iEcc][iSemi] = float(words[6])

        # Now calculate Semi's of each category boundary
        totflux[iEcc][iSemi] = instell[iEcc][iSemi] + heat[iEcc][iSemi]

    # Done, move on to next semi-major axis
    iSemi += 1
    if (iSemi == nsemi):
        # If we've reached the end of semis, increment ecc and reset semi
        iEcc += 1
        iSemi = 0

# Done with simualtiones, Now find transitions
for iEcc in range(necc):
    for iSemi in range(nsemi):
        if (semi[iSemi] == minsemi):
            heat0 = heat[iEcc][iSemi]
            totflux0 = totflux[iEcc][iSemi]
        else:
            if (heat0 > vlim) and (heat[iEcc][iSemi] <= vlim):
                # Tidal Venus limit
                tv[iEcc] = semi[iSemi]
            if (totflux0 > vlim) and (totflux[iEcc][iSemi] <= vlim):
                venus[iEcc] = semi[iSemi]
            if (heat0 > iolim) and (heat[iEcc][iSemi] <= iolim):
                io[iEcc] = semi[iSemi]
            if (heat0 > telim) and (heat[iEcc][iSemi] <= telim):
                te[iEcc] = semi[iSemi]

            heat0 = heat[iEcc][iSemi]
            totflux0 = totflux[iEcc][iSemi]

    # Through all semis for this ecc
    if (tv[iEcc] == -1):
        tv[iEcc] = maxsemi
    if (venus[iEcc] == -1):
        venus[iEcc] = maxsemi
    if (io[iEcc] == -1):
        io[iEcc] = maxsemi
    if (te[iEcc] == -1):
        te[iEcc] = maxsemi

# Now adjust HZ lims to account for eccentricity
for iEcc in range(necc):
    hzrv[iEcc] = hzrv[iEcc]/((1-ecc[iEcc]**2)**0.25)
    hzmoistg[iEcc] = hzmoistg[iEcc]/((1-ecc[iEcc]**2)**0.25)
    hzmaxg[iEcc] = hzmaxg[iEcc]/((1-ecc[iEcc]**2)**0.25)
    hzem[iEcc] = hzem[iEcc]/((1-ecc[iEcc]**2)**0.25)

    # Assumes minecc = 0!
    if (iEcc == 0):
        se[iEcc]=hzmaxg[iEcc]
        snow[iEcc]=hzmaxg[iEcc]
    else:
        snow[iEcc] = max(hzmaxg[iEcc],te[iEcc])
        se[iEcc] = max(hzmaxg[iEcc],io[iEcc])

# Arrays ecc,obl,heat now contain the data to make the figure

plt.ylabel('Eccentricity',fontsize=20)
plt.xlabel('Semi-Major Axis (AU)',fontsize=20)
plt.tick_params(axis='both', labelsize=20)

#plt.xscale('log')
#plt.yscale('log')
plt.xlim(minsemi,maxsemi)
plt.ylim(minecc,maxecc)

#ContSet = plt.contour(semi,ecc,heat,5,colors='black',linestyles='solid',
#                      levels=[0.04,2,300],linewidths=3,origin='lower')
#plt.clabel(ContSet,fmt="%d",inline=True,fontsize=18)

# Now fill in with colors
plt.contourf(semi,ecc,heat,5,levels=[2,300],colors=vpl.colors.orange)
plt.fill_betweenx(ecc,0,hzmoistg,color=vpl.colors.purple)
plt.contourf(semi,ecc,heat,5,levels=[300,1e100],colors=vpl.colors.red)
plt.contourf(semi,ecc,heat,5,levels=[0.04,2],colors=vpl.colors.dark_blue)
plt.contourf(semi,ecc,heat,5,levels=[0,0.04],colors='green')
#plt.contourf(semi,min(hmaxg,))
plt.fill_betweenx(ecc,se,xmax,color=vpl.colors.pale_blue)
plt.fill_betweenx(ecc,snow,xmax,color='gray')

plt.plot(hzrv,ecc,linestyle='dashed',color='k')
plt.plot(hzmoistg,ecc,linestyle='solid',color='k')
plt.plot(hzem,ecc,linestyle='dashed',color='k')
plt.plot(hzmaxg,ecc,linestyle='solid',color='k')

plt.tight_layout()

base="TerrestrialMenagerie"

if (sys.argv[1] == 'pdf'):
    file = base+'.pdf'
if (sys.argv[1] == 'png'):
    file = base+'.png'

plt.savefig(file)
