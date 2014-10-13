#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das Modell mit vel und gamma umzusetzen
# vel ist die Geschwindigkeit (sollte es als aktuelle und maximale/minimale geben)
# gamma ist ein sortenabhängiger Parameter
# ps wird benötigt, da die Wkeit sich zu lösen unabhängig von der vel

# Hier war mal was besseres, aber das kann ich nicht mehr reproduzieren, und möchte erst mal mit der anderen Sim (002) anfangen, weil das einfacher wirkt und weniger params verspricht. 
# Problem ist hier wohl die berechnung von p_out in simulatestep, das hab ich aus Versehen gelöscht... Und auch nicht sonst wo notiert

from __future__ import division
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
        def __init__(self, veldivisor=5000, ps=0.998, gammadivisor=5000, gamma0=0.999, length=0, number=0, counter=[0,0,1,0,0]):
	    #print "erstelle Sim"
            self.veldivisor = veldivisor
            self.ps = ps
            self.gammadivisor = gammadivisor
            self.gamma0 = gamma0
            self.params = (veldivisor, ps, gammadivisor, gamma0)
            self.velmean = 0
            self.length = length
            self.number = number
            self.times = counter
            #TODO Möglichkeit, andere Verteilungen zu berücksichtigen
            #TODO Nicht unbedingt beim Sim berechnen, kostet Zeit
            # berechne die most likeli params der inv-gauß-Verteilung
            #print "berechne"
            #self.mu, self.loc, self.scale = scipy.stats.invgauss.fit(self.times)
            # berechne Momente
            self.mean = np.mean(self.times)
	    self.variance = np.var(self.times)
	    #print "..", self.times
	    self.skewness = scipy.stats.skew(self.times)
	    #print "sk"
	    self.kurtosis = scipy.stats.kurtosis(self.times)
	    #print "..."
	    
def convert():
    length = 20000
    number = 10000
    pkombis = []
    for a in range(2500, 12000, 500):
        for b in np.arange (0.995, 0.999, 0.005):
            for c in range(3000, 12000, 500):
	        for d in np.arange(0.998, 0.9992, 0.0001):
	            pkombis.append((a, b, c, round(d, 4)))
        
    for veldivisor, ps, gammadivisor, gamma0 in pkombis:
        filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(veldivisor,6)) +'_' + str(round(ps,6)) +'_' +  str(round(gammadivisor,6))+ str(round(gamma0,6)) +'_' + ".p"   
        #print filename
        try:
	    with open (filename, 'rb') as datei:
	        mySim = pickle.load(datei)
	        newSim = Simulation(veldivisor, ps, gammadivisor, gamma0, length, number, mySim.times)
	        newfile = 'm'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(veldivisor,6)) +'_' + str(round(ps,6)) +'_' +  str(round(gammadivisor,6))+'_'+ str(round(gamma0,6)) + ".p" 
	        #print newfile, newSim
	        with open(newfile, 'wb') as neuedat:
                    pickle.dump(newSim, neuedat)
                print "yay"    
        except IOError as err:
	    print "fehler:", err
	    
    return None   
	    
	       
#Simuliert einen Schritt für alle Teilchen
# p muss ein vektor mit allen p's sein, da die hier von Teilchen zu Teilchen unterschiedlich sein können
# Es existieren noch mehrere Möglichkeiten, das hier umzusetzen TODO
def simulatestep(p_in, teilchenort, teilchenmobil, number, vel):
    psvektor = np.array([ps] * number)
    zzv = np.random.random(number)
    #bleibe stationär
    zzv2 = zzv < psvektor
    #bleibe mobil
    zzv3 = zzv < p_in
    #print "pin", p_in
    
    '''print "vektoren"
    print p_in
    print zzv
    print zzv2
    print zzv3'''
        
    #berechne neuen Zustand für die Teilchen
    # bin mobil, wenn
    # vorher mobil und es bleibe (zzv3, bestimmt durch p_in, variable WKeiten)
    # oder: nicht mobil und nicht bleibe (zzv2, bestimmt durch gammavektor, fest TODO: geht das geschickter?)
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2)))) 
    # wenn mobil, addiere vel zum Ort
    teilchenortneu = teilchenort + vel*mobilneu
    
    #print "mobneu", mobilneu
    
    vel = np.clip(vel, velmin, velmax)
    # berechne neue Geschwindigkeiten; falls mobil addiere was dazu, clip davor und danach zum Schutz
    velneu = (vel + ((velmax-vel)/veldivisor)) * mobilneu # wenn nicht mobil, schneller, wenn mobil
    #print "velneu", velneu
    #vel ist mindestens 1, für den neuen Ort wird mobil ja eh noch mal befragt
    velneu = np.clip(velneu, 0, velmax)
    #print max(velneu)
    
    #print "p_in", p_in
    #time.sleep(1)
    
    # wo ich nicht mobil bin: gamma0 -> p1: [0, g0, 0,0,0, g0, g0, 0...]
    p1 = np.invert(mobilneu) * gamma0
    
    #wo ich mobil bin, erhöht sich p TODO p2: [p, 0, p,p,p,0,0,p,...]
    p2 = mobilneu * (gamma0 + vel/gammadivisor)
    
    #print "veldings", 1/vel
    #print gamma0/gammadivisor
    #print "p2", p2
    p_out = p1 + p2
    #print "pout", p_out
    p_out = np.clip(p_out, gamma0, 0.9999)
    #print velneu,'\n',  p_out

    return teilchenortneu, mobilneu, velneu, p_out


# simuliert für ps und pm alle teilchen
def simulate(p, length, teilchenort, teilchenmobil):
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    
    number = len(teilchenort)
    vel = np.ones(number)
    #print vel
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length/velmin:
        teilchenort, teilchenmobil, vel, p = simulatestep(p, teilchenort, teilchenmobil, number, vel)
        zeit += 1
    #print "vel nach teil 1", vel
    #print "und p", p
    print "mean p, vel", np.mean(p), np.mean(np.clip(vel, velmin, velmax))
    velmean = np.mean(np.clip(vel, velmin, velmax))
    #plt.hist(vel,25)
    #plt.show()
    #print "teilchenort" , teilchenort, len(teilchenort)
    #time.sleep(2)
    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil, vel, p = simulatestep(p, teilchenort, teilchenmobil, number, vel)
            zeit+=1        
        #print "vel", vel
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # die Arrays aktualisieren (rauswerfen aller fertigen teilchen), es bleiben die übrig, deren ort unterhalb der length ist (d=1)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]  
        vel = vel[d]
        p = p[d]
        #zähle (sum invert...) wie viele schon durch sind, hänge so oft die aktuelle zeit an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)
        # wenn welche fertig sind, verringert sich die number, wichtig für die nächste Schleife
        number = len(teilchenort)
        #print teilchenort
        # (fast) alle teilchen angekommen :)
        if number < 2:
            print "fertig"
            break

    print time.clock()-startzeit
    return hilfscounter, velmean

def main():
    startzeit = time.clock()
    #convert()
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 20000
    # Anzahl der zu simulierenden Teilchen
    number = 10000
    
    schrittweite = 0.0001
    p1 = np.arange(0.9985, 0.9995, schrittweite)
    p2 = np.arange(0.00003, 0.00018, schrittweite)

   
    global gamma, ps, velmax, velmin, veldivisor, gamma0, gammadivisor
    velmax = 4
    velmin = 1.3
    veldivisor = 2000
    ps = 0.998
    gammadivisor = 4000
    gamma0 = 0.999
    
    pkombis = []
   # pkombis = [(3500, 0.996, 5000, 0.9985),(2500, 0.996, 5000, 0.9985),(1500, 0.996, 5000, 0.9985),(4500, 0.996, 5000, 0.9985)] 
    
    for a in range(1000, 10000, 1000):
	for b in np.arange (0.99, 0.999, 0.001):
	    for c in range(1000, 6000, 500):
		for d in np.arange(0.998, 0.999, 0.0001):
		    pkombis.append((a, round(b, 4), c, round(d, 4)))
    print len(pkombis)
   
    ergebnisse = []
    
    #print np.random.choice(len(pkombis))
    zufallskombis = []
   # for j in range(4):
#	zz = random.randint(0,len(pkombis))
#	print zz
#	zufallskombis.append(pkombis[zz])
	
    zufallskombis.append((100000000000, 0.998, 100000000000, 0.999))
	
    zufallskombis.append((100000000000, 0.998, 100000000000, 0.999))
	
    zufallskombis.append((100000000000, 0.998, 100000000000, 0.999))
	
    zufallskombis.append((100000000000, 0.998, 100000000000, 0.999))   
    for veldivisor, ps, gammadivisor, gamma0 in zufallskombis:  
	        print veldivisor, ps, gammadivisor, gamma0,
	        #time.sleep(2)
		#print p, '(', time.strftime("%d%b%Y_%H:%M:%S"), ') ',
		# Simulationen, die schon vorhanden sind, erst mal nicht neu machen
		# Daher vorher alles .p löschen oder verschieben, wenn neue Version
		mySim = None
		#Nur speichern, wenn neu simuliert wurde
		speichern = False
		
		#Testen, ob Simulation mit gleichen Params, Länge der Strecke und Anzahl der Teilchen schon vorhanden
		#Dann diese einfach übernehmen -> ergebnisse enthält am Ende alle Simulationen, egal ob alt oder neu 
		try:
		    #TODO hier wird noch auf *.pp getestet, bis die Sim so gut sind, dass ich wieder massensims erstellen kann!
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(veldivisor,6)) +'_' + str(round(ps,6)) +'_' +  str(round(gammadivisor,6))+'_'+ str(round(gamma0,6)) + ".p" 
		    #print filename
		    with open (filename, 'rb') as datei:
			mySim = pickle.load(datei)
			#print mySim.params
			#soll nicht sein! Rundungsfehler, Genauigkeit?! Kommt auch bisher nicht vor
			#print mySim, mySim.veldivisor
			if not mySim.params == (veldivisor, ps, gammadivisor, gamma0):
			    print "Bullshitkram:", mySim.params, (round(veldivisor,6), ps, gammadivisor, round(gamma0,6))
			    
			# Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
			if not mySim.length == length or not mySim.number == number:
			    print 'neue Sim nötig, da l/n falsch',
			    speichern = True
			    # neue Sim nötig
			    # den lange brauchenden Bereich außer Acht lassen, dafür dann ein fake einsetzen
			    print "neue Sim",
			    mySim = Simulation(veldivisor, ps, gammadivisor, gamma0, length, number, simulate(np.array([gamma0]*number), length, np.zeros(number), np.array([True]*number)))
			    #print mySim.times  
			# wofür das denn? aaaaarrrgg! Kommentieren, Elly!  
			# da muss eigentlich eine fake sim hin... bei der Abfrage teste ich darauf, ob es bereits eine fakesim hierfür gibt, das kommt jetzt erst mal raus, bis ich weiß, was das soll
			#if mySim.times == [0,0,1,0,0]:
			#	print "kein fake, sim..."
			#	mySim = Simulation(round(ps, 6), round(pm,6), pv, length, number,simulate(p, pv, length, np.zeros(number), np.array([True]*number)))
		        print "da!"
		# Simulation mit diesem Namen existiert nicht, daher neu machen
		except (IOError, EOFError):
		    speichern = True
		    print "simuliere, da nicht vorhanden"
		    zeiten, mean =  simulate(np.array([gamma0]*number), length, np.zeros(number), np.array([True]*number))
		    mySim = Simulation(veldivisor, ps, gammadivisor, gamma0, length, number,zeiten)
		    mySim.velmean = mean
		    #print mySim.times
		    #else:
			#print "fake, nicht vorhanden",
			#mySim = Simulation(round(vel, 6), round(gamma,6), length, number)
		    
		# *.p mit der Sim abspeichern für spätere Verwendung    
		if speichern:
		    #print "speichern"
		    filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ str(round(veldivisor,6)) +'_' + str(round(ps,6)) +'_' +  str(round(gammadivisor,6))+'_' + str(round(gamma0,6)) + ".p"
		    with open(filename, 'wb') as datei:
			pickle.dump(mySim, datei)		    
	    
		# ins array kommt jetzt die Sim, entweder eine alte, falls verwertbar oder eine neue
                ergebnisse.append(mySim)
                                
    # Die Liste mit allen für spätere Verwendung speichern, ist diese vorhanden, sind die ganzen .p im Prinzip hinfällig
    #filename = 'l'+str(length)+"/n"+str(number)+'/Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+'_'+str(min(p1))+str(max(p1))+ str(schrittweite)+".pickle"
    #print filename 
    #with open(filename, 'wb') as datei:
    #    pickle.dump(testarray, datei)
    
    #print "times", mySim.times
    figg = plt.figure()
    ll = list()
    pp = list()
    lines = ["r", "y", "b", "m"] 
    for i in range(len(zufallskombis)):
	si = ergebnisse[i]
	#print si
	n, bins, patches = plt.hist(si.times, 100, color=lines[i], normed=1, alpha=0.5)
	#l, = plt.plot(x, scipy.stats.invgauss.pdf(x, si.mu, si.loc, si.scale), lines[i], lw = 3, alpha=0.6)
        #ll.append(l)
        pp.append(patches[0])
        try:
	    print si.params, si.velmean
	except AttributeError:
	    pass
    #print pp    
    figg.legend([pp[0], pp[1], pp[2], pp[3]], [zufallskombis[0], zufallskombis[1], zufallskombis[2], zufallskombis[3]])
    

    
    #for i in range(len(pkombis)):
#	plt.hist(ergebnisse[i], 30, normed=1, alpha=0.5 )
	
    plt.show()

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    main() 
