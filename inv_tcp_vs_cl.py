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
import math

#Required inscluction for running the scriptwithout error
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
         traversed forward to optimize the fit. Press ENTER for DEFAULT.
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


print("Enter the filename or press enter for tcp_vs_cl.xlsx file: ")
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
#no of total elements in whole dataframe
#tot_elements = d.size
#No of elements in a row
#no_row = d['cl'].size
#print(no_row)
#anything above is not required as row will give the no of values in the cl

#Taking the user input considering the default value
try:
    print("\nEnter the approx breaking point value it will be optimized forwards: ")
    clb = int(input("Enter the approx breaking point value it will be optimized forwards: "))
except:
    print("\nsome invalid input is enterd.....")
    print("Going for the default value as max of cl and move forward for optimization")
    clb = int(d['cl'].iloc[3])

try:
    print("\nEnter the chi_sq value near by 0.15: ")
    chi_user = float(input("Enter the chi_sq value near by 0.15: "))
except:
    print("\nsome invalid input is enterd.....")
    print("choosing default value of chi_sq as 0.15")
    chi_user = 0.15
    
#adding a standard deviation column for better fit
std = 0.5
op_std = std + rand(row)*std/10
d['op_std'] = op_std

#Define the break up point
#cause we are trying to maximize the fit of line as per lomash sir procedure
#that's why looping is changed here as line fits from back so we move forward
while clb < int(d['cl'].iloc[-2]):

  #changed in equality than cl as model1 will be fitted on the initial data
  d1 = d.loc[d['cl'] >= clb]
  d2 = d.loc[d['cl'] <  clb]

  ##After taking the seperate range for data for model1 and model2

  #  Fit by equation

  # setting up the model equation
  #please note that change model also in print statement
  def model1(x,m,p):
      return m*x+p

  def model2(x,a,b,c):
      return a+sqrt(b+(c*x))

  # Going with fit
  #initially guessing the values diiferent based on different condition
  init_guess_m1 = [1,1]

  init_guess_m2 = [-5000,1e7,1e5]

  #fit = curve_fit(model, d['cl'],d['tcp'],sigma=d['s_tcp'], p0=init_guess, absolute_sigma=True)
  #fit for model 1
  fit1 = curve_fit(model1, d1['cl'],d1['tcp'], p0=init_guess_m1)
#  fit1 = curve_fit(model1, d1['cl'],d1['tcp'], sigma=d1['op_std'], absolute_sigma=True, p0=init_guess_m1)

  #fit for model 2
  fit2 = curve_fit(model2, d2['cl'],d2['tcp'], p0=init_guess_m2)
#  fit2 = curve_fit(model2, d2['cl'],d2['tcp'], sigma=d2['op_std'], absolute_sigma=True, p0=init_guess_m2)


  # unpacking the fit results for model1:
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

  #checking for validity of fit of model1
  if ((chisq1 > chi_user)):
    print("Could not optimize on clb value: %.1f" %clb)
    clb = clb + 2
    if clb > int(d['cl'].iloc[-3]):
        print("\n\nModel can not be optimized for the taken chi_sqr value kindly increase it")
        print("Exitiing....")
        sys.exit()
        
    continue
  else:
    print("Optimized clb value: %.1f"%clb)
    break

# printing the fit results for model1:
print("\nModel1: y=mx+p ")
print("m: %.2f +/- %.2f"%(fit_m,fit_sm))
print("p: %.2f +/- %.2f"%(fit_p,fit_sp))

# printing the fit results model2:
print("\nModel1: y= a+sqrt(b+(c*x))")
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
  figtext(0.5, 0.5, "FAILED!! :-( ")

print("\nWriting output file to output_tcp_vs_cl.xlsx")
d_op.to_excel('output_tcp_vs_cl.xlsx')
print("\nsaving the figure as tcp_vs_cl.png")
savefig('tcp_vs_cl.png', dpi=400)