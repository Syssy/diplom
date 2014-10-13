#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, die andere Möglichkeit zur Sim umzusetzen.
# Hier wird ausgewürfelt, wann wieder etwas passiert
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


# Jedes Teilchen soll seinen Ort, Zustand (mobil/stationaer), evtl Geschwindigkeit kennen. Dazu ID fuer Ausgabezwecke, die kann spaeter weg
class Teilchen:
    anz = 0
    def __init__(self, ort = 0, mobil = False, vel = 1):
	self.ort = ort
	self.mobil = mobil
	self.vel = vel
	self.myID = Teilchen.anz
	Teilchen.anz += 1

    # zeitspanne zurueck, nach der wieder was passiert.
    #aendert zunaechst den Zustand des Teilchens, wenn es dann mobil ist, geht es noch entsprechend der zeitspanne weiter, sonst nicht
    def simuliere(self, ps=0.999, pm=0.999):
	self.mobil = not self.mobil	
	zz = 0
	zeitspanne = 0
	
	# Parameterwahl abhaengig vom akt Zustand
	if self.mobil:
	    p=pm
	else:
	    p=ps
	
	# Zeitpunkt bestimmen, hier steh ich auf dem Schlauch #TODO
	#while zz <= p:
	#    zz = random.random()
	#    zeitspanne += 1
	#    print zz, zeitspanne
	#print zeitspanne
	#zeitspanne = random.randint(1,10)
	
	# Geometrisch verteilt: Zeit bis zum naechsten Erfolg
	zeitspanne = scipy.stats.geom.rvs(1-p)
	#print zeitspanne
	
	# evtl weiter gehen
	if self.mobil:
	    #print "gehe", 
	    self.ort += zeitspanne * self.vel
	    #print self, self.ort
        else:
	    pass#print "stehe", self	
	return zeitspanne

    # testet, ob das Teilchen schon uebers Ziel ist, wenn ja, gibt auch an, wie weit drueber
    def teste_fertig(self, length):
	if self.ort >= length:
	    return True, self.ort-length
	else:
	    return False, 0
	
    #fuer Ausgabezwecke
    def __repr__(self):
	return ("nr." + str(self.myID)+ "_" + str(self.mobil) + str(self.ort) + " ")


def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    length = 10000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    # Die Parameter (ps, pm) TODO später
    
    zeit = 0
    
    # Ereignisse als dict. Jeweils als key einen Zeitpunkt (enthaelt nur diejenigen, wo auch was passiert, Vergangenheit wird geloescht) und eine Liste aller Teilchen, mit denen dann was passieren soll
    ereignisse = {}
    
    # Init: Zu Zeitpunkt 0 passiert mit allen Teilchen was
    ereignisse[0] = []
    hl = list()
    for i in range(number):
	hl.append(Teilchen())
    ereignisse[zeit]=hl
   # print ereignisse, len(ereignisse)
    
    # Hier kommen die Ankunftszeiten rein
    counter = []
    
    # solange noch Ereignisse ausstehen, wird simuliert
    while len(ereignisse) > 0:
	#print "Durchlauf Nummer", zeit
	
	# Kein Ereignis zu Zeitpunkt zeit
	if zeit not in ereignisse:
	   pass#print "lalallala"
	else:
	    # Liste aller Teilchen, mit denen zu diesem Zeitpunkt was passiert
	    # TODO: Evtl hier parallelisieren, falls diese Listen lang sind, lohnt grad zu Beginn einer Sim mit vielen Teilchen
	    teilchenliste = ereignisse[zeit]
	    #print "teilchenliste", len(teilchenliste),
	    for y in range(len(teilchenliste)):
		teilchen = teilchenliste.pop()
		#print teilchen
		zeitpunkt = teilchen.simuliere(0.999, 0.999)
		#print "nächstes mal", zeit+zeitpunkt, "teilchen", teilchen
		fertig, diff = teilchen.teste_fertig(length)
		#Wenn fertig, den Ankuftszeitpunkt merken, sonst an passender Stelle im Dict wieder einfuegen
		if fertig:
		   # print "FERTIG", zeit, diff, teilchen
		    counter.append(zeit+ (zeitpunkt-diff) )
		else:
		    try:
			ereignisse[zeit + zeitpunkt].append(teilchen)
		    except KeyError as err:
			#print "KeyError", err
			ereignisse.update({zeit + zeitpunkt:[teilchen]})
	    #Zeitpunkt abgearbeitet, Vergangenheit loeschen
	    del ereignisse[zeit]
	#naechste Zeit betrachen    
        zeit += 1  
	#print "ereignisse", ereignisse, len(ereignisse), ' \n\n '
	
    # Ausgabe
    #print "ergebnis: counter", counter	
    n, bins, patches = plt.hist(counter, 50, normed=1, alpha=0.5 )
    plt.show()

    # Ende :)
    print "Zeit "+str(time.clock()- startzeit)     
   

if __name__ == "__main__":
    main() 
