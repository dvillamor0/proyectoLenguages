%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Palabras Reservadas */
#define IF         258
#define ELSE       259
#define INT        260
#define INPUT      261
#define PRINT      262
#define WHILE      263
#define RETURN     284

/* ADT */
#define STRING_TYPE 285
#define LIST_TYPE   286
#define APPEND      287
#define DELETE      288
#define LENGTH      289

/* Identificadores y Literales */
#define ID          264
#define NUMBER      265
#define STRING      266

/* Operador de Asignación */
#define ASSIGN      267

/* Operadores de Comparación */
#define EQ          268
#define NE          269
#define LT          270
#define GT          271
#define LE          272
#define GE          273

/* Operadores Aritméticos */
#define PLUS        274
#define MINUS       275
#define TIMES       276
#define DIV         277

/* Delimitadores */
#define LPAREN      278
#define RPAREN      279
#define COLON       280
#define COMMA       281
#define LBRACKET    282
#define RBRACKET    283
#define DOT         290
#define SEMICOLON   291
#define LBRACE      292
#define RBRACE      293

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
digit           [0-9]
letter          [a-zA-Z_]
digits          {digit}+
id              {letter}({letter}|{digit})*
number          {digit}+(\.{digit}+)?(E[+\-]?{digit}+)?
string_literal  \"([^\"\n]|\\\")*\"
whitespace      [ \t\r\n]+

%%

if          { printf("<IF>\n"); return IF; } 
else        { printf("<ELSE>\n"); return ELSE; }
int         { printf("<INT>\n"); return INT; }
input       { printf("<INPUT>\n"); return INPUT; }
print       { printf("<PRINT>\n"); return PRINT; }
while       { printf("<WHILE>\n"); return WHILE; }
return      { printf("<RETURN>\n"); return RETURN; }

"string"    { printf("<STRING_TYPE>\n"); return STRING_TYPE; }
"list"      { printf("<LIST_TYPE>\n"); return LIST_TYPE; }
"append"    { printf("<APPEND>\n"); return APPEND; }
"delete"    { printf("<DELETE>\n"); return DELETE; }
"length"    { printf("<LENGTH>\n"); return LENGTH; }

{id}        {
               int idx = insTablaSimbolos(yytext);
               yylval = idx;
               printf("<id,%d>\n", idx);
               return ID;
            }

{number}    {
               int idx = insTablaSimbolos(yytext);
               yylval = idx;
               printf("<number,%d>\n", idx);
               return NUMBER;
            }

{string_literal} {
               int idx = insTablaSimbolos(yytext);
               yylval = idx;
               printf("<string,%d>\n", idx);
               return STRING;
            }

"=="        { printf("<EQ>\n"); return EQ; }
"!="        { printf("<NE>\n"); return NE; }
"<="        { printf("<LE>\n"); return LE; }
">="        { printf("<GE>\n"); return GE; }
"<"         { printf("<LT>\n"); return LT; }
">"         { printf("<GT>\n"); return GT; }
"="         { printf("<=>\n"); return ASSIGN; }
"+"         { printf("<PLUS>\n"); return PLUS; }
"-"         { printf("<MINUS>\n"); return MINUS; }
"*"         { printf("<TIMES>\n"); return TIMES; }
"/"         { printf("<DIV>\n"); return DIV; }
"("         { printf("<LPAREN>\n"); return LPAREN; }
")"         { printf("<RPAREN>\n"); return RPAREN; }
":"         { printf("<COLON>\n"); return COLON; }
","         { printf("<COMMA>\n"); return COMMA; }
"["         { printf("<LBRACKET>\n"); return LBRACKET; }
"]"         { printf("<RBRACKET>\n"); return RBRACKET; }
"."         { printf("<DOT>\n"); return DOT; }
";"         { printf("<SEMICOLON>\n"); return SEMICOLON; }
"{"         { printf("<LBRACE>\n"); return LBRACE; }
"}"         { printf("<RBRACE>\n"); return RBRACE; }

{whitespace} {
    for(int i = 0; i < yyleng; i++) {
        if(yytext[i] == '\n') {
            linea++;
        }
    }
}

.           {
    fprintf(stderr, "Error: Caracter no reconocido '%s' en la linea %d\n", yytext, linea);
}

%%

/* Implementación de funciones */
int insTablaSimbolos(const char *lexema) {
    for (int i = 0; i < numIDs; i++) {
        if (strcmp(tablaSimbolos[i], lexema) == 0) {
            return i;
        }
    }
    if (numIDs >= MAX_IDS) {
        fprintf(stderr, "Error: Tabla de simbolos llena.\n");
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
        /* Aquí podría manejarse el token si se desea */
    }

    printf("\n\n== Tabla de Simbolos ==\n");
    for (int i = 0; i < numIDs; i++) {
        printf("ID %d: %s\n", i, tablaSimbolos[i]);
    }

    return 0;
}