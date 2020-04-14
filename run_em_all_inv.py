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


def tcp_vs_cl_model1_check(d,filename):
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
    
 
    #t = linspace(1,100,50, dtype=int)
    t=array(d['cl'].tolist())
    
    #output from model 1
    y_model1 = model1(t,fit_m,fit_p) 
    
    # computing chi-square
    # Compute the value of Chi-Square goodness of fit test using the following formula:
    # Chi-Square = ( (E-O)**2 / E )
    # Where, Chi-Square = goodness of fit test O= observed value E= expected value
    
    #chisq for model1:
    chisq1 = sum((d['tcp'] - model1(d['cl'],fit_m,fit_p))**2/d['tcp'])
    
    #Processing in a new dataframe for 2% error points which are clb's
    d_op = d
    d_op['y_model1'] = y_model1.tolist()
    
    #calculating the percentage difference for both model from data tcp
    d_op['pcdiff1'] =( abs( d_op['tcp'] - d_op['y_model1']) / d['tcp'] *100)
    
    #Finding the 2% variation point
    cl1 = d_op.loc[(d_op['pcdiff1'] > 0.8) & (d_op['pcdiff1'] < 99)]
    #Definig the averaging the values if multiple values come from selection
    def avg(lst): 
        return sum(lst) / len(lst)
    
    #Getting the average of the cl values to get the idea of their location
    clb1 = avg(cl1['cl'].tolist())
    
    #if cl1 and cl2 are nan that means it is being perfectly fit by single model alone
    #in that case it is better to display a message for same
    if filename != 0:
        errorbar(d['cl'],d['tcp'],fmt='.y', label="Simulation")
        xlabel("cl (ps)")
        ylabel("tcp (ps)")
        plot(t, y_model1, label="model1")
        legend()
        figtext(0.5,0.3,"chi-square1: %.2f"%chisq1,fontweight="bold")
        print("\nWriting output file to " + filename[:-4] + ".xlsx")
        d_op.to_excel(filename[:-4] + '.xlsx')
        print("\nsaving the figure as " + filename[:-4] + ".png")
        savefig(filename[:-4] +'.png', dpi=400)
        #clearing axis and closing files
        cla() #clears the axis
        clf() #clears the figure 
        close() #closes the figure window

    
    if(math.isnan(clb1)):
        cl1 = d_op.loc[d_op['cl'].idxmax()]
        clb1 = cl1['cl']
        print("\nWith given input model1 is self sufficient for fitting data point")
        print("Model Passed..")
        return 1
    else:
        print("Model Failed :-( with clb: %.2f"%clb1)
        return 0  



def tcp_vs_cl(d, filename):

    row, col = d.shape
 
    #Autoamating the task of chossing the trb value and chi_sqr value
    #clb value
    print("Going for the default value as max of cl and move forward for optimization")
    clb = int(d['cl'].iloc[0])       
    
    #adding a standard deviation column for better fit
    std = 0.5
    op_std = std + rand(row)*std/10
    d['op_std'] = op_std
    flag = 0
    #Define the break up point
    #cause we are trying to maximize the fit of line as per lomash sir procedure
    #that's why looping is changed here as line fits from back so we move forward
    while clb < int(d['cl'].iloc[-3]):
    
      #changed in equality than cl as model1 will be fitted on the initial data
      d1 = d.loc[d['cl'] >= clb]
      flag = tcp_vs_cl_model1_check(d1, 0) #0 for no p;otting
      
      if flag == 1:
          break
      else:
          clb = clb + 2
          continue
    print(flag)
    print(clb)
    #Checking for wether it has passed or not
    if ((flag == 1) & (clb == int(d['cl'].iloc[0])) ):
        print ("model 1: y=m*x+p is self sufficient for this data")
        tcp_vs_cl_model1_check(d, filename)
        return
    
    if ((flag == 1) & (clb != int(d['cl'].iloc[0])) ):
        
        print ("model 1: y=m*x+p is ***NOT*** self sufficient for this data")
        
        if (clb < (int(d['cl'].iloc[5])) ):
            print("Extending the model bondary due to min no of point requirement")
            clb = int(d['cl'].iloc[4])
        
        print(clb)
        
        d1 = d.loc[d['cl'] >  clb]
        d2 = d.loc[d['cl'] <= clb]
        
        def model1(x,m,p):
            return m*x+p
        
        def model2(x,a,b,c):
            return a+sqrt(b+(c*x))
        
        init_guess_m1 = [1,1]
        init_guess_m2 = [-5000,1e7,1e5]
        
        fit1 = curve_fit(model1, d1['cl'],d1['tcp'], p0=init_guess_m1)
        #Capturing error in case model 2 doesn't converge
        try:
            fit2 = curve_fit(model2, d2['cl'],d2['tcp'], p0=init_guess_m2)
        except:
            print("model 2 is not converging so going ahead with complete model 1 fit")
            tcp_vs_cl_model1_check(d, filename)
            return
        
        ans,cov = fit1
        fit_m,fit_p = ans
        fit_sm,fit_sp = sqrt(diag(cov))
        
        # unpacking the fit results for model2:
        ans,cov = fit2
        fit_a,fit_b,fit_c = ans
        fit_sa,fit_sb,fit_sc = sqrt(diag(cov))
        
        
        #t = linspace(1,100,50, dtype=int)
        #t = array([int(x*2) for x in range(1, 51)])
        #Best method to calculate the t is to copy x axis from xls data
        t=array(d['cl'].tolist())
        
        #output from model 1
        y_model1 = model1(t,fit_m,fit_p) 
        y_model2 = model2(t,fit_a,fit_b,fit_c)
        
        # computing chi-square
        # Compute the value of Chi-Square goodness of fit test using the following formula:
        # Chi-Square = ( (E-O)**2 / E )
        # Where, Chi-Square = goodness of fit test O= observed value E= expected value
        
        #chisq for model1:
        chisq1 = sum((d1['tcp'] - model1(d1['cl'],fit_m,fit_p))**2/d1['tcp'])
        #chisq for model2:
        chisq2 = sum((d2['tcp'] - model2(d2['cl'],fit_a,fit_b,fit_c))**2/d2['tcp'])

        # printing the fit results for model1:
        print("\nModel1: y=mx+p ")
        print("m: %.2f +/- %.2f"%(fit_m,fit_sm))
        print("p: %.2f +/- %.2f"%(fit_p,fit_sp))
        
        # printing the fit results model2:
        print("\nModel2: y= a+sqrt(b+(c*x))")
        print("a: %.2f +/- %.2f"%(fit_a,fit_sa))
        print("b: %.2f +/- %.2f"%(fit_b,fit_sb))
        print("c: %.2f +/- %.2f"%(fit_c,fit_sc))
        
        # ploting the data and fit results
        errorbar(d['cl'],d['tcp'],fmt='.y', label="data")
        xlabel("cl (ff)")
        ylabel("tcp (ps)")
        
        #changing the x axis for partial plotting of model1 and 2
        t1 = array(d1['cl'].tolist())
        t2 = array(d2['cl'].tolist())
        
        #re claculating the model outputs according to trimmed x axis
        y_model1_temp = model1(t1,fit_m,fit_p) 
        y_model2_temp = model2(t2,fit_a,fit_b,fit_c)
        
        #plotting the result for the models
        plot(t1, y_model1_temp, label="model1")
        plot(t2, y_model2_temp, label="model2")
        legend()
        
        #Adding the chisquare value to figure
        figtext(0.5,0.3,"chi-square1: %.2f"%chisq1,fontweight="bold")
        figtext(0.5,0.2,"chi-square2: %.2f"%chisq2,fontweight="bold")
        
        #Processing in a new dataframe for 2% error points which are clb's
        d_op = d
        d_op['y_model1'] = y_model1.tolist()
        d_op['y_model2'] = y_model2.tolist()
        #y_model1.tolist()
        #y_model1.shape
        #y_model2.shape
        
        #calculating the percentage difference for both model from data tcp
        d_op['pcdiff1'] = ( abs( d_op['tcp'] - d_op['y_model1']) / d['tcp'] *100)
        d_op['pcdiff2'] = ( abs( d_op['tcp'] - d_op['y_model2']) / d['tcp'] *100)
        
        #Finding the 2% variation point
        cl1 = d_op.loc[(d_op['pcdiff1'] > 2) & (d_op['pcdiff1'] < 2.5)]
        cl2 = d_op.loc[(d_op['pcdiff2'] > 2) & (d_op['pcdiff2'] < 2.5)]
        
        #Definig the averaging the values if multiple values come from selection
        def avg(lst): 
            return sum(lst) / len(lst)
        
        #Getting the average of the cl values to get the idea of their location
        clb1 = avg(cl1['cl'].tolist())
        clb2 = avg(cl2['cl'].tolist())
        
        #if cl1 and cl2 are nan that means it is being perfectly fit by single model alone
        #in that case it is better to display a message for same
        if(math.isnan(clb1)):
            print("\nWith given input model1 is self sufficient for fitting data point")
            cl1 = d_op.loc[d_op['pcdiff1'].idxmax()]
            clb1 = cl1['cl']
        
        if(math.isnan(clb2)):
            print("\nWith given input model2 is self sufficient for fitting data point")
            cl2 = d_op.loc[d_op['cl'].idxmax()]
            clb2 =cl2['cl']
        
        #Testing wether the model has passsed or not
        if (clb1 <= clb2):
          print('\nThe model has Passed the test input\n')
          print("clb: %.1f, clb1: %.1f, clb2: %.1f"%(clb, clb1, clb2))
        #  figtext(0.5, 0.5, "Passed")
        else:
          print('\nSorry But your Model FAILED!! :-( \n')
          print("clb: %.1f, clb1: %.1f, clb2: %.1f"%(clb, clb1, clb2))
          #figtext(0.5, 0.5, "FAILED!! :-( ")

        figtext(0.5,0.4, "Optimized clb: %.2f"%clb)

        print("\nWriting output file to " + filename[:-4] + ".xlsx")
        d_op.to_excel(filename[:-4] + '.xlsx')
        print("\nsaving the figure as " + filename[:-4] + ".png")
        savefig(filename[:-4] +'.png', dpi=400)
        #clearing axis and closing files
        cla() #clears the axis
        clf() #clears the figure 
        close() #closes the figure window
        return
    else:
        print("Model is not able to pass from any input leaving this datapoint: %.2f"%filename)



def tcp_vs_tr(d, filename):
    
    row, col = d.shape
    #no of total elements in whole dataframe
    #tot_elements = d.size
    #No of elements in a row
    #no_row = d['cl'].size
    #print(no_row)
    #anything above is not required as row will give the no of values in the cl
       
    #Autoamating the task of chossing the trb value and chi_sqr value
    #Trb value
    print("Going for the default value as max of tr and move backwards for optimization")
    trb = int(d['tr'].iloc[-3])
    #chi_sq value
    print("choosing default value of chi_sq as 0.15")
    chi_user = 0.15 #we can't make it huge as the way pc diff is checkrd from start
    
    #adding a standard deviation column for better fit
    std = 0.5
    op_std = std + rand(row)*std/10
    d['op_std'] = op_std
    
    #Define the break up point
    
    while trb>1:
    
      #changed in equality than cl as model1 will be fitted on the initial data
      d1 = d.loc[d['tr'] <= trb]
      d2 = d.loc[d['tr'] >  trb]
    
      ##After taking the seperate range for data for model1 and model2
    
      #  Fit by equation
    
      # setting up the model equation
      #please note that change model also in print statement
      def model1(x,m,p):
          return m*x+p
    
      def model2(x,a,b):
          return (a*x)+b*sqrt(x)
    
      # Going with fit
      #initially guessing the values diiferent based on different condition
      init_guess_m1 = [1,1]
    
      init_guess_m2 = [-5000,1e7]
    
      #fit = curve_fit(model, d['cl'],d['tcp'],sigma=d['s_tcp'], p0=init_guess, absolute_sigma=True)
      #fit for model 1
      fit1 = curve_fit(model1, d1['tr'],d1['tcp'], sigma=d1['op_std'], absolute_sigma=True, p0=init_guess_m1)
    
      #fit for model 2
      fit2 = curve_fit(model2, d2['tr'],d2['tcp'], sigma=d2['op_std'], absolute_sigma=True, p0=init_guess_m2)
    
      # unpacking the fit results for model1:
      ans,cov = fit1
      fit_m,fit_p = ans
      fit_sm,fit_sp = sqrt(diag(cov))
    
      # unpacking the fit results for model2:
      ans,cov = fit2
      fit_a,fit_b = ans
      fit_sa,fit_sb = sqrt(diag(cov))
    
    
      #t = linspace(1,100,50, dtype=int)
      #t = array([int(x*2) for x in range(1, 51)])
      #Best method to calculate the t is to copy x axis from xls data
      t=array(d['tr'].tolist())
    
      #output from model 1
      y_model1 = model1(t,fit_m,fit_p) 
      y_model2 = model2(t,fit_a,fit_b)
    
      # computing chi-square
      # Compute the value of Chi-Square goodness of fit test using the following formula:
      # Chi-Square = ( (E-O)**2 / E )
      # Where, Chi-Square = goodness of fit test O= observed value E= expected value
    
      #chisq for model1:
      chisq1 = sum((d1['tcp'] - model1(d1['tr'],fit_m,fit_p))**2/d1['tcp'])
      #chisq for model2:
      chisq2 = sum((d2['tcp'] - model2(d2['tr'],fit_a,fit_b))**2/d2['tcp'])
    
      #checking for validity of fit of model1
      if ((chisq1 > chi_user)):
        print("Could not optimize on trb value: %.1f" %trb)
        trb = trb - 3
        if trb < int(d['tr'].iloc[3]):
            print("\n\nModel can not be optimized for the taken chi_sqr value kindly increase it")
            print("Exitiing....")
            sys.exit()
        continue
      else:
        print("Optimized trb value: %.1f"%trb)
        break
    
    # printing the fit results for model1:
    print("\nModel1: y=mx+p ")
    print("m: %.2f +/- %.2f"%(fit_m,fit_sm))
    print("p: %.2f +/- %.2f"%(fit_p,fit_sp))
    
    # printing the fit results model2:
    print("\nModel1: y= (a*x)+b*sqrt(x)")
    print("a: %.2f +/- %.2f"%(fit_a,fit_sa))
    print("b: %.2f +/- %.2f"%(fit_b,fit_sb))
    
    # ploting the data and fit results
    #Important sampling every 10th value by d['tr'].iloc[::10]
    errorbar(d['tr'].iloc[::10],d['tcp'].iloc[::10],fmt='.y', label="Simulation")
    xlabel("tr (ps)")
    ylabel("tcp (ps)")
    
    #changing the x axis for partial plotting of model1 and 2
    t1 = array(d1['tr'].tolist())
    t2 = array(d2['tr'].tolist())
    
    #re claculating the model outputs according to trimmed x axis
    y_model1_temp = model1(t1,fit_m,fit_p) 
    y_model2_temp = model2(t2,fit_a,fit_b)
    
    #plotting the result for the models
    plot(t1, y_model1_temp, label="model1")
    plot(t2, y_model2_temp, label="model2")
    legend()
    
    #Adding the chisquare value to figure
    figtext(0.5,0.3,"chi-square1: %.2f"%chisq1,fontweight="bold")
    figtext(0.5,0.2,"chi-square2: %.2f"%chisq2,fontweight="bold")
    
    #Processing in a new dataframe for 2% error points which are trb's
    d_op = d
    d_op['y_model1'] = y_model1.tolist()
    d_op['y_model2'] = y_model2.tolist()
    #y_model1.tolist()
    #y_model1.shape
    #y_model2.shape
    
    #calculating the percentage difference for both model from data tcp
    d_op['pcdiff1'] = ( abs( d_op['tcp'] - d_op['y_model1']) / d['tcp'] *100)
    d_op['pcdiff2'] = ( abs( d_op['tcp'] - d_op['y_model2']) / d['tcp'] *100)
    
    #Finding the 2% variation point
    cl1 = d_op.loc[(d_op['pcdiff1'] > 2) & (d_op['pcdiff1'] < 2.5)]
    cl2 = d_op.loc[(d_op['pcdiff2'] > 2) & (d_op['pcdiff2'] < 2.5)]
    
    #Definig the averaging the values if multiple values come from selection
    def avg(lst): 
        return sum(lst) / len(lst)
    
    #Getting the average of the cl values to get the idea of their location
    trb1 = avg(cl1['tr'].tolist())
    trb2 = avg(cl2['tr'].tolist())
    
    #if cl1 and cl2 are nan that means it is being perfectly fit by single model alone
    #in that case it is better to display a message for same
    if(math.isnan(trb1)):
        print("\nWith given input model1 is self sufficient for fitting data point")
        cl1 = d_op.loc[d_op['tr'].idxmax()]
        trb1 = cl1['tr']
    
    if(math.isnan(trb2)):
        print("\nWith given input model2 is self sufficient for fitting data point")
        tr2 = d_op.loc[d_op['pcdiff2'].idxmax()]
        trb2 =cl2['tr']
    
    
    #Testing wether the model has passsed or not
    if (trb1 >= trb2):
      print('\nThe model has Passed the test input\n')
      print("trb: %.1f, trb1: %.1f, trb2: %.1f"%(trb, trb1, trb2))
    #  figtext(0.5, 0.5, "Passed")
    else:
      print('\nSorry But your Model FAILED!! :-( \n')
      print("trb: %.1f, trb1: %.1f, trb2: %.1f"%(trb, trb1, trb2))
      #figtext(0.5, 0.5, "FAILED!! :-( ")
    figtext(0.5,0.4, "Optimized trb: %.2f"%trb)  
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