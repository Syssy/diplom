#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Weiterverarbeitung einer PAA-Simulation aus Julia
#TODO: mosdi-kompatibel machen durch abfrage nach erstem wert der wahrscheinlichkeitsliste

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import os
import csv

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt

class PAA():
    def __init__(self, params, length, times, maxtime = 240, source="julia"):
        self.params = params
        self.length = length
        self.maxtime = maxtime
        self.times = times
        self.source = source
        self.compressed, self.offset = self.compress()
        self.pd = self.calculate_pd()
    
    def compress(self, comp_factor = 1000):
        '''Fasst Datenpunkte zusammen'''
        offset = self.times.pop(0)/comp_factor 
        comp_probs = []
        for i in range(comp_factor):
            secsum = 0
            for j in range((len(self.times)//comp_factor)):
                secsum += self.times[i*(len(self.times)//comp_factor) + j]
            comp_probs.append(secsum)  
        # Bei mosdi sind immer die 0 am Anfang, offset gibt es da nicht
        if self.source != "julia":
            return comp_probs, 0
        return comp_probs, offset
    
    def calculate_pd(self):
        '''Berechne Peakdaten: Maximalzeitpunkt, Quartile, IQR und IQK'''
        #times = np.array(self.times)
        times = np.array(self.compressed)
        # wsumme ist Summe aller W'keiten, soll 1 sein, ist aber auf Grund von Rundungsungenauigkeiten oft nicht so
        wsumme = sum(times)
        if wsumme < 0.99:
            print ("Summe der Wahrscheinlichkeiten zu gering, moeglicherweise ragt Peak ueber die Maxtime %s hinaus", self.maxtime)
            iqr, qk = float("nan"), float("nan")
            return ([self.offset + np.argmax(times), [float("nan"), float("nan"), float("nan")], float("nan"), float("nan")]) 
        print ("summe", wsumme)
        #Quartile berechnen 
        #TODO: Wenn die Quartile nicht ausreichen und beliebige Quantile genutzt werden sollen, Berechnung anpassen
        #TODO: Vorgehen bei Summen != 1?
        p25, i = 0, 0
        quartiles = [0, 0, 0]
        while p25 < 0.25*wsumme:
            p25+= times[i]
            i += 1
        quartiles[0] = i
        p50 = p25
        while p50 < 0.5 * wsumme:
            p50 += times[i]
            i += 1
        quartiles[1] = i
        p75 = p50
        while p75 < 0.75 * wsumme:
            p75 += times[i]
            i += 1
        quartiles[2] = i
        print ("quartile", quartiles)
        # Interquartilsabstand (Breite)
        iqr = (quartiles[2] - quartiles[0])
        # Interquantilskoeffizient (Schiefe)
        qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
        # Lage des Maximums, quartile, iqr, qk
        peakdata = ([self.offset + np.argmax(times), quartiles, iqr, qk]) 
        #plt.plot(times)
        #plt.show()
        return peakdata
    
def main():
    source_directory = "savedata_julia/l1000/"
    
    dest_directory = "savedata_python/l1000/"
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    for filename in filenames:
        print(filename)
        if not os.path.exists(dest_directory+filename+".p"):
            with open (source_directory + filename , "r" ) as data:
                times = [float(x) for x in data]
                params = [float(p) for p in filename[4:].split("_")]
                aPAA = PAA(params, 1000, times)
                with open(dest_directory+filename +".p", "wb") as savedata:
                    pickle.dump(aPAA, savedata)
                    print("...")
        
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 