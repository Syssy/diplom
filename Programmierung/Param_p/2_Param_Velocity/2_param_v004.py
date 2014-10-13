#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen und dabei einen Geschwindigkeitsfaktor mit rein zu bringen
# ps ist Wkeit station�r zu bleiben, wenn ich es schon bin
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
        def __init__(self, ps, pm, pv = 1, length=0, number=0, counter=[0,0,1,0,0]):
	    print "erstelle Sim",
            self.params = (ps, pm, pv)
            self.length = length
            self.number = number
            self.times = counter
            #TODO M�glichkeit, andere Verteilungen zu ber�cksichtigen
            #TODO Nicht unbedingt beim Sim berechnen, kostet Zeit
            # berechne die most likeli params der inv-gau�-Verteilung
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
       
	    
	    
#Simuliert einen Schritt f�r alle Teilchen
# ps, pm sind die bekannten Params, pv hat dann irgendwie TODO Einfluss auf die vel
# Es existieren noch mehrere M�glichkeiten, das hier umzusetzen
def simulatestep(ps, pm, pv, teilchenort, teilchenmobil, number, vel):
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
        #print "ss"
   # print teilchen, number
    #zzvVel = np.random.randint(-1,2, size=number)
   # zzvVel2 = np.random.random(number)
    
    #zzvVel3 = (zzvVel2 < pv) * zzvVel
    #print zzvVel
    #berechne neuen Zustand f�r die Teilchen# bin mobil, wenn
    # vorher mobil und es bleibe (zzv3, pm)
    # oder: war nicht mobil und bleibe nicht (invertiert zu oder)
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    
    #vel = vel + zzvVel3 * mobilneu
    #vel = vel * mobilneu
    
    
    #print vel
    
    #np.clip(vel, 0, 12, vel)
    
    #print "vel, ss", vel
    
    # wenn mobil, addiere 1 zum Ort
    teilchenortneu = teilchenort + vel*mobilneu
    
    return teilchenortneu, mobilneu, vel


# simuliert f�r ps und pm alle teilchen
def simulate(ps, pm, pv, length, teilchenort, teilchenmobil):
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    
    number = len(teilchenort)
    vel = np.ones(number)
    vel = vel * pv
    #print vel
    #Teil 1: Sim bis L�nge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length/100:
        teilchenort, teilchenmobil, vel = simulatestep(ps, pm, pv, teilchenort, teilchenmobil, number, vel)
        zeit += 1
    #print "vel nach teil 1", vel
    #print "teilchenort" , teilchenort, len(teilchenort)
    #time.sleep(2)
    #Teil 2: Ab jetzt k�nnen Teilchen fertig sein
    while True:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil, vel = simulatestep(ps, pm, pv, teilchenort, teilchenmobil, number, vel)
            zeit+=1        
        #print "vel", vel
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen), es bleiben die �brig, deren ort unterhalb der length ist (d=1)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]  
        vel = vel[d]
        #z�hle (sum invert...) wie viele schon durch sind, h�nge so oft die aktuelle zeit an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)
        # wenn welche fertig sind, verringert sich die number 
        number = len(teilchenort)
        # alle teilchen angekommen :)
        if number < 5:
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
    
    pss = [0.9999]
    pms = [0.9999]
    pvs = [0.003, 0.005, 0.001, 0.008]
    
    pps = [(0.999, 0.999, 2), (0.999, 0.999, 1), (0.998, 0.9995, 0.4), (0.9985, 0.9995, 0.5)]
   
    #print pms, pss, pvs
    #testarray = np.array([[[None]*len(pss)]*len(pms)]*len(pvs))
    testarray = np.array([None] * len(pps))
    #print testarray, np.shape(testarray)
    
    '''for i in range(len(pss)):
        print "\n teste", round(pss[i],6), 'zeit', time.clock()-startzeit, ' '  
        for j in range(len(pms)):
	    for k in range(len(pvs)):
		ps = pss[i]
		pm = pms[j]
		pv = pvs[k]'''
    for i in range(len(pps)):
		ps, pm, pv = pps[i]	      
		print ps, pm, '(', time.strftime("%d%b%Y_%H:%M:%S"), ') ',
		# Simulationen, die schon vorhanden sind, erst mal nicht neu machen
		# Daher vorher alles .p l�schen oder verschieben, wenn neue Version
		mySim = None
		#Nur speichern, wenn neu simuliert wurde
		speichern = False
		
		#Testen, ob Simulation mit gleichen Params, L�nge der Strecke und Anzahl der Teilchen schon vorhanden
		#Dann diese einfach �bernehmen -> testarray enth�lt am Ende alle Simulationen, egal ob alt oder neu 
		try:
		    #TODO hier wird noch auf *.pp getestet, bis die Sim so gut sind, dass ich wieder massensims erstellen kann!
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+"_" + str(pv)+ ".p"
		    with open (filename, 'rb') as datei:
			mySim = pickle.load(datei)
			#soll nicht sein! Rundungsfehler, Genauigkeit?! Kommt auch bisher nicht vor
			if not mySim.params==(round(ps,6), round(pm,6), pv):
			    print "Bullshitkram:", mySim.params, (round(ps,6), round(pm,6))
			    
			# Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da L�nge/Anzahl verschieden
			if not mySim.length == length or not mySim.number == number:
			    print 'neue Sim n�tig, da l/n falsch',
			    speichern = True
			    # neue Sim n�tig
			    # den lange brauchenden Bereich au�er Acht lassen, daf�r dann ein fake einsetzen
			    if ps < 0.5 or pm > 0.5:
				print "neue Sim",
				mySim = Simulation(round(ps, 6), round(pm,6), pv, length, number, simulate(ps, pm, pv, length, np.zeros(number), np.array([True]*number)))
			    print mySim.times  
			# wof�r das denn? aaaaarrrgg! Kommentieren, Elly!  
			# da muss eigentlich eine fake sim hin... bei der Abfrage teste ich darauf, ob es bereits eine fakesim hierf�r gibt, das kommt jetzt erst mal raus, bis ich wei�, was das soll
			#if mySim.times == [0,0,1,0,0]:
			#	print "kein fake, sim..."
			#	mySim = Simulation(round(ps, 6), round(pm,6), pv, length, number,simulate(ps, pm, pv, length, np.zeros(number), np.array([True]*number)))
		    
		# Simulation mit diesem Namen existiert nicht, daher neu machen
		except (IOError, EOFError):
		    speichern = True
		    # Wie oben den Bereich ignorieren
		    if ps < 0.5 or pm > 0.5:
			print "simuliere, da nicht vorhanden"
			mySim = Simulation(round(ps, 6), round(pm,6), pv, length, number, simulate(ps, pm, pv, length, np.zeros(number), np.array([True]*number)))
		    else:
			print "fake, nicht vorhanden",
			mySim = Simulation(round(ps, 6), round(pm,6), pv, length, number)
		    
		# *.p mit der Sim abspeichern f�r sp�tere Verwendung    
		if speichern:
		    #print "speichern"
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+"_"+str(pv) + ".p"
		    with open(filename, 'wb') as datei:
			pickle.dump(mySim, datei)		    
	    
		# ins array kommt jetzt die Sim, entweder eine alte, falls verwertbar oder eine neue
		
                #testarray[k][j][i]=mySim
                testarray[i]=mySim
                #print k, j, i
		#print mySim.times

                                
    # Die Liste mit allen f�r sp�tere Verwendung speichern, ist diese vorhanden, sind die ganzen .p im Prinzip hinf�llig
    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+'_'+str(min(p1))+str(max(p1))+ str(schrittweite)+".pickle"
    print filename 
    with open(filename, 'wb') as datei:
        pickle.dump(testarray, datei)

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
