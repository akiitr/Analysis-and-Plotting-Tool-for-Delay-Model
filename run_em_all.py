# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 20:18:08 2020

@author: anubhav
"""
#import segment
import os, sys
import pandas as pd
from scipy.optimize import curve_fit
from pylab import *


def tcp_vs_cl(d, filename):
    
    row, col = d.shape
       
    #adding a standard deviation column for better fit
    std = 0.5
    op_std = std + rand(row)*std/10
    d['op_std'] = op_std
    
    #Define the break up point
    def model1(x,m,p):
        return (m*x)+p
    
    # Going with fit
    #initially guessing the values diiferent based on different condition
    init_guess_m1 = [1,100]
    
    #fit for model 1
    fit1 = curve_fit(model1, d['cl'],d['tcp'], sigma=d['op_std'], absolute_sigma=True, p0=init_guess_m1)
    
    # unpacking the fit results for model1:
    ans,cov = fit1
    fit_m,fit_p = ans
    fit_sm,fit_sp = sqrt(diag(cov))
    
    # printing the fit results for model1:
    print("\nModel (m*x)+p")
    print("m: %.2f +/- %.2f"%(fit_m,fit_sm))
    print("p: %.2f +/- %.2f"%(fit_p,fit_sp))
    
    # ploting the data and fit results
    errorbar(d['cl'],d['tcp'],fmt='.y', label="Simulation")
    xlabel("cl (ps)")
    ylabel("tcp (ps)")
    
    #t = linspace(1,100,50, dtype=int)
    t=array(d['cl'].tolist())
    
    #output from model 1
    y_model1 = model1(t,fit_m,fit_p) 
    
    plot(t, y_model1, label="model1")
    legend()
    
    # computing chi-square
    # Compute the value of Chi-Square goodness of fit test using the following formula:
    # Chi-Square = ( (E-O)**2 / E )
    # Where, Chi-Square = goodness of fit test O= observed value E= expected value
    
    #chisq for model1:
    chisq1 = sum((d['tcp'] - model1(d['cl'],fit_m,fit_p))**2/d['tcp'])
    figtext(0.5,0.3,"chi-square1: %.2f"%chisq1,fontweight="bold")
    
    #Processing in a new dataframe for 2% error points which are clb's
    d_op = d
    d_op['y_model1'] = y_model1.tolist()
    
    #calculating the percentage difference for both model from data tcp
    d_op['pcdiff1'] =( abs( d_op['tcp'] - d_op['y_model1']) / d['tcp'] *100)
    
    #Finding the 2% variation point
    cl1 = d_op.loc[(d_op['pcdiff1'] > 2) & (d_op['pcdiff1'] < 3)]
    #Definig the averaging the values if multiple values come from selection
    def avg(lst): 
        return sum(lst) / len(lst)
    
    #Getting the average of the cl values to get the idea of their location
    clb1 = avg(cl1['cl'].tolist())
    
    #if cl1 and cl2 are nan that means it is being perfectly fit by single model alone
    #in that case it is better to display a message for same
    if(math.isnan(clb1)):
        cl1 = d_op.loc[d_op['cl'].idxmax()]
        clb1 = cl1['cl']
        print("\nWith given input model1 is self sufficient for fitting data point")
        print("Model Passed..")
    else:
        print("Model Failed :-( with clb: %.2f"%clb1)
        

    print("\nWriting output file to " + filename[:-4] + ".xlsx")
    d_op.to_excel(filename[:-4] + '.xlsx')
    print("\nsaving the figure as " + filename[:-4] + ".png")
    savefig(filename[:-4] +'.png', dpi=400)
    #clearing axis and closing files
    cla() #clears the axis
    clf() #clears the figure 
    close() #closes the figure window
    return  



def tcp_vs_tr(d, filename):
    
    row, col = d.shape
    
    #adding a standard deviation column for better fit
    std = 0.5
    op_std = std + rand(row)*std/10
    d['op_std'] = op_std
    
    #definig model
    def model2(x,a,b,c):
        return a*x+b*sqrt(x)+c  

    # Going with fit
    #initially guessing the values diiferent based on different condition
    init_guess_m2 = [-5000,1e7,1e5]
    
    #fit for model 2
    fit2 = curve_fit(model2, d['tr'],d['tcp'], sigma=d['op_std'], absolute_sigma=True, p0=init_guess_m2)
    
    # unpacking the fit results for model2:
    ans,cov = fit2
    fit_a,fit_b,fit_c = ans
    fit_sa,fit_sb,fit_sc = sqrt(diag(cov))
    
    # printing the fit results model2:
    print("\nModel: y= a+sqrt(b+(c*x))")
    print("a: %.2f +/- %.2f"%(fit_a,fit_sa))
    print("b: %.2f +/- %.2f"%(fit_b,fit_sb))
    print("c: %.2f +/- %.2f"%(fit_c,fit_sc))
    
    # ploting the data and fit results
    errorbar(d['tr'],d['tcp'],fmt='.y', label="Simulation")
    xlabel("tr (ff)")
    ylabel("tcp (ps)")
    
    #t = linspace(1,100,50, dtype=int)
    t=array(d['tr'].tolist())
    
    #output from model 2
    y_model2 = model2(t,fit_a,fit_b,fit_c) 
    
    plot(t, y_model2, label="model")
    legend()
    
    # computing chi-square
    # Compute the value of Chi-Square goodness of fit test using the following formula:
    # Chi-Square = ( (E-O)**2 / E )
    # Where, Chi-Square = goodness of fit test O= observed value E= expected value
    
    #chisq for model2:
    chisq2 = sum((d['tcp'] - model2(d['tr'],fit_a,fit_b,fit_c))**2/d['tcp'])
    figtext(0.5,0.3,"chi-square: %.2f"%chisq2,fontweight="bold")
    
    #Processing in a new dataframe for 2% error points which are trb's
    d_op = d
    d_op['y_model2'] = y_model2.tolist()
    
    #calculating the percentage difference for both model from data tcp
    d_op['pcdiff2'] =( abs( d_op['tcp'] - d_op['y_model2']) / d['tcp'] *100)
    
    #Finding the 2% variation point
    tr2 = d_op.loc[(d_op['pcdiff2'] > 2) & (d_op['pcdiff2'] < 3)]
    #Definig the averaging the values if multiple values come from selection
    def avg(lst): 
        return sum(lst) / len(lst)
    
    #Getting the average of the tr values to get the idea of their location
    trb2 = avg(tr2['tr'].tolist())
    
    #if tr1 and tr2 are nan that means it is being perfectly fit by single model alone
    #in that case it is better to display a message for same
    if(math.isnan(trb2)):
        tr2 = d_op.loc[d_op['tr'].idxmax()]
        trb2 = tr2['tr']
        print("\nWith given input model is self sufficient for fitting data point")
        print("Model Passed..")
    else:
        print("Model Failed :-( with trb: %.2f"%trb2)
        
    print("\nWriting output file to " + filename[:-4] + ".xlsx")
    d_op.to_excel(filename[:-4] + '.xlsx')
    print("\nsaving the figure as " + filename[:-4] + ".png")
    savefig(filename[:-4] +'.png', dpi=400)
    #clearing axis and closing files
    cla() #clears the axis
    clf() #clears the figure 
    close() #closes the figure window
    return       


#Task 1: try opening all file
#checking for all files in the current working directory
all_files = os.listdir('.')
 
#seperating the text files for tcp and tr format
tr_files = list(filter(lambda x: x[-6 :] == 'ff.txt', all_files))
cl_files = list(filter(lambda x: x[-6 :] == 'ps.txt', all_files))

for x in tr_files:
    with open(x,'r') as fd:
        fobj = fd.read().strip()
    lines = fobj.split('\n')
    tr = []
    tcp = []
    d = pd.DataFrame()
    for line in lines:
        tr.append(float(line.split('\t')[0]))
        tcp.append(float(line.split('\t')[1]))
    
    d['tr'] = tr
    d['tcp']= tcp
    #sending the designed datframe to plotting and anlysis tool
    print("\nGoing for analysis of file: " + x)
    tcp_vs_tr(d,x)
    
for x in cl_files:
    with open(x, 'r') as fd:
        fobj = fd.read().strip()
        lines = fobj.split('\n')
    cl = []
    tcp = []
    d = pd.DataFrame()
    for line in lines:
        cl.append(float(line.split('\t')[0]))
        tcp.append(float(line.split('\t')[1]))
    
    d['cl'] = cl
    d['tcp']= tcp
    #sending the designed datframe to plotting and anlysis tool
    print("\nGoing for analysis of file: " + x)
    tcp_vs_cl(d,x)