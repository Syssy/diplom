#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Weiterverarbeitung einer PAA-Simulation aus Julia
#TODO: mosdi-kompatibel machen?

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
        self.pd = self.calculate_pd()
        self.times = self.compress(comp_factor)
        self.version = version
    
    def compress(self, comp_factor = 1000):
        '''Fasst Datenpunkte zusammen'''
        #print ("compress, argmax vorher", np.argmax(self.times))
        comp_probs = []
        for j in range((len(self.times)//comp_factor)): # zb len(times) = 20000, factor = 100 -> j in range von 20
            secsum = 0
            for i in range(comp_factor): # i in range von 100
                secsum += self.times[j*comp_factor + i] # zugriff auf i + j * faktor
            comp_probs.append(secsum) 
        #print ("compress, argmax nachher", np.argmax(comp_probs)) 
        return comp_probs
    
    def calculate_pd(self):
        '''Berechne Peakdaten: Maximalzeitpunkt, Quartile, IQR und IQK'''
        #times = np.array(self.times)
        times = np.array(self.times)
        #print ("laenge", len(self.times))
        # wsumme ist Summe aller W'keiten, soll 1 sein, ist aber auf Grund von Rundungsungenauigkeiten oft nicht so
        wsumme = sum(times)
        if wsumme < 0.99:
            print ("Summe der Wahrscheinlichkeiten zu gering, moeglicherweise ragt Peak ueber die Maxtime ", self.maxtime, " hinaus")
            iqr, qk = float("nan"), float("nan")
            return ([np.argmax(times), [float("nan"), float("nan"), float("nan")], float("nan"), float("nan")]) 
        #print ("summe", wsumme)
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
        peakdata = ([(np.argmax(times)/10000), quartiles, iqr, qk]) 
        #plt.plot(times)
        #plt.show()
        #print ("peakdata", peakdata)
        return peakdata
    
    
def erzeuge_Tabelle(directory, csv_name, time_range = [1,240], iqr_range = [0,50], iqk_range = [0.1,1]):
    '''Tabelle anlegen mit allen Peaks (Sim-Parameter) die die gegebenen Vorgaben (range) erfuellen'''
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    starttime = time.clock()
    peaks_found = []
    print ("erzeuge_Tabelle")
    # Ueberpruefe jeden Peak
    for filename in filenames:
        with open(directory+filename, "rb") as mydata:
            myPAA = pickle.load(mydata)
            params = myPAA.params
            #print (myPAA)
            #time.sleep(1)
            #Ueberpruefung, ob Peak die Vorgaben erfuellt
            if myPAA.pd[0] > time_range[0] and myPAA.pd[0] < time_range[1] and myPAA.pd[2] > iqr_range[0] and myPAA.pd[2] < iqr_range[1] and myPAA.pd[3] > iqk_range[0] and myPAA.pd[3] < iqk_range[1]:
                # Die Peakdaten an die Params dranhaengen, das ganze dann als Zeile der Tabelle
                params.extend([myPAA.pd[0], myPAA.pd[2], myPAA.pd[3]]) 
                # params.extend(myPAA.pd)
                peaks_found.append(params)
                #plt.show()
    print ("zeit", time.clock() - starttime)       
    # Abspeichern der Tabelle als csv Datei
    with open(csv_name, 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        #mywriter.writerows (tabelle)
        print ("Anzahl gefundener Peaks", len(peaks_found))
        for i in range(len(peaks_found)):
            mywriter.writerow(peaks_found[i])
    print ("fertig mit Tabelle")  
    return peaks_found


def plotte_Zeitpunkt(directory, time_range = [1,240], iqr_range = [0,100], iqk_range = [0,1]):
    '''Alle zu geg Zeit/IQR/IQK gefundenen Peaks plotten'''
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    tabellenname = "xy_" + str(time_range[0]) + "_" + str(time_range[1]) + "_" + str(iqr_range[0]) + "_" + str(iqr_range[1]) + "_"+  str(iqk_range[0]) + "_" + str(iqk_range[1]) + ".csv"
    peaks_found = []
    if os.path.exists(tabellenname):
        print (tabellenname)
        with open (tabellenname, "r", newline='') as csvfile:
            myreader = csv.reader(csvfile)
            for line in myreader:
               # print (line)
                peaks_found.append([float(x) for x in line])
    else:
        peaks_found = erzeuge_Tabelle(directory, tabellenname, time_range, iqr_range, iqk_range)
    
    starttime = time.clock()
    fig = plt.figure()
    plt.suptitle("Zeit: " + str(time_range) + " IQR: " + str(iqr_range) + " IQK: " + str(iqk_range))
    # der Übersicht halber für alle vier relevanten Parameter ein Plot, jeden Plot anlegen
    ax0 = fig.add_subplot(221)
    ax0.set_title("pmm")
    plt.ylabel("Schiefe (IQK)")
    ax1 = fig.add_subplot(222)
    ax1.set_title("pml")
    ax2 = fig.add_subplot(223)
    ax2.set_title("paa")
    plt.xlabel("Breite (IQR)")
    plt.ylabel("Schiefe (IQK)")
    ax3 = fig.add_subplot(224)
    ax3.set_title("pll")
    plt.xlabel("Breite (IQR)")
    ax = [ax0, ax1, ax2, ax3]
    for peak in peaks_found:
        #print (peak)
        #TODO: Die markersize sinnvoll nutzen
        # TODO: Sinnvolle Kennzeichung über formen und farben der punkte
        for i, j in enumerate([0, 2, 4, 8]):
            ax[i].plot([peak[10]], [peak[11]], "go", markersize = 2*abs(np.median([time_range[1], time_range[0]])-peak[9]))
            t = ax[i].text(peak[10], peak[11], str(peak[j]), size= "small")
    plt.show()

def plot_single_peak(filename):
    '''Einzelnen Peak plotten'''
    with open (filename, "rb") as data:
        aPeak = pickle.load(data)
        plt.plot(aPeak.times)
        hoehe = np.max(aPeak.times)
        plt.plot([aPeak.pd[1][0] * 10, aPeak.pd[1][0] * 10], [0, hoehe])
        plt.plot([aPeak.pd[1][1] * 10, aPeak.pd[1][1] * 10], [0, hoehe])
        plt.plot([aPeak.pd[1][2] * 10, aPeak.pd[1][2] * 10], [0, hoehe])
        
        plt.title(filename)
        print (aPeak.pd)
        print (aPeak.params)
        plt.show()
    return

def plot_peak_from_uncompressed(filename):
    print ("start plot uncompressed")
    with open (filename, "r") as data:
        times = [float(x) for x in data]       
        params = [float(p) for p in filename[25:].split("_")]
        print (params)
        aPAA = PAA(params, 1000, times)
        print ("ohne compress:", aPAA.pd, len(aPAA.times))
        print ("nach compress:", aPAA.calculate_pd(), len(aPAA.times))
        plt.plot(times)
        plt.show()
        plt.plot(aPAA.times)
        plt.show()
        print ("ende uncompressed")
    return

def plot_3feste_Params(directory, pmm = [], pml = [], paa =[], pll=[], variabel = "pmm"):
    '''drei Parameter bleiben fest, einer wird verändert (im sinnvollen bereich), alle Params werden als Liste übergeben, die festen halt mit nur einem Element, der veränderliche mit mehreren
    evtl: erzeuge Liste mit noch nicht für diesen Plot vorhandenen Simulationen'''
        #TODO: Flexibler machen für verschiedene feste Params
        #TODO TODO
    mydict = {"pmm": pmm, "pml": pml, "paa": paa, "pll": pll}
    dict2 =  {"pmm": 0, "pml": 2, "paa": 4, "pll": 8}
    print (mydict)
    myPAA_list, todolist = [], []
    #Zugriffsnummer des variablen Parameters
    vp = dict2[variabel]
    #print ("nummer", vp)
    
    for p1 in pmm:
        for p2 in pml:
            for p3 in paa:
                for p4 in pll:
                    filename = "Sim_" + str(p1) + "_"+ str(p2) + "_" + str(p3) + "_" + str(p4) + ".p"
                    myPAA_list.append(filename)
    #print (myPAA_list)
    for filename in myPAA_list:
        if os.path.exists(directory + filename):
            #print (filename)
            with open (directory + filename , "rb" ) as data:
                myPAA = pickle.load(data)
                print("pd, params", myPAA.pd, myPAA.params)
                if myPAA.pd[2] == myPAA.pd[2]:
                #plt.set_label(str(myPAA.params[0]) + str(myPAA.pd[0]))
                    # Achsen x:Breite, y:Schiefe
                    #plt.plot([myPAA.pd[2]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[0]/10), label=str(myPAA.params[vp]) +" "+ str(myPAA.pd[0]) )
                    #plt.text(myPAA.pd[2], myPAA.pd[3], str(myPAA.params[vp]))
                    # Achsen x:Zeitpunkt, y:Schiefe
                    plt.plot([myPAA.pd[1][1]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[2]), label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[2],2)) )
                    plt.text(myPAA.pd[1][1], myPAA.pd[3], str(myPAA.params[vp]))
                    # Achsen: x:Zeitpunkt, y:Breite
                    #plt.plot([myPAA.pd[0]],[myPAA.pd[2]], "o", markersize = (myPAA.pd[3]*10), label=str(myPAA.params[vp]) +" "+ str(myPAA.pd[3]) )
                    #plt.text(myPAA.pd[0], myPAA.pd[2], str(myPAA.params[vp]))
        else:
            todolist.append(filename)
    #plt.xlabel("Breite (IQR)")
    plt.xlabel("Zeitpunkt")
    #plt.ylabel("Breite (IQR)")
    plt.ylabel("Schiefe (IQK)")
    print ("todolist", todolist)   
    del mydict[variabel]
    plt.suptitle("fest:" + str(mydict) + "\n variabel: " + variabel)
    plt.legend(title= variabel+ ",  breite", numpoints = 1, loc = 4)
    plt.show()    
    return

def umbenennen(directory):
    '''Unbenennung der Sim-Namen'''
    filenames = [name for name in os.listdir(directory) if name.startswith("sim_")]
    for filename in filenames:
        print (filename)
        newfilename = ""
        with open (directory + filename, "rb") as data:
            aPAA = pickle.load(data)
            params = aPAA.params
            newfilename = "Sim_" + str(params[0]) + "_" + str(params[2]) + "_" + str(params[4]) + "_" + str(params[8]) + ".p"
            print (newfilename)
        os.rename(directory+filename, directory+newfilename)
  
def main():
    source_directory = "savedata_julia/l1000/"
    dest_directory = "savedata_python/l1000/"
    fig_dir = "savefigs_python/l1000"
    #filenames.reverse()
    #umbenennen(dest_directory)
    
    #pmm = [0.8]
    #pmm = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    pmm = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    pml = [0.001]
    #pml = [0.005, 0.003, 0.001, 0.0007, 0.0005, 0.0003, 0.0001, 0.00005]
    paa = [0.9985]
    #paa = [0.997, 0.998, 0.9985, 0.999, 0.9992, 0.9993, 0.9994, 0.9995, 0.9996]
    pll = [0.99999]
    #pll = [0.9999, 0.999925, 0.99995, 0.999975, 0.99999, 0.999993, 0.999995, 0.999997, 0.999999]
    
   # plot_3feste_Params(dest_directory, pmm, pml, paa, pll, "pmm")
    
   # param = [0.4, 0.0001, 0.999, 0.99995]
   # filename = dest_directory + "Sim_" + str(pmm[0]) + "_" + str(pml[0]) + "_" + str(paa[0]) + "_" + str(pll[4]) + ".p"
   # filename = dest_directory + "Sim_0.55_0.0005_0.997_0.999997.p"
    
  #  filename2 = source_directory+ "Sim_0.4_0.59995_5.0e-5_0.0019999743_0.998_0.0_5.0008297e-5_0.0_0.99995"
  #  plot_single_peak(filename)
    #plot_peak_from_uncompressed(filename2)
   # plotte_Zeitpunkt(dest_directory, [15,195], [1,20], [0.5,1])  
    
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    for filename in filenames:   
        params = [float(p) for p in filename[4:].strip(".p").split("_")]   
        newfilename = "Sim_" + str(params[0]) + "_" + str(params[2]) + "_" + str(params[4]) + "_" + str(params[8]) + ".p"
        if not os.path.exists(dest_directory+newfilename):
            with open (source_directory + filename , "r" ) as data:
                print(filename)
                times = [float(x) for x in data]
                params = [float(p) for p in filename[4:].split("_")]
                aPAA = PAA(params, 1000, times)
                with open(dest_directory+newfilename, "wb") as savedata:
                    pickle.dump(aPAA, savedata)
    ##erzeuge_Tabelle(dest_directory, "mycsv.csv", [40,60], [1,20])
    print ("Fertig")    
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()      