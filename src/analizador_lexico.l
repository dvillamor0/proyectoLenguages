%{
    /**
     * @archivo: analizador_lexico.l
     * @descripción: Analizador léxico para un lenguaje de programación personalizado
     * @autor: [Nombre del autor]
     * @fecha: [Fecha de creación/modificación]
     */
    
    // Inclusión de bibliotecas estandar para entrada/salida, manejo de memoria y cadenas.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    // Inclusión del header generado por el analizador sintactico.
    #include "analizador_sintactico.tab.h"

    /**
     * @constante: MAX_SYMBOLS
     * @descripción: Define el tamaño máximo de la tabla de símbolos
     * @valor: 1000 entradas
     */
    #define MAX_SYMBOLS 1000

    /**
     * @constantes: Tipos de símbolos
     * @descripción: Identificadores para categorizar las entradas en la tabla de símbolos
     */
    #define SYMTAB_IDENTIFIER 1  // Identificador (variables, funciones)
    #define SYMTAB_NUMBER 2      // Número de punto flotante
    #define SYMTAB_NATURAL 3     // Número natural (entero sin signo)

    /**
     * @estructura: SymbolEntry
     * @descripción: Representa una entrada en la tabla de símbolos
     * @miembros:
     *   - name: Nombre o lexema del símbolo
     *   - type: Tipo del símbolo según las constantes definidas
     *   - value: Unión que almacena el valor según el tipo del símbolo
     */
    typedef struct {
        char *name;   // Nombre del simbolo.
        int type;     // Tipo de simbolo (identificador o numero).
        union {
            double number_value;  // Valor numerico (para numeros).
            char *string_value;   // Valor en forma de cadena (no se usa en este codigo).
            unsigned int natural_value; // Valor para numeros naturales.

        } value;
    } SymbolEntry;

    /**
     * @variable: symbol_table
     * @descripción: Tabla de símbolos implementada como un arreglo de entradas
     */
    SymbolEntry symbol_table[MAX_SYMBOLS];
    
    /**
     * @variable: symbol_count
     * @descripción: Contador que mantiene el número actual de símbolos en la tabla
     * @inicialización: 0
     */
    int symbol_count = 0;

    /**
     * @función: install_id
     * @descripción: Instala un identificador en la tabla de símbolos
     * @parámetros: char *lexeme - Cadena que representa el identificador
     * @retorno: Índice del símbolo en la tabla
     */
    int install_id(char *lexeme);
    
    /**
     * @función: install_num
     * @descripción: Instala un número en la tabla de símbolos
     * @parámetros: char *lexeme - Cadena que representa el número
     * @retorno: Índice del símbolo en la tabla
     */
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

/**
 * @función: install_id
 * @descripción: Instala un identificador en la tabla de símbolos. Si el identificador
 *              ya existe, retorna su índice. Si no, crea una nueva entrada.
 *
 * @parámetros:
 *   - lexeme: Cadena que representa el identificador a instalar
 *
 * @retorno: Índice del símbolo en la tabla
 *
 * @complejidad: O(n) donde n es el número actual de símbolos en la tabla
 * 
 * @manejo_errores: Termina el programa si la tabla está llena
 */
int install_id(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    // Busca el identificador en la tabla existente
    for (int i = 0; i < symbol_count; i++) {
        if (symbol_table[i].type == SYMTAB_IDENTIFIER && 
            strcmp(symbol_table[i].name, lexeme) == 0) {
            return i;
        }
    }
    
    // Si no existe, crea una nueva entrada
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_IDENTIFIER;
    return symbol_count++;
}

/**
 * @función: install_num
 * @descripción: Instala un número en la tabla de símbolos. Convierte el lexema
 *              a un valor numérico de punto flotante y lo almacena.
 *
 * @parámetros:
 *   - lexeme: Cadena que representa el número a instalar
 *
 * @retorno: Índice del símbolo en la tabla
 *
 * @observaciones: A diferencia de los identificadores, no verifica duplicados
 *                de números. Cada número se instala como una nueva entrada.
 *
 * @manejo_errores: Termina el programa si la tabla está llena
 */
int install_num(char *lexeme) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "Symbol table full\n");
        exit(1);
    }
    
    // Crea una nueva entrada para el número
    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_NUMBER;
    symbol_table[symbol_count].value.number_value = atof(lexeme);
    return symbol_count++;
}