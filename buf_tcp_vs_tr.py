#! python3.7
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:13:10 2020

@author: anubhav
"""

#importing the necessary librarires
from pylab import *
from scipy.optimize import curve_fit
import pandas as pd
import sys

#Required instruction for running the scriptwithout error
print("""
      ========= WelCome to Analysis and Plotting Tool v1.0 ====================
      
      This Tool requires following things to run succesfully
      1. This tool is for analyzing the tcp_vs_cl analysis.
      2. Make sure a xlsx file is available in the the same folder as this tool
         containg the tcp values and cl values in the (C:\pythonscrpts\) folder
      3. You will be prompted by giving the filename kindly provide full filename
         along with the file extension.
      4. Two model will be used to fit the curve judiciously if you want to 
         change the model definition you can edit their definition in the
         tcp_vs_cl.py file which conatins model using fun model1 and model2.
         Initial guess values for the fit also can be changed accordingly.
      5. You will be asked to provide the starting breaking point for models
         This breaking point will be optimized to fit the 2% error. By default 
         clb(breaking point) value will be choosen as last value and will be 
         traversed backword to optimize the fit. Press ENTER for DEFAULT.
      6. chi_sq value can be used to increase or decrease the tolerance of variation
         0.15 value corresponds to 2% variation from the data points. By default 
         this value will be 0.15. Press ENTER for DEFAULT.
      7. The pararmeter defined in the model will be at output with std deviation
         along with the user defined model.
      8. With the given chi_sq value the Model's result will be shown either
         Passed or failed with the clb values where the clb values fit the data
         and model optimized clb is given by clb while x% varition clb value for
         model 1 and model 2 will be given by clb1 and clb2 respectively.
      9. At last regardless of model is passed or failed the all calculation
         excel sheet will be dumped in the working directory with the name 
         output_tcp_vs_cl.xlsx please check it to be sure of all calculation and
         report if any bug exists. The plot also will be saved in the same directory
         with name as tcp_vs_cl.png
     10. Hope it's Helpful!!
     
      """)

#reading the excel file
print("Enter the filename or press enter for tcp_vs_cl.xlsx file in next line:")
filename = input("Enter the filename or press enter for tcp_vs_cl.xlsx file: ")

if filename == '':
    filename = "tcp_vs_cl.xlsx"

try:
    d = pd.read_excel(filename)
except:
    print('\nError: File Does not Exist!!')
    sys.exit()
#Text processing on the data using pandas dataframe
#no of row and column
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
    
print("\nWriting output file to output_tcp_vs_cl.xlsx")
d_op.to_excel('output_tcp_vs_cl.xlsx')
print("\nsaving the figure as tcp_vs_cl.png")
savefig('tcp_vs_cl.png', dpi=400)