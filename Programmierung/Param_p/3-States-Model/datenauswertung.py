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
        wert = myIMSFile.points[i][1335]
        #print (wert, end=",")
        data.append(sig(wert))
        data2.append(-wert)
    #data = [sig(point) for point in myIMSFile.points[1000]]
    #data2 = [-point for point in myIMSFile.points[1000]]
    #print (myIMSFile.points[1000])
    plt.plot(data2)
    plt.show()
    print (max(data2))
    plt.hist(data2, bins= max(data2))
    plt.show()
    plt.hist(data, bins = 250)
    plt.show()
    
             
if __name__ == "__main__":
    logging.basicConfig(level=20)
    main()
