#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein erster Versuch, das 1-Param-Modell 1a umzusetzen

import random
import numpy as np
import matplotlib.pyplot as plt
import time
import statsmodels.api as sm
import scipy.stats as stats
import csv

startzeit = time.clock()

# Meine ganzen Variablen, Todo: Soll später mal eingelesen werden
# Länge der zu simulierenden Strecke
length = 10000
# Anzahl der zu simulierenden Teilchen
number = 5000
# Der Parameter. Damit man was zu vergleichen hat, mehrere davon
single_params = (0.001, 0.0009, 0.00105, 0.0099)
# Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
counter = []
hilfscounter = []
# aktueller zustand:
mobil = True

#Ausgabe, welche Plots:
qq_Plot = False
fit_qq_Plot = True
histogram_separate = True
histogram_spec =True

# Hauptschleife, hier wird simuliert
for p in single_params:
    print "Teste jetzt: ", p, time.clock()-startzeit
    hilfscounter = []
    for i in range(number):
        j = 0
        # init mit != ,da ja eigentihc auch nicht 100pro gleichzeitig
        timecounter = 0# +(0.1/number)*i
        while j < length:
            zz = random.random()
            if mobil and (zz < p) or not mobil and (zz > p):
                mobil = False
            else:
                mobil = True
                j+=1
            timecounter+=1
        hilfscounter.append(timecounter)
    counter.append(hilfscounter)
#print counter
    
print "Ende Sim",(time.clock()- startzeit)

with open('single1a.csv', 'wb') as csvfile:
    mywriter = csv.writer(csvfile, delimiter=';')
    for c in counter:
        mywriter.writerow(c)

# ein Histogramm erstellen
if histogram_separate:
    num_bins = 50
    #meine_range= (length, length+ length*(1/min(single_params)))
    meine_range = (length, 4*length)
    meine_range = None
    print min(single_params), meine_range
    figg = plt.figure()
    ax = figg.add_subplot(221)
    n, bins, patches = plt.hist(counter[0], num_bins, range = meine_range, normed=1, alpha=0.5 )
    ax = figg.add_subplot(222)
    n, bins, patches = plt.hist(counter[1], num_bins, range = meine_range, normed=1, alpha=0.5 )
    ax = figg.add_subplot(223)
    n, bins, patches = plt.hist(counter[2], num_bins, range = meine_range, normed=1, alpha=0.5 )
    ax = figg.add_subplot(224)
    n, bins, patches = plt.hist(counter[3], num_bins, range = meine_range, normed=1, alpha=0.5 )

# ein Histogramm erstellen
if histogram_spec:
    num_bins = 50
    meine_range= (length, length+ length*(1/min(single_params)))
    #print min(single_params), meine_range
    figg = plt.figure()
    n, bins, patches = plt.hist(counter[0], num_bins, normed=1, alpha=0.5 )
    n, bins, patches = plt.hist(counter[1], num_bins, normed=1, alpha=0.5 )
    n, bins, patches = plt.hist(counter[2], num_bins, normed=1, alpha=0.5 )
    n, bins, patches = plt.hist(counter[3], num_bins, normed=1, alpha=0.5 )

    print "Hist erstellt",(time.clock()-startzeit)

vergleich = stats.invgauss

# Und einen qq-Plot erstellen
if qq_Plot:
    fig = plt.figure()
    ax = fig.add_subplot(221)
    sm.qqplot (np.array(counter[0]), vergleich, distargs= (0.005,),  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[0]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(222)
    sm.qqplot (np.array(counter[1]), vergleich, distargs= (0.005,),  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[1]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(223)
    sm.qqplot (np.array(counter[2]), vergleich, distargs= (0.005,),  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[2]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(224)
    sm.qqplot (np.array(counter[3]), vergleich, distargs= (0.005,),  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[3]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    print "qqplot erstellt", (time.clock()-startzeit)

if fit_qq_Plot:
    fig = plt.figure()
    ax = fig.add_subplot(221)
    sm.qqplot (np.array(counter[0]), vergleich, fit = True,  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[0]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(222)
    sm.qqplot (np.array(counter[1]), vergleich, fit = True,  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[1]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(223)
    sm.qqplot (np.array(counter[2]), vergleich, fit = True,  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[2]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    ax = fig.add_subplot(224)
    sm.qqplot (np.array(counter[3]), vergleich, fit = True,  line = 'r', ax =ax)
    txt = ax.text(-1.8, 3500, str(single_params[3]) ,verticalalignment='top')
    txt.set_bbox(dict(facecolor='k', alpha=0.1))
    print "qqplot erstellt", (time.clock()-startzeit)

plt.show()

# Ende :)
print (time.clock()- startzeit)
