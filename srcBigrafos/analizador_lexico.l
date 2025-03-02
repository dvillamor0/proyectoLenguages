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
    #define SYMTAB_NODE 3
    #define SYMTAB_LINK 4

    // Estructura que representa una entrada en la tabla de simbolos.
    typedef struct {
        char *name;   
        int type;    
        union {
            double number_value;  
            char *string_value;   
            struct {  
                int dimensions;      // Número de dimensiones
                int *sizes;          // Tamaño de cada dimensión
                double *data;        // Valores almacenados en la matriz
            } matrix;
            struct {              // Información específica para nodos
                int parent;       // Índice del nodo padre en la jerarquía
                int *children;    // Lista de índices de nodos hijos
                int child_count;  // Número de hijos
                int *links;       // Lista de enlaces
                int link_count;   // Número de enlaces
            } node_info;
        } value;
    } SymbolEntry;


    // Declaracion de la tabla de simbolos y contador de entradas.
    SymbolEntry symbol_table[MAX_SYMBOLS];
    int symbol_count = 0;

    // Declaracion de las funciones para instalar identificadores y numeros.
    int install_id(char *lexeme);
    int install_num(char *lexeme);
    int install_node(char *lexeme, int parent);
    void add_link(int node_index, int link_target);
%}

%option noyywrap
%option yylineno

/* Definiciones de expresiones regulares */
DIGIT       [0-9]
LETTER      [a-zA-Z]
ID          {LETTER}({LETTER}|{DIGIT})*
NUMBER      {DIGIT}+(\.{DIGIT}+)?([Ee][+-]?{DIGIT}+)?  
WHITESPACE  [ \t\n\r]+
COMMENT     #[^\n]*\n
MATRIX_ELEMENT \[[0-9]+\]
%%
{WHITESPACE}    { /* Skip whitespace */ }
{COMMENT}       { /* Skip comments */ }

"Fun"       { return TOKEN_FUN; }
"Ret"       { return TOKEN_RET; }
"If"        { return TOKEN_IF; }
"While"     { return TOKEN_WHILE; }
"Ent"       { return TOKEN_ENT; }
"Flo"       { return TOKEN_FLO; }

"enl"       { return TOKEN_EDGE; }
"tipo"      { return TOKEN_TYPE; }
"hijo"      { return TOKEN_CHILD; }
"lnk"       { return TOKEN_LNK; }
"nod"       { return TOKEN_NODE; }

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

{ID}        { yylval.symbol_index = install_id(yytext); return TOKEN_ID; }
{NUMBER}    { yylval.symbol_index = install_num(yytext); return TOKEN_NUMBER; }
{MATRIX_ELEMENT} {yylval.symbol_index = install_id(yytext); return TOKEN_MATRIX_ELEMENT; }


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

*
 * Función: install_node
 * ----------------------
 * Instala un nodo en la tabla de símbolos.
 *
 * Parámetros:
 *   lexeme - Nombre del nodo.
 *   parent - Índice del nodo padre en la jerarquía (-1 si no tiene padre).
 *
 * Retorna:
 *   Índice del nodo en la tabla.
 */
 
int install_node(char *lexeme, int parent) {
    if (symbol_count >= MAX_SYMBOLS) {
        fprintf(stderr, "La tabla de símbolos está llena\n");
        exit(1);
    }

    symbol_table[symbol_count].name = strdup(lexeme);
    symbol_table[symbol_count].type = SYMTAB_NODE;
    symbol_table[symbol_count].value.node_info.parent = parent;
    symbol_table[symbol_count].value.node_info.children = NULL;
    symbol_table[symbol_count].value.node_info.child_count = 0;
    symbol_table[symbol_count].value.node_info.links = NULL;
    symbol_table[symbol_count].value.node_info.link_count = 0;

    if (parent != -1) {
        // Añadir este nodo como hijo del padre
        SymbolEntry *parent_node = &symbol_table[parent];
        parent_node->value.node_info.child_count++;
        parent_node->value.node_info.children = realloc(
            parent_node->value.node_info.children,
            parent_node->value.node_info.child_count * sizeof(int)
        );
        parent_node->value.node_info.children[parent_node->value.node_info.child_count - 1] = symbol_count;
    }

    return symbol_count++;
}


/*
 * Función: add_link
 * ----------------------
 * Añade un enlace entre dos nodos.
 *
 * Parámetros:
 *   node_index - Índice del nodo origen.
 *   link_target - Índice del nodo destino.
 */
void add_link(int node_index, int link_target) {
    SymbolEntry *node = &symbol_table[node_index];
    node->value.node_info.link_count++;
    node->value.node_info.links = realloc(
        node->value.node_info.links,
        node->value.node_info.link_count * sizeof(int)
    );
    node->value.node_info.links[node->value.node_info.link_count - 1] = link_target;
}
