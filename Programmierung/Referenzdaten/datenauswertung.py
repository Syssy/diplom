#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Berechung der Schiefe/IQR/IQK von Referenzdaten

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import random
import os
import csv

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt

import ims_core

def sig(zahl):
    result = 0
    if zahl != 0:
        result = -(zahl*0.0024617)/4.9456
    
    return result


def calculate_peakdata(aPeak):
    print ("bearbeite Peak: ", aPeak)
    myIMSFile = ims_core.ims(aPeak[0])
    data = np.array(myIMSFile.points)
    # Gewuenschtes Rechteck ausschneiden
    data = data[int(aPeak[10]):int(aPeak[11]), int(aPeak[12]):int(aPeak[13])]
    aPeak[13] = int(aPeak[13])
    # Werte kumulieren
    data = [[-wert for wert in line] for line in data]
    #plt.imshow(data, origin = "lower")
    #plt.show()
    kum_data = []
    for i in range(len(data)):
        kum_data.append(sum(data[i]))
    kum_data = [wert/len(data[0]) for wert in kum_data]
    #plt.plot(kum_data)
    #plt.show()
     #Charakteristika berechnen:
    #Maxstelle
    maximalstelle = np.argmax(np.array(kum_data))
    maximalwert = max(kum_data)
    #print("maximums ", maximalstelle, maximalwert)
    # Wertehistogramm, mit so vielen Bins wie verschiedene Werte
    n, bins = np.histogram(kum_data, bins=max(kum_data)+abs(min(kum_data)))
    #print ("wertehistogramm", n, np.argmax(n))
    # Rauschschwelle: Bestimme Maximalstelle des Wertehistogramms, bei doppeltem Index (soll ja normalverteilt sein) liegt die Schwelle
    rauschschwelle = bins[2*np.argmax(n)]
    #plt.hist(kum_data, bins = max(kum_data) + abs(min(kum_data)))
    #plt.show()
    # Rausschneiden des Peaks, erst hinten, dann vorne
    for i in range(maximalstelle,len(kum_data)):
        if kum_data[i] < rauschschwelle:
            kum_data = kum_data[:i]
            break
    for i in range(maximalstelle, 0, -1):
        if kum_data[i] < rauschschwelle:
            kum_data = kum_data[i:]
            break
    #print ("Peakdaten", kum_data, " summe ", sum(kum_data))    
    wsumme = sum(kum_data)
    print ("Schiefe", scipy.stats.skew(kum_data))
    data5 = []
    for i, n in enumerate(kum_data):
        for j in range(int(n)):
            data5.append(i)
    p25, i = 0, 0
    quartiles = [0, 0, 0]
    while p25 < 0.25*wsumme:
        p25+= kum_data[i]
        i += 1
    quartiles[0] = i
    p50 = p25
    while p50 < 0.5 * wsumme:
        p50 += kum_data[i]
        i += 1
    quartiles[1] = i
    p75 = p50
    while p75 < 0.75 * wsumme:
        p75 += kum_data[i]
        i += 1
    quartiles[2] = i
    print (quartiles)
    print (np.percentile(data5, 25),np.percentile(data5, 50), np.percentile(data5, 75))
    iqr = (quartiles[2] - quartiles[0])
    # Interquantilskoeffizient (Schiefe)
    qk = (quartiles[2] + quartiles[0] - 2*quartiles[1]) / (quartiles[2] - quartiles[0])
    print ("iqr ", iqr, " Iqk ", qk)
    aPeak[2] = iqr
    aPeak[3] = qk
    # die Quartile so zu berechnen liefert sehr ähnliche ergebnisse wie das aufsummieren per hand, so wie es in der sim_PAA gemacht ist
    print ("IQR", (np.percentile(data5, 75) - np.percentile(data5, 25)), "IQK", (np.percentile(data5, 75) + np.percentile(data5, 25) - 2*np.percentile(data5, 50)) / (np.percentile(data5, 75) - np.percentile(data5, 25)))
    plt.plot([np.percentile(data5, 75), np.percentile(data5, 75)], [0,30])
    plt.plot([np.percentile(data5, 25),np.percentile(data5, 25)], [0,30])
    plt.plot([np.percentile(data5, 50),np.percentile(data5, 50)], [0,50])
    plt.hist(data5, bins= len(kum_data))
    #plt.plot(kum_data)
    #plt.show()
   
    return aPeak

# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "beschreibung")  
    p.add_argument("--inputfile", "-i", type = str,  help = "input file (table of peakdata)")
    
    return p

# Nutzung für Testzwecke
def main():
    p = get_argument_parser()
    args = p.parse_args()
    
    pd_table = []
    with open(args.inputfile, "r") as myfile:
        for line in myfile:
            pd_table.append(line.split(";"))
    
    pd_table.pop(0)
    print (pd_table)
    print (pd_table[0][0])
    
    #for peak in pd_table:
        #print ("pd vorher ", peak)
        #peak = calculate_peakdata(peak)
        #print ("pd nachher ", peak)
    pd_table = [calculate_peakdata(peak) for peak in pd_table]
    
    with open ("calc_"+ args.inputfile, "w") as myfile:
        csvwriter = csv.writer(myfile)
        csvwriter.writerows(pd_table)
    #data_files = set([pd_table[i][0] for i in range(len(pd_table))])
    #print (data_files)
    
  
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()
