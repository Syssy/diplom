# -*- coding: utf-8 -*-

from   struct import calcsize
from   struct import unpack
from   struct import pack
import sys
import matplotlib.patches as pat
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
import itertools
import numpy as np
#import scipy.stats as stats
#import statsmodels.api as sm
    
def to_float(value):
    
    if value == 0: return 0
    val = (value & 32768) << 16;
    val |= (((value >> 10) & 31) + 112) << 23;
    val |= (value & 1023) << 13;
    s = pack('>I', val)
    return unpack('>f', s)[0]
            
class imsFile:
    def __init__(self, filename):
        self.filename = filename
        filetype = filename.split(".")[-1].lower()
        self.scale_retention = 0
        self.points = list()
        self.scale_drift = list()
        self.scale_correction = list()
        self.strValLines = list()
        self.floatValLines = list()
        self.ret = 0
        self.drift = 0
        self.extent = [0, 0, 0, 0]
        strPos = [0, 1, 2, 3, 4, 6, 7, 8, 13, 14, 15, 16, 17, 24, 25, 26, 30, 49, 51, 53, 55, 56, 60, 67, 75, 80, 88, 89, 99]
        floatPos  = [18, 19, 28, 29, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 50, 52, 54, 56, 58, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 81, 82, 83, 84, 85, 86, 87, 90, 91, 92, 93, 94, 100, 101, 102, 103, 104, 105, 107, 108, 109, 110, 111, 112, 114, 115, 116, 119]
        with open(filename, mode="rb") as f:
            if filetype == "csv":
            
                i = -1
                for line in f:
                    i += 1
                    linie = str(line.strip(), encoding="utf8")
                    num_lines = 0;
                    if len(linie) < 2: continue
                    qsp = linie.split(",")
                                    
                    if i == 130:
                        self.scale_retention = [float(x) for x in qsp[2:len(qsp) - 1]]
                    
                    elif i == 132:
                        self.scale_drift.append(float(qsp[0]))
                        self.scale_correction.append(float(qsp[1]))
                        # zweite Spalte: driftzeit
                        for ii in range (2, len(qsp) - 1):
                            tmp = float(qsp[ii])
                            tmp = -tmp if (tmp < 0) else 0
                            lst = list()
                            lst.append(tmp)
                            self.points.append(lst)
                    
                    
                    elif i > 132:
                        self.scale_drift.append(float(qsp[0]))
                        self.scale_correction.append(float(qsp[1]))
                        
                        for ii in range (2, len(qsp) - 1):
                            tmp = -float(qsp[ii])
                            #tmp = -tmp if (tmp < 0) else 0
                            self.points[ii - 2].append(tmp)

                    
                    else:
                        if floatPos.count(i) > 0 and len(qsp) > 2:
                            self.floatValLines.append(float((qsp[2].split(";"))[0]))
                            
                        if strPos.count(i) > 0 and len(qsp) > 2:
                            self.strValLines.append(qsp[2])
                            
                self.ret = len(self.scale_retention)
                self.drift = len(self.scale_drift)
                            
                            
                            
            elif filetype == "ims":
                data = f.read(3)
                # Länge und Strings einlesen
                for i in range(29):
                    data = f.read(2)
                    length = unpack("<h", data)[0]
                    data = f.read(length)
                    self.strValLines.append(unpack("<" + str(length) + "s", data)[0])
                    
                #Floats einlesen
                for i in range(64):
                    data = f.read(4)
                    self.floatValLines.append(unpack("<f", data)[0])
                
                data = f.read(2)
                self.ret = int(unpack("<h", data)[0])
                data = f.read(2)
                self.drift = int(unpack("<h", data)[0])
                
                
                data = f.read(1)
                bytesize = ord(unpack("<c", data)[0])
                

                # Inverse Mobilitätsskale einlesen
                for i in range(self.drift):
                    data = f.read(4)
                    self.scale_drift.append(unpack("<f", data)[0])

                # Driftzeitskala einlesen
                for i in range(self.drift):
                    data = f.read(4)
                    self.scale_correction.append(unpack("<f", data)[0])
                   
                # Punkte einlesen
                self.scale_retention = list()
                for i in range(self.ret):
                    # Retentionszeitskala einlesen
                    data = f.read(4)
                    self.scale_retention.append(unpack("<f", data)[0])
                    
                    self.points.append(list())
                    for j in range(self.drift):
                        data = f.read(bytesize)
                        if bytesize == 4:
                            a = unpack("<f", data)[0]
                            self.points[i].append(-a)
                        elif bytesize == 2:
                            a = unpack("<h", data)[0]
                            self.points[i].append(-1. * to_float(a))
                            
            self.extent[0] = self.scale_correction[0]
            self.extent[1] = self.scale_correction[-1]
            self.extent[2] = self.scale_retention[0]
            self.extent[3] = self.scale_retention[-1]

def sig(zahl):
    
    result = 0
    if zahl != 0:
        result = (zahl*0.0024617)/4.9456
    
    return result
            
## main script
if __name__ == "__main__":
    
    #filename = r"/home2/kopczyns/ims-repo/NI.csv"
    if len(sys.argv) < 2:
        print("usage: python3 py_visualize.py measurement")
        exit()
    filename = sys.argv[1]
    a = imsFile(filename)
    print (a.points)
    
    
    
    
    cdict = {'red':   ((0.0, 1.0, 1.0),
                (0.05, 0.0, 0.0),
                (0.1, 1.0, 1.0),
                (0.2, 1.0, 1.0),
                (0.6, 1.0, 1.0),
                (1.0, 1.0, 1.0)),

        'green': ((0.0, 1.0, 1.0),
                (0.05,0.0, 0.0),
                (0.1, 0.0, 0.0),
                (0.2, 0.0, 0.0),
                (0.6, 1.0, 1.0),
                (1.0, 1.0, 1.0)),

        'blue':  ((0.0, 1.0, 1.0),
                (0.05, 1.0, 1.0),
                (0.1, 1.0, 1.0),
                (0.2, 0.0, 0.0),
                (0.6, 0.0, 0.0),
                (1.0, 0.0, 0.0))}

    cmap = mplc.LinearSegmentedColormap('ims_colormap',cdict,256)
    axis = plt.gca().set_color_cycle(['black', 'DarkGray', 'green', 'brown'])
    #plt.text(1.0, 300.0, filename )
    marker = ['.', '*', 'x', '+']
    # Matrix in RxT
    
   # print (a.points)
    
    #print (a)
    newl = np.array(a.points)
    #print (len(a.points[0]), type(a.points[0]))
    #print (np.shape(newl))
    #print (sig(newl[245][1476]),sig(newl[250][801]),sig(newl[240][1476]), sig(newl[235][14]))
   # print (a.points[250])
  #  chrom = list()
    # betrachte ein einzelnes Chromatogram/Spektrum
   # for i in range(len(newl)):
    #    wert = newl[i][1476]
        #print (wert, end=",")
     #   chrom.append(wert)
    
   # plt.plot(chrom)
    #print (newl[1500])
    aspec = newl[244]#[1455:1540]
    aspeclist = list()
   # print (aspec)
    for i in range(len(aspec)):
        zahl = aspec[i]
        for j in range(int(zahl-2)):
            aspeclist.append(i+1000)
   # n, bins, patches = plt.hist(aspeclist, 200, normed=1, alpha=0.5 )
  #  plt.plot(aspec)
    #sm.qqplot(aspeclist, scipy.stats.invgauss, fit = True , line = 'r')
    #print (aspeclist)
   # plt.show()       
    
    maxi = 0
    lala = []
   # for i in range(244,245):
    #    for j in range(2399):
     #       maxi = max(maxi, sig(newl[i][j]))
      #      lala.append(sig(newl[i][j]))
      #      print (newl[i][j], end=' ')
     #   print ('\n')
    #print(maxi)
   # print ("lala,", lala)
    
   # plt.plot(np.linspace(0,100, len(lala)), lala)
   # plt.plot(lala, color = "r")
    #points = [[sig(x) for x in y] for y in a.points]
    #print (points, 'points')
    
    #fig, ax = plt.subplots() 
    #print (a.points, a.extent)
    #cax = ax.imshow(a.points, interpolation="nearest", origin="lower",vmin=0, vmax=100, cmap=cmap, extent = a.extent, aspect="auto") 
    #cbar = fig.colorbar(cax)
    #plt.subplots_adjust(left=0.02, bottom=0.02, right=1, top=1, wspace=None, hspace=None)
    #plt.legend()
     
    # Matrix in RxT
    plt.imshow(a.points, interpolation="nearest", origin="lower",vmin=0, vmax=100, cmap=cmap, extent = a.extent, aspect="auto")      
    #plt.subplots_adjust(left=0.02, bottom=0.02, right=1, top=1, wspace=None, hspace=None)
    plt.legend()
    #fig.set_title("hall")
    plt.show(block=True)
   
    