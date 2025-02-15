%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Palabras Reservadas */
#define IF       258  /* Estructura condicional */
#define ELSE     259  /* Complemento de IF */
#define INT      260  /* Tipo de dato entero */
#define INPUT    261  /* Entrada de datos */
#define PRINT    262  /* Salida de datos */
#define WHILE    263  /* Estructura iterativa */
#define RETURN   284  /* Retorno de función */

/* Identificadores y Literales  */
#define ID       264  /* Identificadores de variables/funciones */
#define NUMBER   265  /* Constantes numéricas */
#define STRING   266  /* Cadenas de caracteres */


/* Operador de Asignación */
#define ASSIGN   267  /* = */

/* Operadores de Comparación */
#define EQ       268  /* == */
#define NE       269  /* != */
#define LT       270  /* <  */
#define GT       271  /* >  */
#define LE       272  /* <=  */
#define GE       273  /* >=  */

/* 3.3 Operadores Aritméticos */
#define PLUS     274  /* + */
#define MINUS    275  /* - */
#define TIMES    276  /* * */
#define DIV      277  /* / */

/* 4. Delimitadores */
#define LPAREN   278  /* ( */
#define RPAREN   279  /* ) */
#define COLON    280  /* : */
#define COMMA    281  /* , */

int yylval;

/* Tabla de símbolos */
#define MAX_IDS 1000
char *tablaSimbolos[MAX_IDS];
int numIDs = 0;

/* Declaración de la función */
int insTablaSimbolos(const char *lexema);

/* Variable para llevar el conteo de líneas */
int linea = 1;

/* Declaración de yyin */
extern FILE *yyin;
%}

/* Expresiones regulares */
digit     [0-9]
letter    [a-zA-Z_]
digits    {digit}+
id        {letter}({letter}|{digit})*
number    {digit}+(\.{digit}+)?(E[+\-]?{digit}+)?
string    \"([^\"\n]|\\\")*\"
whitespace [ \t\r\n]+

%%

if         { printf("<IF>\n"); return IF; }
else       { printf("<ELSE>\n"); return ELSE; }
int        { printf("<INT>\n"); return INT; }
input      { printf("<INPUT>\n"); return INPUT; }
print      { printf("<PRINT>\n"); return PRINT; }
while      { printf("<WHILE>\n"); return WHILE; }
return     { printf("<RETURN>\n"); return RETURN; }  

{id}       {
                int idx = insTablaSimbolos(yytext);
                yylval = idx;
                printf("<id,%d>\n", idx);
                return ID;
            }

{number}   {
                int idx = insTablaSimbolos(yytext);
                yylval = idx;
                printf("<number,%d>\n", idx);
                return NUMBER;
            }

{string}   {
                int idx = insTablaSimbolos(yytext);
                yylval = idx;
                printf("<string,%d>\n", idx);
                return STRING;
            }

"=="       { printf("<EQ>\n"); return EQ; }
"!="       { printf("<NE>\n"); return NE; }
"<="       { printf("<LE>\n"); return LE; }
">="       { printf("<GE>\n"); return GE; }
"<"        { printf("<LT>\n"); return LT; }
">"        { printf("<GT>\n"); return GT; }

"="        { printf("<=>\n"); return ASSIGN; }
"+"        { printf("<PLUS>\n"); return PLUS; }
"-"        { printf("<MINUS>\n"); return MINUS; }
"*"        { printf("<TIMES>\n"); return TIMES; }
"/"        { printf("<DIV>\n"); return DIV; }

"("        { printf("<LPAREN>\n"); return LPAREN; }
")"        { printf("<RPAREN>\n"); return RPAREN; }
":"        { printf("<COLON>\n"); return COLON; }
","        { printf("<COMMA>\n"); return COMMA; }

{whitespace} {
                /* Contar líneas */
                for(int i=0; i<yyleng; i++) {
                    if(yytext[i] == '\n') {
                        linea++;
                    }
                }
                /* Ignorar espacios en blanco */
            }

.          { fprintf(stderr, "Error: Caracter no reconocido '%s'\n", yytext); }

%%

/* Implementación de funciones */
int insTablaSimbolos(const char *lexema) {
    for (int i = 0; i < numIDs; i++) {
        if (strcmp(tablaSimbolos[i], lexema) == 0) {
            return i;
        }
    }
    if (numIDs >= MAX_IDS) {
        fprintf(stderr, "Error: Tabla de símbolos llena.\n");
        exit(1);
    }
    tablaSimbolos[numIDs] = strdup(lexema);
    return numIDs++;
}

int yywrap() {
    return 1;
}

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *f = fopen(argv[1], "r");
        if (!f) {
            perror("Error al abrir el archivo");
            return 1;
        }
        yyin = f;
    }

    int token;
    while ((token = yylex()) != 0) {
        
    }

    printf("\n\n== Tabla de Símbolos ==\n");
    for (int i = 0; i < numIDs; i++) {
        printf("ID %d: %s\n", i, tablaSimbolos[i]);
    }

    return 0;
}