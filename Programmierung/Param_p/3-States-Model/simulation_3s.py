#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Erste Version für die 3 Zustände Simulation mit erst mal vier Parametern

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import random

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt
import seaborn

# Speichert alle interessanten Dinge einer Simulation ab
# Hat Methoden zur Simulation, sowie zur Berechnung von Peakdaten
class Simulation():
    """Simuliert und speichert Daten einer Simulation
    """
    version_number = 1.0
    
    def __init__(self, params, length, number, mode, times = [], pd = (), version = version_number):
        """__init__
        
        params - Parameter; Wahrscheinlichkeit, stationaer/mobil zu bleiben, wenn ein Teilchen schon in diesem Zustand ist
        length - Laenge der Saule
        number - Anzahl simulierter Teilchen
        mode - Wie wird simuliert, each_timestep (T) oder by_event (E)
        times - Ankunftszeiten
        pd - aus den times errechnete Peakdaten: ((loc, scale), (width, left-width, right-width), height)
        v - Versionsnummer eben ;)
        """
        #TODO: Vielleicht sinnvoll abzuspeichern, welches Modell, falls nur 4 Parameter
        #self.check_params(params)
        self.params = params
        self.kum_params = self.kumulate_params(params)
        self.num_states = len(params)
        self.zielmatrix = self.erstelle_zielmatrix(params, self.num_states)
        self.length = length
        self.number = number
        self.mode = mode
        if times:
            self.times = times
            self.mean = np.mean(self.times)
            self.variance = np.var(self.times)
            self.skewness = scipy.stats.skew(self.times)
            self.kurtosis = scipy.stats.kurtosis(self.times)
        # peakdaten der form: ((loc,scale),width,height)
        if pd:
            self.pd = pd
        self.version = version

    def erstelle_zielmatrix(self, params, num_states):
        if num_states == 3:
            zielmatrix = [0,0,0]
            for i in range(num_states):
                nenner = 1 - params[i][i]
                #print ("i ", i, " folge ", (i+1)%3)
                zaehler = params[i][(i+1)%3]
                #print("z ", zaehler, " n ", nenner)
                zielmatrix[i] = zaehler/nenner
        else:
            print("kann nur drei Zustände")
        #print ("zielmatrix", zielmatrix)
        return zielmatrix

    def kumulate_params(self, params):
        result = []
        for p in params:
            r = []
            r.append(p[0])
            for pp in range(len(p)-1):
                r.append(r[pp]+p[pp+1])
            result.append(r)    
        return result
 
    def _simulate_step(self, locations, mobile_states, number): #TODO: 3s
        """Simuliere einen Schritt für alle Teilchen innerhalb der each_timestep-Simulation
        
        Wahrscheinlichkeit stationaer/mobil zu bleiben, Zugriff über self.params
        (new_)locations -- np-array aller Orte vor bzw. nach diesem Aufruf
        (new_)mobile_states -- np-array aller Teilchenstates vor bzw. nach diesem Aufruf
        number -- Anzahl der zu simulierenden Teilchen, nicht immer gleich self.number, da es am Ende weniger werden
        """
        zzv = np.random.random(number)
        #zzv = np.array([0.29, 0.9, 0.69, 0.79, 0.19, 0.29, 0.89, 0.01, 0.49])
        #zzv = np.array([0.3, 0.9, 0.7, 0.8, 0.2, 0.3, 0.9, 0.01, 0.5])
        #print ("zzv", zzv)
        #print ("sl", mobile_states, locations)
        
        mobile_states = np.array(mobile_states)
        
        maske_0 = mobile_states == 0
        maske_1 = mobile_states == 1
        maske_2 = mobile_states == 2
        
        new_locations = locations + (maske_0 *100)
        
               
        uebergang_00 = zzv > self.kum_params[0][0]
        uebergang_01 = zzv > self.kum_params[0][1]
        uebergang_02 = zzv > self.kum_params[0][2]
        #print ("uebergang_0", ((0) + uebergang_00 + uebergang_01 + uebergang_02))
        uebergang_0 = ((0) + uebergang_00 + uebergang_01 + uebergang_02) * maske_0
        
        
        uebergang_10 = zzv > self.kum_params[1][0]
        uebergang_11 = zzv > self.kum_params[1][1]
        uebergang_12 = zzv > self.kum_params[1][2]
        uebergang_1 = ((0) + uebergang_10 + uebergang_11 + uebergang_12) * maske_1
        
        #print ("uebergang_1", ((0) + uebergang_10 + uebergang_11 + uebergang_12))
        
        uebergang_20 = zzv > self.kum_params[2][0]
        uebergang_21 = zzv > self.kum_params[2][1]
        uebergang_22 = zzv > self.kum_params[2][2]
        uebergang_2 = ((0) + uebergang_20 + uebergang_21 + uebergang_22) * maske_2
        
        #print ("uebergang_2", ((0) + uebergang_20 + uebergang_21 + uebergang_22))
        
        #print (uebergang_0)
        #print (uebergang_1)
        #print (uebergang_2)
        
        new_mobile_states= (uebergang_0 + uebergang_1 + uebergang_2)
        #print (new_mobile_states, new_locations)
        
        #zzv2 = zzv < self.params[0]
        #zzv3 = zzv < self.params[1]
        #zzv3 = zzv < self.params[2]
        
        ##berechne neuen Zustand für die Teilchen    
        ## entweder: vorher mobil und bleibe es (zzv3, pm)
        ## oder: war nicht mobil und bleibe nicht (invertiert zu oder)
        #new_mobile_states =  np.bitwise_or(np.bitwise_and(mobile_states, zzv3), (np.invert(np.bitwise_or(mobile_states, zzv2))))
        # wenn mobil, addiere 200 zum Ort; Festlegung auf 0.2mm mitte November 2014
        #new_locations = locations + (100 * new_mobile_states)
        #time.sleep(1)      
        #print (" ")
        return new_locations, new_mobile_states

    def simulate_each_timestep(self): #TODO: 3s
        """ Simuliere jeden Zeitschritt fuer jedes Teilchen"""
        # starttime für Laufzeitmessungen
        starttime = time.clock()
        # Wird Liste aller Ankunftstimes
        arrival_counter = []
        # Simulationszeit in Sekunden
        steps_needed = 0
        # Anzahl zu simulierender Teilchen
        number = self.number
        logging.log(25, "Starte Sim, timestep")
        time_step = 1
        
        # aktuelle Orte der Teilchen
        locations = np.zeros(number)
        # akutelle Zustaende der Teilchen 
        mobile_states = np.array([0]*number)
    
        #Teil 1: Sim bis frueheste Teilchen ankommen koennen, hier muss noch keine Abbruchbed. getestet werden. 
        # 0.1, da dann das Carriergas durch ist.
        while steps_needed < self.length/100:
            locations, mobile_states = self._simulate_step(locations, mobile_states, number)
            steps_needed += time_step
        #logging.log(20, "Teil1 vorbei, zeit:%s, simdauer:%s", steps_needed, time.clock()-starttime)
        #Teil 2: Ab jetzt koennen Teilchen fertig sein, teste erst, dann x neue Runden
        while True:
            # d ist bitmaske aller aktuell angekommenen Teilchen
            d = locations <= self.length
            logging.log(15, "in der trueschleife, zeit: %s, d:%s", steps_needed, len(d))
            # die beiden Arrays aktualisieren (rauswerfen aller fertigen Teilchen)
            locations = locations[d]
            mobile_states = mobile_states[d]   
            #zähle (suminvert...) wie viele schon durch, haenge deren Zeiten ans Ergebnis an
            for j in range(np.sum(np.invert(d))):
                arrival_counter.append(steps_needed)

            # Abbruchbedingung: alle teilchen angekommen :) oder Simulation dauert schon zu lange :(
            number = len(locations)
            if number < 5:
                logging.log(25, "fertig, simzeit: %s, realtime: %s", steps_needed, (time.clock()-starttime))
                break
            if steps_needed > 4800000:
                logging.log(25, "das bringt nix, Überschreitung der Maximalzeit, %s", (time.clock()-starttime))
                # alle noch nicht fertigen Teilchen bekommen 100 Sek Strafe, damit man sieht, dass Simulation nicht zu Ende durchgefuehrt wurde
                for j in range(len(locations)):
                    arrival_counter.append(steps_needed+2000000)
                break    
            
            # Damit es schneller geht, nach je x schritten nur testen
            for x in range (10):
                locations, mobile_states = self._simulate_step(locations, mobile_states, number)
                steps_needed+=time_step
        
        self.times = [date/20000 for date in arrival_counter]
       
    def _test_finished(self, particle_list): #TODO: 3s
        """Teste, ob die Teilchen schon durch sind. Aufruf durch simulate_by_event"""
        
        #extrahiere nicht fertige Teilchen als (zustands-ort)-Paare
        particles = [(state, location) for state, location in particle_list if location < self.length]
        
        #extrahiere zeiten fertiger Teilchen
        times = [(location-self.length)/200 for state, location in particle_list if location >= self.length]
        
        #Rueckgabe der nicht fertigen Teilchen und Ankunftszeiten fertiger Teilchen
        return particles, times
        
    def _simulate_event(self, particle_list): #TODO: 3s
        """Simuliere ein zeitliches Event, gebe neue Ereignisliste zurueck, Aufruf durch simulate_by_event"""
        
        periods, n_states, n_locations = [], [], []
        #TODO: Versuche, das noch zu parallelisieren
        # Dazu: ziehe je 3 geom zz listen und 3 zz listen
        # das gibt dann wohl 9 Listen ? die korrekt gezippt werden müssen... 
        # Ob das den Aufwand wert ist?
        
        
        # extrahiere je eine liste von Zustaenden und Orten
        states, locations = zip(*particle_list)
        #print("sl ", states, locations)
        global summe
        summe += len(particle_list)
        for s, l in particle_list:
            
            #Zufallszahlen ziehen: Geom fuer zeitpunkt des naechsten events, zz fuer naechsten zustand
            period = scipy.stats.geom.rvs(1-self.params[s][s])
            zz = random.random()
            
            #print("period ", period, " zz ", zz)
            
            #TODO neue zustandsberechnung überprüfen für volle drei Zustände!
            # Berechne neuen Zustand (gehe 1 weiter und evtl noch einen, falls zufalls das sagt, mod 3)
            n_zustand = (s + 1 + ( zz > self.zielmatrix[s])) % 3
            #print ("rechnung ", (s+1+(zz > self.zielmatrix[s]))%3, "bool ",zz > self.zielmatrix[s]  )
            
            #print("zustand, alt ", s, " neu ", n_zustand)
            
            #n_locations.append(!n_zustand*period +l)
            
            #loc = l + period*100 if s== 0 else l
            
            #Wenn alter Zustand mobil war, gehe vor, sonst nicht
            if s == 0:
                n_locations.append(l+period*100)
            else:
                n_locations.append(l)
           # print ("Zustaende ", s, n_zustand, " gehe ",l, period, loc)
            
            #n_locations.append(loc)
            #Entsprechende neue Zustaende und Zeitpunkte anhaengen
            n_states.append(n_zustand)
            periods.append(period)
            
        return list(zip(periods, n_states, n_locations)) #new_events
        
    def simulate_by_event(self): #TODO: 3s
        """Simuliere mit Hilfe einer Liste von Events"""
        starttime = time.clock()
        logging.log(25, "Starte Sim, Event")
        length = self.length
        number = self.number
        act_time = 0
    
        global summe
        summe = 0
        num_ev = 0
        # Ereignisse als dict. Jeweils als key einen Zeitpunkt (enthaelt nur diejenigen, wo auch was passiert, Vergangenheit wird geloescht) und eine Liste aller Teilchen, mit denen dann was passieren soll. Init mit mehreren leeren Listen, damit Abbruchbedingung passt
        events = {1:[], 2:[], 3:[], 4:[]}
        hl = list()
        # Init: Zu Zeitpunkt 0 passiert mit allen Teilchen was
        # Teilchen repraesentiert als Tupel von Zustand (0=stat, 1=mob) und Ort
        for i in range(number):
            hl.append((0, 0))
        events[0]=hl
        #act_time = 1
        
        # Hier kommen die Ankunftszeiten rein
        arrival_counter = []
        
        # solange noch Ereignisse ausstehen, wird simuliert
        while len(events) >= 5 and act_time < 4800000:
        #while act_time < 10:
            if act_time in events:
                logging.log(15, "betrachte zeitpunkt %s", act_time)
                # teste, ob zum aktuellen Zeitpunkt schon Teilchen fertig, fuege deren Zeiten ein
                particle_list = np.array(events[act_time])
                particle_list, times = self._test_finished(particle_list)
                arrival_counter.extend([(act_time-(date)) for date in times])
                
                #logging.log(5, "noch da2, %s", arrival_counter)
                # Falls die Teilchen dieses Zeitpunktes alle durch sind, wird nicht mehr simuliert
                # sonst Simulation aller uebriger Teilchen
                if len(particle_list) > 0:
                    num_ev += 1
                    new_events = self._simulate_event(particle_list)
                    #print(new_events)
                    for timediff, state, location in new_events:
                        try:
                            # Zeitpunkt schon vorhanden -> einfuegen
                            events[act_time + timediff].append((state, location))
                        except KeyError as err:
                            # Zeitpunkt nicht vorhanden -> erstellen
                            events.update({act_time + timediff:[(state, location)]})
                ##Zeitpunkt abgearbeitet, Vergangenheit loeschen                         
                del events[act_time]
            #naechste Zeit betrachen    
            act_time += 1  
        # Zeitpunkte normalisieren
        #print (events)
        if len(events) > 0:
            print ("Das wird nix")
            for ev in events:
                #print (ev, events[ev])
                for teilchen in events[ev]:
                    arrival_counter.append(act_time+2000000) #TODO richtig?
        #print (arrival_counter)
        print (summe/num_ev)
        self.times = [date/20000 for date in arrival_counter]
        logging.log(25, "fertig, simschritte: %s, realtime: %s", act_time, (time.clock()-starttime))
        
    def set_pd(self, pd, v = version_number): #TODO: 3s
        """setzt Peakdaten und Versionsnummer neu, falls veraltet, nicht vorhanden, nicht zu gebrauchen"""
        self.pd = pd
        self.version = v

    def __repr__(self):
        result = ''
        for param in self.params:
            result+=("[")
            for p in param:
                result+=(str(round(p, 6)) + " ")
            result+=("] ")
        #result+=("]")                      
        return (result + self.mode)
        
    def get_moment(self, moment):
        """Gebe den Wert des moment zurück."""
        if moment == "mean":
            return self.mean
        if moment == "variance":
            return self.variance
        if moment == "skewness":
            return self.skewness
        if moment == "kurtosis":
            return self.kurtosis
        return None
        
    def simulate(self, mode = None):  #TODO: 3s
        '''Simuliert je nach Modus, TODO: Achtung, Direktaufruf der Simulationsmethoden fuehrt zu potenziell falsch eingetragenem Mode'''
        if self.mode == "E" or mode == "E":
            self.simulate_by_event()
        elif self.mode == "T" or mode == "T":
            self.simulate_each_timestep()
        else:
            print ("Bitte gewuenschten Simulationsmodus mit angeben ", self.mode, "nicht gueltig")
    
    def _find_intersection(self, fun1, fun2, x0):
        '''finde Schnittpunkt zweier Funktionen (fun1, fun2) ausgehend von geschätzten Wert(en) x0'''
        return scipy.optimize.fsolve(lambda x : fun1(x) - fun2(x), x0)      
    
    
    def ig_function(self, mu_i, loc_i, scale_i, x):
        if x <= 0:
            return 0
        else:
            return np.exp(-(scale_i*((x-loc_i) - mu_i)**2) /(2* (x-loc_i) * mu_i**2)) * math.sqrt(2*math.pi*(x-loc_i)**3)
     
    
    def calculate(self): #TODO: Peakdata anpassen
        """Berechne Momente, Breite und Hoehe bei halber Peakhoehe, sowie Loc und Scale, ausgehend von Gaussverteilung"""
        # Momente berechnen
        self.mean = np.mean(self.times) 
        self.variance = np.var(self.times)
        self.skewness = scipy.stats.skew(self.times)
        self.kurtosis = scipy.stats.kurtosis(self.times)
        
        # Peakdaten berechnen
        # Finde Parameter fuer passende Gausskurve zum Schneiden
        loc_n, scale_n = scipy.stats.norm.fit(self.times)
        mu_i, loc_i, scale_i= scipy.stats.invgauss.fit(self.times)
        print ("igparams: ", mu_i, loc_i, scale_i)
        hist, bins = np.histogram(self.times, bins=50, normed = True)
        offset = bins[1:]-bins[:-1]
        print ("hist", hist, "\nmax", max(hist), "argmax", np.argmax(hist), "len", len(hist))
        print ("bins", bins, "maxdings", bins[np.argmax(hist)+1], "len", len(bins))
        #plt.plot([bins[np.argmax(hist)+1],bins[np.argmax(hist)+1]] , [0, max(hist)])
        #plt.show()
        x = np.linspace(min(self.times)-50, max(self.times)+50, 1000000)
        plt.plot(bins[:-1]+offset, hist, x, scipy.stats.invgauss.pdf(x, mu_i, loc_i, scale_i), x, scipy.stats.norm.pdf(x, loc_n, scale_n), [bins[np.argmax(hist)+1], bins[np.argmax(hist)+1], bins[np.argmax(hist)+1]] , [0, max(hist)/2, max(hist)])
        #plt.show()
        # halben Maximalwert berechnen
        halfmax = max(hist) / 2
        #halfmax = 1/(math.sqrt(2*math.pi)*scale_n *2)
        #print ("halfmax", halfmax)
            
        # Funktionen erstellen, die dann für die find intersections genutzt werden. TODO: Hier noch andere verteilungen ermöglichen
        # Funktion der Normalverteilung
        norm = lambda x: np.exp(-(x-loc_n)**2 /(2*scale_n**2)) / math.sqrt(2*math.pi * scale_n**2)
        # Funktion einer Linie
        linie = lambda x: halfmax + 0*x
        # Funktion der IG
        ig_funct = lambda x: np.exp(-(scale_i*((x-loc_i) - mu_i)**2) /(2* (x-loc_i) * mu_i**2)) * math.sqrt(2*math.pi*(x-loc_i)**3)
        print (norm(5))
        print(ig_funct(70))
        
        print ("test", self._find_intersection(linie, self.testfunction, [loc_i+scale_i]))
        intersections = self._find_intersection(linie, norm, [loc_n+scale_n, loc_n-scale_n])
        print (intersections)
        sects = self._find_intersection(linie, ig_funct, [loc_n-scale_n])
        print (sects)
        time.sleep(1)
        # print ("max bei", norm(loc), "starte test bei:", loc-scale, loc+scale)
        # finde Schnittpunkte zwischen Linie auf halber Hoehe und Gausskurve, Startwerte sind median +- standardabweichung
        logging.log(15, "Intersections %s", intersections)
        
        #width ist Abstand zwischen den Schnittpunkten
        l_w = loc_n - min(intersections)
        r_w = max(intersections) - loc_n
        width = abs(max(intersections) - min(intersections))
        ls =  (loc_n, scale_n)
        pd = (self.mean, (width, l_w, r_w), halfmax)
        self.set_pd(pd)

def check_params(params):
    for p in params:
        if sum(p) != 1:
            logging.log(40, "Fehler bei den params, in %s, %s", p, params)
            print (sum(p))
            return False
        if min(p)<0:
            logging.log(30, "Negativer Param, in %s, %s", p, params)
            return False
    return True
    
# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "beschreibung")  
    p.add_argument("--inputfile", "-i", type = str,  help = "input file (pickled)")
    p.add_argument("--moment", "-m" , help = "which moment is of interest")
    p.add_argument("--recalc", "-rc", type=str, help = "recalculate moments")
    p.add_argument("--number", "-n", help = "how many files to recalculate")
    
    return p

# Nutzung für Testzwecke
def main(): #TODO: 3s
    number = 2000
    length = 200000
    print ("n", number, "l", length, time.strftime("%d%b%Y_%H:%M:%S"))
    p = get_argument_parser()
    args = p.parse_args()
    
    #params = [[0.5, 0.499, 0.001],[0.0005, 0.9995, 0.0],[0.000001, 0.0, 0.99999]]
    #params = [[0.7,0.0,0.3],[0.0,0.0,0.0],[0.0006, 0.0, 0.9994]]
    #params = [[0.7,0.3,0.0],[0.00006, .99994, 0.0],[0.0,0.0,0.0]]
    #params = [[0.0,0.5,0.5],[0.0,0.5,0.5],[0.0, 0.5, 0.5]]
    
    pmms = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    pmls = [0.01, 0.001, 0.0005, 0.0001] 
    pms = []
    for pmm in pmms:
        for pml in pmls:
            pma = 1 - pmm - pml
            pms.append([pmm, pms, pml])
            
    paas = [0.999, 0.9993, 0.9996, 0.9999, 0.99992, 0.99994]   
    pas = []
    for paa in paas:
        pam = 1 - paa
        pas.append([pam, paa, 0.0])
        
    plls = [0.99999, 0.999995, 0.999999]    
    
    pms = [[0.8, 0.199, 0.001],[0.5, 0.499, 0.001],[0.5, 0.4999, 0.0001]]
    pas = [[0.0008, 0.9992, 0.0],[0.0005, 0.9995, 0.0],[0.0001, 0.9999, 0.0]]
    pls = [[0.00005, 0.0, 0.99995],[0.00001, 0.0, 0.99999],[0.000005, 0.0, 0.999995]]
    
    for pm in pms:
        for pa in pas:
            for pl in pls:
                params = [pm, pa, pl]                
                neueSim = Simulation(params, length, number, "E", [])
    
                if neueSim.check_params(params):
                    #print ("params", params)
                    #neueSim.simulate_by_event()
                    #neueSim.calculate()
                    #print("pd by EVENT", neueSim.pd, len(neueSim.times))
                    #n, bins, patches = plt.hist(neueSim.times, 50, normed=1, alpha=0.5)   
                    #plt.ylabel("")
                    #plt.xlabel("Zeit / s")
                    #plt.title("params: "+ str(neueSim.params[0])+" "+ str(neueSim.params[1])+" "+ str(neueSim.params[2]) + " by event")
                    #plt.savefig("p"+ str(neueSim.params[0])+"_"+ str(neueSim.params[1])+"_"+ str(neueSim.params[2]) + "_event_n" + str(number) + ".png")
                    #plt.hold(False)
        #plt.show()

                    neueSim.simulate_each_timestep()
                    neueSim.calculate()
                    #print ("times by step", neueSim, neueSim.times)
                    print ("pd by TIMESTEP", neueSim.pd, neueSim.get_moment("skewness"), len(neueSim.times))
                    n, bins, patches = plt.hist(neueSim.times, 50, normed=1, alpha=0.5)
                    plt.ylabel("")
                    plt.xlabel("Zeit / s")
                    plt.title("params: "+ str(neueSim.params[0])+" "+ str(neueSim.params[1])+" "+ str(neueSim.params[2]) + " timestep")
                    #print (neueSim.params, neueSim.mean, neueSim.pd, neueSim.pd[0])
                    plt.savefig("p"+ str(neueSim.params[0])+"_"+ str(neueSim.params[1])+"_"+ str(neueSim.params[2]) + "_timestep_n" + str(number) + ".png")
                    plt.hold(False)
                    #plt.show()
             
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()
