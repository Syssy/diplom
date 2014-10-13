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
        def __init__(self, ps, pm, length=0, number=0, counter=[0,0,1,0,0]):
	    print "erstelle Sim",
            self.params = (ps, pm)
            self.length = length
            self.number = number
            self.times = counter
            #TODO Möglichkeit, andere Verteilungen zu berücksichtigen
            # berechne die most likeli params der inv-gauß-Verteilung
            #print "berechne"
            self.mu, self.loc, self.scale = scipy.stats.invgauss.fit(self.times)
            # berechne Momente
            self.mean = np.mean(self.times)
	    self.variance = np.var(self.times)
	    #print "..", self.times
	    self.skewness = scipy.stats.skew(self.times)
	    #print "sk"
	    self.kurtosis = scipy.stats.kurtosis(self.times)
	    #print "..."
	    
	   # print self.times
       
	    
	    
#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil, number):
    #print "ss"
 
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
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    
    number = len(teilchenort)
    
    pm_start = pm/2
    
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length:
	while pm_start < pm:
	    teilchenort, teilchenmobil = simulatestep(ps, pm_start, teilchenort, teilchenmobil, number)
            zeit += 1
            pm_start += pm/length
           # print pm_start,
	teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
        zeit += 1            
    print "Teil2"
    aktnumber = number
    #Teil 2: Ab jetzt können Teilchen fertig sein
    while aktnumber > number/2:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, aktnumber)
            zeit+=1       
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen), es bleiben die übrig, deren ort unterhalb der length ist (d=1)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]  
        #zähle (sum invert...) wie viele schon durch sind, hänge so oft die aktuelle zeit an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)
        # wenn welche fertig sind, verringert sich die number 
        aktnumber = len(teilchenort)
    
    print "Teil3"
    pm_akt = pm
    ps_akt = ps
    #Teil 3: Ab jetzt ist so viel Platz, dass ich wieder öfter hängen bleibe, aber auch schneller wieder los komme
    while True:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, aktnumber)
            zeit+=1       
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen), es bleiben die übrig, deren ort unterhalb der length ist (d=1)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]  
        #zähle (sum invert...) wie viele schon durch sind, hänge so oft die aktuelle zeit an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)
        # wenn welche fertig sind, verringert sich die number 
        aktnumber = len(teilchenort)
        
        ps_akt = max((ps_akt - ps/length), (ps-ps/10),0)
        pm_akt = max((pm_akt - pm/length), (pm-pm/20),0)
        
        #print ps, ps_akt, pm, pm_akt, "   ", pm-pm/10
       
        # alle teilchen angekommen :)
        
        if aktnumber < 1:
            print "fertig"
            break

    #print time.clock()-startzeit
    return hilfscounter

def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 10000
    # Anzahl der zu simulierenden Teilchen
    number = 10000
    
    # Die Parameter (ps, pm) Damit man was zu vergleichen hat, mehrere davon    
    #pss = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    #pms = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    
    #pss=np.array([0.0012, 0.0013, 0.959, 0.9592])
    #pms=np.array([0.0012, 0.0013, 0.959, 0.9592])
    
    schrittweite = 0.0001
    p1 = np.arange(0.9985, 0.9995, schrittweite)
    p2 = np.arange(0.00003, 0.00018, schrittweite)
    #pms = np.concatenate((p1, p2), axis = 0)
    #pss = np.concatenate((p1, p2), axis = 0)
    pss = p1
    pms = p1
    
    pss = [0.999, 0.9995]
    pms = [0.999, 0.9999]
    
    pps = [(0.999, 0.999, 2), (0.999, 0.999, 1), (0.998, 0.9995, 0.4), (0.9985, 0.9995, 0.5)]
   
    #print pms, pss, pvs
    testarray = np.array([[None]*len(pss)]*len(pms))
    #testarray = np.array([None] * len(pps))
    #print testarray, np.shape(testarray)
    
    for i in range(len(pss)):
        print "\n teste", round(pss[i],6), 'zeit', time.clock()-startzeit, ' '  
        for j in range(len(pms)):
		ps = pss[i]
		pm = pms[j]	      
		print ps, pm, '(', time.strftime("%d%b%Y_%H:%M:%S"), ') ',
		# Simulationen, die schon vorhanden sind, erst mal nicht neu machen
		# Daher vorher alles .p löschen oder verschieben, wenn neue Version
		mySim = None
		#Nur speichern, wenn neu simuliert wurde
		speichern = False
		
		#Testen, ob Simulation mit gleichen Params, Länge der Strecke und Anzahl der Teilchen schon vorhanden
		#Dann diese einfach übernehmen -> testarray enthält am Ende alle Simulationen, egal ob alt oder neu 
		try:
		    #TODO hier wird noch auf *.pp getestet, bis die Sim so gut sind, dass ich wieder massensims erstellen kann!
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".pp"
		    with open (filename, 'rb') as datei:
			mySim = pickle.load(datei)
			#soll nicht sein! Rundungsfehler, Genauigkeit?! Kommt auch bisher nicht vor
			if not mySim.params==(round(ps,6), round(pm,6)):
			    print "Bullshitkram:", mySim.params, (round(ps,6), round(pm,6))
			    
			# Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
			if not mySim.length == length or not mySim.number == number:
			    print 'neue Sim nötig, da l/n falsch',
			    speichern = True
			    # neue Sim nötig
			    # den lange brauchenden Bereich außer Acht lassen, dafür dann ein fake einsetzen
			    if ps < 0.5 or pm > 0.5:
				print "neue Sim",
				mySim = Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
			    print mySim.times    
			if mySim.times == [0,0,1,0,0]:
				print "kein fake, sim..."
				mySim = Simulation(round(ps, 6), round(pm,6), length, number,simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))

		    
		# Simulation mit diesem Namen existiert nicht, daher neu machen
		except (IOError, EOFError):
		    speichern = True
		    # Wie oben den Bereich ignorieren
		    if ps < 0.5 or pm > 0.5:
			print "simuliere, da nicht vorhanden"
			mySim = Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
		    else:
			print "fake, nicht vorhanden",
			mySim = Simulation(round(ps, 6), round(pm,6), length, number)
		    
		# *.p mit der Sim abspeichern für spätere Verwendung    
		if speichern:
		    #print "speichern"
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6)) + ".p"
		    with open(filename, 'wb') as datei:
			pickle.dump(mySim, datei)		    
	    
		# ins array kommt jetzt die Sim, entweder eine alte, falls verwertbar oder eine neue
		
                testarray[j][i]=mySim
                #testarray[i]=mySim
		#print mySim.times

                                
    # Die Liste mit allen für spätere Verwendung speichern, ist diese vorhanden, sind die ganzen .p im Prinzip hinfällig
    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+'_'+str(min(p1))+str(max(p1))+ str(schrittweite)+".pickle"
    print filename 
    with open(filename, 'wb') as datei:
        pickle.dump(testarray, datei)

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
