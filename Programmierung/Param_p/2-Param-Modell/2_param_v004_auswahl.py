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

#Simuliert einen Schritt für alle Teilchen
def simulatestep(ps, pm, teilchenort, teilchenmobil, number):
   # print teilchen, number
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
def simulate(ps, pm, length, teilchenort, teilchenmobil):
    # Hauptschleife, hier wird simuliert
    startzeit = time.clock()
    #print "Teste jetzt: ", round(ps,6), round (pm,6), '  ',
    hilfscounter = []
    zeit = 0
    number = len(teilchenort)
 
    #Teil 1: Sim bis Länge, hier muss noch keine Abbruchbed. getestet werden
    while zeit < length/10000:
        teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
        zeit += 0.0001

    logging.log(20, "Teil1 vorbei")
    #Teil 2: Ab jetzt können Teilchen fertig sein
    while True:
    # Damit es schneller geht, nach je x schritten nur testen
        for x in range (100):
            teilchenort, teilchenmobil = simulatestep(ps, pm, teilchenort, teilchenmobil, number)
            zeit+=0.0001

        # d ist bitmaske aller aktuell angekommenen Teilchen
        d = teilchenort <= length*1
        logging.log(10, teilchenort)
        logging.log(10,d)
        logging.log(10, zeit)
        # die beiden aktualisieren (rauswerfen aller fertigen teilchen)
        teilchenort = teilchenort[d]
        teilchenmobil = teilchenmobil[d]   
        #zähle (suminvert...) wie viele schon durch, hänge deren zeiten an
        for j in range (np.sum(np.invert(d))):
            hilfscounter.append(zeit)

        # alle teilchen angekommen :)
        number = len(teilchenort)
 
        if number < 1:
            logging.log(25, "fertig")
            break
        if zeit > 700:
            for j in range(len(teilchenort)):
                hilfscounter.append(zeit+50)
            break    

    #print time.clock()-startzeit
    return hilfscounter

def statistische_Berechnungen(liste):
    peakdaten = []
    ergebnisse = []
    filename = "l" + str(length) + "n" + str(number) + "_peakdaten"
    i = 0
    for sim in liste:
    #while len(peakdaten) < 5:
       # sim = liste[i]
        breite, hoehe, ls = peak_width.fpwahph(sim.times, 50, True, sim.params)
        skew = scipy.stats.skew(sim.times)
        pd = (sim.params, ls, breite, hoehe, skew)
        if ls[0] < 650 and ls[1] < 40 and ls[0] > 120 and breite < 140:
            peakdaten.append(pd)
            with open(filename, "r+") as datei:
                x = datei.read()
               # print (datei, x)
                datei.write(str(pd) + '\n')
            ergebnisse.append(sim)
        i += 1    
    print (ergebnisse, len(peakdaten))        
    plt.show()
    logging.log(25, "plotte Groessenverhaeltnisse")
    #print (peakdaten)
    filename += ".p"
    with open(filename, "wb") as datei:
        pickle.dump(peakdaten, datei)
    #peak_width.plot_relation(filename)
    logging.log (15, "plot fertig")
    
    return liste

def main():
    startzeit = time.clock()
    
    # Meine ganzen Variablen, TODO: Soll spaeter mal eingelesen werden
    # Laenge der zu simulierenden Strecke
    global length, number
    length = 1000000
    # Anzahl der zu simulierenden Teilchen
    number = 1000
    # Die Parameter (ps, pm) Damit man was zu vergleichen hat, mehrere davon
    schrittweite = 0.0001
    p1 = np.arange(0.9985, 0.9996, schrittweite)
    p2 = np.arange(0.0005, 0.0016, schrittweite)
    pss = np.concatenate((p2, p1), axis = 0)
    #pss = np.concatenate((pss, [0]), axis =0)
    pms = np.concatenate((p1, p2), axis = 0)
    #pms = np.concatenate((pms, [1]), axis =0)
    #print p1, len(p1), p2, len(p2)
    #print "pss ", pss, len(pss), "\n pms, ", pms, len(pms)
    
    pss=[0.99, 0.9925, 0.995, 0.9975, 0.999, 0.99925, 0.9995, 0.99975, 0.9999, 0.999925, 0.99995, 0.999975, 0.99999]
    pss1=[0.99, 0.992, 0.994, 0.996, 0.998, 0.999, 0.9992, 0.9996, 0.9998, 0.9999, 0.99992, 0.99994, 0.99996, 0.99998, 0.99999, 0.999992]
    pss2 = [0.991, 0.993, 0.995, 0.997, 0.9991, 0.9993, 0.9995, 0.9997, 0.99991, 0.99993, 0.99995, 0.99997, 0.999991, 0.999993]
    #pss=[0.99, 0.995, 0.999, 0.9995, 0.9999, 0.99995, 0.999925, 0.999975, 0.99999]
    pss1.extend(pss2)
    print (sorted(pss1))
    #pss1.reverse()
    pms=[0.9999, 0.9997, 0.99991, 0.9995]
    #pss = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    #pms = np.array([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001, 0.9987, 0.9988, 0.9989, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995])
    
    ##testcounter = np.array([[None]*num_sim]*num_sim)
    #print testcounter, np.shape(testcounter)
    
    pkombis = [(0.99999, 0.99995),(0.995, 0.99),(0.9995, 0.999),(0.999, 0.995)]
   # pkombis = [(0.995, 0.995),(0.9997, 0.9995),(0.9995, 0.9999),(0.9999, 0.9995)]
   # pkombis = [(0.995, 0.999),(0.999, 0.9995),(0.995, 0.995),(0.9999, 0.9995)]
    
    pkombis = [(0.9996, 0.99992),  (0.998, 0.992),(0.997, 0.99),(0.996, 0.99),  (0.998, 0.991)]
   # pkombis = [(0.999991, 0.99999),(0.99996, 0.99991),(0.99998, 0.99998),(0.99998, 0.99999),(0.99997, 0.99999)]#,(0.99999, 0.99998),(0.999991, 0.99999),(0.99999, 0.99999),(0.99995, 0.99991),(0.99994, 0.99991),(0.999991, 0.99998),(0.999992, 0.99999)]
    #pkombis = [(0.0001, 0.0001), (0.00001, 0.00001), (0.0002, 0.0001), (0.0001, 0.0002) ]
    
    testarray = np.array([[None]*len(pss)]*len(pms))

    #print 'pss, pms ', pss, '\n', pms
     #print params
    # Zählt, wie viele Schritte nötig waren, wird eine Liste von Listen, je eine pro gestestetem Parameter
    #counter = []
    ergebnisse = []
    simlist = []
    #for zahl in range(25):
    #        pm = random.choice(pss1)
    #        ps = random.choice(pss1)
    #for ps in pss1:
        #pss.reverse()
       # for pm in pss1:
    for ps, pm in pkombis:
        #logging.log(31, "teste %s, zeit %s", round(pss[i],6), time.strftime("%d%b%Y_%H:%M:%S"))
        #for j in range(len(pms)):
            #ps = pss[i]
            #pm = pms[j]
            logging.log(29, "ps, pm, %s %s", ps, pm)
            speichern = False
            try:
        #TODO hier wird noch auf *.pp getestet, bis die Sim so gut sind, dass ich wieder massensims erstellen kann!
                filename = 'v004/l'+str(length)+"/n"+str(number)+ '/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p" 
                logging.log(15,"filename: %s", filename)
                with open(filename, 'rb') as datei:
                    logging.log(20,"geoeffnet")
                    mySim = pickle.load(datei)
                    logging.log(20, mySim)
                    # Sim mit gleichen Params zwar vorhanden, aber nicht nutzbar, da Länge/Anzahl verschieden
                    if not mySim.length == length or not mySim.number == number:
                        logging.warn('neue Sim nötig, da l/n oder so falsch,')
                        speichern = True
                        # neue Sim nötig
                        logging.log(39, "neue Sim")
                        mySim = simulation.Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
                        #print mySim.times  
            except (IOError, EOFError, UnicodeDecodeError, AttributeError, TypeError):
                speichern =  True
                logging.log(25,"simuliere, da nicht vorhanden")
                mySim = simulation.Simulation(round(ps, 6), round(pm,6), length, number, simulate(ps, pm, length, np.zeros(number), np.array([True]*number)))
                simlist.append(mySim)
            '''breite, hoehe, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
            pd = (mySim.params, ls, breite, hoehe)
            filename = "l" + str(length) + "n" + str(number) + "_peakdaten"
            with open(filename, "r+") as datei:
                x = datei.read()
               # print (datei, x)
                datei.write(str(pd) + '\n')'''
                #counter.append(mySim.times)
                #testcounter.append(mySim.times)
                #testarray[j][i]=mySim
            ergebnisse.append(mySim)
            logging.log(15, mySim.times)
            if speichern:
                filename = 'v004/l'+str(length)+"/n"+str(number)+ '/Sim_'+ str(round(ps,6)) +'_' +  str(round(pm,6))+ ".p" 
                logging.log(20, "Speichern, %s, %s", time.strftime("%d%b%Y_%H:%M:%S"), mySim)
                with open(filename, 'wb') as datei:
                    pickle.dump(mySim, datei)
        #  testarray[i][j]
    
    '''#print testarray
    for s in testarray:
        for t in s:
            if t:
                print t.times'''
    # Den Counter für spätere Verwendung zwischenspeichern,
    #filename = 'einetimesliste' + ".p" 
    #with open(filename, 'wb') as datei:
        #print "speicherer", ergebnisse[3].times
    #    pickle.dump(ergebnisse[3].times, datei)
    
    #Die Peak-Breiten bei halber Maximalhöhe berechnen:
    
    ergebnisse = statistische_Berechnungen(ergebnisse)
    
    
    #filename = 'Sim_'+ time.strftime("%d%b%Y_%H:%M:%S")+".pickle"
    #print filename
    
    #Ausgabe, welche Plots:
    qq_Plot = False
    fit_Plot = False
    histogram_separate = False
    histogram_spec = True
    
    #with open(filename, 'wb') as datei:
     #   pickle.dump(testarray, datei)
  
    #plotkram.plot_file(filename, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    #plotkram.plot(simlist, histogram_separate, histogram_spec, qq_Plot, fit_Plot)
    #plotkram.plot_heatmap_from_file(filename, len(pss), "skewness")
   # n, bins, patches = plt.hist(mySim.times, 100, alpha=0.5 )
   # plt.show()
    
    figg = plt.figure()
    ll = list()
    pp = list()
    maxi = 0
    lines = ["r", "y", "b", "m", "g", "k"] 
    for i in range(len(ergebnisse)):
        si = ergebnisse[i]
        maxi = max(maxi, max(si.times))
        n, bins, patches = plt.hist(si.times, 50, color=lines[i], normed=1, alpha=0.5)
        #l, = plt.plot(x, scipy.stats.invgauss.pdf(x, si.mu, si.loc, si.scale), lines[i], lw = 3, alpha=0.6)
        #ll.append(l)
        pp.append(patches[0])
       #try:
#    logging.info("%s %s", si.params_var, si.velmean)
#except AttributeError:
#    pass
    #print pp    
    #figg.legend([pp[0], pp[1], pp[2], pp[3]], [zufallskombis[0], zufallskombis[1], zufallskombis[2], zufallskombis[3]])
    plt.suptitle("l:" + str(length) + " n:" + str(number))
    figg.legend([pp[0], pp[1], pp[2], pp[3]], [ergebnisse[0],ergebnisse[1],ergebnisse[2],ergebnisse[3]])
    figg.legend([pp[0], pp[1], pp[2], pp[3], pp[4]], [ergebnisse[0],ergebnisse[1],ergebnisse[2],ergebnisse[3], ergebnisse[4]])
    figg.legend(pp, ergebnisse)
    plt.show()    
    
    rauschen = []
    for i in range(int(number/2)):
        rauschen.append(random.uniform(0,round(maxi)))
    for sim in ergebnisse:
        for t in sim.times:
            rauschen.append(t)
    plt.hist(rauschen, 300, alpha = 0.6)
    #plt.show()
    
    
    # Ende :)
    print ("Zeit "+str(time.clock()- startzeit))
    

if __name__ == "__main__":
    logging.basicConfig(level=25)
    main() 
