%{
    /**
     * @archivo: analizador_sintactico.y
     * @descripción: Analizador sintáctico para un lenguaje de programación personalizado
     *              que construye un Árbol de Sintaxis Abstracta (AST)
     * @autor: [Nombre del autor]
     * @fecha: [Fecha de creación/modificación]
     * @versión: 1.0
     */
    
    // Inclusión de las bibliotecas estándar necesarias para la entrada/salida y manejo de memoria.
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    // Inclusión de cabeceras del compilador para el manejo del AST, análisis semántico y generación de código intermedio.
    #include "ast.h"
    #include "analizador_semantico.h"
    #include "intermediate_code.h" 

    /**
     * @declaraciones_externas: Elementos definidos en otros archivos del compilador
     * @descripción: Funciones y variables exportadas por el analizador léxico (yylex)
     */
    extern int yylex();
    extern FILE* yyin;
    extern int yylineno;
    
    /**
     * @función: yyerror
     * @descripción: Función para manejar errores durante el análisis sintáctico
     * @parámetros: const char *s - Mensaje de error
     */
    void yyerror(const char *s);

    /**
     * @variable: ast_root
     * @descripción: Puntero a la raíz del Árbol de Sintaxis Abstracta (AST)
     * @inicialización: NULL
     */
    Node* ast_root = NULL;
%}

/**
 * @directiva: parse.error
 * @descripción: Configura Bison para mostrar mensajes de error detallados
 *              durante el análisis sintáctico
 */
%define parse.error verbose

/**
 * @unión: %union
 * @descripción: Define los tipos de datos que pueden ser asociados con símbolos
 *              de la gramática (terminales y no terminales)
 */
%union {
    int symbol_index;         // Índice en la tabla de símbolos para identificadores y valores
    struct Node *node;        // Puntero a nodo del AST para construcciones sintácticas
}

/**
 * @tokens: Declaración de tokens con sus tipos asociados
 * @descripción: Define los tokens (símbolos terminales) reconocidos por el analizador léxico
 */
%token <symbol_index> TOKEN_ID TOKEN_NUMBER
%token TOKEN_FUN TOKEN_RET TOKEN_IF TOKEN_WHILE TOKEN_ENT TOKEN_FLO TOKEN_NAT TOKEN_ARREGLO
%token TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE
%token TOKEN_PLUS TOKEN_MINUS TOKEN_MULT TOKEN_DIV TOKEN_ASSIGN
%token TOKEN_SEMICOLON TOKEN_COMMA TOKEN_LPAREN TOKEN_RPAREN TOKEN_LBRACE TOKEN_RBRACE
%token TOKEN_LBRACK TOKEN_RBRACK 
%type <symbol_index> relop type

/**
 * @no_terminales: Declaración de símbolos no terminales con sus tipos asociados
 * @descripción: Define los símbolos no terminales de la gramática y su tipo de dato asociado
 */
%type <node> program function_list function param_list param
%type <node> block statement_list statement declaration_stmt assignment_stmt
%type <node> if_stmt while_stmt return_stmt condition expr arg_list
%type <node> array_decl array_literal array_access array_elements


/**
 * @precedencia: Declaración de precedencia y asociatividad de operadores
 * @descripción: Define la precedencia relativa y asociatividad de los operadores
 *              (menor precedencia arriba, mayor precedencia abajo)
 */
%left TOKEN_PLUS TOKEN_MINUS
%left TOKEN_MULT TOKEN_DIV
%nonassoc TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE

%%

/**
 * @regla: program
 * @descripción: Punto de entrada de la gramática que define un programa
 *              como una lista de funciones
 * @acción_semántica: Crea el nodo raíz del AST de tipo NODE_PROGRAM
 */
program 
    : function_list    { 
        $$ = create_node(NODE_PROGRAM, $1, NULL);
        ast_root = $$;  // Asigna la raíz del AST para su posterior procesamiento.
    }
    ;

/**
 * @regla: function_list
 * @descripción: Define una lista de funciones que puede contener
 *              una o más declaraciones de funciones
 * @acción_semántica: Mantiene una lista enlazada de nodos de función
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

/**
 * @regla: function
 * @descripción: Define la estructura de una función con su nombre,
 *              lista de parámetros y bloque de código
 * @acción_semántica: Crea un nodo de función en el AST con los parámetros y el bloque
 */
function
    : TOKEN_FUN TOKEN_ID TOKEN_LPAREN param_list TOKEN_RPAREN block
                                     { 
                                        Node *func = create_node(NODE_FUNCTION, $4, $6);
                                        func->symbol_index = $2;  // Asigna el índice del identificador de la función.
                                        $$ = func;
                                     }
    ;

/**
 * @regla: param_list
 * @descripción: Define la lista de parámetros de una función,
 *              que puede estar vacía o contener varios parámetros separados por comas
 * @acción_semántica: Construye una lista enlazada de nodos de parámetros
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

/**
 * @regla: param
 * @descripción: Define un parámetro individual con su tipo y nombre
 * @acción_semántica: Crea un nodo identificador para el parámetro
 */
param
    : type TOKEN_ID                   {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $2;  // Asigna el índice del identificador del parámetro.
                                        $$ = id;
                                     }
    ;

/**
 * @regla: type
 * @descripción: Define los tipos de datos primitivos del lenguaje
 * @acción_semántica: Retorna el token correspondiente al tipo
 */
type
    : TOKEN_ENT                      { $$ = TOKEN_ENT; }
    | TOKEN_FLO                      { $$ = TOKEN_FLO; }
    | TOKEN_NAT                      { $$ = TOKEN_NAT; }
    ;

/**
 * @regla: block
 * @descripción: Define un bloque de código delimitado por llaves
 *              que contiene una lista de sentencias
 * @acción_semántica: Crea un nodo de bloque que contiene las sentencias
 */
block
    : TOKEN_LBRACE statement_list TOKEN_RBRACE
                                     { $$ = create_node(NODE_BLOCK, $2, NULL); }
    ;

/**
 * @regla: statement_list
 * @descripción: Define una lista de sentencias dentro de un bloque,
 *              que puede estar vacía o contener múltiples sentencias
 * @acción_semántica: Construye una lista enlazada de nodos de sentencias
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

/**
 * @regla: statement
 * @descripción: Define los diferentes tipos de sentencias permitidas en el lenguaje
 * @acción_semántica: Pasa el nodo creado por la regla específica
 */
statement
    : declaration_stmt
    | assignment_stmt
    | if_stmt
    | while_stmt
    | return_stmt
    | array_decl
    ;

/**
 * @regla: declaration_stmt
 * @descripción: Define una sentencia de declaración de variable con
 *              tipo, nombre y valor inicial
 * @acción_semántica: Crea un nodo de declaración con el identificador y la expresión
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

/**
 * @regla: assignment_stmt
 * @descripción: Define una sentencia de asignación a una variable
 *              existente o a un elemento de un arreglo
 * @acción_semántica: Crea un nodo de asignación con el destino y el valor
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

/**
 * @regla: if_stmt
 * @descripción: Define una sentencia condicional if con su condición
 *              y bloque de código asociado
 * @acción_semántica: Crea un nodo if con la condición y el bloque
 */
if_stmt
    : TOKEN_IF TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_IF, $3, $5); }
    ;

/**
 * @regla: while_stmt
 * @descripción: Define una sentencia de bucle while con su condición
 *              y bloque de código a repetir
 * @acción_semántica: Crea un nodo while con la condición y el bloque
 */
while_stmt
    : TOKEN_WHILE TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_WHILE, $3, $5); }
    ;

/**
 * @regla: return_stmt
 * @descripción: Define una sentencia de retorno de valor desde una función
 * @acción_semántica: Crea un nodo return con la expresión a retornar
 */
return_stmt
    : TOKEN_RET expr TOKEN_SEMICOLON  { $$ = create_node(NODE_RETURN, $2, NULL); }
    ;

/**
 * @regla: condition
 * @descripción: Define una condición como una expresión relacional
 *              (comparación entre dos expresiones)
 * @acción_semántica: Crea un nodo de operación binaria con el operador relacional
 */
condition
    : expr relop expr                { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = $2;  // El índice del operador relacional.
                                     }
    ;

/**
 * @regla: relop
 * @descripción: Define los operadores de relación para comparaciones
 * @acción_semántica: Retorna el token correspondiente al operador
 */
relop
    : TOKEN_RELOP_LT                 { $$ = TOKEN_RELOP_LT; }
    | TOKEN_RELOP_LE                 { $$ = TOKEN_RELOP_LE; }
    | TOKEN_RELOP_EQ                 { $$ = TOKEN_RELOP_EQ; }
    | TOKEN_RELOP_NE                 { $$ = TOKEN_RELOP_NE; }
    | TOKEN_RELOP_GT                 { $$ = TOKEN_RELOP_GT; }
    | TOKEN_RELOP_GE                 { $$ = TOKEN_RELOP_GE; }
    ;

/**
 * @regla: expr
 * @descripción: Define las expresiones del lenguaje, incluyendo:
 *              - Identificadores
 *              - Números
 *              - Acceso a elementos de arreglos
 *              - Literales de arreglos
 *              - Llamadas a funciones
 *              - Operaciones aritméticas
 *              - Expresiones agrupadas con paréntesis
 * @acción_semántica: Crea los nodos correspondientes según el tipo de expresión
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

/**
 * @regla: arg_list
 * @descripción: Define la lista de argumentos para una llamada a función,
 *              que puede estar vacía o contener múltiples expresiones
 * @acción_semántica: Construye una lista enlazada de nodos de expresiones
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

/**
 * @regla: array_decl
 * @descripción: Define la declaración de arreglos, con o sin inicialización
 * @acción_semántica: Crea nodos para representar la declaración y tamaño del arreglo
 */
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

/**
 * @regla: array_literal
 * @descripción: Define un literal de arreglo como una lista de elementos
 *              encerrados entre corchetes
 * @acción_semántica: Crea un nodo para representar el literal de arreglo
 */
array_literal
    : TOKEN_LBRACK array_elements TOKEN_RBRACK {
        $$ = create_node(NODE_ARRAY_LITERAL, $2, NULL);
    }
    | TOKEN_LBRACK TOKEN_RBRACK {
        $$ = create_node(NODE_ARRAY_LITERAL, NULL, NULL);  // Empty array
    }
    ;

/**
 * @regla: array_elements
 * @descripción: Define la lista de elementos dentro de un literal de arreglo
 * @acción_semántica: Construye una lista enlazada de nodos de expresiones
 */
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

/**
 * @regla: array_access
 * @descripción: Define el acceso a un elemento de un arreglo mediante su índice
 * @acción_semántica: Crea un nodo para representar el acceso por índice
 */
array_access
    : TOKEN_ID TOKEN_LBRACK expr TOKEN_RBRACK {
        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
        id->symbol_index = $1;
        $$ = create_node(NODE_ARRAY_ACCESS, id, $3);
    }
    ;

%%

/**
 * @función: yyerror
 * @descripción: Función para manejo de errores sintácticos detectados durante el parseo
 * 
 * @parámetros:
 *   - s: Mensaje de error proporcionado por Bison
 * 
 * @comportamiento:
 *   Imprime un mensaje de error en stderr que incluye:
 *   - El mensaje de error original
 *   - El número de línea donde ocurrió el error (obtenido de yylineno)
 */
void yyerror(const char *s) {
    fprintf(stderr, "Error: %s at line %d\n", s, yylineno);
}

/**
 * @función: main
 * @descripción: Punto de entrada principal del compilador que coordina
 *              las fases de análisis y generación de código
 * 
 * @parámetros:
 *   - argc: Número de argumentos de línea de comandos
 *   - argv: Array de cadenas de argumentos
 * 
 * @retorno:
 *   - 0: Compilación exitosa
 *   - 1: Error durante la compilación
 * 
 * @flujo_de_ejecución:
 *   1. Verifica los argumentos de línea de comandos
 *   2. Abre el archivo de entrada
 *   3. Ejecuta el análisis sintáctico (yyparse)
 *   4. Si el análisis es exitoso:
 *      a. Ejecuta el análisis semántico
 *      b. Genera código intermedio
 *   5. Muestra mensajes de progreso y estado
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