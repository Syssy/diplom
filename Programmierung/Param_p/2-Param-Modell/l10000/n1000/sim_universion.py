#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import numpy as np
import matplotlib.pyplot as plt
import time
#import statsmodels.api as sm
import scipy.stats as stats
import scipy
#import plotkram
#import simulation
import pickle


# Speichert alle interessanten Dinge einer Simulation ab
class Simulation():
        def __init__(self, ps, pm, length, number, counter):
            self.params = (ps, pm)
            self.length = length
            self.number = number
            self.times = counter
            #TODO Möglichkeit, andere Verteilungen zu berücksichtigen
            # berechne die most likeli params der inv-gauß-Verteilung
            self.mu, self.loc, self.scale = scipy.stats.invgauss.fit(self.times)
            # berechne Momente
            self.mean = np.mean(self.times)
	    self.variance = np.var(self.times)
	    self.skewness = scipy.stats.skew(self.times)
	    self.kurtosis = scipy.stats.kurtosis(self.times)
	    
	    
#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil):
    number = len(teilchenort)
 
   # print teilchen, number
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    
    #berechne neuen Zustand für die Teilchen
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
    while zeit < length:
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
    #pss = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    #pms = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    
    #pss=np.array([0.0012, 0.0013, 0.959, 0.9592])
    #pms=np.array([0.0012, 0.0013, 0.959, 0.9592])
    
    schrittweite = 0.00004
    p1 = np.arange(0.9985, 0.9995, schrittweite)
    p2 = np.arange(0.0005, 0.0015, schrittweite)
    pss = np.concatenate((p1, p2), axis = 0)
    pms = np.concatenate((p1, p2), axis = 0)

    testarray = np.array([[None]*len(pss)]*len(pms))
    
    for i in range(len(pss)):
        print "teste", round(pss[i],6), 'zeit', time.clock()-startzeit, ' '  
        for j in range(len(pms)):
            ps = pss[i]
            pm = pms[j]
            print ps, pm, '(', time.strftime("%d%b%Y_%H:%M:%S"), ') ',
            # Simulationen, die schon vorhanden sind, erst mal nicht neu machen
            # Daher vorher alles .p löschen oder verschieben, wenn neue Version
            mySim = None
            try:
                filename = 'Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p"
                datei = open(filename, 'rb')
                mySim = pickle.load(datei)
                datei.close()

		# Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
		if not mySim.params==(round(ps,6), round(pm,6)):
		    print "False:", mySim.params, (round(ps,6), round(pm,6))
		
                if (mySim.length != length) or (mySim.number != number) or (mySim.params != (round(ps,6), round(pm,6)) ):
		    mySim = Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
	    		   
		#Simulation mit gleichen Params, Länge der Strecke und Anzahl der Teilchen schon vorhanden
                # Also diese einfach übernehmen -> testarray   
                else :#mySim.length == length and mySim.number == number:
		    print "vorhanden", filename,
	  # Simulation mit diesen Params existiert nicht, daher neu machen
            except IOError:
		print "simuliere..."
                mySim = Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
            # Abgespeichert wird jetzt die Sim, entweder eine alte, falls verwertbar oder eine neue
            testarray[i][j]=mySim
            #Zwischenergebnisse abspeichern
            filename = 'Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p"
            with open(filename, 'wb') as datei:
                pickle.dump(mySim, datei)
                    
            
    # Die Liste mit allen für spätere Verwendung speichern, ist diese vorhanden, sind die ganzen .p im Prinzip hinfällig
    filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+".pickle"
    print filename 
    with open(filename, 'wb') as datei:
        pickle.dump(testarray, datei)

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
