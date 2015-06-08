#!/usr/bin/env python
# -*- coding: latin-1 -*-

# Ein Versuch, das zwei-Parameter-Modell umzusetzen, Klappe die zweite...
# ps ist Wkeit stationär zu bleiben, wenn ich es schon bin
# pm ist Wkeit mobil zu bleiben, wenn ich es schon bin

import random
import numpy as np
import time
import scipy.stats as stats
import scipy
#import plotkram
import simulation
import pickle
import matplotlib.pyplot as plt
import logging
import peak_width
import argparse

#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil, number):
    zzv = np.random.random(number)
    zzv2 = zzv < ps
    zzv3 = zzv < pm
    
    #berechne neuen Zustand für die Teilchen    
    # vorher mobil und es bleibe (zzv3, pm)
    # oder: war nicht mobil und bleibe nicht (invertiert zu oder)
    mobilneu =  np.bitwise_or(np.bitwise_and(teilchenmobil, zzv3),(np.invert(np.bitwise_or(teilchenmobil, zzv2))))
    # wenn mobil, addiere 1 zum Ort
    teilchenortneu = teilchenort + mobilneu
    
    return teilchenortneu, mobilneu

# simuliert für ps und pm alle teilchen
    # Hauptschleife, hier wird simuliert
def simulate(ps, pm, length, teilchenort, teilchenmobil):
    startzeit = time.clock()
    print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    number = len(teilchenort)
 
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while False:#zeit < length/10000:
        teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
        zeit += 0.00001
        #logging.log(20, "%s %s", length/10000, zeit)
    logging.log(25, "Teil1 vorbei, zeit:%s", zeit)
    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
    # Damit es schneller geht, nach je x schritten nur testen
        for x in range (1000):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
            zeit+=0.0001

        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length*1
        logging.log(10, teilchenort)
        logging.log(10,d)
        logging.log(15, zeit)
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]   
        #zähle (suminvert...) wie viele schon durch, hänge deren zeiten an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)

        # alle teilchen angekommen :)
        number = len(teilchenort)
 
        if number < 1:
            logging.log(25, "fertig, %s, %s", zeit, (time.clock()-startzeit))
            break
        if zeit > 150:
            logging.log(25, "dat bringt nix, %s", (time.clock()-startzeit))
            for j in range(len(teilchenort)):
                hilfscounter.append(zeit+100)
            break    

    #print time.clock()-startzeit
    return hilfscounter

    # erstelle liste mit peakdaten zur gegebenen simulationsliste und plotte für diese das zeit/breiten- bzw zwei/skew-verhältnis
def plotte(liste):
    peakdaten = []
    filename = "l" + str(length) + "n" + str(number) + "_peakdaten"
    for sim in liste:
        breite, hoehe, ls = peak_width.fpwahph(sim.times, 50, False, sim.params)
        skew = scipy.stats.skew(sim.times)
        pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], skew)
        #willkürlich gewählt: loc <> xy, scale < z breite < v...
        if ls[0] < 650 and ls[1] < 60 and breite < 160 and ls[0] > 50:
            peakdaten.append(pd)
            #print ("pd", pd)
            with open(filename, "r+") as datei:
                x = datei.read()
               # print (datei, x)
                datei.write(str(pd) + '\n')         
    if len(peakdaten) > 0:
        plt.show()
    logging.log(25, "plotte Groessenverhaeltnisse")
    #print ("pd", peakdaten)
    filename += ".p"
    with open(filename, "wb") as datei:
        pickle.dump(peakdaten, datei)
    peak_width.plot_relation(filename)
    logging.log (15, "plot1 fertig")
    

    if len(liste) < 25:
        figg = plt.figure()
        legende = list()
        pp = list()
        maxi = 0
        lines = ["r", "y", "b", "m", "g", "k"] 
        for i in range(len(liste)):
            si = liste[i]
            if (si.pd[0][0] < 600):
                maxi = max(maxi, max(si.times))
                n, bins, patches = plt.hist(si.times, 50, normed=1, alpha=0.5)
                #l, = plt.plot(x, scipy.stats.invgauss.pdf(x, si.mu, si.loc, si.scale), lines[i], lw = 3, alpha=0.6)
                #ll.append(l)
                pp.append(patches[0])
                legende.append(str(round(si.params[0], 5))+ ' '+ str(round(si.params[1], 5)))
      
        #print pp    
        #figg.legend([pp[0], pp[1], pp[2], pp[3]], [zufallskombis[0], zufallskombis[1], zufallskombis[2], zufallskombis[3]])
        plt.suptitle("l:" + str(length) + " n:" + str(number))
        #figg.legend([pp[0], pp[1], pp[2], pp[3]], [ergebnisse[0],ergebnisse[1],ergebnisse[2],ergebnisse[3]])
        #figg.legend([pp[0], pp[1], pp[2], pp[3], pp[4]], [ergebnisse[0],ergebnisse[1],ergebnisse[2],ergebnisse[3], ergebnisse[4]])
        figg.legend(pp, legende)
        plt.show()    
        
        rauschen = []
        for i in range(int(number/2)):
            rauschen.append(random.uniform(0,round(maxi)))
        for sim in liste:
            for t in sim.times:
                rauschen.append(t)
        plt.hist(rauschen, 300, alpha = 0.6)
        #plt.show()
    '''
    #Ausgabe, welche Plots:
    qq_Plot = False
    fit_Plot = False
    histogram_separate = False
    histogram_spec = True
    
    #filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+".pickle"
    #print filename
    
    #with open(filename, 'wb') as datei:
    #   pickle.dump(testarray, datei)
    #plotkram.plot_file(filename, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    #plotkram.plot_heatmap_from_file(filename, len(pss), "skewness")
   # plt.show()'''
    return liste

def kombiniere(args, kwargs = 5):
    pkombis = []
    if not args:
        args = "choice"
    print ("args", args)
    if args == "choice":                    
        schrittweite = 0.0002
        pss = np.arange(0.989, 0.991, schrittweite)
        pms = np.arange(0.990, 0.999, schrittweite*10)
        
        for zahl in range(kwargs):
                pm = random.choice(pss)
                ps = random.choice(pms) 
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
   
    #festgelegte auswahl
    if args == "auswahl":
        pkombis = [(0.99999, 0.99995),(0.995, 0.99),(0.9995, 0.999),(0.999, 0.995)]
        # pkombis = [(0.995, 0.995),(0.9997, 0.9995),(0.9995, 0.9999),(0.9999, 0.9995)]
        # pkombis = [(0.995, 0.999),(0.999, 0.9995),(0.995, 0.995),(0.9999, 0.9995)]
            
        pkombis = [(0.9996, 0.99992),  (0.998, 0.992),(0.997, 0.99),(0.996, 0.99),  (0.998, 0.991)]
        
        pkombis = [(0.99999, 0.999999999), (0.1, 0.999999999)]
        
        # pkombis = [(0.999991, 0.99999),(0.99996, 0.99991),(0.99998, 0.99998),(0.99998, 0.99999),(0.99997, 0.99999)]#,(0.99999, 0.99998),(0.999991, 0.99999),(0.99999, 0.99999),(0.99995, 0.99991),(0.99994, 0.99991),(0.999991, 0.99998),(0.999992, 0.99999)]
        #pkombis = [(0.0001, 0.0001), (0.00001, 0.00001), (0.0002, 0.0001), (0.0001, 0.0002) ]
    
    # groessere auswahl
    if args == "einige": 
        ps1=[0.99, 0.992, 0.994, 0.996, 0.998, 0.999, 0.9992, 0.9994, 0.9996, 0.9998, 0.9999, 0.99992, 0.99994, 0.99996, 0.99998, 0.99999, 0.999992]
        ps2 = [0.991, 0.993, 0.995, 0.997, 0.9991, 0.9993, 0.9995, 0.9997, 0.99991, 0.99993, 0.99995, 0.99997, 0.999991, 0.999993]
        #pxs=[0.99, 0.9925, 0.995, 0.9975, 0.999, 0.99925, 0.9995, 0.99975, 0.9999, 0.999925, 0.99995, 0.999975, 0.99999]
        #pss=[0.99, 0.995, 0.999, 0.9995, 0.9999, 0.99995, 0.999925, 0.999975, 0.99999]
        #pss1.reverse()
        ps1.extend(ps2)
        #pms=[0.9999, 0.9997, 0.99991, 0.9995]
        #pss = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
        #pms = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
        for ps in ps1:
            for pm in ps1:
                pk = (ps, pm)
                pkombis.append(pk)
    
    #ps oder pm fest, das andere variabel
    if args == "d1":
        pss = [0.99, 0.991, 0.992, 0.993, 0.994, 0.995, 0.996, 0.997, 0.998, 0.999]# 0.9992, 0.9993, 0.9994,0.9995, 0.9996]#,0.9997, 0.9998, 0.9999,0.99991, 0.99992, 0.99993, 0.99994]
        #pss = [0.1*ps + 0.9 for ps in pms]
        #pss = np.array(pss)*0.1
        #pss += 0.9
        pm = 0.993
        for i in range(len(pss)):
           pkombis.append((pss[i],pm))
      
    # ps und pm abhängig  
    if args == "d2":
        pss = [ 0.991, 0.993, 0.995, 0.997, 0.999, 0.9992, 0.9994, 0.9996]#,0.9997, 0.9998, 0.9999]
        pms = [ 0.1*((1/ps)-1) + ps for ps in pss]
#        for ps in pss:
#            for pm in pms:
#                pkombis.append((ps, pm))
        for i in range(len(pss)):
            print (pss[i]-pms[i], 1/pss[i])
            pkombis.append((pss[i], pms[i]))
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
            if ps > 0.99 and pm > 0.99:
                pkombis.append((round(ps, 5), round(pm, 5)))
        
    if args == "wdh":
        pkombis = [(0.9992, 0.999)]
    logging.log(25, "pkombis %s, anzahl: %s", pkombis, len(pkombis))
    return (sorted(list(set(pkombis))))

    # Updatet von alter Version
def update_sim(aSim):
    breite, hoehe, ls = peak_width.fpwahph(aSim.times, 50, False, aSim.params)
    pd = (ls, breite, hoehe)
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
    
    p = get_argument_parser()
    args = p.parse_args()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    global length, number
    length = 200000
    # Anzahl der zu simulierenden Teilchen
    number = 10000
    
    # Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
    #counter = []
    ergebnisse = []
    
    #liste aller zu simulierenden kombis erstellen
    pkombis = kombiniere(args.pkombioption, args.number)
    #pkombis.reverse()
    
    # todo: wie viele noch nicht bearbeitet, ready: wie viele schon fertig
    todo, ready = len(pkombis), 0
    for ps, pm in pkombis:
            logging.log(24, "ps, pm, %s %s", ps, pm)
            # gehe erst mal davon aus, dass Sim vorhanden ist, daher nicht speichern
            speichern = False
            try:
                filename = 'v004/l'+str(length)+"/n"+str(number)+ '/Sim_'+ str(round(ps,5)) +'_' +  str(round(pm,5))+ ".pp" 
                logging.log(15,"filename: %s", filename)
                with open(filename, 'rb') as datei:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(datei)
                    logging.log(20, mySim)
                    # test, ob aktuelle version. Im Moment nicht nötig, aber schmeißt noch AttributeError, wenn nicht vorhanden, sodass Dinge nachberechnet werden können, spaeter kann hier weitere versionanpassung rein
                    if mySim.version < 4.1:
                        logging.log(31, "alte version")
                        mySim = update_sim(mySim)
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden, sollte nicht vorkommen, da im filename schon laenge und anzahl drin sind
                    if not mySim.length == length or not mySim.number == number:
                        logging.warn('neue Sim nötig, da l/n oder so falsch,')
                        speichern = True
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                        mySim = simulation.Simulation(round(ps, 5), round(pm,5), length, number, "S", simulate(round(ps, 5), round(pm, 5), length, np.zeros(number), np.array([True]*number))) 
            
            # alte Version, daher aktualisieren
            except AttributeError as err:
                speichern = True
                logging.log(25, err)
                mySim = update_sim(mySim)
                
            # nicht vorhanden, daher neue Sim machen
            except IOError:
                speichern =  True
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 5), round(pm,5), todo, ready)
                zeitendings =simulate(round(ps,5), round(pm, 5), length, np.zeros(number), np.array([True]*number))
                n, bins, patches = plt.hist(zeitendings, 50, normed = 1, alpha = 0.5)
                plt.show()
                #mySim = simulation.Simulation(round(ps, 5), round(pm,5), length, number, "S", simulate(round(ps,5), round(pm, 5), length, np.zeros(number), np.array([True]*number)))
                print( peak_width.fpwahph(zeitendings, 50, False))
#                breite, hoehe, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                #print(ls, breite, hoehe)
                #pd = (ls, breite, hoehe)
                #mySim.set_pd(pd)
            
            # komischer Fehler, im Zweifel wohl auch neu simulieren ? TODO
            except (EOFError, UnicodeDecodeError, TypeError)  as err:
                logging.log(35, err)
                time.sleep(20)
                
            todo -= 1
            ready += 1 
            ergebnisse.append(mySim)
            #logging.log(20, mySim.pd)
            if speichern:
                filename = 'v004/l'+str(length)+"/n"+str(number)+ '/Sim_'+ str(round(ps,5)) +'_' +  str(round(pm,5))+ ".p" 
                logging.log(20, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                with open(filename, 'wb') as datei:
                    pickle.dump(mySim, datei)
                

    # Den Counter für spätere Verwendung zwischenspeichern,
    #filename = 'einetimesliste' + ".p" 
    #with open(filename, 'wb') as datei:
        #print "speicherer", ergebnisse[3].times
    #    pickle.dump(ergebnisse[3].times, datei)
    
    #Die Zeit- Hoehen/skew- Plots und Spektrum erstellen:
    n, bins, patches = plt.hist(ergebnisse[0].times, 50, normed=1, alpha=0.5 )
    plt.show()
    
    ergebnisse = plotte(ergebnisse)  
 
    # Ende :)
    print ("Zeit "+str(time.clock()- startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 
