#!/usr/bin/env python
# -*- coding: utf-8 -*- 
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
    version_number = 1.0
    
    def __init__(self, params, length, times, maxtime = 240, source="julia", comp_factor = 1000, version = version_number):
        self.params = params
        self.length = length
        self.maxtime = maxtime
        self.times = times
        self.source = source
        # nur bei Julia:
        if source == "julia":
            self.offset = times.pop(0)/10000
        # Bei mosdi sind immer die 0 am Anfang, offset gibt es da nicht
        else:
            self.offset = 0
        self.pd = self.calculate_pd()
        self.times = self.compress(comp_factor)
        self.version = version
    
    def compress(self, comp_factor = 1000):
        '''Fasst Datenpunkte zusammen'''
        comp_probs = []
        for i in range(comp_factor):
            secsum = 0
            for j in range((len(self.times)//comp_factor)):
                secsum += self.times[i*(len(self.times)//comp_factor) + j]
            comp_probs.append(secsum)  
        return comp_probs
    
    def calculate_pd(self):
        '''Berechne Peakdaten: Maximalzeitpunkt, Quartile, IQR und IQK'''
        #times = np.array(self.times)
        times = np.array(self.times)
        # wsumme ist Summe aller W'keiten, soll 1 sein, ist aber auf Grund von Rundungsungenauigkeiten oft nicht so
        wsumme = sum(times)
        if wsumme < 0.99:
            print ("Summe der Wahrscheinlichkeiten zu gering, moeglicherweise ragt Peak ueber die Maxtime ", self.maxtime, " hinaus")
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
        quartiles[0] = i/10000
        p50 = p25
        while p50 < 0.5 * wsumme:
            p50 += times[i]
            i += 1
        quartiles[1] = i/10000
        p75 = p50
        while p75 < 0.75 * wsumme:
            p75 += times[i]
            i += 1
        quartiles[2] = i/10000
        #print ("quartile", quartiles)
        # Interquartilsabstand (Breite)
        iqr = (quartiles[2] - quartiles[0])
        # Interquantilskoeffizient (Schiefe)
        qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
        # Lage des Maximums, quartile, iqr, qk
        peakdata = ([(self.offset + np.argmax(times))/10000, quartiles, iqr, qk]) 
        #plt.plot(times)
        #plt.show()
        print (peakdata)
        return peakdata
    
    
def erzeuge_Tabelle(directory, csv_name, time_range = [1,240], iqr_range = [0,100], iqk_range = [0,1]):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    starttime = time.clock()
    peaks_found = []
    for filename in filenames:
        params = [float(p) for p in filename[4:].strip(".p").split("_")]
        #print (filename)
        #print (directory + filename)
        with open(directory+filename, "rb") as mydata:
         #   print (mydata)
        #    myPAA = PAA.PAA(params, 1000, [0, 0.5, 0.5])
            myPAA = pickle.load(mydata)
            #print (myPAA)
            #time.sleep(1)
            if myPAA.pd[0] > time_range[0] and myPAA.pd[0] < time_range[1] and myPAA.pd[2] > iqr_range[0] and myPAA.pd[2] < iqr_range[1] and myPAA.pd[3] > iqk_range[0] and myPAA.pd[3] < iqk_range[1]:
                #print ("  passt  ")
                #plt.plot(mytimes)
                params.extend(myPAA.pd) 
                peaks_found.append(params)
                #plt.show()
    print ("zeit", time.clock() - starttime)       
    #TODO aus den Daten die PD, also Loc, IQR und QK 
    with open(csv_name, 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        #mywriter.writerows (tabelle)
        print ("laengen", len(peaks_found))
        for i in range(len(peaks_found)):
            mywriter.writerow(peaks_found[i])
    print ("fertig mit Tabelle")  
    return peaks_found


def plotte_Zeitpunkt(directory, time_range = [1,240], iqr_range = [0,100], iqk_range = [0,1]):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    tabellenname = "xy_" + str(time_range[0]) + "_" + str(time_range[1]) + "_" + str(iqr_range[0]) + "_" + str(iqr_range[1]) + "_"+  str(iqk_range[0]) + "_" + str(iqk_range[1]) + ".csv"
    peaks_found = erzeuge_Tabelle(directory, tabellenname, time_range, iqr_range, iqk_range)
    starttime = time.clock()
    fig = plt.figure()
    ax0 = fig.add_subplot(221)
    ax0.set_title("pmm")
    ax1 = fig.add_subplot(222)
    ax1.set_title("pml")
    ax2 = fig.add_subplot(223)
    ax2.set_title("paa")
    ax3 = fig.add_subplot(224)
    ax3.set_title("pll")
    ax = [ax0, ax1, ax2, ax3]
    for peak in peaks_found:
        print (peak)
        #TODO: Die markersize sinnvoll nutzen
        for i, j in enumerate([0, 2, 4, 8]):
            ax[i].plot([peak[11]], [peak[12]], "go", markersize = (time_range[1]-peak[9]))
            t = ax[i].text(peak[11], peak[12], str(peak[j]), size= "small")
        #for p in peak:
            #print (p)
            #time.sleep(1)
    plt.show()
        
    
def main():
    source_directory = "savedata_julia/l1000/"
    dest_directory = "savedata_python/l1000/"
    fig_dir = "savefigs_python/l1000"
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    #filenames.reverse()
    plotte_Zeitpunkt(dest_directory, [30,70], [1,15], [0.2,1])  
    for filename in filenames:
        if not os.path.exists(dest_directory+filename+".p"):
            print(filename)
            with open (source_directory + filename , "r" ) as data:
                    times = [float(x) for x in data]
                    params = [float(p) for p in filename[4:].split("_")]
                    aPAA = PAA(params, 1000, times)
                    with open(dest_directory+filename +".p", "wb") as savedata:
                        pickle.dump(aPAA, savedata)
    #erzeuge_Tabelle(dest_directory, "mycsv.csv", [40,60], [1,20])
        
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()      