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
import seaborn

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
    for i in range(len(myIMSFile.points)):
        wert = myIMSFile.points[i][args.drift]
        #print (wert, end=",")
        data.append(sig(wert))
        data2.append(-wert)
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
    print (myIMSFile.points)
    data3 = myIMSFile.points[1037:1105][312:894]      
    print (data3)
    plt.imshow(data3)
    plt.show()
    
    
    #Schiefe berechnen:
    #Maxstelle
    maximalstelle = np.argmax(np.array(data2))
    maximalwert = max(data2)
    print(maximalstelle, maximalwert)
    # Wertehistogramm, mit so vielen Bins wie verschiedene Werte
    n, bins = np.histogram(data2, bins=max(data2)+abs(min(data2)))
    print (n, np.argmax(n))
    # Rauschschwelle: Bestimme Maximalstelle des Wertehistogramms, bei doppeltem Index (soll ja normalverteilt sein) liegt die Schwelle
    rauschschwelle = bins[2*np.argmax(n)]
    plt.hist(data2, bins = max(data2) + abs(min(data2)))
    plt.show()
    # Rausschneiden des Peaks, erst hinten, dann vorne
    for i in range(maximalstelle,len(data2)):
        if data2[i] < rauschschwelle:
            data2 = data2[:i]
            break
    for i in range(maximalstelle, 0, -1):
        if data2[i] < rauschschwelle:
            data2 = data2[i:]
            break
    print (scipy.stats.skew(data2))
    plt.plot(data2)
    plt.show()
    
  
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()
