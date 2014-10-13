#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import numpy as np
import time
import scipy.stats as stats
import scipy
import plotkram
import simulation
import pickle
import matplotlib.pyplot as plt

#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil):
    number = len(teilchenort)
 
   # print teilchen, number
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    
    #berechne neuen Zustand für die Teilchen    
    # vorher mobil und es bleibe (zzv3, pm)
    # oder: war nicht mobil und bleibe nicht (invertiert zu oder)
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    # wenn mobil, addiere 1 zum Ort
    teilchenortneu = teilchenort + mobilneu
    
    return teilchenortneu, mobilneu


# simuliert für ps und pm alle teilchen
def simulate(ps, pm, length, teilchenort, teilchenmobil):
    # Hauptschleife, hier wird simuliert
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length/2:
        teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil)
        zeit += 1

    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil)
            zeit+=1        

        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]   
        #zähle (suminvert...) wie viele schon durch, hänge deren zeiten an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)

        # alle teilchen angekommen :)
        if len(teilchenort)< 1:
            #print "fertig"
            break

    #print time.clock()-startzeit
    return hilfscounter


def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 10000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    # Die Parameter (ps, pm) Damit man was zu vergleichen hat, mehrere davon
    schrittweite = 0.0001
    p1 = np.arange(0.9985, 0.9996, schrittweite)
    p2 = np.arange(0.0005, 0.0016, schrittweite)
    pss = np.concatenate((p2, p1), axis = 0)
    #pss = np.concatenate((pss, [0]), axis =0)
    pms = np.concatenate((p1, p2), axis = 0)
    #pms = np.concatenate((pms, [1]), axis =0)
    #print p1, len(p1), p2, len(p2)
    #print "pss ", pss, len(pss), "\n pms, ", pms, len(pms)
    
    pss=[0.999]
    pms=[0.999]
    #pss = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    #pms = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    
    ##testcounter = np.array([[None]*num_sim]*num_sim)
    #print testcounter, np.shape(testcounter)
    testarray = np.array([[None]*len(pss)]*len(pms))
    
    #print 'pss, pms ', pss, '\n', pms
     #print params
    # Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
    #counter = []
    simlist = []
    for i in range(len(pss)):
        print "teste", round(pss[i],6), 'zeit', time.clock()-startzeit, ' '  
        for j in range(len(pms)):
            ps = pss[i]
            pm = pms[j]
            #print ps, pm, ' ',
            #if (ps < 0.005 or ps > 0.995) and (pm < 0.005 or pm > 0.995):
            mySim = simulation.Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
            simlist.append(mySim)
            #counter.append(mySim.times)
            #testcounter.append(mySim.times)
            testarray[i][j]=mySim
            filename = 'Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p"
            with open(filename, 'wb') as datei:
                pickle.dump(mySim, datei)
               #  testarray[i][j]
    
    '''#print testarray
    for s in testarray:
        for t in s:
            if t:
                print t.times'''
            
    # Den Counter für spätere Verwendung zwischenspeichern,
    
    filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+".pickle"
    print filename
    
    #Ausgabe, welche Plots:
    qq_Plot = False
    fit_Plot = False
    histogram_separate = True
    histogram_spec = False
    
    with open(filename, 'wb') as datei:
        pickle.dump(testarray, datei)
  
    #plotkram.plot_file(filename, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    #plotkram.plot(simlist, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    #plotkram.plot_heatmap_from_file(filename, len(pss), "skewness")
    n, bins, patches = plt.hist(mySim.times, 50, normed=1, alpha=0.5 )
    plt.show()
    
    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
