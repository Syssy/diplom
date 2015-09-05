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
        self.comp_factor = comp_factor
        # pd der Form: (loc, [quartile], iqr, qk)
        self.pd = self.calculate_pd()
        #self.times = self.compress(comp_factor)
        self.version = version
    
    def compress(self, comp_factor = 1000):
        '''Fasst Datenpunkte zusammen'''
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
        times = np.array(self.times)
        # wsumme ist Summe aller W'keiten, soll 1 sein, ist aber auf Grund von Rundungsungenauigkeiten oft nicht so
        wsumme = sum(times)
        if wsumme < 0.99:
            print ("Summe der Wahrscheinlichkeiten zu gering, moeglicherweise ragt Peak ueber die Maxtime ", self.maxtime, " hinaus")
            #iqr, qk = float("nan"), float("nan")
            compressed = self.compress(self.comp_factor)
            return ([np.argmax(compressed)/10, [float("nan"), float("nan"), float("nan")], float("nan"), float("nan")]) 
        print ("summe", wsumme)
        #Quartile berechnen, dabei minimale differenzen zu Summe 1 erlauben
        p25, i = 0, 0
        quartiles = [0, 0, 0]
        while p25 < 0.25*wsumme:
            p25+= times[i]
            i += 1
        #print (p25, i)
        quartiles[0] = i/10000
        p50 = p25
        while p50 < 0.5 * wsumme:
            p50 += times[i]
            i += 1
        #print (p50, i)
        quartiles[1] = i/10000
        p75 = p50
        while p75 < 0.75 * wsumme:
            p75 += times[i]
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
        self.times = self.compress(self.comp_factor)
        # Lage des Maximums, quartile, iqr, qk
        peakdata = ([((np.argmax(self.times))/10), quartiles, iqr, qk]) 
        return peakdata
       
def erzeuge_Tabelle(directory, csv_name, time_range = [0,240], iqr_range = [0,150], iqk_range = [0,1]):
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
            #Ueberpruefung, ob Peak die Vorgaben erfuellt
            if myPAA.pd[0] > time_range[0] and myPAA.pd[0] < time_range[1] and myPAA.pd[2] > iqr_range[0] and myPAA.pd[2] < iqr_range[1] and myPAA.pd[3] > iqk_range[0] and myPAA.pd[3] < iqk_range[1]:
                # Die Peakdaten als Zeile die Tabelle anhaengen
                #print (myPAA)
                params.extend([myPAA.pd[0], myPAA.pd[2], myPAA.pd[3]]) 
                peaks_found.append(params)
    print ("zeit", time.clock() - starttime)       
    # Abspeichern der Tabelle als csv Datei
    #TODO Tabelle in irgendnen ordner packen
    with open(csv_name, 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        print ("Anzahl gefundener Peaks", len(peaks_found))
        for i in range(len(peaks_found)):
            mywriter.writerow(peaks_found[i])
    print ("fertig mit Tabelle") 
    return peaks_found

def plotte_Zeitpunkt(directory, time_range = [0,240], iqr_range = [0,100], iqk_range = [0,1]):
    '''Alle zu geg Zeit/IQR/IQK gefundenen Peaks plotten'''
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    tabellenname = "xy_" + str(time_range[0]) + "_" + str(time_range[1]) + "_" + str(iqr_range[0]) + "_" + str(iqr_range[1]) + "_"+  str(iqk_range[0]) + "_" + str(iqk_range[1]) + ".csv"
    peaks_found = []
    if os.path.exists(tabellenname):
        print (tabellenname)
        with open (tabellenname, "r", newline='') as csvfile:
            myreader = csv.reader(csvfile)
            for line in myreader:
                peaks_found.append([float(x) for x in line])
    else:
        peaks_found = erzeuge_Tabelle(directory, tabellenname, time_range, iqr_range, iqk_range)
        
    starttime = time.clock()
    # Zunaechst ein Plot ohne Parameterbeschriftung
    plt.suptitle("Retentionszeiten von: " + str(time_range[0]) + " bis: " + str(time_range[1]))
    plt.xlabel("Breite (IQR)")
    plt.ylabel("Schiefe (QK)")
    for peak in peaks_found:
        print (peak)
        plt.plot([peak[3]], [peak[4]], "go")
    plt.show()    
    # Vier Plots fuer jeden Parameter, mit Beschriftung
    fig = plt.figure()
    plt.suptitle("Zeit: " + str(time_range) + " IQR: " + str(iqr_range) + " IQK: " + str(iqk_range))
    # der Übersicht halber für alle vier relevanten Parameter ein Plot, jeden Plot anlegen
    ax0 = fig.add_subplot(121)
    ax0.set_title("ps")
    plt.ylabel("Schiefe (IQK)")
    plt.xlabel("Breite (IQR)")
    ax1 = fig.add_subplot(122)
    ax1.set_title("pm")
    plt.ylabel("Schiefe (IQK)")
    plt.xlabel("Breite (IQR)")
    ax = [ax0, ax1]
    for peak in peaks_found:
        #print (peak)
        #TODO: Die markersize sinnvoll nutzen
        # TODO: Sinnvolle Kennzeichung über formen und farben der punkte
        for i, j in enumerate([0, 1]):
            ax[i].plot([peak[3]], [peak[4]], "go")#, markersize = 2*abs(np.median([time_range[1], time_range[0]])-peak[9]))
            t = ax[i].text(peak[3], peak[4], str(peak[j]), size= "small")
    plt.show()

def plot_single_peak(filename, quartiles = True):
    '''Einzelnen Peak und seine Quartile plotten'''
    with open (filename, "rb") as data:
        aPeak = pickle.load(data)
        fig, ax = plt.subplots()
        #print (aPeak.times)
        plt.plot(aPeak.times, label = " ")
        hoehe = np.max(aPeak.times)
        # Quartile mitplotten
        if quartiles:
            plt.plot([aPeak.pd[1][0] * 10, aPeak.pd[1][0] * 10], [0, hoehe])
            plt.plot([aPeak.pd[1][1] * 10, aPeak.pd[1][1] * 10], [0, hoehe])
            plt.plot([aPeak.pd[1][2] * 10, aPeak.pd[1][2] * 10], [0, hoehe])
        #plt.axis([0.0,2400,0.0,0.03])
        plt.title("ps: " + str(aPeak.params[0]) +" pm: " + str(aPeak.params[1])) 
        #ax.set_xticklabels([0, 50, 100, 150, 200])
        plt.legend(title = "loc " + str(round(aPeak.pd[0],2))+ " iqr "+str(round(aPeak.pd[2],2)) + " skew " +str(round(aPeak.pd[3],2)))
        plt.annotate(str(aPeak.pd[0])+str(aPeak.pd[2])+str(aPeak.pd[3]),(aPeak.pd[1][2] * 10, aPeak.pd[1][2] * 10))
        plt.show()
    return

def plot_festen_param(directory, ps, pm, variabel):
    ''' Einen Parameter (fest) vorgeben, den anderen variieren'''
    if variabel == "pm":
        vp = 1
        fest = "ps"
        fester_param = ps
        variable_params = pm
    else:
        vp = 0
        fest = "pm"
        fester_param = pm
        variable_params = ps
    myPAA_list = []
    
    for p0 in ps:
        for p1 in pm:
            filename = "Sim_" + str(p0) + "_"+ str(p1) + ".p"
            myPAA_list.append(filename)
    #print (myPAA_list)
        
    for filename in myPAA_list:
        if os.path.exists(directory + filename):
            with open (directory + filename , "rb" ) as data:
                myPAA = pickle.load(data)
                print("pd, params", myPAA.pd, myPAA.params)
                if myPAA.pd[2] == myPAA.pd[2]:
                    #plt.plot([myPAA.pd[0]],[myPAA.pd[2]], "o", markersize = (myPAA.pd[3])*500, label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[3],3)) )
                    #plt.text(myPAA.pd[0], myPAA.pd[2], str(myPAA.params[vp]))
                    plt.plot([myPAA.pd[0]],[myPAA.pd[3]], "o", markersize = (myPAA.pd[2])*1, label=str(myPAA.params[vp]) +"  "+ str(round(myPAA.pd[2],3)) )
                    plt.text(myPAA.pd[0], myPAA.pd[3], str(myPAA.params[vp]))
    plt.xlabel("Zeitpunkt")
    #plt.ylabel("Breite")   
    plt.ylabel("Schiefe")   
    plt.xlim([0, 200])
    plt.ylim([0, 1])
    plt.legend(title=  variabel + ",  Breite", numpoints = 1, loc = 1)
    
    plt.suptitle("Fester Parameter: " + fest + " = " + str(fester_param[0]))
    figname = variabel + "_fest_" + fest + "_"+ str(fester_param[0]) + ".png"
    plt.savefig(figname, bbox_inches = 'tight')                
    plt.show()
    return
 
def plot_erreichbare_regionen(directory):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    for filename in filenames:
        with open(directory+filename, "rb") as mydata:
            myPAA = pickle.load(mydata)
            # Wenn nicht zu spät und kein Nan
            if myPAA.pd[0] < 240 and myPAA.pd[2] == myPAA.pd[2]:
                point = plt.plot([myPAA.pd[0]], myPAA.pd[2], "ro-")
                t = plt.text(myPAA.pd[0], myPAA.pd[2], str(round(myPAA.params[0],6))+'\n'+str(round(myPAA.params[1],3)), size= "small")
    plt.suptitle("Erreichbare Zeit-Breiten-Kombinationen")
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Breite")
    plt.show()
    return
 

def get_argument_parser():
    p = argparse.ArgumentParser(
        description = "Beschreibung") 
    p.add_argument("--length", "-l", type = int, default = "1000",
                   help = "Laenge der Saeule")
    p.add_argument("--source", "-s", default = "julia",
                   help = "Laenge der Saeule")
    
    p.add_argument("--test", "-t", action = "store_true", help = "nutzlos; Test")
    return p
  
def main():
    
    p = get_argument_parser()
    args = p.parse_args()
    
    source = args.source
    length = args.length
    source_directory = "savedata_"+source+"/l"+str(length)+"/2_states/"
    dest_directory = "savedata_python/l1000/2_states/" + source + "/"
    
    #source_directory = "savedata_java/l999/3s/"
    #dest_directory = "savedata_python/l999/3s/"
    #fig_dir = "savefigs_python/l1000"
   

    filename = dest_directory + "Sim_0.999985_0.99000007.p"
    #plot_single_peak(filename, False)
   # plotte_Zeitpunkt(dest_directory, [0,240], [0,30], [0,1])  
    plot_erreichbare_regionen(dest_directory)
    
    pss = [0.998, 0.999, 0.9992, 0.9994, 0.9996, 0.9999]
    #pss = [0.9995]
    #pms = [0.1, 0.3, 0.5, 0.7, 0.9]
    #pms = [0.9, 0.99, 0.995, 0.999]
    pms = [0.99]
    #plot_festen_param(dest_directory, pss, pms, variabel="ps")
   
    filenames = [name for name in os.listdir(source_directory) if name.startswith("Sim_")]
    print (len(filenames))
    for filename in filenames:
        params = [float(p) for p in filename[4:].strip(".p").split("_")]   
        newfilename = "Sim_" + str(params[0]) + "_" + str(params[1]) + ".p"
        if not os.path.exists(dest_directory+newfilename):
            with open (source_directory + filename , "r" ) as data:
                #print (newfilename)
                print(filename)
                times = [float(x) for x in data]
                params = [float(p) for p in filename[4:].split("_")]
                aPAA = PAA(params, 1000, times)
                with open(dest_directory+newfilename, "wb") as savedata:
                    pickle.dump(aPAA, savedata)
    #erzeuge_Tabelle(dest_directory, "mycsv.csv")
    print ("Fertig")    
        
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()      