#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import numpy as np
import matplotlib.pyplot as plt
import time
import statsmodels.api as sm
import scipy.stats as stats
import csv
import plotkram

startzeit = time.clock()

# Meine ganzen Variablen, Todo: Soll spaeter mal eingelesen werden
# Laenge der zu simulierenden Strecke
length = 100000
# Anzahl der zu simulierenden Teilchen
number = 10000
# Die Parameter (ps, pm) Damit man was zu vergleichen hat, mehrere davon
params = [(0.5, 0.5),(0.9, 0.5),(0.999, 0.999),(0.5, 0.9)]
# Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
counter = []
hilfscounter = []
# aktueller zustand:
mobile = True

#Ausgabe, welche Plots:
qq_Plot = False
fit_Plot = False
histogram_separate = True
histogram_spec = False

# Hauptschleife, hier wird simuliert
for (ps,pm) in params:
    zwischenzeit = time.clock()
    print "Teste jetzt: ", (ps, pm)#, time.clock()-startzeit
    hilfscounter = []
    for i in range(number):
        zzv = np.random.random(length)
       # if (i-1)% 1000 == 0:
       #     print "wieder 1000"
       #j sind die schon gegangenen Schritte
        j = 0
        mobile = True
        # init mit != ,da ja eigentlich auch nicht 100pro gleichzeitig
        timecounter = 0# +(0.1/number)*i
    
        while j < length:
            zz=random.random()
            #zz = zzv[timecounter%9967] #random.random()
           # print zz
            if (mobile and (zz > pm)) or (not mobile and (zz < ps)):
                mobile = False
            else:
                j = j+1
                mobile = True
            timecounter+=1
        hilfscounter.append(timecounter)
    # zählt anzahl durchgänge (= anzahl gezogener zufallszahlen)
    summe = (sum(hilfscounter))
    #print summe
    counter.append(hilfscounter)
    print time.clock()-zwischenzeit
#print counter
    
print "Ende Sim",(time.clock()- startzeit)

filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")
print filename

with open(filename, 'wb') as csvfile:
    mywriter = csv.writer(csvfile, delimiter=';')
    for c in counter:
        mywriter.writerow(c)

# ein Histogramm erstellen

plotkram.plot_histogram(filename, histogram_separate, histogram_spec,30)
plotkram.plot_qq(filename, qq_Plot, fit_Plot)

# Ende :)
print (time.clock()- startzeit)
