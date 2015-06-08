#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Berechung der Schiefe von Referenzdaten

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import random
import os

import scipy.stats   
import numpy as np
import matplotlib.pyplot as plt

import simulation_3s as sim 
import ims_core

def sig(zahl):
    result = 0
    if zahl != 0:
        result = -(zahl*0.0024617)/4.9456
    
    return result


# für Kommandozeilentests, Aufruf nur in main()    
def get_argument_parser():
    p = argparse.ArgumentParser(
    description = "beschreibung")  
    p.add_argument("--inputfile", "-i", type = str,  help = "input file (pickled)")
    p.add_argument("--moment", "-m" , default = "skewness", help = "which moment is of interest")
    p.add_argument("--drift", "-d", type = int, help = "Driftzeitpunkt des gewuenschen Chromatogramms")
    #p.add_argument("--recalc", "-rc", type=str, help = "recalculate moments")
    #p.add_argument("--number", "-n", help = "how many files to recalculate")
    
    return p

# Nutzung für Testzwecke
def main():
    p = get_argument_parser()
    args = p.parse_args()
    myIMSFile = ims_core.ims(args.inputfile)
    data, data2 = [], []
    #for i in range(len(myIMSFile.points)):
        #wert = myIMSFile.points[i][args.drift]
        ##print (wert, end=",")
        #data.append(sig(wert))
        #data2.append(-wert)
    #data = [sig(point) for point in myIMSFile.points[1000]]
    #data2 = [-point for point in myIMSFile.points[1000]]
    #print (myIMSFile.points[1000])
    #plt.plot(data2)
    #plt.show()


    #data2 = [dat for dat in data2 if dat > 3]
    #plt.plot(data2)
    #plt.show()
    
    # Einzelpeak:
    #TODO: Einzelpeak isolieren (Auswahl eines Rechtecks per Hand) und zu diesem wie unten das Rauschhistogramm bestimmen. Evtl mal die versch. Retentionszeiten aufsummieren, gucken, ob das einen Unterschied in der Breite/IQR macht
    
    #testdata = [[0, 1, 2, 3, 4],[5, 6, 7, 8, 9],[2, 4, 6, 8, 0],[1, 3, 5, 7, 9],[1, 1, 1, 1, 1]]
    #print (testdata)
    #test2 = testdata[1:41:3]
    #print(test2)
    
    #Einzelpeak aussuchen
    #print (myIMSFile.points)
    data3 = np.array(myIMSFile.points)
    #print (data3)
    #plt.imshow(data3, origin = "lower", interpolation="nearest",vmin=-3, vmax=80)
    #plt.show()
    #data3 = data3[200:1400,1045:1080]
    #data3 = data3[200:1400,1037:1105]
    data3 = data3[200:1400,1057:1059]
    data3 = [[-wert for wert in dings] for dings in data3]
    #print (data4)
    plt.imshow(data3, origin = "lower", interpolation="nearest",vmin=0, vmax=100)
    plt.show()
    
    #aufsummieren
    data4 = []
    for i in range(len(data3)):
        data4.append(sum(data3[i]))
    data4 = [wert/len(data3[0]) for wert in data4]
    plt.plot(data4)
    plt.show()

    
    #Schiefe berechnen:
    #Maxstelle
    maximalstelle = np.argmax(np.array(data4))
    maximalwert = max(data4)
    print(maximalstelle, maximalwert)
    # Wertehistogramm, mit so vielen Bins wie verschiedene Werte
    n, bins = np.histogram(data4, bins=max(data4)+abs(min(data4)))
    print (n, np.argmax(n))
    # Rauschschwelle: Bestimme Maximalstelle des Wertehistogramms, bei doppeltem Index (soll ja normalverteilt sein) liegt die Schwelle
    rauschschwelle = bins[2*np.argmax(n)]
    plt.hist(data4, bins = max(data4) + abs(min(data4)))
    plt.show()
    # Rausschneiden des Peaks, erst hinten, dann vorne
    for i in range(maximalstelle,len(data4)):
        if data4[i] < rauschschwelle:
            data4 = data4[:i]
            break
    for i in range(maximalstelle, 0, -1):
        if data4[i] < rauschschwelle:
            data4 = data4[i:]
            break
    print (data4)    
    print ("Schiefe", scipy.stats.skew(data4))
    data5 = []
    for i, n in enumerate(data4):
        for j in range(int(n)):
            data5.append(i)
    print ("IQR", (np.percentile(data5, 75) - np.percentile(data5, 25)))
    plt.plot([np.percentile(data5, 75), np.percentile(data5, 75)], [0,30])
    plt.plot([np.percentile(data5, 25),np.percentile(data5, 25)], [0,30])
    plt.plot([np.percentile(data5, 50),np.percentile(data5, 50)], [0,50])
    plt.hist(data5, bins= len(data4))
    plt.plot(data4)
    plt.show()
    
  
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()