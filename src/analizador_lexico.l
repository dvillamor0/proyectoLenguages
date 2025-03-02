%{
    // Inclusión de bibliotecas estandar para entrada/salida, manejo de memoria y cadenas.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    // Inclusión del header generado por el analizador sintactico.
    #include "analizador_sintactico.tab.h"

    // Definicion del maximo de simbolos en la tabla.
    #define MAX_SYMBOLS 1000

    // Constantes para identificar el tipo de simbolo.
    #define SYMTAB_IDENTIFIER 1
    #define SYMTAB_NUMBER 2
    #define SYMTAB_NATURAL 3

    // Estructura que representa una entrada en la tabla de simbolos.
    typedef struct {
        char *name;   // Nombre del simbolo.
        int type;     // Tipo de simbolo (identificador o numero).
        union {
            double number_value;  // Valor numerico (para numeros).
            char *string_value;   // Valor en forma de cadena (no se usa en este codigo).
            unsigned int natural_value; // Valor para numeros naturales.

        } value;
    } SymbolEntry;

    // Declaracion de la tabla de simbolos y contador de entradas.
    SymbolEntry symbol_table[MAX_SYMBOLS];
    int symbol_count = 0;

    // Declaracion de las funciones para instalar identificadores y numeros.
    int install_id(char *lexeme);
    int install_num(char *lexeme);
%}

%option noyywrap
%option yylineno

/* Definiciones de expresiones regulares */
DIGIT       [0-9]
LETTER      [a-zA-Z_]
ID          {LETTER}({LETTER}|{DIGIT})*
NUMBER      {DIGIT}+(\.{DIGIT}+)?([Ee][+-]?{DIGIT}+)?  
WHITESPACE  [ \t\n\r]+
COMMENT     #[^\n]*\n

%%
{WHITESPACE}    { /* Skip whitespace */ }
{COMMENT}       { /* Skip comments */ }

"Fun"       { return TOKEN_FUN; }
"Ret"       { return TOKEN_RET; }
"If"        { return TOKEN_IF; }
"While"     { return TOKEN_WHILE; }
"Ent"       { return TOKEN_ENT; }
"Flo"       { return TOKEN_FLO; }
"Nat"       { return TOKEN_NAT; }
"Arreglo"   { return TOKEN_ARREGLO; }


"<"         { return TOKEN_RELOP_LT; }
"<="        { return TOKEN_RELOP_LE; }
"=="        { return TOKEN_RELOP_EQ; }  
"!="        { return TOKEN_RELOP_NE; }
">"         { return TOKEN_RELOP_GT; }
">="        { return TOKEN_RELOP_GE; }

"+"         { return TOKEN_PLUS; }
"-"         { return TOKEN_MINUS; }
"*"         { return TOKEN_MULT; }
"/"         { return TOKEN_DIV; }
"="         { return TOKEN_ASSIGN; }   
";"         { return TOKEN_SEMICOLON; }
","         { return TOKEN_COMMA; }
"("         { return TOKEN_LPAREN; }
")"         { return TOKEN_RPAREN; }
"{"         { return TOKEN_LBRACE; }
"}"         { return TOKEN_RBRACE; }
"["         { return TOKEN_LBRACK; }
"]"         { return TOKEN_RBRACK; }

{ID}        { yylval.symbol_index = install_id(yytext); return TOKEN_ID; }
{NUMBER}    { yylval.symbol_index = install_num(yytext); return TOKEN_NUMBER; }

.           { printf("Lexical Error: Unexpected character %s\n", yytext); }
%%

/*
 * Funcion: install_id
 * ---------------------
 * Instala un identificador en la tabla de simbolos.
 *
 * Parametro:
 *   lexeme - Cadena que representa el identificador.
 *
 * Retorna:
 *   Indice del simbolo en la tabla.
 *
 * Procedimiento:
 *   - Verifica si la tabla esta llena.
 *   - Busca si el identificador ya existe.
 *   - Si no existe, lo agrega y aumenta el contador.
 */
int install_id(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    for (int i = 0; i < symbol_count; i++) {
        if (symbol_table[i].type == SYMTAB_IDENTIFIER && 
            strcmp(symbol_table[i].name, lexeme) == 0) {
            return i;
        }
    }
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_IDENTIFIER;
    return symbol_count++;
}

/*
 * Funcion: install_num
 * ----------------------
 * Instala un numero en la tabla de simbolos.
 *
 * Parametro:
 *   lexeme - Cadena que representa el numero.
 *
 * Retorna:
 *   Indice del simbolo en la tabla.
 *
 * Procedimiento:
 *   - Verifica si la tabla esta llena.
 *   - Agrega el numero, convirtiendo la cadena a valor numerico.
 *   - Aumenta el contador y retorna el indice.
 */
int install_num(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_NUMBER;
    symbol_table[symbol_count].value.number_value = atof(lexeme);
    return symbol_count++;
}
