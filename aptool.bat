@echo off
call C:\ProgramData\Anaconda3\Scripts\activate.bat
call :start

:start
echo --------------------------------------------------------
echo ".....Running Complete Analysis and plotting Tool......"
echo --------------------------------------------------------
echo Kindly Choose an option from below functions
echo Enter 1: for tcp_vs_cl
echo Enter 2: for tcp_vs_tr
echo Enter 0: for Exitting.
echo --------------------------------------------------------
SET /P choice="Enter your choice as stated above: "
2>nul call :case_%choice%
if errorlevel 1 call :default #for unidentified input 


:case_1
echo "You have choosen tcp_vs_cl starting...."
python tcp_vs_cl.py
echo Close image to continue....
tcp_vs_cl.png
call :start

:case_2
echo "You have choosen tcp_vs_tr starting...."
python tcp_vs_tr.py
echo Close image to continue....
tcp_vs_tr.png
call :start

:default
echo Unknown entry--> "%choice%"
call :start

:case_0
echo "Exitting now......."
pause
exit