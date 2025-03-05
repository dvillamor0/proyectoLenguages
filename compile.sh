#!/bin/bash -x

echo "Current directory: $(pwd)"
echo "PATH: $PATH"

# Create the compilados directory if it doesn't exist
mkdir -p compilados

# Determine the appropriate flex library based on OS
if [[ "$(uname)" == "Darwin" ]]; then
    # MacOS uses -ll
    FLEX_LIB="-ll"
else
    # Linux and others use -lfl
    FLEX_LIB="-lfl"
fi

echo "Using Flex library: $FLEX_LIB on $(uname) system"

# Navigate to the src directory
cd src

if [ ! -f "preprocesador.l" ]; then
    echo "Error: preprocesador.l not found!"
    exit 1
fi

echo "Compiling Preprocessor..."
flex preprocesador.l &&
mv lex.yy.c ../compilados/preprocesador.yy.c &&
gcc -o ../compilados/preprocesador ../compilados/preprocesador.yy.c $FLEX_LIB

echo "Compiling Compiler..."
bison -o ../compilados/analizador_sintactico.tab.c --defines=../compilados/analizador_sintactico.tab.h -d analizador_sintactico.y &&
flex analizador_lexico.l &&
mv lex.yy.c ../compilados/analizadorLexico.yy.c &&
gcc -o ../compilados/compiler -I. -I../compilados \
../compilados/analizadorLexico.yy.c \
../compilados/analizador_sintactico.tab.c \
ast.c \
analizador_semantico.c \
intermediate_code.c \
$FLEX_LIB

echo "Compiling Assembler..."
flex ensamblador.l &&
mv lex.yy.c ../compilados/ensamblador.yy.c &&
gcc -o ../compilados/ensamblador ../compilados/ensamblador.yy.c $FLEX_LIB -lm

echo "Compiling Linker/Loader..."
flex linkerLoader.l &&
mv lex.yy.c ../compilados/linkerLoader.yy.c &&
gcc -o ../compilados/linkerLoader ../compilados/linkerLoader.yy.c $FLEX_LIB -lm

echo "Compilation completed successfully!"

# Return to the original directory
cd .. 