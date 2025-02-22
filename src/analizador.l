%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parser.tab.h"
#include "tokens.h"
#include "symbol_table.h"

/* Declaración de variables globales */
char *tablaSimbolos[MAX_IDS];
int numIDs = 0;

/* Declaración de la función */
int insTablaSimbolos(const char *lexema);
%}

%option yylineno

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
    yylval.token_type = idx;
    printf("<id,%d>\n", idx);
    return ID;
}

{number}    {
    int idx = insTablaSimbolos(yytext);
    yylval.token_type = idx;
    printf("<number,%d>\n", idx);
    return NUMBER;
}

{string_literal} {
    int idx = insTablaSimbolos(yytext);
    yylval.token_type = idx;
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

{whitespace} { /* ignorar espacios en blanco */ }

.           {
    fprintf(stderr, "Error: Caracter no reconocido '%s' en la linea %d\n", yytext, yylineno);
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