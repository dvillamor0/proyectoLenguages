%{
    // Inclusión de las bibliotecas estándar necesarias para la entrada/salida y manejo de memoria.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    // Inclusión de cabeceras del compilador para el manejo del AST, análisis semántico y generación de código intermedio.
    #include "ast.h"
    #include "analizador_semantico.h"
    #include "intermediate_code.h" 

    // Declaración externa de funciones y variables utilizadas en el proceso de análisis léxico.
    extern int yylex();
    extern FILE* yyin;
    extern int yylineno;
    void yyerror(const char *s);

    // Declaración de la raíz del árbol de sintaxis abstracta.
    Node* ast_root = NULL;
%}

%define parse.error verbose  // Configuración para mostrar errores de parseo de forma detallada.

%union {
    int symbol_index;         // Unión para almacenar índices de símbolos.
    struct Node *node;        // Unión para almacenar nodos del AST.
}

// Declaración de tokens con sus tipos de datos asociados.
%token <symbol_index> TOKEN_ID TOKEN_NUMBER TOKEN_STRING
%token TOKEN_FUN TOKEN_RET TOKEN_IF TOKEN_WHILE TOKEN_ENT TOKEN_FLO TOKEN_NAT TOKEN_ARREGLO
%token TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE
%token TOKEN_PLUS TOKEN_MINUS TOKEN_MULT TOKEN_DIV TOKEN_ASSIGN
%token TOKEN_SEMICOLON TOKEN_COMMA TOKEN_LPAREN TOKEN_RPAREN TOKEN_LBRACE TOKEN_RBRACE
%token TOKEN_LBRACK TOKEN_RBRACK

/* Bigraph operation tokens */
%token TOKEN_BIG TOKEN_NOD TOKEN_RNOD TOKEN_ENL TOKEN_RENL TOKEN_TIP TOKEN_RTIP TOKEN_HIJ TOKEN_LNK TOKEN_RLNK

%type <symbol_index> relop type

// Declaración de no terminales y su tipo asociado (puntero a nodo).
%type <node> program function_list function param_list param
%type <node> block statement_list statement declaration_stmt assignment_stmt
%type <node> if_stmt while_stmt return_stmt condition expr arg_list
%type <node> array_decl array_literal array_access array_elements

/* Bigraph non-terminals */
%type <node> bigraph_decl bigraph_init bigraph_operation bigraph_array_access
%type <node> node_list string_expr

// Declaración de la precedencia y asociatividad de los operadores.
%left TOKEN_PLUS TOKEN_MINUS
%left TOKEN_MULT TOKEN_DIV
%nonassoc TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE

%%

/*
 * Regla: program
 * ---------------
 * Define la producción principal del programa.
 * Se crea el nodo raíz del AST (tipo NODE_PROGRAM) a partir de la lista de funciones.
 */
program 
    : function_list    { 
        $$ = create_node(NODE_PROGRAM, $1, NULL);
        ast_root = $$;  // Asigna la raíz del AST para su posterior procesamiento.
    }
    ;

/*
 * Regla: function_list
 * --------------------
 * Define la lista de funciones. Puede ser una única función o una lista de ellas.
 */
function_list
    : function                        { $$ = $1; }
    | function_list function          { 
                                        $$ = $1;
                                        // Se recorre la lista hasta el último nodo y se enlaza la nueva función.
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $2;
                                     }
    ;

/*
 * Regla: function
 * ----------------
 * Define la estructura de una función: palabra clave, identificador, parámetros y bloque.
 */
function
    : TOKEN_FUN TOKEN_ID TOKEN_LPAREN param_list TOKEN_RPAREN block
                                     { 
                                        Node *func = create_node(NODE_FUNCTION, $4, $6);
                                        func->symbol_index = $2;  // Asigna el índice del identificador de la función.
                                        $$ = func;
                                     }
    ;

/*
 * Regla: param_list
 * -----------------
 * Define la lista de parámetros de una función.
 * Puede estar vacía o contener uno o más parámetros separados por comas.
 */
param_list
    : /* empty */                     { $$ = NULL; }
    | param                           { $$ = $1; }
    | param_list TOKEN_COMMA param    {
                                        $$ = $1;
                                        // Se recorre la lista de parámetros y se enlaza el nuevo parámetro.
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $3;
                                     }
    ;

/*
 * Regla: param
 * ------------
 * Define un parámetro, que consta de un tipo y un identificador.
 */
param
    : type TOKEN_ID                   {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $2;  // Asigna el índice del identificador del parámetro.
                                        $$ = id;
                                     }
    ;

/*
 * Regla: type
 * -----------
 * Define los tipos de datos válidos para los parámetros y declaraciones (entero o flotante).
 */
type
    : TOKEN_ENT                      { $$ = TOKEN_ENT; }
    | TOKEN_FLO                      { $$ = TOKEN_FLO; }
    | TOKEN_NAT                      { $$ = TOKEN_NAT; }
    ;

/*
 * Regla: block
 * ------------
 * Define un bloque de código, delimitado por llaves, que contiene una lista de sentencias.
 */
block
    : TOKEN_LBRACE statement_list TOKEN_RBRACE
                                     { $$ = create_node(NODE_BLOCK, $2, NULL); }
    ;

/*
 * Regla: statement_list
 * ---------------------
 * Define una lista de sentencias dentro de un bloque.
 */
statement_list
    : /* empty */                     { $$ = NULL; }
    | statement_list statement        {
                                        if ($1 == NULL) {
                                            $$ = $2;
                                        } else {
                                            $$ = $1;
                                            // Se recorre la lista de sentencias y se enlaza la nueva sentencia.
                                            Node *last = $1;
                                            while(last->next) last = last->next;
                                            last->next = $2;
                                        }
                                     }
    ;

/*
 * Regla: statement
 * ----------------
 * Define las diferentes sentencias válidas en el lenguaje.
 */
statement
    : declaration_stmt
    | assignment_stmt
    | if_stmt
    | while_stmt
    | return_stmt
    | array_decl
    | bigraph_operation
    | TOKEN_SEMICOLON              { $$ = NULL; }
    ;

/*
 * Regla: declaration_stmt
 * ------------------------
 * Define una sentencia de declaración, con asignación inicial.
 */
declaration_stmt
    : type TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON
                                     {
                                        // Se crea un nodo identificador y se asocia a la declaración.
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $2;
                                        $$ = create_node(NODE_DECLARATION, id, $4);
                                     }
    ;

/*
 * Regla: assignment_stmt
 * -----------------------
 * Define una sentencia de asignación a una variable existente.
 */
assignment_stmt
    : TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $1;
        $$ = create_node(NODE_ASSIGNMENT, id, $3);
    }
    | array_access TOKEN_ASSIGN expr TOKEN_SEMICOLON {
        $$ = create_node(NODE_ARRAY_ASSIGNMENT, $1, $3);
    }
    ;

/*
 * Regla: if_stmt
 * --------------
 * Define una sentencia condicional (if) con su condición y bloque de sentencias.
 */
if_stmt
    : TOKEN_IF TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_IF, $3, $5); }
    ;

/*
 * Regla: while_stmt
 * -----------------
 * Define una sentencia de bucle while con su condición y bloque de sentencias.
 */
while_stmt
    : TOKEN_WHILE TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_WHILE, $3, $5); }
    ;

/*
 * Regla: return_stmt
 * ------------------
 * Define una sentencia de retorno, que devuelve el resultado de una expresión.
 */
return_stmt
    : TOKEN_RET expr TOKEN_SEMICOLON  { $$ = create_node(NODE_RETURN, $2, NULL); }
    ;

/*
 * Regla: condition
 * ----------------
 * Define la condición de sentencias if y while, compuesta por una expresión relacional.
 */
condition
    : expr relop expr                { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = $2;  // El índice del operador relacional.
                                     }
    ;

/*
 * Regla: relop
 * ------------
 * Define los operadores relacionales válidos.
 */
relop
    : TOKEN_RELOP_LT                 { $$ = TOKEN_RELOP_LT; }
    | TOKEN_RELOP_LE                 { $$ = TOKEN_RELOP_LE; }
    | TOKEN_RELOP_EQ                 { $$ = TOKEN_RELOP_EQ; }
    | TOKEN_RELOP_NE                 { $$ = TOKEN_RELOP_NE; }
    | TOKEN_RELOP_GT                 { $$ = TOKEN_RELOP_GT; }
    | TOKEN_RELOP_GE                 { $$ = TOKEN_RELOP_GE; }
    ;

/*
 * Regla: expr
 * -----------
 * Define las expresiones aritméticas y de llamada a función.
 */
expr
    : TOKEN_ID {
        $$ = create_node(NODE_IDENTIFIER, NULL, NULL);
        $$->symbol_index = $1;
    }
    | TOKEN_NUMBER {
        $$ = create_node(NODE_NUMBER, NULL, NULL);
        $$->symbol_index = $1;
    }
    | array_access {
        $$ = $1;
    }
    | array_literal {
        $$ = $1;
    }
    | TOKEN_ID TOKEN_LPAREN arg_list TOKEN_RPAREN {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $1;
        $$ = create_node(NODE_FUNCTION_CALL, id, $3);
    }
    | expr TOKEN_PLUS expr {
        $$ = create_node(NODE_BINARY_OP, $1, $3);
        $$->symbol_index = TOKEN_PLUS;
    }
    | expr TOKEN_MINUS expr {
        $$ = create_node(NODE_BINARY_OP, $1, $3);
        $$->symbol_index = TOKEN_MINUS;
    }
    | expr TOKEN_MULT expr {
        $$ = create_node(NODE_BINARY_OP, $1, $3);
        $$->symbol_index = TOKEN_MULT;
    }
    | expr TOKEN_DIV expr {
        $$ = create_node(NODE_BINARY_OP, $1, $3);
        $$->symbol_index = TOKEN_DIV;
    }
    | TOKEN_LPAREN expr TOKEN_RPAREN {
        $$ = $2;
    }
    ;

/*
 * Regla: arg_list
 * ---------------
 * Define la lista de argumentos en la llamada a una función.
 * Puede estar vacía o contener uno o más argumentos separados por comas.
 */
arg_list
    : /* empty */                     { $$ = NULL; }
    | expr                            { $$ = $1; }
    | arg_list TOKEN_COMMA expr       {
                                        $$ = $1;
                                        // Se enlaza el nuevo argumento al final de la lista.
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $3;
                                     }
    ;

array_decl
    : TOKEN_ARREGLO type TOKEN_ID TOKEN_LBRACK expr TOKEN_RBRACK TOKEN_SEMICOLON {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $3;
        
        // Create array type node with size expression
        Node *array_type = create_node(NODE_ARRAY_TYPE, NULL, NULL);
        array_type->symbol_index = $2;  // Store the base type token
        
        // Create array declaration node
        $$ = create_node(NODE_ARRAY_DECL, id, $5);  // Left: ID, Right: Size expression
    }
    | TOKEN_ARREGLO type TOKEN_ID TOKEN_LBRACK expr TOKEN_RBRACK TOKEN_ASSIGN array_literal TOKEN_SEMICOLON {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $3;
        
        // Create array type node with size expression
        Node *array_type = create_node(NODE_ARRAY_TYPE, NULL, NULL);
        array_type->symbol_index = $2;  // Store the base type token
        
        // Create array declaration node with initialization
        Node *size_and_type = create_node(NODE_ARRAY_SIZE, $5, array_type);
        $$ = create_node(NODE_ARRAY_DECL, id, create_node(NODE_ARRAY_INIT, size_and_type, $8));
    }
    ;

array_literal
    : TOKEN_LBRACK array_elements TOKEN_RBRACK {
        $$ = create_node(NODE_ARRAY_LITERAL, $2, NULL);
    }
    | TOKEN_LBRACK TOKEN_RBRACK {
        $$ = create_node(NODE_ARRAY_LITERAL, NULL, NULL);  // Empty array
    }
    ;

array_elements
    : expr {
        $$ = $1;
    }
    | array_elements TOKEN_COMMA expr {
        $$ = $1;
        Node *last = $1;
        while (last->next) last = last->next;
        last->next = $3;
    }
    ;

array_access
    : TOKEN_ID TOKEN_LBRACK expr TOKEN_RBRACK {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $1;
        $$ = create_node(NODE_ARRAY_ACCESS, id, $3);
    }
    ;

/* 
 * Bigraph-related grammar rules
 */

// Bigraph declaration
bigraph_decl
    : TOKEN_BIG TOKEN_ID TOKEN_SEMICOLON {
        // Declare empty bigraph
        Node *node = create_node(NODE_BIGRAPH_DECL, NULL, NULL);
        node->symbol_index = $2;
        $$ = node;
    }
    | TOKEN_BIG TOKEN_ID TOKEN_ASSIGN bigraph_init TOKEN_SEMICOLON {
        // Declare and initialize bigraph
        Node *node = create_node(NODE_BIGRAPH_DECL, $4, NULL);
        node->symbol_index = $2;
        $$ = node;
    }
    ;

// Bigraph initialization with array of nodes
bigraph_init
    : TOKEN_LBRACK node_list TOKEN_RBRACK {
        $$ = $2;
    }
    ;

// List of node names for initialization
node_list
    : string_expr {
        $$ = $1;
    }
    | node_list TOKEN_COMMA string_expr {
        $$ = $1;
        Node *last = $1;
        while(last->next) last = last->next;
        last->next = $3;
    }
    ;

// String expression (for node names)
string_expr
    : TOKEN_STRING {
        Node *node = create_node(NODE_STRING_LITERAL, NULL, NULL);
        node->symbol_index = $1;
        $$ = node;
    }
    ;

// Array access for bigraph operations
bigraph_array_access
    : TOKEN_ID TOKEN_LBRACK expr TOKEN_RBRACK {
        Node *node = create_node(NODE_ARRAY_ACCESS, NULL, $3);
        node->symbol_index = $1;
        $$ = node;
    }
    ;

// Bigraph operations
bigraph_operation
    : TOKEN_ID TOKEN_NOD TOKEN_LPAREN string_expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Add node: b1:nod("a");
        Node *node = create_node(NODE_BIGRAPH_ADD_NODE, $4, NULL);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_NOD TOKEN_LPAREN string_expr TOKEN_COMMA string_expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Replace node: b2:nod("c","d");
        Node *node = create_node(NODE_BIGRAPH_REPLACE_NODE, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_RNOD TOKEN_LPAREN string_expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Remove node: b2:rnod("b");
        Node *node = create_node(NODE_BIGRAPH_REMOVE_NODE, $4, NULL);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_ENL TOKEN_LPAREN expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Add edge: b2:enl(nodos[0],nodos[3]);
        Node *node = create_node(NODE_BIGRAPH_ADD_EDGE, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_RENL TOKEN_LPAREN expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Remove edge: b2:renl(nodos[0],nodos[3]);
        Node *node = create_node(NODE_BIGRAPH_REMOVE_EDGE, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_TIP TOKEN_LPAREN string_expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Add type relation: b2:tip("pc",nodos[0]);
        Node *node = create_node(NODE_BIGRAPH_ADD_TYPE, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_RTIP TOKEN_LPAREN string_expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Remove type relation: b2:rtip("pc",nodos[0]);
        Node *node = create_node(NODE_BIGRAPH_REMOVE_TYPE, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_ENL TOKEN_LPAREN TOKEN_ID TOKEN_COMMA TOKEN_ID TOKEN_RPAREN TOKEN_SEMICOLON {
        // Compose bigraphs: b3:enl(b1,b2);
        Node *left = create_node(NODE_IDENTIFIER, NULL, NULL);
        left->symbol_index = $4;
        Node *right = create_node(NODE_IDENTIFIER, NULL, NULL);
        right->symbol_index = $6;
        Node *node = create_node(NODE_BIGRAPH_COMPOSE, left, right);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_HIJ TOKEN_LPAREN expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Add parent-child relation: b2:hij(nodos[2],nodos[0]);
        Node *node = create_node(NODE_BIGRAPH_ADD_PARENT, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_LNK TOKEN_LPAREN expr TOKEN_COMMA expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Set link count: b2:lnk(nodos[0],2);
        Node *node = create_node(NODE_BIGRAPH_SET_LINK, $4, $6);
        node->symbol_index = $1;
        $$ = node;
    }
    | TOKEN_ID TOKEN_RLNK TOKEN_LPAREN expr TOKEN_RPAREN TOKEN_SEMICOLON {
        // Remove link count: b2:rlnk(nodos[0]);
        Node *node = create_node(NODE_BIGRAPH_REMOVE_LINK, $4, NULL);
        node->symbol_index = $1;
        $$ = node;
    }
    ;

%%

/*
 * Función: yyerror
 * ----------------
 * Función de manejo de errores de parseo.
 * Imprime un mensaje de error junto con el número de línea donde ocurrió.
 */
void yyerror(const char *s) {
    fprintf(stderr, "Error: %s at line %d\n", s, yylineno);
}

/*
 * Función: main
 * -------------
 * Función principal del compilador.
 * Se encarga de inicializar el proceso de compilación, abrir el archivo de entrada,
 * ejecutar el análisis sintáctico, el análisis semántico y la generación de código intermedio.
 */
int main(int argc, char **argv) {
    // Mensaje de inicio del compilador.
    printf("Debug: Iniciando compilador\n");
    
    // Verificar que se haya proporcionado al menos un archivo de entrada.
    if (argc < 2) {
        fprintf(stderr, "Debug: No se proporciono archivo de entrada\n");
        fprintf(stderr, "Uso: %s <archivo_de_entrada>\n", argv[0]);
        return 1;
    }

    // Intentar abrir el archivo de entrada y notificar el estado.
    printf("Debug: Intentando abrir archivo: %s\n", argv[1]);
    if (!(yyin = fopen(argv[1], "r"))) {
        fprintf(stderr, "Debug: Error al abrir archivo de entrada\n");
        perror(argv[1]);
        return 1;
    }
    printf("Debug: Archivo de entrada abierto exitosamente\n");

    // Iniciar el proceso de analisis sintactico.
    printf("Debug: Iniciando analisis sintactico\n");
    int parse_result = yyparse();
    printf("Debug: Resultado del analisis = %d (0 indica exito)\n", parse_result);
    
    // Si el analisis sintactico es exitoso, proceder con el analisis semantico y la generacion de codigo intermedio.
    if (parse_result == 0) {
        if (ast_root) {
            printf("Debug: AST creado exitosamente\n");
            printf("Debug: Iniciando analisis semantico\n");
            init_semantic_analysis(ast_root);
            printf("Debug: Analisis semantico completado\n");
            
            printf("Debug: Generando codigo intermedio\n");
            char output_file[256];
            strncpy(output_file, argv[2], sizeof(output_file) - 1);
            output_file[sizeof(output_file) - 1] = '\0';
            char *dot = strrchr(output_file, '.');
            if (dot) {
                strcpy(dot, ".tac");
            } else {
                strcat(output_file, ".tac");
            }
            generate_intermediate_code(ast_root, output_file);
            printf("Debug: Generacion de codigo intermedio completada\n");
        } else {
            fprintf(stderr, "Debug: La raiz del AST es NULL a pesar de un analisis exitoso\n");
            return 1;
        }
    } else {
        fprintf(stderr, "Debug: Analisis sintactico fallido\n");
        return 1;
    }
    
    // Mensaje final indicando que la compilacion se completo exitosamente.
    printf("Debug: Compilacion completada exitosamente\n");
    return 0;
}