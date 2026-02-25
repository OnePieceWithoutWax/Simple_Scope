@echo off

if exist %UserProfile%\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\anaconda3
) else if exist %UserProfile%\AppData\Local\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\anaconda3
) else if exist %UserProfile%\AppData\Local\Continuum\anaconda3\condabin\activate.bat (
  SET conda_folder=%UserProfile%\AppData\Local\Continuum\anaconda3
) else (
  echo "Anaconda not found in 1 of the 3 places we searched, double check where your anaconda prompt shortcut points to..."
  pause
  exit
)
echo --Found anaconda folder at...
echo %conda_folder%
@echo on

REM Activate your conda enviroment
call %conda_folder%\Scripts\activate.bat %conda_folder%

REM call conda activate simplescope
call %conda_folder%\condabin\conda.bat activate simplescope

echo running pre-build script (Version info, etc)...
python "%~dp0pre_build.py"
if errorlevel 1 (
  echo pre_build.py failed, aborting.
  pause
  exit /b 1
)

echo Building Simple_Scope packages...

echo Building single-file executable...
call pyinstaller single_file.spec

echo Building directory structure...
call pyinstaller directory.spec

echo Running post-build cleanup...
python "%~dp0post_build.py"

echo Done! Built packages are in the 'dist' folder.
pause
