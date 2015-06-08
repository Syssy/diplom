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
import os

import numpy as np
import scipy.stats as stats
import scipy
import matplotlib.pyplot as plt
import statsmodels.api as sm

import plotkram
import simulation
import peak_width


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
    #plotkram.plot_widthmap(sim_list)
    logging.log(25, "starte plotting")
    sims = plotkram.plot_widthandskew(sim_list)
    #peak_data = []
    #sims = []
    #for sim in sim_list:
        #try:
            #pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], sim.skewness)
            ##willkürlich gewählt: loc <> xy, scale < z width < v...
            #if sim.pd[0][0] < 240 and sim.pd[0][1] < 60 and sim.pd[1] < 50 and sim.pd[0][0] > 0:
                #peak_data.append(pd)
                #sims.append(sim)
                ##print ("pd", pd)
                ##with open(filename, "r+") as data:
                ##   x = data.read()
                  ## print (data, x)
                    ##data.write(str(pd) + '\n')    
        #except AttributeError as err:
            #print (sim.params, err)
            #sim.recalculate_moments()
            #with open('v005/l' + str(length) + "/n" + str(number) + '/Sim_' + str(round(sim.params[0], 10)) + 
                      #'_' + str(round(sim.params[1], 10)) + ".p", "wb") as datei:
                #pickle.dump(sim, datei)
            #pd = (sim.params, sim.pd[0], sim.pd[1], sim.pd[2], sim.skewness)
            ##willkürlich gewählt: loc <> xy, scale < z width < v...
            #if sim.pd[0][0] < 240 and sim.pd[0][1] < 60 and sim.pd[1] < 50 and sim.pd[0][0] > 0:
                #peak_data.append(pd)
                #sims.append(sim)
                
    #if len(peak_data) > 0:
        #plt.show()
    #logging.log(25, "plotte Groessenverhaeltnisse")
    ##print ("pd", peak_data)
    #filename = "l" + str(length) + "n" + str(number) + "_peakdaten.p"
    #with open(filename, "wb") as data:
        #pickle.dump(peak_data, data)
    #peak_width.plot_relation(filename)
    #logging.log (15, "plot1 fertig")
        
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
            # teste hier auf bestimmte eigenschaften
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
        px = np.arange(0.9999, 0.99992, schrittweite)   
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
        schrittweite = 0.00001
        ps_catalogue = np.arange(0.99992, 0.99999, schrittweite)
        
        schrittweite = 0.05
        pm_catalogue = np.arange(0.5, 0.99, schrittweite)
        
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
        
        pkombis = [(0.99985, 0.62),(0.99985, 0.63), (0.99985, 0.64), (0.99985, 0.65)]
        pkombis = [(0.99985, 0.3)]
        #pkombis = [(0.99994, 0.85), (0.9999, 0.75),(0.999945, 0.01), (0.9998, 0.4),(0.999825, 0.001), (0.99992, 0.9)]
        #pkombis = [(0.99991, 0.75),(0.99991, 0.76),(0.99991, 0.77),(0.99991, 0.78),(0.99991, 0.79)]

    if args == "auswahl25":  
        pkombis = [(0.99996, 0.9), (0.99996, 0.905),
                   (0.99995, 0.875),(0.99995, 0.876),
                   (0.99994, 0.85), (0.99994, 0.855),
                   (0.99993, 0.825),(0.99993, 0.826),
                   (0.99992, 0.8), (0.99992, 0.802),
                   (0.99991, 0.774), (0.99991, 0.775), (0.99991, 0.776),
                   (0.9999, 0.75),
                   (0.99985, 0.625), (0.99985, 0.626), (0.99985, 0.627), 
                   (0.9998, 0.5), 
                   (0.99975, 0.372), (0.99975, 0.373), (0.99975, 0.374), 
                   (0.9997, 0.25),(0.9997, 0.251),(0.9997, 0.252),
                   (0.9996, 0.001)]
    if args == "auswahl50":
        pkombis = [(0.99998, 0.9), (0.99998, 0.899),
                   (0.999975, 0.86),(0.999975, 0.87),(0.999975, 0.88),(0.999975, 0.89),
                   (0.99997, 0.85), (0.99997, 0.847),(0.99997, 0.848),(0.99997, 0.849),
                   (0.99996, 0.8), (0.99996, 0.85),
                   (0.99995, 0.72),(0.99995, 0.74),(0.99995, 0.76),(0.99995, 0.78),
                   (0.99994, 0.7), (0.99994, 0.71),
                   (0.99993, 0.642), (0.99993, 0.644), (0.99994, 0.646), (0.99994,0.648),
                   (0.99992, 0.6), (0.99992, 0.63),
                   (0.99991, 0.54),(0.99991, 0.55),(0.99991, 0.56),
                   (0.9999, 0.5), (0.9999, 0.51),
                   (0.99989, 0.45),
                   (0.99987, 0.3), (0.99987, 0.33),
                   (0.99985, 0.23),(0.99985, 0.24),(0.99985, 0.25)
            ]
    if args == "auswahl75":
        pkombis = [(0.99997, 0.72),(0.99997, 0.74),(0.99997, 0.76),(0.99997, 0.78),
                   (0.99996, 0.7),
                   (0.99995, 0.61),(0.99995, 0.62),(0.99995, 0.63),(0.99995, 0.64),
                   (0.99994, 0.54),(0.99994, 0.55),(0.99994, 0.56),
                   (0.99993, 0.41),(0.99993, 0.42),(0.99993, 0.43),(0.99993, 0.44),
            ]
    if args == "auswahl100":
        pkombis = [(0.99998, 0.8), (0.99998, 0.801),
                   (0.99997, 0.7), (0.99997, 0.705),
                   (0.99996, 0.6), (0.99996, 0.603),
                   (0.99995, 0.5), (0.99995, 0.501),
                   (0.99994, 0.395), (0.99994, 0.4),
                   (0.99993, 0.295), (0.99993, 0.3),
                   (0.99991, 0.1), (0.99991, 0.105)                   
            ]
        
    if args == "auswahl125":
        pkombis = [(0.99997, 0.626), (0.99997, 0.628), (0.99997, 0.630), (0.99997, 0.632),(0.99997, 0.634),
                   (0.99996, 0.5),
                   (0.99995, 0.353), (0.99995, 0.354), (0.99995, 0.355), (0.99995, 0.356), (0.99995, 0.357), (0.99995, 0.358), 
                   (0.99994, 0.25), (0.99994, 0.2501),
                   (0.99993, 0.12), (0.99993, 0.13), (0.99993, 0.14), 
                   (0.99992, 0.001)
            ]
    
    # groessere  
    if args == "einige": 
        #ps_catalogue = [0.999, 0.9995, 0.9999, 0.99991, 0.99992, 0.99993, 0.99994, 0.99995]
        ps_catalogue = [0.9989, 0.9993, 0.9995, 0.9997]
        pm_catalogue = [0.99, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.01, 0.001, 0.0001]
        
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
        pkombis = [(0.999, 0.999), (0.05, 0.99)]
    
    logging.log(20, "pkombis %s, anzahl: %s", pkombis, len(pkombis))    
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
    p.add_argument("--reverse", "-r", action = "store_true",
                   help = "pkombis von hinten durchtesten")
    
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
    number = 10000
    
    # Die Simulationen werden hier zwischengespeichert
    ergebnisse = []
    
    #liste aller zu simulierenden kombis erstellen
    pkombis = combine_params(args.pkombioption, args.number)
    if args.reverse:
        pkombis.reverse()
    
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
                        mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, "E")
                        mySim.simulate_by_event()
                        width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                        pd = (ls, width, heigth)
                        mySim.set_pd(pd)
                        
            # alte Version, daher aktualisieren
            except AttributeError as err:
                store = True
                logging.log(25, err)
                mySim = update_sim(mySim)
                
            # nicht vorhanden, daher neue Sim machen
            except IOError:
                store =  True
                logging.log(25,"%s, %s, simuliere, da nicht vorhanden, todo %s, ready %s", round(ps, 10), round(pm,10), nr_todo, nr_ready)
                
                mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, "T")
                mySim.simulate_by_event()
                width, heigth, ls = peak_width.fpwahph(mySim.times, 50, False, mySim.params)
                pd = (ls, width, heigth)
                mySim.set_pd(pd)
                mySim.recalculate_moments()
               # mySim = simulation.Simulation(round(ps, 10), round(pm,10), length, number, 
                #                              simulate(round(ps,10), round(pm, 10), length, np.zeros(number), np.array([True]*number)))
            
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
    #ergebnisse = plot_simulations(ergebnisse)  
 
    print(ergebnisse[0].pd)
    n, bins, patches = plt.hist(ergebnisse[0].times, 40, normed=1, alpha=0.5, label = "ps = "+str(ergebnisse[0].params[0])+"\npm = "+str(ergebnisse[0].params[1]))
    plt.xlabel("Zeit")
    plt.ylabel("")
    #print sim_array[i][j].length
    plt.suptitle("Laenge:"+ str(length)+ " Anzahl:"+ str(number))
    plt.legend()
    plt.show()
    print(ergebnisse[1].pd)
    n, bins, patches = plt.hist(ergebnisse[1].times, 40, normed=1, alpha=0.5, label = "ps = "+str(ergebnisse[1].params[0])+"\npm = "+str(ergebnisse[1].params[1]))
    plt.xlabel("Zeit")
    plt.ylabel("")
    #print sim_array[i][j].length
    plt.suptitle("Laenge:"+ str(length)+ " Anzahl:"+ str(number))
    plt.legend()
    plt.show()
    
    
#    plotkram.plot_widthandskew(ergebnisse)
    
    # Ende :)
    print ("Zeit " + str(time.clock()-startzeit))
    
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 
