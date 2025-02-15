%{
/* Definición de las constantes manifiestas */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Función para imprimir un número en binario con exactamente 21 bits
void print_binary(int num) {
    unsigned int mask = 1 << 20; // Máscara para el bit más significativo (bit 20, el bit más a la izquierda en 21 bits)
    
    // Imprimir los 21 bits
    for (int i = 0; i < 21; i++) {
        if (num & mask) {
            printf("1");
        } else {
            printf("0");
        }
        mask >>= 1;  // Desplazamos la máscara para el siguiente bit
    }
}


int yylval;
int direccionInicial;  // Esta es la dirección inicial que se usará en la suma

/* Definir un tipo de token para identificadores */
#define RELATIVE 1
#define DIR 2

%}

/* Regular definitions */
delim       [ \t\n]
ws          {delim}+
digit       [0-9]
number      {digit}+(\.{digit}+)?(e[+-]?{digit}+)?

relative    \#([0-9]+)      
dir         \([0-9]+\)       

%%

{ws}        { printf("\n");}

{relative}  { 
    direccionInicial = atoi(yytext + 1); 
    //printf("relativo: %d\n", direccionInicial);
    printf("\n");  
    return RELATIVE;
}

{dir}       { 
    int dir_value = atoi(yytext + 1); 
    int suma = direccionInicial + dir_value;
    print_binary(suma);  
    return DIR;
}

.|\n { ECHO;}

%%

int main() {
    while (yylex() != 0) {
        /* Cada llamada a yylex() lee un token */
    }
    return 0;
}
