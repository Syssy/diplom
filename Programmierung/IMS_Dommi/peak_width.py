# -*- coding: utf-8 -*-

from ims_core import *
import sys
import matplotlib.pyplot as plt
import numpy as np

def sig(zahl):
    
    result = 0
    if zahl != 0:
        result = (-zahl*0.0024617)/4.9456
    
    return result


if __name__ == "__main__":
    
    #filename = r"/home2/kopczyns/ims-repo/NI.csv"
    if len(sys.argv) < 2:
        print("usage: python3 py_visualize.py measurement")
        exit()
    filename = sys.argv[1]
    ims_file = ims(filename)
    #print first IMS spectrum
    #print(ims_file.points[0]) 
    chrom = list()
    #print first Chromatogram
    for i in range(len(ims_file.points)):
	#RIP bei ca 800, und Peak bei 1744 (example von Dommi)
        print(ims_file.points[i][1477], end = ",")
        chrom.append(sig(ims_file.points[i][1477]))

    plt.plot(chrom)
    plt.show()