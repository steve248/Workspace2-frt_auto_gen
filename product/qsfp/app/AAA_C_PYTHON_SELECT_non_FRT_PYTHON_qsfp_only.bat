@echo off
    REM Created by Steve Lin to select a Python script in Current directory
    REM set new environment variables, the tmp file is in temp directory

REM     if exist C:\Python27\ (
REM OLD         echo. Found Python 27
REM OLD         set Path=C:\Python27\;%Path%
REM OLD         set PYTHONHOME=C:\Python27\
REM OLD         set PythonPath==C:\Python27;=C:\Python27\DLLs;=C:\Python27\LIB;=C:\Python27\LIB\LIB-TK
REM OLDREM     ) else (
REM OLDREM         echo. Did not find Python 27
REM OLDREM     )

    REM show current environmental variables
    echo:----------------------
    set pythonpath 
    echo:----------------------

    REM Check current environmental variables
    set pythonpath | findstr "Iron"
    if %ERRORLEVEL%==0 echo.^>^>^> Change environmental variables to use C python, instead of Iron Python
    if %ERRORLEVEL%==0 goto SET_C_PYTHON_ENV
    GOTO ALREADY_SET_C_PYTHON_ENV

:SET_C_PYTHON_ENV
    echo ===============================================
    echo OLD PYTHONPATH %PYTHONPATH%

    set | findstr "Python" 
    REM set | findstr "Python" > steve_tmp
    REM echo A. %TMP%\%0_tmp
    REM echo B. %TMP%\%~n0_tmp
    REM pause
 
    set | findstr "Python" > %TMP%\%~n0_tmp
    set frt_root=%TMP%\%~n0_tmp

    ipy -c "import sys, re;[sys.stdout.write(re.sub('IronPython 2.7', 'Python27', line)) for line in sys.stdin]" < %frt_root% >%TMP%\%~n0_tmp.tmp
    ipy -c "import sys, re;[sys.stdout.write(re.sub('^', 'SET ', line)) for line in sys.stdin]" < %TMP%\%~n0_tmp.tmp >%TMP%\%~n0_tmp.bat

    REM set new environment
    call %TMP%\%~n0_tmp.bat
    del %TMP%\%~n0_*

    echo NEW PYTHONPATH %PYTHONPATH%
    echo =============================================== Done change environment to C Python in "C:\python27"

:ALREADY_SET_C_PYTHON_ENV

    set outfile=%TMP%\xxx_batchfilexx.junk

    REM Find all python script in this directory, non-recursively, and newest file is last
    REM newest last
    REM dir/b /od *.PY > %outfile%
    REM newest first
    dir/b /o-d *.PY > %outfile%


    REM Assign a number to each python script in this directory, non-recursively, and newest file is last
    findstr /e /n ".py" %outfile% > %outfile%.tmp

    REM Ask user to select a number, effetively select a Python script
    REM echo.^>^>^> Current Python scripts:
    echo.^>^>^> Current Python scripts. Newest first:
    REM ipy -c "import sys, re;[sys.stdout.write(re.sub('^', '   ', line)) for line in sys.stdin]" < %outfile%.tmp 
    python -c "import sys, re;[sys.stdout.write(re.sub('^', '   ', line)) for line in sys.stdin]" < %outfile%.tmp 
    set /P nu=Enter a number:  

    REM Based on user input, find the name of the Python script that was selected
    REM ipy -c "import sys, re;[sys.stdout.write( re.sub('^%nu%:', '', line)    ) for line in sys.stdin if line.startswith('%nu%:')]" < %outfile%.tmp >%outfile%.tmp.tmp
    python -c "import sys, re;[sys.stdout.write( re.sub('^%nu%:', '', line)    ) for line in sys.stdin if line.startswith('%nu%:')]" < %outfile%.tmp >%outfile%.tmp.tmp
    set nu=
    for /f "delims=" %%a in ('type %outfile%.tmp.tmp ^| findstr /v "linux"') do @set this_python_script=%%a
    echo.
    echo ^>^>^> Select "%this_python_script%"


    REM Ask user to send STDOUT to log file or not
    set /P STDOUT_TO_FILE=^>^>^> Send STDOUT to log file y/n (CR=N): 


    if "%STDOUT_TO_FILE%"=="Y" set STDOUT_TO_FILE%=y

    REM Clean up new environment variables and tmp file
    del %outfile%
    del %outfile%.*

    set stdfile=JUNK.log

:NEXT
    echo.----------------------------------------------------------------------------- start
    echo.


REM @echo on
    echo.
    REM echo. Executing "ipy  %this_python_script%"...
    echo. Executing "python  %this_python_script%...
    echo.

    set msa_file_name=SFF-8636 rev23 QSFP Managemente Interface from docx

    if "%this_python_script%"=="doc_to_csv_table_qsfp.py" (
        set input_file="C:\Workspace2\frt_auto_gen\msa_and_memory_map\QSFP\%msa_file_name%.txt" 
        set output_file="C:\Workspace2\frt_auto_gen\product\qsfp\app_output\csv"
    ) ELSE (
        IF "%this_python_script%"=="csv_table_to_memory_test_qsfp.py" (
            set input_file="C:\Workspace2\frt_auto_gen\product\qsfp\app_output\csv\%msa_file_name%_all_table.csv"
            set output_file="C:\Workspace2\frt_auto_gen\product\qsfp\memory"

        ) ELSE (
            IF "%this_python_script%"=="csv_table_to_io_test_qsfp.py" (
                set input_file="C:\Workspace2\frt_auto_gen\product\qsfp\app_output\csv\%msa_file_name%_all_table.csv"
                set output_file="C:\Workspace2\frt_auto_gen\product\qsfp\io"
            ) ELSE (
                echo The variable not contains "csv_table_to_memory_test_qsfp"
                echo The variable not contains "%this_python_script%"
            )
        )
    )

    echo Run python %this_python_script% --input=%input_file% --output=%output_file%
    if "%STDOUT_TO_FILE%"=="y" goto LOG_STDOUT

:NO_LOG
    REM ipy %this_python_script% 
    python %this_python_script% --input=%input_file% --output=%output_file%
    goto DONE

:LOG_STDOUT
    echo.STDOUT to file %stdfile%. Wait...
    echo.
    echo python %this_python_script% --input=%input_file% --output=%output_file% > %stdfile%
    python %this_python_script% --input=%input_file% --output=%output_file% > %stdfile%

    echo.
    echo.STDOUT to file %stdfile%
    echo.
    goto DONE

:DONE
    REM clear the tmp envrionment variabls
    set sff_file_name=
    set  inpupt_file=
    set output_file=


    echo.
    echo.----------------------------------------------------------------------------- end
    echo.** Executing %~n0, namely %0
    echo.** script    %this_python_script%

    pause
    goto NEXT

    REM Repeatedly execut the test script
    set this_python_script=
:END
