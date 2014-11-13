#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen, Klappe die zweite...
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import pickle
import time
import logging
import argparse

import numpy as np
import scipy.stats as stats
import scipy
import matplotlib.pyplot as plt

import plotkram
import simulation
import peak_width

#
def simulate_step(ps, pm, location, mobile_state, number):
    """Simuliere einen Schritt für alle Teilchen.
    
    ps, pm -- Wahrscheinlichkeit stationaer/mobil zu bleiben
    (new_)location -- np-array aller Orte vor bzw. nach diesem Aufruf
    (new_)mobile_state -- np-array aller Teilchenzustaende vor bzw. nach diesem Aufruf
    number -- Anzahl der zu simulierenden Teilchen
    """
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    logging.log(10, zzv[0:10])
    logging.log(10, zzv2[0:10])
    logging.log(10, zzv3[0:10])
    #berechne neuen Zustand für die Teilchen    
    # entweder: vorher mobil und bleibe es (zzv3, pm)
    # oder: war nicht mobil und bleibe nicht (invertiert zu oder)
    new_mobile_state =  np.bitwise_or(np.bitwise_and(mobile_state, zzv3), (np.invert(np.bitwise_or(mobile_state, zzv2))))
    # wenn mobil, addiere 200 zum Ort; Festlegung auf 0.2mm mitte November 2014
    new_location = location + (200 * new_mobile_state)
    logging.log(10, location[0:10])
    logging.log(10, new_location[0:10])
    logging.log(10, mobile_state[0:10])
    logging.log(10, new_mobile_state[0:10])
    return new_location, new_mobile_state

    # simuliert für ps und pm alle teilchen
def simulate(ps, pm, length, location, mobile_state):
    """Hauptschleife, Simuliere und teste, ob fertig."""
    startzeit = time.clock()
    arrival_counter = []
    time_needed = 0
    number = len(location)
 
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while time_needed < length/20000000:
        location, mobile_state = simulate_step(ps, pm, location, mobile_state, number)
        time_needed += 0.00001
        logging.log(10, time_needed)
    #time.sleep(2)
    # Zeit soll hier 1/10s sein
    logging.log(24, "Teil1 vorbei, zeit:%s, simdauer:%s", time_needed, time.clock()-startzeit)
    logging.log(23, location[0:10])
    #Teil 2: Ab jetzt können Teilchen fertig sein, teste erst, dann x neue Runden
    while True:
        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = location < length
        logging.log(10, location)
        logging.log(15, d[0])
        logging.log(15, "in der trueschleife, zeit: %s", time_needed)
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen)
        location = location[d]
        mobile_state = mobile_state[d]   
        #zähle (suminvert...) wie viele schon durch, hänge deren zeitenen an
        for j in range(np.sum(np.invert(d))):
            arrival_counter.append(time_needed)

        # alle teilchen angekommen :) oder Simulation dauert schon zu lange :(
        number = len(location)
        if number < 1:
            logging.log(25, "fertig, %s, %s", time_needed, (time.clock()-startzeit))
            break
        if time_needed > 240:
            logging.log(25, "dat bringt nix, %s", (time.clock()-startzeit))
            for j in range(len(location)):
                arrival_counter.append(time_needed+100)
            break    
        
        # Damit es schneller geht, nach je x schritten nur testen
        for x in range (1000):
            location, mobile_state = simulate_step(ps, pm, location, mobile_state, number)
            time_needed+=0.00001
       
    #print time.clock()-startzeit
    return arrival_counter

def my_magic_color_generator(num_colors = 11): # leider doch nicht so magic  #print (num_colors)
    b = num_colors > 6
    c = num_colors > 12
    d = num_colors > 24
    
    rr = 0xff
    gg = 0x00
    bb = 0x00
   
    yield "#FF0000"
    if d:
        yield "#FF2000"
    if c:
        yield "#FF4000"
    if d:
        yield "#FF6000"
    if b:    
        yield "#FF8000"
    if d:
        yield "#FFA000"
    if c:
        yield "#FFBF00"
    if d:
        yield "#FFDF00"
    yield "#FFFF00"
    if d:
        yield "#DFFF00"
    if c:
        yield "#BFFF00"
    if d:
        yield "#A0FF00"
    if b:
        yield "#80FF00"
    if d:
        yield "#60FF00"
    if c:
        yield "#40FF00"
    if d:
        yield "#20FF00"
    yield "#00FF00"
    if d:
        yield "#00FF20"
    if c:
        yield "#00FF40"
    if d:
        yield "#00FF60"
    if b:
        yield "#00FF80"
    if d:
        yield "#00FFC0"
    if c:
        yield "#00FFBF"
    if d:
        yield "#00FFDF"
    yield "#00FFFF"
    if d:
        yield "#00DFFF"
    if c:
        yield "#00BFFF"
    if d:
        yield "#00A0FF"
    if b:
        yield "#0080FF"
    if d:
        yield "#0060FF"
    if c:
        yield "#0040FF"
    if d:
        yield "#0020FF"
    yield "#0000FF"
    if d:
        yield "#2000FF"
    if c:
        yield "#4000FF"
    if d:
        yield "#6000FF"
    if b:
        yield "#8000FF"
    if d:
        yield "#A000FF"
    if c:
        yield "#BF00FF"
    if d:
        yield "#DF00FF"
    yield "#FF00FF"
    if d:
        yield "#FF00DF"
    if c:
        yield "#FF00BF"
    if d:
        yield "#FF00A0"
    if b:
        yield "#FF0080"
    if d:
        yield "#FF0060"
    if c:
        yield "#FF0040"
    if d:
        yield "#FF0020"
        
def zyklus(zahl=6):
    ausgabe = 0x0
    
    uebergang = (2**np.log2((zahl/6)) - 1) * 2
    ue2 = int(((zahl/6)-1)*2)
    
    logzahl = np.log2(zahl/6)
    
    print ("zahlsqrtzeug", np.log2((zahl/6)), ue2)
    
    zy = int((zahl-ue2)/2)
    print ("anzahl 0/f", zy)   
    
    uebergangssummand = 0xff
    for j in range(int(logzahl)):
        uebergangssummand /= 2
    uebergangssummand = int(uebergangssummand)
    print ("ue2", ue2, "logzahl", logzahl, "zy", zy, "ueber", hex(uebergangssummand))
    for i in range(zy):
        yield ausgabe
    for i in range(ue2):
        ausgabe += uebergangssummand
        yield ausgabe
    for i in range(zy):
        yield ausgabe
    for i in range(ue2):
        ausgabe -= uebergangssummand
        yield ausgabe
    

    # erstelle liste mit peakdaten zur gegebenen simulationsliste und plotte für diese das zeit/breiten- bzw zwei/skew-verhältnis
def plot_simulations(sim_list):
    """Erstelle diverse Plots"""
    plotkram.plot_widthmap(sim_list)
    peak_data = []
    sims = []
    filename = "l" + str(length) + "n" + str(number) + "_peakdaten"
    for sim in sim_list:
        width, heigth, ls = peak_width.fpwahph(sim.times, 50, False, sim.params)
        skew = scipy.stats.skew(sim.times)
        pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], skew)
        #willkürlich gewählt: loc <> xy, scale < z width < v...
        if ls[0] < 240 and ls[1] < 60 and width < 50 and ls[0] > 0:
            peak_data.append(pd)
            sims.append(sim)
            #print ("pd", pd)
            #with open(filename, "r+") as data:
             #   x = data.read()
               # print (data, x)
                #data.write(str(pd) + '\n')         
    if len(peak_data) > 0:
        plt.show()
    logging.log(25, "plotte Groessenverhaeltnisse")
    #print ("pd", peak_data)
    filename += ".p"
    with open(filename, "wb") as data:
        pickle.dump(peak_data, data)
    peak_width.plot_relation(filename)
    logging.log (15, "plot1 fertig")
        
    # und jetzt noch ein Spektrum mit max 48 Chroms
    if len(sims) < 29:
        figg = plt.figure()
        legende = list()
        pp = list()
        time_max = 0
        colors = my_magic_color_generator(len(sims))
        plt.ylim((0, 1))
        plt.xlim((0, 250))
        for i, si in enumerate(sims):
            logging.log(24, "simparams: %s, peakdaten %s, max %f", si, pd, max(si.times))
            if (si.pd[0][0]<240 and si.pd[0][0]>0.01):
                time_max = max(time_max, max(si.times))
                n, bins, patches = plt.hist(si.times, 50, normed=1, color = next(colors), alpha=0.5)
                pp.append(patches[0])
                legende.append(str(round(si.params[0], 10)) + ' ' + str(round(si.params[1], 10)))        
        plt.suptitle("l:" + str(length) + " n:" + str(number))
        figg.legend(pp, legende)
        plt.show()    
        
        # evtl noch ein Spektrum mit hinzugefuegten Rauschen und ohne farbliche Unterscheidung
        if len(sim_list) < 25:
            noise = []
            for i in range(int(number*len(sim_list)/10)):
                #noise.append(random.uniform(0, round(time_max)))
                noise.append(random.uniform(0, 240))
            for sim in sim_list:
                for t in sim.times:
                    noise.append(t)
            plt.hist(noise, 500, normed = 1, alpha = 0.6)
            #plt.show()

    return sim_list

def combine_params(args, kwargs = 5):
    pkombis = []
    if not args:
        args = "choice"
    print ("args", args)
    if args == "choice":                    
        schrittweite = 0.0002
        ps_catalogue = np.arange(0.989, 0.991, schrittweite)
        pm_catalogue = np.arange(0.990, 0.999, schrittweite*10)
        
        for zahl in range(kwargs):
                pm = random.choice(ps_catalogue)
                ps = random.choice(pm_catalogue) 
                pkombis.append((ps, pm))
        logging.log(25, pkombis)        
  
    # unglaublich viele ;)        
    if args == "viele":
        schrittweite = 0.0004
        px = np.arange(0.993, 0.997, schrittweite)
        for ps in px:
            for pm in px:
                pkombis.append((ps, pm))
        
        schrittweite = 0.0001
        px = np.arange(0.999, 0.9999, schrittweite)
        for ps in px:
            for pm in px:
                pkombis.append((ps, pm))
        
        '''px = np.arange(0.998, 0.9992, schrittweite)
        for ps in px:
            for pm in px:
                pkombis.append((ps, pm))'''
        
        schrittweite = 0.00001
        px = np.arange(0.9999, 0.99993, schrittweite)   
        for ps in px:
            for pm in px:
                pkombis.append((ps, pm))
                
        '''px = np.arange(0.9998, 0.99991, schrittweite)
        for ps in px:
            for pm in px:
                pkombis.append((ps, pm))'''
        pkombis.reverse()
        print (len(pkombis))
    
    if args == "viele005":
        schrittweite = 0.0001
        ps_catalogue = np.arange(0.999, 0.99999, schrittweite)
        
        schrittweite = 0.01
        pm_catalogue = np.arange(0.01, 0.15, schrittweite)
        
        pkombis = []
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                pkombis.append((ps, pm))
       
    
    #festgelegte auswahl
    if args == "auswahl":
        pkombis = [(0.99999, 0.99995),(0.995, 0.99),(0.9995, 0.999),(0.999, 0.995)]
        # pkombis = [(0.995, 0.995),(0.9997, 0.9995),(0.9995, 0.9999),(0.9999, 0.9995)]
        # pkombis = [(0.995, 0.999),(0.999, 0.9995),(0.995, 0.995),(0.9999, 0.9995)]
            
        pkombis = [(0.9996, 0.99992),  (0.998, 0.992),(0.997, 0.99),(0.996, 0.99),  (0.998, 0.991)]
        
        pkombis = [(0.99999, 0.99999), (0.999999999, 0.999999999), (0.99999999, 0.999999), (0.99999999, 0.9999999)]
        pkombis = [(0.99992, 0.3),(0.99992, 0.2), (0.99992, 0.1),(0.99992, 0.05)]
     #   pkombis = [(0.999, 0.5), (0.999, 0.1), (0.999, 0.01), (0.999, 0.001), (0.999, 0.0001), (0.999, 0.00001), (0.999, 0.000001), (0.9999, 0.5), (0.9999, 0.1), (0.9999, 0.01), (0.9999, 0.001), (0.9999, 0.0001), (0.9999, 0.00001), (0.9999, 0.000001), (0.99992, 0.5), (0.99992, 0.1), (0.99992, 0.01), (0.99992, 0.001), (0.99992, 0.0001), (0.99992, 0.00001), (0.99992, 0.000001), (0.99994, 0.1), (0.99994, 0.01), (0.99994, 0.001), (0.99994, 0.0001), (0.99994, 0.00001), (0.99994, 0.000001), (0.99996, 0.1), (0.99996, 0.01), (0.99996, 0.001), (0.99996, 0.0001), (0.99996, 0.00001), (0.99996, 0.000001), (0.999, 0.999), (0.001, 0.001), (0.5, 0.5), (1, 1)]

    
    # groessere auswahl
    if args == "einige": 
        ps_catalogue = [0.992, 0.9992, 0.99992]
        pm_catalogue = [0.99, 0.9, 0.7, 0.5, 0.1, 0.01, 0.001]
        
       # pkombis.append((1, 1))
        for ps in ps_catalogue:
            for pm in pm_catalogue:
                pkombis.append((ps, pm))
        #pkombis = sorted(pkombis)
    
    #ps oder pm fest, das andere variabel
    if args == "d1":
        ps_catalogue = [0.99, 0.991, 0.992, 0.993, 0.994, 0.995, 0.996, 0.997, 0.998, 0.999]# 0.9992, 0.9993, 0.9994,0.9995, 0.9996]#,0.9997, 0.9998, 0.9999,0.99991, 0.99992, 0.99993, 0.99994]
        #ps_catalogue = [0.1*ps + 0.9 for ps in pm_catalogue]
        #ps_catalogue = np.array(ps_catalogue)*0.1
        #ps_catalogue += 0.9
        pm = 0.993
        for ps in ps_catalogue:
           pkombis.append((ps,pm))
      
    # ps und pm abhängig  
    if args == "d2":
        ps_catalogue = [ 0.991, 0.993, 0.995, 0.997, 0.999, 0.9992, 0.9994, 0.9996]#,0.9997, 0.9998, 0.9999]
        pm_catalogue = [ 0.1*((1/ps)-1) + ps for ps in ps_catalogue]
#        for ps in ps_catalogue:
#            for pm in pm_catalogue:
#                pkombis.append((ps, pm))
        for i in range(len(ps_catalogue)):
            print (ps_catalogue[i]-pm_catalogue[i], 1/ps_catalogue[i])
            pkombis.append((ps_catalogue[i], pm_catalogue[i]))
        logging.log(25, pkombis)     
    
    # auf festes ps und pm wird was drauf addiert
    if args == "d3":
        sdditor = np.array([0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09])*0.001
        mdittor = np.array([0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09])*0.001
        ps = 0.99
        pm = 0.993
        for s, m in zip(sdditor, mdittor):
            pkombis.append((ps+s, pm+m))
       
    #  fuenf irgendwie zufaellige  ps und pm > 0.99
    if args == "5random":
        while len(pkombis) < 5:
            ps = np.random.random()
            pm = random.random()
            if ps > 0.999:# and pm > 0.99:
                pkombis.append((round(ps, 10), round(pm, 10)))
        
    if args == "wdh":#???
        pkombis = [(0.995, 0.991)]
    logging.log(25, "pkombis %s, anzahl: %s", pkombis, len(pkombis))
    return (sorted(list(set(pkombis))))

    # Updatet von alter Version
def update_sim(aSim):
    width, heigth, ls = peak_width.fpwahph(aSim.times, 50, False, aSim.params)
    pd = (ls, width, heigth)
    aSim.set_pd(pd)
    return aSim

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "beschreibung") 
    p.add_argument("--choice", "-c",
                   help = "zufaellige auswahl von n pkombis")
    p.add_argument("--viele", "-v", dest = "anoption",  
                   help = "eine sehr große Menge")
    p.add_argument("--auswahl1", "-a", dest = "anoption",
                   help = "eine festgelegte auswahl an kombis")
    p.add_argument("--einige", '-e', dest = "anoption",
                   help = "eine festgelegte, aber sehr große auswahl an kombis")
    p.add_argument("--dependency1", '-d1', dest = "anoption", 
                   help = "pm fest, ps variabel")
    p.add_argument("--dependency2", "-d2", dest = "anoption", 
                   help = "ps abhängig von pm")
    p.add_argument("--dependency3", "-d3", dest = "anoption", default = "dependency3",
                   help = "ps und pm fest plus unterschiedlichem offset")
    p.add_argument("--number", "-n", type = int, default = "5",
                   help = "how many choices to create")
    p.add_argument("--pkombioption", "-p",  
                   help = "Wie sollen die ps/pm-Kombinationen gewaehlt werden")
    
    p.add_argument("--test", "-atgfjzfjzf", action = "store_true", help = "plot a heatmap from single file with multiple simulations")
    return p

def main():
    startzeit = time.clock()
    logging.log(35, time.strftime("%d%b%Y_%H:%M:%S"))
    
    p = get_argument_parser()
    args = p.parse_args()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke, in mikrometern
    global length, number
    length = 200000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    
    # Die Simulationen werden hier zwischengespeichert
    ergebnisse = []
    
    #liste aller zu simulierenden kombis erstellen
    pkombis = combine_params(args.pkombioption, args.number)
    #pkombis.reverse()
    
    # nr_todo: wie viele noch nicht bearbeitet, nr_ready: wie viele schon fertig
    nr_todo, nr_ready = len(pkombis), 0
    for ps, pm in pkombis:
            logging.log(24, "ps, pm, %(ps)f %(pm)f", locals())
            # gehe erst mal davon aus, dass Sim vorhanden ist, daher nicht speichern
            store = False
            try:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                logging.log(15,"filename: %s", filename)
                with open(filename, 'rb') as data:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(data)
                    logging.log(20, mySim)
                    # test, ob aktuelle version. Im Moment nicht nötig, aber schmeißt noch AttributeError, wenn nicht vorhanden, sodass Dinge nachberechnet werden können, spaeter kann hier weitere versionanpassung rein
                    if mySim.version < 4.1:
                        logging.log(31, "alte version")
                        mySim = update_sim(mySim)
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename schon laenge und anzahl drin sind
                    if (not mySim.length == length) or (not mySim.number == number):
                        logging.warn('neue Sim nötig, da l/n oder so falsch,')
                        store = True
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                        mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, 
                                                      simulate(round(ps, 10), round(pm, 10), length, np.zeros(number), np.array([True]*number))) 
            
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim = update_sim(mySim)
                
            # nicht vorhanden, daher neue Sim machen
            except IOError:
                store =  True
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
                mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, 
                                              simulate(round(ps,10), round(pm, 10), length, np.zeros(number), np.array([True]*number)))
                width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                pd = (ls, width, heigth)
                mySim.set_pd(pd)
            
            # komischer Fehler, im Zweifel wohl auch neu simulieren ? TODO
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(35, err)
                time.sleep(20)
                
            nr_todo -= 1
            nr_ready += 1 
            ergebnisse.append(mySim)
            logging.log(20, "peakdaten: ls, b, h: %s", mySim.pd)
            if store:
                filename = 'v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(ps,10)) + '_' + str(round(pm,10)) + ".p" 
                logging.log(25, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                with open(filename, 'wb') as data:
                    pickle.dump(mySim, data)
                

    # Den Counter für spätere Verwendung zwischenspeichern,
    #filename = 'einetimesliste' + ".p" 
    #with open(filename, 'wb') as data:
        #print "speicherer", ergebnisse[3].times
    #    pickle.dump(ergebnisse[3].times, data)
    
    #Die Zeit- Hoehen/skew- Plots und Spektrum erstellen:
    ergebnisse = plot_simulations(ergebnisse)  
 
    # Ende :)
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=25)
    main() 
