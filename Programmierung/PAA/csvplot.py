#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Plottet die mosdi-ausgabe

from __future__ import division
import pickle
import logging
import argparse
import time
import math
import os
import csv

import scipy.stats   
#import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt

def plot(filename):
    with open(filename, "r") as data:
        print ("data", data)
        wkeiten, wkeiten2 = [], []
        for i, x in enumerate(data):
            wkeiten.append(float(x))
            if i > 708000 and i < 708200:
                print (i, x)
        #print ("ausschnitt", wkeiten[9990:10010])
        plt.plot(wkeiten)
        plt.show()
        print ("sum, len wkeiten ", sum(wkeiten), len(wkeiten))  
        laenge = len(wkeiten)
        bins = 100
        print (laenge//bins)
        for i in range(bins):
            summe = 0
            for j in range(laenge//bins):
                summe += (wkeiten[(i*(laenge//bins))+j])
            wkeiten2.append(summe)
        print ("wkeiten2", wkeiten2, sum(wkeiten2))    
        plt.plot(wkeiten2)
        plt.show()
    
def erzeuge_Tabelle(directory):
    filenames = [name for name in os.listdir(directory) if name.startswith("Sim_")]
    params = [name[4:] for name in filenames]
    params = [p.split("_") for p in params]
    #params = [[p.strip(" ").split(" ") for p in pp] for pp in params]
    print (params[1])
    newparams = []
    for pkombi in params:
        param = []
        for p in pkombi:
            param.append(float(p))
        newparams.append(param)
    print (newparams)
    for filename in filenames[1:2]:
        print (filename)
        with open(directory+filename, "r") as data:
            reader = csv.reader(data)
            mytimes = []
            for line in reader:
                mytimes.append(line)
            #    print (line)
            #print (mytimes)
            print ("data", data)
            mytimes = np.array(mytimes)
            print (len(mytimes), type(mytimes))
            print ("max", max(mytimes))
            print ("argmax", np.argmax(mytimes[500000:700000]))
            plt.plot(mytimes)
            plt.show()
            
    #TODO aus den Daten die PD, also Loc, IQR und QK 
    with open('mycsvfile.csv', 'w', newline='') as csvfile:
        mywriter = csv.writer(csvfile)
        mywriter.writerows(newparams)
      
      
def main():
    erzeuge_Tabelle("savedata_julia/l1000/")
    time.sleep(20)
    plot("filename")
    #plot("output2")
    with open("filename", "r") as data:
        #print (data)
        wkeiten = data.readline().strip().split(",")
        #print (type(wkeiten[0]))
        #print (wkeiten)
        wkeiten2, wkeiten3 = [], []
        for i in range(len(wkeiten)-1):
            #print(wkeiten[i], type(wkeiten[i]))
            wkeiten2.append(float(wkeiten[i]))
            print(wkeiten2[i], i)
        print (sum(wkeiten2))    
        for i in range(100):
            summe = 0
            for j in range(1000):
                summe += wkeiten2[i*j]
            wkeiten3.append(summe)
        print (wkeiten3)    
        n, bin, patches = plt.hist(wkeiten3, 50)
        plt.show()
       
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main() 
