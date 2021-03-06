@echo off
call C:\ProgramData\Anaconda3\Scripts\activate.bat
call :start

:start
echo --------------------------------------------------------
echo ".....Running Complete Analysis and plotting Tool......"
echo --------------------------------------------------------
echo This script will create all the plots in buffer scripts from its actual text files
echo To successfully running this follow below guidelines
echo Step 1: Put run_em_all.py and batch script in the same folder as the text files
echo Step 2: Run run_em_all and choose 1 to run it
echo choose 0 to exit and report any error to akiitr at git hub
echo --------------------------------------------------------
echo Enter 1: for running run_em_all_buf
echo Enter 2: for running run_em_all_inv
echo Enter 3: for running run_em_all_inv_trail
echo Enter 0: for Exitting.
echo --------------------------------------------------------
SET /P choice="Enter your choice as stated above: "
2>nul call :case_%choice%
if errorlevel 1 call :default #for unidentified input 


:case_1
echo "You have choosen run_em_all_buf.py starting...."
python run_em_all_buf.py
call :start

:case_2
echo "You have choosen run_em_all_inv.py starting...."
python run_em_all_inv.py
call :start

:case_3
echo "You have choosen run_em_all_inv_trial.py starting...."
python run_em_all_inv_trial.py
call :start

:default
echo Unknown entry "%choice%"
call :start

:case_0
echo "Exitting now......."
pause
exit