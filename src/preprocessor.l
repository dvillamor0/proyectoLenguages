%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
%}

%option noyywrap

%%

POWER\(([0-9]+),([0-9]+)\) { 
    int arg1 = atoi(yytext+6); 
    char *comma_pos = strchr(yytext, ','); 
    int arg2 = atoi(comma_pos+1); // +1 para saltar la coma
    printf("memoria = ['0', '1', %d, %d, '00001000000000000000000000000001', '00001010000000000000000000000010', '00001100000000000000000000000011', '00001110000000000000000000000000', '10001101100000000000000000010000', '00001110000000000000000000000010', '10001100000000000000000000001110', '00110010111000000000000000000000', '00101101000000000000000000000000', '10111000000000000000000000001010', '00010010000000000000000000010010', '10111000000000000000000000010001', '00010000000000000000000000010010', '11111000000000000000000000000000', 1]\n",arg1, arg2); 
    printf("stack = []\n");
    printf("cp = 4\n");
    printf("while cp < len(memoria):\n");
    printf("    try:\n");
    printf("        ejecutar_instruccion()\n");
    printf("    except Exception as e:\n");
    printf("        print(\"el resultado es: \",memoria[18])\n");
    printf("        break\n");
    printf("print(\"el resultado es:\",memoria[18])\n");
} /* Reescribir cuando detecta HOLA con argumentos */
SQUAREROOT\(([0-9]+)\) { 
    int arg1 = atoi(yytext+11);
    printf("memoria = ['0', '1', %d, '00001000000000000000000000000010', '00001010000000000000000000000000', '10011000100000000000000000001100', '00001110000000000000000000000001', '00110100101000000000000000000000', '10100001000000000000000000001011', '00100010111000000000000000000000', '10000000000000000000000000000111', '10001100000000000000000000001110', '00010000000000000000000000010000', '10000000000000000000000000001111', '00010010000000000000000000010000', '11111000000000000000000000000000', 1]\n",arg1); 
    printf("stack = []\n");
    printf("cp = 3\n");
    printf("while cp < len(memoria):\n");
    printf("    try:\n");
    printf("        ejecutar_instruccion()\n");
    printf("    except Exception as e:\n");
    printf("        print(\"el resultado es: \",memoria[16])\n");
    printf("        break\n");
    printf("print(\"el resultado es: \",memoria[16])\n");
}
HOLA               { printf("x = 10\n"); printf("x = x + x\n"); } /* Reescribir cuando detecta HOLA */
#.*                ; /* Eliminar comentarios de línea */
("""(.|\n)*?""") ; /* Eliminar comentarios de bloque con triple comillas dobles */
("'''.*?'''")      ; /* Eliminar comentarios de bloque con triple comillas simples */
.                  { putchar(yytext[0]); } /* Imprimir cualquier otro carácter */

%%

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <archivo_python>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error al abrir el archivo");
        return 1;
    }

    yyin = file;
    yylex();
    fclose(file);
    return 0;
}
