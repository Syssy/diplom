#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

# für's profiling wurden viele der methoden noch mal aufgespalten, damit ich sehe, wo sich das programm am längsten aufhält

import random
import numpy as np
#import matplotlib.pyplot as plt
import time
#import statsmodels.api as sm
import scipy.stats as stats
import scipy
#import plotkram
#import simulation
import pickle


# Speichert alle interessanten Dinge einer Simulation ab
'''class Simulation():
        def __init__(self, ps, pm, length=0, number=0, counter=[0,0,1,0,0]):
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
	    
	   # print self.times'''
       
def berechneKrams(times):
    #print times
    #mu, loc,scale = scipy.stats.invgauss.fit(times)
    # berechne Momente
    mean = np.mean(times)
    variance = np.var(times)
    skewness = scipy.stats.skew(times)
    kurtosis = scipy.stats.kurtosis(times)
	    
	
def ss1(teilchenmobil, zzv2, zzv3):
    return  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    
def ss2 (teilchenort, mobilneu):
    return teilchenort + mobilneu
	
#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil, number):
    #number = len(teilchenort)
 
   # print teilchen, number
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    
    #berechne neuen Zustand für die Teilchenzzv
    mobilneu = ss1(teilchenmobil, zzv2, zzv3)
    teilchenortneu = ss2(teilchenort, mobilneu)
    #mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    # wenn mobil, addiere 1 zum Ort
    #teilchenortneu = teilchenort + mobilneu
    
    return teilchenortneu, mobilneu


# simuliert für ps und pm alle teilchen
def simulate1(ps, pm, length, teilchenort, teilchenmobil):
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    number = len(teilchenort)
    
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length:
        teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
        zeit += 1

    hilfscounter = simulate2(ps, pm, length, teilchenort, teilchenmobil, zeit)
    return hilfscounter

def aufraumen(hilfscounter, teilchenort, teilchenmobil, length, zeit):
    # d ist bitmaske aller aktuell angekommenen Teilchen
    d = teilchenort <= length
    # die beiden aktualisieren (rauswerfen aller fertigen teilchen); es bleiben die übrig, deren ort unterhalb der length (=1 in d) ist
    teilchenort = teilchenort[d]
    teilchenmobil = teilchenmobil[d]   
    #zähle (sum invert...) wie viele schon durch sind, hänge für jedes die aktuelle Zeit an
    for j in range (np.sum(np.invert(d))):
        hilfscounter.append(zeit)
        
    return hilfscounter, teilchenort, teilchenmobil


def simulate2(ps, pm, length, teilchenort, teilchenmobil, zeit):
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []

    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
	number = len(teilchenort)
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil,number)
            zeit+=1        

        hilfscounter, teilchenort, teilchenmobil = aufraumen(hilfscounter, teilchenort, teilchenmobil, length, zeit)
        # alle teilchen angekommen :)
        if len(teilchenort)< 1:
            #print "fertig"
            break

    #print time.clock()-startzeit
    #print hilfscounter
    return hilfscounter


def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 10000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    
    schrittweite = 0.0001
    p1 = np.arange(0.9985, 0.9995, schrittweite)
    p2 = np.arange(0.00003, 0.00018, schrittweite)
    #pms = np.concatenate((p1, p2), axis = 0)
    #pss = np.concatenate((p1, p2), axis = 0)
    pss = p1
    pms = p1
    print pms, pss
    testarray = np.array([[None]*len(pss)]*len(pms))
    
    for i in range(len(pss)):
        print "teste", round(pss[i],6), 'zeit', time.clock()-startzeit, ' '  
        for j in range(len(pms)):
            ps = pss[i]
            pm = pms[j]
            #print ps, pm, '(', time.strftime("%d%b%Y_%H:%M:%S"), ') ',
            # Simulationen, die schon vorhanden sind, erst mal nicht neu machen
            # Daher vorher alles .p löschen oder verschieben, wenn neue Version
            mySim = None
            #Nur speichern, wenn neu simuliert wurde
            speichern = False
            
	    #Testen, ob Simulation mit gleichen Params, Länge der Strecke und Anzahl der Teilchen schon vorhanden
            #Dann diese einfach übernehmen -> testarray enthält am Ende alle Simulationen, egal ob alt oder neu 
	    try:
	        filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".pp"
	        with open (filename, 'rb') as datei:
		    #mySim = pickle.load(datei)
		    #soll nicht sein! Rundungsfehler, Genauigkeit?! Kommt auch bisher nicht vor
		    #if not mySim.params==(round(ps,6), round(pm,6)):
			#print "Bullshitkram:", mySim.params, (round(ps,6), round(pm,6))
			
		    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
		    if False:#not mySim.length == length or not mySim.number == number:
			print 'neue Sim nötig, da l/n falsch',
			speichern = True
			# neue Sim nötig
			# den lange brauchenden Bereich außer Acht lassen, dafür dann ein fake einsetzen
		        if ps < 0.5 or pm > 0.5:
			    print "neue Sim",
			    simulate(ps, pm, length, np.zeros(number), np.array([True]*number))
			else:
			    print "fake, do nothing"

	    # Simulation mit diesem Namen existiert nicht, daher neu machen
	    except (IOError, EOFError):
	        speichern = True
	        # Wie oben den Bereich ignorieren
	        if ps < 0.5 or pm > 0.5:
		    #print "s,dnv",
		    simulate1(ps, pm, length, np.zeros(number), np.array([True]*number))
	            #berechneKrams(simulate1(ps, pm, length, np.zeros(number), np.array([True]*number)))
	        #else:
		 #   print "fake, nicht vorhanden",
		    
	    # *.p mit der Sim abspeichern für spätere Verwendung    
	    if speichern:
	        filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p"
	       # with open(filename, 'wb') as datei:
		#    pickle.dump(mySim, datei)		    
	 
            # ins array kommt jetzt die Sim, entweder eine alte, falls verwertbar oder eine neue
            testarray[i][j]=mySim

                                
    # Die Liste mit allen für spätere Verwendung speichern, ist diese vorhanden, sind die ganzen .p im Prinzip hinfällig
    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+'_'+str(min(p1))+str(max(p1))+ str(schrittweite)+".pickle"
    #print filename 
    #with open(filename, 'wb') as datei:
    #    pickle.dump(testarray, datei)

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
