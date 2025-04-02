@ECHO off
if exist %UserProfile%\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\anaconda3
) else if exist %UserProfile%\AppData\Local\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\anaconda3
) else if exist %UserProfile%\AppData\Local\Continuum\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\Continuum\anaconda3
) else (
  echo Anaconda not found in 1 of the 3 places we searched, double check where your anaconda prompt shortcut points to...
  pause
  exit
)
echo --Found anaconda folder at...
echo %conda_folder%
@ECHO on

call %conda_folder%\Scripts\activate.bat %conda_folder%

: # create environment
call %conda_folder%\condabin\conda.bat env create --file=environment.yml

pause