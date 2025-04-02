@ECHO off
:: Find Anaconda installation location
if exist %UserProfile%\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\anaconda3
) else if exist %UserProfile%\AppData\Local\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\anaconda3
) else if exist %UserProfile%\AppData\Local\Continuum\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\Continuum\anaconda3
) else (
  echo Anaconda not found in the expected locations. Please check your Anaconda installation.
  pause
  exit /b 1
)

echo Found Anaconda folder at: %conda_folder%

:: Activate the base conda environment first
call %conda_folder%\Scripts\activate.bat %conda_folder%

:: Now activate the simplescope environment
call %conda_folder%\condabin\conda.bat activate simplescope

:: Get the directory where this batch file is located
SET script_dir=%~dp0

:: Run the main.py script
echo Starting Simple Scope application...
python "%script_dir%\Simple_Scope\main.py"

:: If you want the command window to stay open after an error, uncomment the line below
if %ERRORLEVEL% NEQ 0 pause

:: End of script
