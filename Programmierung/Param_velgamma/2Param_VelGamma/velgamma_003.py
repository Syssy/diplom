#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das Modell mit vel und gamma umzusetzen
# vel ist die Geschwindigkeit
# gamma ist ein sortenabhängiger Parameter
# Hier ist jetzt p einfach die Wechselwahrscheinlichkeit, nicht wie sonst die WKeit im akt. Zustand zu bleiben
# In dieser Version sind velmin und velmax feste Params, habe aber mit verschiedenen Werten dafür experimentiert
# Die Vel wird neu berechnet als alte vel + der veldivisorste Teil der differenz der alten vel und velmax. Wenn eines hängen bleibt, wird es wieder auf velmin runtergesetzt
# Die W'keit hängen zu bleiben ist gamma/velneu, also nur abhängig vom sortenspezifischen Parameter und der vel des einzelnen Teilchens
# Die W'keit von stationär zu mobil zu wechseln ist ps und hier abhängig von gamma


from __future__ import division
import random
import numpy as np
import matplotlib.pyplot as plt
import time
import scipy.stats as stats
import scipy
import pickle
import logging


# Speichert alle interessanten Dinge einer Simulation ab
class Simulation():
        def __init__(self, params_fest, params_var, length=0, number=0, counter=[0,0,1,0,0]):
	    #print "erstelle Sim"
	    #sowas wie velmin, velmax, evtl. ps
	    self.params_fest = params_fest
	    #sowas wie gamma, veldivisor,
	    self.params_var = params_var
            #self.velmax = velmax
            #self.velmin = velmin
            #self.ps = ps
            #self.veldivisor = veldivisor
            #self.gamma = gamma
            #self.params = (ps, gammadivisor, gamma0)
            self.velmean = 0
            self.pmean = 0
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
	    
'''def convert():
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
	    
    return None '''  
	    
	       
#Simuliert einen Schritt für alle Teilchen
# p muss ein vektor mit allen p's sein, da die hier von Teilchen zu Teilchen unterschiedlich sein können
# Es existieren noch mehrere Möglichkeiten, das hier umzusetzen, vor allem die Neuberechnung der vel/p könnte auch anders sein TODO
def simulatestep(p_in, gamma, vd, psvektor, teilchenort, teilchenmobil, number, vel):
    zzv = np.random.random(number)
    #bleibe stationär
    zzv2 = zzv > psvektor
    #bleibe mobil
    zzv3 = zzv > p_in
    
    logging.log(5, "vektoren \n %s \n %s \n %s \n %s", p_in, zzv, zzv2, zzv3)#, '\n', zzv, '\n', zzv2, '\n',zzv3)
        
    #berechne neuen Zustand für die Teilchen
    # bin mobil, wenn
    # vorher mobil und es bleibe (zzv3, bestimmt durch p_in, variable WKeiten)
    # oder: nicht mobil und nicht bleibe (zzv2, bestimmt durch gammavektor, fest TODO: geht das geschickter?)
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2)))) 
    # wenn mobil, addiere vel zum Ort
    teilchenortneu = teilchenort + vel*mobilneu

    #vel = np.clip(vel, velmin, velmax)
    # berechne neue Geschwindigkeiten; falls mobil addiere was dazu, clip davor und danach zum Schutz
    velneu = (vel + ((velmax-vel)/vd)) * mobilneu # wenn nicht mobil:0;  schneller, wenn mobil
    #velneu = (vel + (vel/vd)) * mobilneu
    #vel ist mindestens 1, für den neuen Ort wird mobil ja eh noch mal befragt
    velneu = np.clip(velneu, velmin, velmax)
    
    p_out = gamma/velneu
    #if min(p_out) <= 0:
#	logging.warn("mininumsproblem")
#	time.sleep(2)
 #   if max(p_out) > gamma:
#	logging.warn("maximumsproblem %s", p_out)
    logging.log(5, "mobil, ort, vel, pout \n %s \n %s \n %s \n %s", mobilneu, teilchenortneu, velneu, p_out)
    #p_out = np.clip(p_out, 0.00001, 0.09)
    
    #logging.debug("mobil, ort, vel, pout \n %s \n %s \n %s \n %s", mobilneu, teilchenortneu, velneu, p_out)
    
    #time.sleep(0.1)
    return teilchenortneu, mobilneu, velneu, p_out


# simuliert
def simulate(gamma, vd, p, length, teilchenort, teilchenmobil):
    startzeit = time.clock()
    logging.debug("teste jetzt: %s %s", gamma, vd)
    hilfscounter = []
    zeit = 0
    
    number = len(teilchenort)
   # vel = np.ones(number)
    vel = np.array([velmin] * number)
    psvektor = np.array([ps] * number)
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < (length)/np.max(vel):
	logging.debug(zeit)
        teilchenort, teilchenmobil, vel, p = simulatestep(p,gamma, vd, psvektor, teilchenort, teilchenmobil, number, vel)
        zeit += 1
    #Jede Menge debugging-Kram   
    #beziehe bei den velmean nur die ein, die grad nicht hängen
    logging.log(19, vel)
    x = vel > velmin
    logging.log(20, "mean vel, p, 1-p, %s, %s %s", np.mean(vel[x]), np.mean(p), 1- np.mean(p))
    logging.log(20, "max/min vel, p, 1-p, %s %s, %s %s", np.max(vel), np.min(vel), np.max(p), 1- np.max(p))
    logging.log(25, "Teil 1 beendet, %s, %s", zeit, time.strftime("%d%b%Y_%H:%M:%S"))
    logging.log(18, teilchenort)
    # velmean wird bei der Simulation mit abgespeichert. Dient der Übersicht und weiterführenden Überlegungen. Ist an sich aber aussagelos, da es nur einen einzelnen Zeitpunkt zeigt und nicht unbedingt repräsentativ ist. Außerdem sagt es nix über die Verteilung der Geschwindigkeiten aus, was wohl viel interessanter wäre. Daher die Histogrammausgabe
    velmean = np.mean(vel[x])
    pmean = np.mean(p[x])
    #logging.log(20, "vel %s \n p %s", vel, p)
    #fig = plt.figure()
    #ax = fig.add_subplot(121)
    #ax.hist(vel,30, normed=0)
    #ax.legend("vel")
    #ax = fig.add_subplot(122)
    #ax.hist(p,30, color="g", normed=1)
    #ax.legend("p")
    #plt.show()
    #time.sleep(2)
    
    #Teil 2: Ab jetzt können Teilchen fertig sein
        
#    logging.log(25, "Teil 2 beendet, %s, %s", zeit, time.strftime("%d%b%Y_%H:%M:%S"))    
    while True:
	# Damit es schneller geht, nach je x schritten nur testen
        for x in range (5):
            teilchenort, teilchenmobil, vel, p = simulatestep(p, gamma, vd, psvektor, teilchenort, teilchenmobil, number, vel)
            zeit+=1        
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length
        # wenn mindestens eins fertig wurde, werden die arrays aktualisiert, sonst weiter simulieren, dient der Zeiteinsparung
        if not np.all(d):
	    # die Arrays aktualisieren (rauswerfen aller fertigen teilchen), es bleiben die übrig, deren ort unterhalb der length ist (d=1)
	    teilchenort = teilchenort[d]
	    teilchenmobil = teilchenmobil[d]  
	    vel = vel[d]
	    p = p[d]
	    psvektor = psvektor[d]
	    #zähle (sum invert...) wie viele schon durch sind, hänge so oft die aktuelle zeit an
	    for j in range (np.sum(np.invert(d))):
		hilfscounter.append(zeit)
	    # wenn welche fertig sind, verringert sich die number, wichtig für die nächste Schleife
	    number = len(teilchenort)
	    # (fast) alle teilchen angekommen :)
	    #print number, time.clock()-startzeit, 
	    if number < 1:
		print "fertig"
		break

    print time.clock()-startzeit
    return hilfscounter, velmean, pmean

def main():
    startzeit = time.clock()
    # Meine ganzen Variablen
    # Laenge der zu simulierenden Strecke
    length = 50000
    # Anzahl der zu simulierenden Teilchen
    number = 2000
   
    global velmin, velmax, ps #gamma, veldivisor sind variabel, ps wird als vektor durchgereicht
    velmin = 0.5
    velmax = 5
    #ps = 0.0005
    logging.log(31, "length %s number %s velmin %s velmax %s", length, number, velmin, velmax)
    
    #pkombis sind je ein gamma und ein veldivisor
  #  pkombis = [(0.0005, 50000), (0.003, 20000), (0.0009, 80000), (0.005, 100000)]
  #  pkombis = [(0.0007, 500000), (0.0004, 50000), (0.005, 500000), (0.009, 10000)]
  #  pkombis = [ (0.005, 200), (0.003, 100), (0.0005, 30000), (0.00017, 500000), (0.001, 500000)] #save: v002 fig2
   
    pkombis = [(0.009, 1000), (0.001, 5000), (0.009, 500), (0.001, 30000), (0.005, 500000)] 
   # pkombis = [(0.01, 100), (0.01, 1000), (0.01, 5000), (0.01, 10000), (0.01, 50000)]
  #  pkombis = [(0.01, 4000), (0.01, 2000), (0.01, 3000), (0.01, 1700), (0.01, 2900)]
    
 #   for a in np.arange(0.0005, 0.0055, 0.0005):
#	for b in np.arange (20000, 210000, 10000):
#	    pkombis.append((round(a, 6), b))
#	    for c in range(0, 10000, 500):
#		for d in np.arange(0.9985, 0.9991, 0.0001):
#		    pkombis.append((a, round(b, 4), c, round(d, 4)))
   # print len(pkombis)
    logging.log(20, pkombis)
    ergebnisse = []
    
    #print np.random.choice(len(pkombis))
 #   zufallskombis = []
 #   for j in range(4):
#	zz = random.randint(0,len(pkombis))
#	print zz
#	zufallskombis.append(pkombis[zz])
    
    for gamma, vd  in pkombis: 
	        ps = gamma/3
	        logging.log(20,"gamma %s, vd %s %s", gamma, vd, time.strftime("%d%b%Y_%H:%M:%S"))
		#time.sleep(2)
		# Simulationen, die schon vorhanden sind, erst mal nicht neu machen
		# Daher vorher alles .p löschen oder verschieben, wenn neue Version
		mySim = None
		#Nur speichern, wenn neu simuliert wurde
		speichern = False
		
		#Testen, ob Simulation mit gleichen Params, Länge der Strecke und Anzahl der Teilchen schon vorhanden
		#Dann diese einfach übernehmen -> ergebnisse enthält am Ende alle Simulationen, egal ob alt oder neu 
		try:
		    #TODO hier wird noch auf *.pp getestet, bis die Sim so gut sind, dass ich wieder massensims erstellen kann!
		    filename = 'v003/l'+str(length)+"/n"+str(number)+'/v'+str(velmin) +'v'+str(velmax)+ '/Sim_'+ str(round(vd,8)) +'_' +  str(round(gamma,8))+ ".p" 
		    logging.log(15,"filename: %s", filename)
		    with open(filename, 'rb') as datei:
			mySim = pickle.load(datei)
			#print mySim.params
			#soll nicht sein! Rundungsfehler, Genauigkeit?! Kommt auch bisher nicht vor
			#print mySim, mySim.veldivisor
			if not (mySim.params_var[0], mySim.params_var[1]) == (gamma, vd):
			    logging.error("Bullshitkram: %s %s %s %s", mySim.params_var[1], vd, mySim.params_var[0], gamma)
			    
			# Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
			if not mySim.length == length or not mySim.number == number or not mySim.params_fest ==(velmin, velmax):
			    logging.warn('neue Sim nötig, da l/n oder feste Params falsch,')
			    speichern = True
			    # neue Sim nötig
			    print "neue Sim",
		            zeiten, velmean, pmean =  simulate(gamma, vd, np.array([gamma]*number), length, np.zeros(number), np.array([True]*number))
		            mySim = Simulation((velmin, velmax), (gamma, vd), length, number,zeiten)
		            mySim.velmean, mySim.pmean = velmean, pmean
			    #print mySim.times  
		# Simulation mit diesem Namen existiert nicht, daher neu machen
		except (IOError, EOFError):
		    speichern =  True
		    logging.log(25,"simuliere, da nicht vorhanden")
		    zeiten, velmean, pmean =  simulate(gamma, vd, np.array([gamma]*number), length, np.zeros(number), np.array([True]*number))
		    mySim = Simulation((velmin, velmax), (gamma, vd), length, number,zeiten)
		    mySim.velmean, mySim.pmean = velmean, pmean
		   
		except(AttributeError):
		    logging.warning("Falsche Simulationsversion gefunden")
		# *.p mit der Sim abspeichern für spätere Verwendung    
		if speichern:
		    logging.log(25, "speichern")
		    filename = 'v003/l'+str(length)+"/n"+str(number)+'/v'+str(velmin) +'v'+str(velmax)+ '/Sim_'+ str(round(vd,8)) +'_' +  str(round(gamma,8))+ ".p"
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
    
    # Bildschirm-Ausgabe
    figg = plt.figure()
    ll = list()
    pp = list()
    lines = ["r", "y", "b", "m","c"] 
    maxi = 0
    for i in range(len(pkombis)):
	si = ergebnisse[i]
	maxi = max(maxi, max(si.times))
	#logging.log(25, si.velmean)
	# normed wichtig, damit vergleichbar, alpha, damit es etwas durchsichtig ist
	n, bins, patches = plt.hist(si.times, 50, color=lines[i], normed=1, alpha=0.5)
	#l, = plt.plot(x, scipy.stats.invgauss.pdf(x, si.mu, si.loc, si.scale), lines[i], lw = 3, alpha=0.6)
        #ll.append(l)
        pp.append(patches[0])
        try:
	    logging.info("%s %s", si.params_var, si.velmean, si.pmean)
	except AttributeError:
	    pass
    #print pp    
    #figg.legend([pp[0], pp[1], pp[2], pp[3]], [zufallskombis[0], zufallskombis[1], zufallskombis[2], zufallskombis[3]])
    #figg.legend([pp[0], pp[1], pp[2], pp[3]], [pkombis[0], pkombis[1], pkombis[2], pkombis[3]])
    figg.legend([pp[0], pp[1], pp[2], pp[3], pp[4]], [pkombis[0], pkombis[1], pkombis[2], pkombis[3], pkombis[4]])
    plt.suptitle('velmin:' + str(velmin) + ' velmax:' + str(velmax))
    plt.show()
    
    # Rauschen dazugeben
    #print maxis
    rauschen = []
    for i in range(int(number/2)):
	rauschen.append(random.randint(0,maxi))
    #rauschen = sorted(rauschen)
    #print rauschen

    eindings = []
    eindings.append(rauschen)
    for sim in ergebnisse:
	for t in sim.times:
	    rauschen.append(t)
    plt.hist(rauschen, 300, color = "k", normed = 1, alpha = 1)
#    n, bins, patches = plt.hist(rauschen, 500, stacked=True, color= "k",normed=1, alpha = 0.9)
    #plt.show()
    
    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
    

if __name__ == "__main__":
    logging.basicConfig(level=20)
    logging.captureWarnings(True)
    main() 
