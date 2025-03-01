%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "analizador_sintactico.tab.h"

/* Estructura para representar dos nodos */
typedef struct {
    char *nodo1;
    char *nodo2;
} NodePair;

/* Tabla de símbolos sencilla: en este ejemplo, se manejan bigrafos y arreglos */
typedef enum { SYM_BIGRAPH, SYM_ARRAY } SymbolType;

typedef struct Symbol {
    char *name;
    SymbolType type;
    struct Symbol *next;
} Symbol;

Symbol *symbolTable = NULL;

/* Función para agregar un símbolo a la tabla */
void addSymbol(const char *name, SymbolType type) {
    Symbol *sym = (Symbol *)malloc(sizeof(Symbol));
    sym->name = strdup(name);
    sym->type = type;
    sym->next = symbolTable;
    symbolTable = sym;
}

/* Función para buscar un símbolo en la tabla */
Symbol* lookupSymbol(const char *name) {
    Symbol *sym = symbolTable;
    while(sym) {
        if(strcmp(sym->name, name) == 0)
            return sym;
        sym = sym->next;
    }
    return NULL;
}

/* Función para generar código intermedio (IR) */
void genIR(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    printf("\n");
    va_end(args);
}

/* Declaración de yyerror para informar errores de sintaxis */
void yyerror(const char *s) {
    fprintf(stderr, "Error: %s\n", s);
}
%}

/* Definición de la unión de valores semánticos */
%union {
    char *str;
    NodePair *pair;
}

/* Declaración de tokens */
%token TOKEN_EDGE
%token TOKEN_TYPE
%token TOKEN_CHILD
%token TOKEN_LNK
%token TOKEN_NODE

%token TOKEN_COMMA
%token TOKEN_LPAREN
%token TOKEN_RPAREN

%token IDENTIFIER
%token STRING
%token NAT

%%

/* Producción para ELEMENTO_ARREGLO: 
   Reconoce la sintaxis: identifier ( NAT )
   Y devuelve el symbol_index calculado: getSymbolIndex(identifier) + NAT + 1 */
ELEMENTO_ARREGLO:
    IDENTIFIER TOKEN_LPAREN NAT TOKEN_RPAREN
    {
        int sym_index = getSymbolIndex($1);
        int natVal = atoi($3);
        int result = sym_index + natVal + 1;
        ElementoArreglo *ea = malloc(sizeof(ElementoArreglo));
        if (!ea) {
            fprintf(stderr, "Error de asignación de memoria\n");
            exit(1);
        }
        ea->symbol_index = result;
        $$ = ea;
        printf("[Semántica] ELEMENTO_ARREGLO: %s(%s) => %d\n", $1, $3, result);
    }
;

/* Producción auxiliar para 2 nodos como operandos.
   Reconoce: ( ELEMENTO_ARREGLO , ELEMENTO_ARREGLO ) */
bg_2_node:
      TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_COMMA ELEMENTO_ARREGLO TOKEN_RPAREN
      {
          
          np->nodo1 = $2->symbol_index;
          np->nodo2 = $4->symbol_index;
          $$ = np;
          printf("[Semántica] bg_2_node: se identificaron 2 nodos, %d y %d\n", np->nodo1, np->nodo2);
      }
;

/* Reglas para los nodos (bg_vertice) */
bg_vertice:
      /* Agregar un vértice: IDENTIFIER ':' TOKEN_NODE TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_RPAREN */
      IDENTIFIER ':' TOKEN_NODE TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_RPAREN
      {
          Symbol *sym = lookupSymbol($1);
          if(!sym || sym->type != SYM_BIGRAPH) {
              fprintf(stderr, "Error semántico: '%s' no es un bigrafo declarado.\n", $1);
              exit(1);
          }
          genIR("CALL agregarNodo, %s, %s", $1, $5);
          printf("[Semántica] bg_vertice: Agregar nodo %s a %s.\n", $5, $1);
      }
    | /* Intercambiar dos nodos: IDENTIFIER ':' TOKEN_NODE bg_2_node */
      IDENTIFIER ':' TOKEN_NODE bg_2_node
      {
          Symbol *sym = lookupSymbol($1);
          if(!sym || sym->type != SYM_BIGRAPH) {
              fprintf(stderr, "Error semántico: '%s' no es un bigrafo declarado.\n", $1);
              exit(1);
          }
          genIR("CALL intercambiarNodos, %s, (%s,%s)", $1, $3->nodo1, $3->nodo2);
          printf("[Semántica] bg_vertice: Intercambiar nodos en %s: (%s,%s).\n", $1, $3->nodo1, $3->nodo2);
      }
    | /* Borrar un nodo: IDENTIFIER ':''r' TOKEN_NODE TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_RPAREN */
      IDENTIFIER ':''r' TOKEN_NODE TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_RPAREN
      {
          Symbol *sym = lookupSymbol($1);
          if(!sym || sym->type != SYM_BIGRAPH) {
              fprintf(stderr, "Error semántico: '%s' no es un bigrafo declarado.\n", $1);
              exit(1);
          }
          genIR("CALL eliminarNodo, %s, %s", $1, $5);
          printf("[Semántica] bg_vertice: Eliminar nodo %s de %s.\n", $5, $1);
      }
;

/* Reglas para enlaces (bg_enlace) */
bg_enlace:
      /* Agregar enlace entre nodos usando bg_2_node */
      IDENTIFIER ':' TOKEN_EDGE bg_2_node
      {
          Symbol *sym = lookupSymbol($1);
          if(!sym || sym->type != SYM_BIGRAPH) {
              fprintf(stderr, "Error semántico: '%s' no es un bigrafo declarado.\n", $1);
              exit(1);
          }
          genIR("CALL agregarEnlace, %s, (%s,%s)", $1, $3->nodo1, $3->nodo2);
          printf("[Semántica] bg_enlace: Agregar enlace en %s con operandos (%s,%s).\n", $1, $3->nodo1, $3->nodo2);
      }
    | /* Composición entre bigrafos: IDENTIFIER ':' TOKEN_EDGE TOKEN_LPAREN IDENTIFIER TOKEN_COMMA IDENTIFIER TOKEN_RPAREN */
      IDENTIFIER ':' TOKEN_EDGE TOKEN_LPAREN IDENTIFIER TOKEN_COMMA IDENTIFIER TOKEN_RPAREN
      {
          genIR("CALL componerBigrafo, %s, %s", $4, $6);
          printf("[Semántica] bg_enlace: Composición de bigrafos: %s y %s.\n", $4, $6);
      }
    | /* Borrar enlace: IDENTIFIER ':''r' TOKEN_EDGE bg_2_node */
      IDENTIFIER ':''r' TOKEN_EDGE bg_2_node
      {
          genIR("CALL eliminarEnlace, %s, (%s,%s)", $1, $3->nodo1, $3->nodo2);
          printf("[Semántica] bg_enlace: Eliminar enlace en %s con operandos (%s,%s).\n", $1, $3->nodo1, $3->nodo2);
      }
;

/* Regla para control (bg_ctl) */
bg_ctl:
      IDENTIFIER ':' TOKEN_TYPE TOKEN_LPAREN STRING TOKEN_COMMA ELEMENTO_ARREGLO TOKEN_RPAREN
      {
          genIR("CALL definirTipo, %s, %s, %s", $1, $3, $5);
          printf("[Semántica] bg_ctl: Definir tipo %s para %s en %s.\n", $3, $5, $1);
      }
;

/* Regla para parentesco (bg_parent) */
bg_parent:
      IDENTIFIER ':' TOKEN_CHILD bg_2_node
      {
          genIR("CALL crearParentesco, %s, (%s,%s)", $1, $3->nodo1, $3->nodo2);
          printf("[Semántica] bg_parent: Crear parentesco en %s con operandos (%s,%s).\n", $1, $3->nodo1, $3->nodo2);
      }
;

/* Regla para enlaces de salida (bg_exit) */
bg_exit:
      IDENTIFIER ':' TOKEN_LNK TOKEN_LPAREN ELEMENTO_ARREGLO TOKEN_COMMA NAT TOKEN_RPAREN
      {
          genIR("CALL crearEnlaceSalida, %s, %s, %s", $1, $3, $5);
          printf("[Semántica] bg_exit: Crear enlace de salida en %s con %s y nat %s.\n", $1, $3, $5);
      }
;

%%

int main(int argc, char **argv) {
    yyparse();
    return 0;
}
