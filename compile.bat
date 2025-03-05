@echo off
setlocal enabledelayedexpansion

echo Current directory: %CD%
echo PATH: %PATH%

REM Create the compilados directory if it doesn't exist
if not exist compilados mkdir compilados

echo Using Flex library on Windows system

REM Navigate to the src directory
cd src

echo Compiling Preprocessor...
flex preprocesador.l
if %ERRORLEVEL% neq 0 goto error
move lex.yy.c ..\compilados\preprocesador.yy.c
if %ERRORLEVEL% neq 0 goto error
gcc -o ..\compilados\preprocesador.exe ..\compilados\preprocesador.yy.c -lfl
if %ERRORLEVEL% neq 0 goto error

echo Compiling Compiler...
bison -o ..\compilados\analizador_sintactico.tab.c --defines=..\compilados\analizador_sintactico.tab.h -d analizador_sintactico.y
if %ERRORLEVEL% neq 0 goto error
flex analizador_lexico.l
if %ERRORLEVEL% neq 0 goto error
move lex.yy.c ..\compilados\analizadorLexico.yy.c
if %ERRORLEVEL% neq 0 goto error
gcc -o ..\compilados\compiler.exe -I. -I..\compilados ^
..\compilados\analizadorLexico.yy.c ^
..\compilados\analizador_sintactico.tab.c ^
ast.c ^
analizador_semantico.c ^
intermediate_code.c ^
-lfl
if %ERRORLEVEL% neq 0 goto error

echo Compiling Assembler...
flex ensamblador.l
if %ERRORLEVEL% neq 0 goto error
move lex.yy.c ..\compilados\ensamblador.yy.c
if %ERRORLEVEL% neq 0 goto error
gcc -o ..\compilados\ensamblador.exe ..\compilados\ensamblador.yy.c -lfl -lm
if %ERRORLEVEL% neq 0 goto error

echo Compiling Linker/Loader...
flex linkerLoader.l
if %ERRORLEVEL% neq 0 goto error
move lex.yy.c ..\compilados\linkerLoader.yy.c
if %ERRORLEVEL% neq 0 goto error
gcc -o ..\compilados\linkerLoader.exe ..\compilados\linkerLoader.yy.c -lfl -lm
if %ERRORLEVEL% neq 0 goto error

echo Compilation completed successfully!

REM Return to the original directory
cd ..
goto end

:error
echo An error occurred during compilation! Error code: %ERRORLEVEL%
cd ..
pause
exit /b %ERRORLEVEL%

:end
echo Press any key to exit...
pause
exit /b 0 