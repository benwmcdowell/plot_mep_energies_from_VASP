# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 12:41:07 2020

@author: Ben
"""
from os import listdir
import matplotlib.pyplot as plt
import getopt
import sys
from numpy import array

def mep_energies(filepath,save,plot_type):
    files=listdir(filepath)
    images=0
    for i in files:
        try:
            if int(i)>images:
                images=int(i)
        except ValueError:
            pass
    images+=1
    #energies and reaction coordinates (rc) are stored as: [[initial energy, final energy] for i in range(images)]
    energies=array([[0.0,0.0] for i in range(images)])
    rc=array([[0.0,0.0] for i in range(images)])
    try:
        for i in range(images):
            with open('./'+str('{:02d}'.format(i))+'/OUTCAR','r') as file:
                for line in file:
                    if 'TOTEN' in line:
                        if i==1:
                            energies[i][0]=float(line.split()[4])
                        energies[i][1]=float(line.split()[4])
                    #the reaction coordinate output using the default VASP optimizer
                    elif 'left and right image' in line:
                        rc[i]=float(line.split()[4])+rc[i-1]
                        if i==images-2:
                            rc[i+1]=float(line.split()[5])+rc[i]
                    #the reaction coordinate output using one of the VTST optimizers
                    elif 'distance to prev, next image' in line:
                        rc[i]=float(line.split()[8])+rc[i-1]
                        if i==images-2:
                            rc[i+1]=float(line.split()[9])+rc[i]
    except IOError:
        print('something wrong with subdirectory OUTCAR files')
        sys.exit(1)
    
    #reaction coordinates are normalized to the range [0,1]
    #energies are plotted relative to the minimum energy among the mep images
    for i in range(2):
        rc[:,i]=rc[:,i]/rc[-1][i]
        energies[:,i]=energies[:,i]-min(energies[:,i])
    
    if save==True:
        with open('./mep_energies','w') as output:
            output.write('initial rc\tfinal rc\tinitial energies\tfinal energies\n')
            for i in range(images):
                output.write(str(rc[i][0])+'\t'+str(rc[i][1])+'\t'+str(energies[i][0])+'\t'+str(energies[i][1])+'\n')
    
    plt.figure()
    if plot_type=='final':
        plt.scatter(rc[:,1],energies[:,1])
    if plot_type=='change':
        plt.scatter(rc[:,0],energies[:,0],label='initial_energy')
        plt.scatter(rc[:,1],energies[:,1],label='final_energy')
    plt.xlabel('reaction coordinate')
    plt.ylabel('energy / eV')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    inputfile='./'
    save=False
    plot_type='change'
    try:
        opts,args=getopt.getopt(sys.argv[1:],'hi:sf',['help','input=','save','final'])
    except getopt.GetoptError:
        print('error in command line syntax')
        sys.exit(2)
    for i,j in opts:
        if i in ['-h','--help']:
            print('input options:\n\t-i, --input\t\tspecify an input path other than current directory\n\t-s, --save\t\trecord output in txt file\n\t-f, --final\t\tplot just the final energies\n\nhelp options:\n\t-h, --help\t\tdisplay this help message')
            sys.exit()
        if i in ['-i','--input']:
            inputfile=j
        if i in ['-s','--save']:
            save=True
        if i in ['-f', '--final']:
            plot_type='final'
    mep_energies(inputfile,save,plot_type)