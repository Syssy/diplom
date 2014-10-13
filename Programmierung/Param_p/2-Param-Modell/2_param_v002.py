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
import simulation
import pickle


# Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil):
    number = len(teilchenort)
 
   # print teilchen, number
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    
    '''
    #für Testzwecke: Alle Fälle erstellen
    teilchenmobil = [True, True, True, True, False, False, False, False]
    zzv2 = [True, True, False, False, True, True, False, False]
    zzv3 = [True, False, True, False, True, False, True, False]'''
       
    #print '\n', zzv, 'ZZ, \n', teilchenmobil, 'teilchen aktuell \n', zzv2, ' stay stationary\n', zzv3, " stay mobile \n"
    #berechne neuen Zustand für die Teilchen
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    #print mobilneu, 'neu \n'
    #print teilchenort
    # wenn mobil, addiere 1 zum Ort
    teilchenortneu = teilchenort + mobilneu
    #print teilchenortneu
    
    return teilchenortneu, mobilneu


# simuliert für ps und pm alle teilchen
def simulate(ps, pm, length, teilchenort, teilchenmobil):
    #print teilchenort, teilchenmobil
    # Hauptschleife, hier wird simuliert
    startzeit = time.clock()
    print "Teste jetzt: ", round(ps,5), round (pm,5)
    hilfscounter = []
    zeit = 0
    
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length:
        teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil)
        zeit += 1

    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
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
   # print "ort", teilchenort, teilchenmobil
    print time.clock()-startzeit
    return hilfscounter

def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, Todo: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 100000
    # Anzahl der zu simulierenden Teilchen
    number = 50000
    
    # Die Parameter (ps, pm) Damit man was zu vergleichen hat, mehrere davon
    pms = np.arange(0.9995, 0.99995, 0.00001) 
    #pms = np.arange(0.9997, 0.99995, 0.000001)
    pss = np.arange(-0.00007, 0.0005, 0.000001)
    #print pss, '\n', pms
    params = [(0.99907, 0.99965), (0.99937, 0.99955), (0.9994, 0.9996), (0.99955, 0.99992)]
              #,(0.997, 0.9975), (0.9975, 0.997), (0.9985, 0.999), (0.999, 0.9985)]

    #print params
    # Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
    counter = []
    simlist = []
    for x in range(3):
        pm = random.choice(pms)
        ps = pm - random.choice(pss)
        if ps > 0.99999 :
            print "bam!", ps
            ps = 0.99995
        #print ps, pm
    for ps, pm in params:
        #ps = 0.9994 
        #pm = ps-0.0004*x
        mySim = simulation.Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
        simlist.append(mySim)
        counter.append(mySim.times)
    #print counter
    # Den Counter für spätere Verwendung zwischenspeichern,
    
    #filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+".pickle"
    #print filename
    
    #Ausgabe, welche Plots:
    qq_Plot = True
    fit_Plot = True
    histogram_separate = True
    histogram_spec = True
    
    #with open(filename, 'wb') as datei:
    #    pickle.dump(simlist, datei)
    
    '''# Und die Ausgabe
    with open(filename, 'wb') as csvfile:
        mywriter = csv.writer(csvfile, delimiter=';')
        for c in counter:
            mywriter.writerow(c)
        
    plotkram.plot_histogram(filename, histogram_separate, histogram_spec,30)
    plotkram.plot_qq(filename, qq_Plot, fit_Plot)'''
    #plotkram.plot_file(filename, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    plotkram.plot(simlist, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
