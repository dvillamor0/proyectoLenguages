%{
#include <stdio.h>
#include <stdlib.h>
#include "tokens.h"
#include "symbol_table.h"

void yyerror(const char *s);
int yylex(void);

extern int yylineno; 
extern char *tablaSimbolos[];
extern FILE *yyin;

SymbolTable *symbolTable;

SymbolType get_symbol_type(int token) {
    if (token == INT) return TYPE_INT;
    if (token == STRING_TYPE) return TYPE_STRING;
    if (token == LIST_TYPE) return TYPE_LIST;
    return TYPE_UNKNOWN;
}
%}

/*================================================================
  Declaraciones de Bison
================================================================*/

%union {
    int token_type;
    char* string_val;
}

%token IF ELSE INPUT PRINT WHILE RETURN
%token APPEND DELETE LENGTH
%token <token_type> ID NUMBER STRING
%token ASSIGN
%token EQ NE LT GT LE GE
%token PLUS MINUS TIMES DIV
%token LPAREN RPAREN COLON COMMA
%token LBRACKET RBRACKET DOT SEMICOLON
%token LBRACE RBRACE
%token <token_type> INT STRING_TYPE LIST_TYPE

%type <token_type> type_specifier
%type <token_type> expr
%type <token_type> assignment_expr
%type <token_type> logical_expr
%type <token_type> relational_expr
%type <token_type> additive_expr
%type <token_type> multiplicative_expr
%type <token_type> unary_expr
%type <token_type> postfix_expr
%type <token_type> primary_expr
%type <token_type> list_expr
%type <token_type> expr_list
%type <token_type> expr_list_opt

%right ASSIGN
%left EQ NE
%left LT GT LE GE
%left PLUS MINUS
%left TIMES DIV
%right UMINUS
%nonassoc THEN
%nonassoc ELSE

%%

/*================================================================
  Reglas de la Gramática
================================================================*/

program
    : /* Crear la tabla de símbolos antes de cualquier declaración. */
      { symbolTable = create_symbol_table(); }
      statement_list
      {
        /* Después de analizar correctamente todo, imprimir la tabla de símbolos. */
        print_symbol_table(symbolTable);
      }
    ;

/* Una lista de declaraciones, posiblemente vacía. */
statement_list
    : /* vacío */
    | statement_list statement
    ;

/* Una declaración puede ser de varias formas. */
statement
    : declaration
    | expr_stmt
    | compound_stmt
    | if_stmt
    | while_stmt
    | io_stmt
    | return_stmt
    ;

/* Las declaraciones compuestas (bloques) usan llaves. */
compound_stmt
    : LBRACE 
      {
        /* Entrar en un nuevo ámbito al encontrar '{' */
        enter_scope(symbolTable);
      }
      statement_list 
      RBRACE 
      {
        /* Salir del ámbito al encontrar la '}' correspondiente */
        exit_scope(symbolTable);
      }
    ;

/* Declaración if. El %prec THEN ayuda a tratar con el else colgante. */
if_stmt
    : IF LPAREN expr RPAREN compound_stmt %prec THEN
    | IF LPAREN expr RPAREN compound_stmt ELSE compound_stmt
    ;

/* Declaración while. */
while_stmt
    : WHILE LPAREN expr RPAREN compound_stmt
    ;

/* Declaración de una variable: ya sea "int x;" o "int x = expr;" etc. */
declaration
    : type_specifier ID SEMICOLON
      {
        SymbolType type = get_symbol_type($1);
        Symbol *sym = insert_symbol(symbolTable, tablaSimbolos[$2], type);
        (void)sym;  /* Evitar la advertencia de variable no utilizada si se desea. */
      }
    | type_specifier ID ASSIGN expr SEMICOLON
      {
        SymbolType type = get_symbol_type($1);
        Symbol *sym = insert_symbol(symbolTable, tablaSimbolos[$2], type);
        (void)sym;  /* Podríamos realizar comprobación de tipos aquí si quisiéramos. */
      }
    ;

/* Especificador de tipo: INT, STRING_TYPE, LIST_TYPE */
type_specifier
    : INT         { $$ = INT; }
    | STRING_TYPE { $$ = STRING_TYPE; }
    | LIST_TYPE   { $$ = LIST_TYPE; }
    ;

/* Declaraciones de expresión. */
expr_stmt
    : SEMICOLON
    | expr SEMICOLON
    ;

/* Declaraciones de E/S (entrada/impresión). */
io_stmt
    : INPUT LPAREN expr RPAREN SEMICOLON
    | PRINT LPAREN expr RPAREN SEMICOLON
    ;

/* Sentencias de retorno. */
return_stmt
    : RETURN expr SEMICOLON
    | RETURN SEMICOLON
    ;

/* La gramática de expresiones comienza aquí. */
expr
    : assignment_expr
    ;

/* Expresión de asignación. */
assignment_expr
    : logical_expr
    | ID ASSIGN assignment_expr
      {
        /* Verificar que la variable en el LHS esté declarada. */
        Symbol *sym = lookup_symbol(symbolTable, tablaSimbolos[$1]);
        if (sym == NULL) {
            printf("Error: Variable '%s' no declarada (línea %d)\n", tablaSimbolos[$1], yylineno);
        }
        $$ = $3;
      }
    ;

/* Expresiones lógicas (==, !=). */
logical_expr
    : relational_expr
    | logical_expr EQ relational_expr
    | logical_expr NE relational_expr
    ;

/* Expresiones relacionales (<, >, <=, >=). */
relational_expr
    : additive_expr
    | relational_expr LT additive_expr
    | relational_expr GT additive_expr
    | relational_expr LE additive_expr
    | relational_expr GE additive_expr
    ;

/* Expresiones aditivas (+, -). */
additive_expr
    : multiplicative_expr
    | additive_expr PLUS multiplicative_expr
    | additive_expr MINUS multiplicative_expr
    ;

/* Expresiones multiplicativas (*, /). */
multiplicative_expr
    : unary_expr
    | multiplicative_expr TIMES unary_expr
    | multiplicative_expr DIV unary_expr
    ;

/* Expresiones unarias (menos unario). */
unary_expr
    : postfix_expr
    | MINUS unary_expr %prec UMINUS
      {
        /* Si necesitas almacenar o evaluar el negativo, hazlo aquí. */
        $$ = $2;
      }
    ;

/* Expresiones postfijas (llamadas a métodos de listas, por ejemplo, list.append(expr)). */
postfix_expr
    : primary_expr
    | postfix_expr DOT list_method
      {
        /* Verificar que la variable en el LHS esté declarada y sea de tipo lista. */
        Symbol *sym = lookup_symbol(symbolTable, tablaSimbolos[$1]);
        if (sym == NULL) {
            printf("Error: Variable '%s' no declarada (línea %d)\n", tablaSimbolos[$1], yylineno);
        } else if (sym->type != TYPE_LIST) {
            printf("Error: Los métodos de lista solo se permiten en variables de tipo lista (la variable '%s' es de tipo %s)\n",
                   tablaSimbolos[$1], get_type_name(sym->type));
        }
      }
    ;

/* Métodos de lista: append, delete, length. */
list_method
    : APPEND LPAREN expr RPAREN
    | DELETE LPAREN expr RPAREN
    | LENGTH LPAREN RPAREN
    ;

/* Expresiones primarias: referencias a variables, constantes, paréntesis, literales de listas. */
primary_expr
    : ID
      {
        /* Verificar si esta variable ha sido declarada. */
        Symbol *sym = lookup_symbol(symbolTable, tablaSimbolos[$1]);
        if (sym == NULL) {
            printf("Error: Variable '%s' no declarada (línea %d)\n", tablaSimbolos[$1], yylineno);
        }
        $$ = $1;
      }
    | NUMBER
      {
        $$ = $1;
      }
    | STRING
      {
        $$ = $1;
      }
    | LPAREN expr RPAREN
      {
        $$ = $2;
      }
    | list_expr
      {
        $$ = $1;
      }
    ;

/* Expresiones de listas, por ejemplo, [1,2,3]. */
list_expr
    : LBRACKET expr_list_opt RBRACKET
      {
        $$ = $2;
      }
    ;

/* Lista de expresiones opcional dentro de corchetes. */
expr_list_opt
    : /* vacío */
      {
        $$ = 0;
      }
    | expr_list
      {
        $$ = $1;
      }
    ;

/* Una o más expresiones separadas por comas. */
expr_list
    : expr
    | expr_list COMMA expr
    ;

%%

/*================================================================
  Reporte de Errores y Función Principal
================================================================*/

void yyerror(const char *s) {
    fprintf(stderr, "Error sintáctico en la línea %d: %s\n", yylineno, s);
}

int main(int argc, char **argv) {
    if (argc > 1) {
        if (!(yyin = fopen(argv[1], "r"))) {
            perror(argv[1]);
            return 1;
        }
    }

    int result = yyparse();

    /* Limpiar la tabla de símbolos. */
    if (symbolTable != NULL) {
        delete_symbol_table(symbolTable);
    }

    return result;
}
