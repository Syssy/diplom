#!/usr/bin/env python
# -*- coding: latin-1 -*- 
# Plottet die mosdi-ausgabe

from __future__ import division
import pickle
import logging
import argparse
import time
import math

import scipy.stats   
#import scipy.optimize
import numpy as np
import matplotlib.pyplot as plt

def plot_from_julia(filename):
    with open(filename, "r") as data:
        print (data)
        wkeiten, wkeiten2 = [], []
        for i, x in enumerate(data):
            wkeiten.append(float(x))
            if i > 9990 and i < 10010:
                print (i, x)
        print (wkeiten[9990:10010])
        plt.plot(wkeiten)
        plt.show()
        print (sum(wkeiten), len(wkeiten))  
        laenge = len(wkeiten)
        bins = 100
        print (laenge//bins)
        for i in range(bins):
            summe = 0
            for j in range(laenge//bins):
                summe += (wkeiten[(i*(laenge//bins))+j])
            wkeiten2.append(summe)
        print (wkeiten2, sum(wkeiten2))    
        plt.plot(wkeiten2)
        plt.show()
    
        
def main():
    #plot_from_julia("filename")
    plot_from_julia("output2")
    time.sleep(2)
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
