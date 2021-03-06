#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Weiterverarbeitung einer PAA-Simulation aus Julia/Java für Simulationen mit zwei Zuständen

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import os
import csv

#import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt

#TODO source PAA-Sim bzw MoSDi wäre schöner

class PAA():
    def __init__(self, params, model, length, distribution, maxtime=240, source="julia", comp_factor=1000):
        self.params = params
        self.model = model
        self.length = length
        self.maxtime = maxtime
        self.distribution = distribution
        self.source = source
        self.comp_factor = comp_factor
        # pd der Form: (loc, [quartile], iqr, qk)
        self.pd = self.calculate_pd()
    
    def compress(self, comp_factor=1000):
        '''Fasst Datenpunkte zusammen'''
        comp_probs = []
        for j in range((len(self.distribution)//comp_factor)): # zb len(distribution) = 20000, factor = 100 -> j in range von 20
            secsum = 0
            for i in range(comp_factor): # i in range von 100
                secsum += self.distribution[j*comp_factor + i] # zugriff auf i + j * faktor
            comp_probs.append(secsum) 
        #print ("compress, argmax nachher", np.argmax(comp_probs)) 
        return comp_probs
    
    def calculate_pd(self):
        '''Berechne Peakdaten: Maximalzeitpunkt, Quartile, IQR und IQK, und fasst Daten zusammen'''
        distribution = np.array(self.distribution)
        # wsumme ist Summe aller W'keiten, soll 1 sein, ist aber auf Grund von Rundungsungenauigkeiten oft nicht so
        wsumme = sum(distribution)
        if wsumme < 0.99:
            print ("Summe der Wahrscheinlichkeiten zu gering, moeglicherweise ragt Peak ueber die Maxtime ", self.maxtime, " hinaus")
            #iqr, qk = float("nan"), float("nan")
            self.distribution = self.compress(self.comp_factor)
            return ([np.argmax(self.distribution)/10, [float("nan"), float("nan"), float("nan")], float("nan"), float("nan")]) 
        print ("summe", wsumme)
        #Quartile berechnen, dabei minimale differenzen zu Summe 1 erlauben
        p25, i = 0, 0
        quartiles = [0, 0, 0]
        while p25 < 0.25*wsumme:
            p25+= distribution[i]
            i += 1
        #print (p25, i)
        quartiles[0] = i/10000
        p50 = p25
        while p50 < 0.5 * wsumme:
            p50 += distribution[i]
            i += 1
        #print (p50, i)
        quartiles[1] = i/10000
        p75 = p50
        while p75 < 0.75 * wsumme:
            p75 += distribution[i]
            i += 1
        #print (p75, i)
        quartiles[2] = i/10000
        # Interquartilsabstand (Breite)
        iqr = (quartiles[2] - quartiles[0])
        #print ("iqr", iqr)
        # Quartilskoeffizient (Schiefe)
        try:
            qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
        except ZeroDivisionError as err:
            # Fehler tritt auf, wenn zu viele Teilchen auf einmal, bei extrem hohem pm, schiefe ist dann 0
            print (err)
            print (quartiles)
            qk = 0
        # Nun Daten komprimieren, um Maximalstelle dem optischen Peak entsprechend zu berechnen
        self.distribution = self.compress(self.comp_factor)
        # Lage des Maximums, quartile, iqr, qk
        peakdata = ([((np.argmax(self.distribution))/10), quartiles, iqr, qk]) 
        return peakdata

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "Wandelt Wahrscheinlichkeitslisten (csv) vom PAA in Simulationsobjekte um, komprimiert die Daten") 
    p.add_argument("model", choices = ["2s", "3a"],
                   help = "Modell: 2 oder 3 Zustände (2s/3a)")
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--maxtime", "-m", type = int, default = "240",
                   help = "Maximale Retentionszeit in Sekunden")
    p.add_argument("--source", "-s", choices = ["julia", "PAA-Sim", "P", "paasim", "java", "MoSDi", "mosdi", "M"],  default = "julia",
                   help = "Quelle der PAA-Daten")
    p.add_argument("--output", "-o", action = "store_true",
                   help = "Wenn gewählt, wird zu jeder verarbeiteten Simulation die komprimierte Wahrscheinlichkeitsverteilung ausgegeben")
    return p
  
def main():
    p = get_argument_parser()
    args = p.parse_args()
    
    if args.source in ["julia", "PAA-Sim", "P", "paasim"]:
        args.source = "julia"
    if args.source in ["java", "MoSDi", "mosdi", "M"]:
        args.source = "java"
    
    # Verzeichnis, in dem PAA-Ergebnisse liegen
    source_directory = "savedata_"+ args.source+"/" + args.model +"/l"+str(args.length)+"/"
    # Verzeichnis, in das die Simulationobjekte gespeichert werden
    dest_directory = "savedata_python/"+ args.model+"/l" + str(args.length) + "/from_" + args.source + "/"
    
    # Alle Dateien im Quellordner durchgehen
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    filenames.reverse()
    print ("Anzahl Files: ", str(len(filenames)))
    for filename in filenames:
        params = [float(p) for p in filename[4:].strip(".p").split("_")]   
        if args.model == "2s":
            newfilename = "Sim_" + str(params[0]) + "_" + str(params[1]) + ".p"
        elif args.model == "3a":
            newfilename = "Sim_" + str(params[0]) + "_" + str(params[2]) + "_" + str(params[4]) + "_" + str(params[8]) + ".p"
        elif args.model == "3s":
            newfilename = "Sim_" + str(params[0]) + "_" + str(params[1]) + "_" + str(params[2]) + "_" + str(params[3]) +"_" + str(params[4]) + "_" + str(params[5]) + "_" + str(params[6]) + "_" + str(params[7]) + "_" + str(params[8]) + ".p"
        else:
            logging.log(40, "Aktuell nur Modell 2s, 3s oder 3a verfuegbar")
        # Nur aufbereiten, wenn noch nicht existent    
        if not os.path.exists(dest_directory+newfilename):
            with open (source_directory + filename , "r" ) as data:
                print(filename + " wird umgewandelt")
                distribution = [float(x) for x in data]
                params = [float(p) for p in filename[4:].split("_")]
                aPAA = PAA(params, args.model, args.length, distribution, source = args.source)
                with open(dest_directory+newfilename, "wb") as savedata:
                    pickle.dump(aPAA, savedata)
                if args.output:
                    print ("Verteilung: ", aPAA.distribution)
    print ("Fertig")    
        
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()   
    