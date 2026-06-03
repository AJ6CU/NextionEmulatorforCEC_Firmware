@echo off

SET "folder_name=CEC"
SET "install_dir=%~dp0

SET "wheel=cec_nextion_emulator-0.1.0-py3-none-any.whl"
SET "startscript=cecNext.bat"

@REM SET "default_ini_file=defaultCECNextionEmulator.ini"
@REM SET "target_ini_file=.CECNextionEmulator.ini"

SET "full_wheel_path=%install_dir%\%wheel%"
REM SET "full_startscript_path=%install_dir%\%startscript%"
REM SET "full_default_ini_file_path=%install_dir%\%default_ini_file%"

python "-m" "venv" "%USERPROFILE%\Documents\%folder_name%"
cd "%USERPROFILE%\Documents\%folder_name%\Scripts"
CALL activate.bat

pip "install" "%full_wheel_path%"


COPY  "%install_dir%%startscript%" "%USERPROFILE%\Documents\%folder_name%\Scripts\%startscript%"
@REM COPY  "%install_dir%%default_ini_file%" "%USERPROFILE%\%target_ini_file%"

CALL "%USERPROFILE%\Documents\%folder_name%\Scripts\deactivate.bat"
