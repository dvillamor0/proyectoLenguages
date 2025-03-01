#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "analizador_semantico.h"
#include "analizador_sintactico.tab.h" 

extern struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
} symbol_table[];

// Enumeracion de tipos de datos
typedef enum {
    TYPE_UNKNOWN,
    TYPE_INTEGER,
    TYPE_FLOAT,
    TYPE_VOID
} DataType;

// Estructura que contiene la informacion de un simbolo
typedef struct {
    char *name;
    DataType type;
    int is_function;
    DataType return_type;
    DataType *param_types;
    int param_count;
} SymbolInfo;

// Estructura que representa la tabla de simbolos
typedef struct {
    SymbolInfo *entries;
    int size;
    int capacity;
} SymbolTable;

// Declaracion de funciones estaticas para manejo de la tabla de simbolos y analisis semantico
static SymbolTable* create_symbol_table();
static void add_symbol(SymbolTable *table, const char *name, DataType type);
static void add_function(SymbolTable *table, const char *name, DataType return_type);
static SymbolInfo* lookup_symbol(SymbolTable *table, const char *name);
static DataType check_types(Node *node, SymbolTable *table);
static void analyze_semantics(Node *root, SymbolTable *table);

// Funcion: create_symbol_table
// ------------------------------
// Crea e inicializa una tabla de simbolos con capacidad inicial de 100 entradas.
static SymbolTable* create_symbol_table() {
    SymbolTable *table = malloc(sizeof(SymbolTable));
    table->capacity = 100;
    table->size = 0;
    table->entries = malloc(sizeof(SymbolInfo) * table->capacity);
    return table;
}

// Funcion: add_symbol
// -------------------
// Agrega un simbolo (variable) a la tabla de simbolos.
// Si la tabla esta llena, duplica su capacidad.
static void add_symbol(SymbolTable *table, const char *name, DataType type) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = type;
    table->entries[table->size].is_function = 0;
    table->size++;
}

// Funcion: add_function
// ---------------------
// Agrega una funcion a la tabla de simbolos.
// Si la tabla esta llena, duplica su capacidad.
static void add_function(SymbolTable *table, const char *name, DataType return_type) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = return_type;
    table->entries[table->size].is_function = 1;
    table->entries[table->size].return_type = return_type;
    table->entries[table->size].param_types = NULL;
    table->entries[table->size].param_count = 0;
    table->size++;
}

// Funcion: lookup_symbol
// ------------------------
// Busca un simbolo en la tabla por su nombre.
// Retorna un puntero a la informacion del simbolo o NULL si no se encuentra.
static SymbolInfo* lookup_symbol(SymbolTable *table, const char *name) {
    for (int i = 0; i < table->size; i++) {
        if (strcmp(table->entries[i].name, name) == 0) {
            return &table->entries[i];
        }
    }
    return NULL;
}

// Funcion: get_type_from_token
// ----------------------------
// Asigna un tipo de dato segun el token recibido.
// Se utiliza para determinar el tipo de una variable.
static DataType get_type_from_token(int token) {
    switch (token) {
        case TOKEN_ENT:
            return TYPE_INTEGER;
        case TOKEN_FLO:
            return TYPE_FLOAT;
        default:
            return TYPE_UNKNOWN;
    }
}

// Funcion: check_types
// ---------------------
// Realiza el analisis de tipos de una expresion representada por un nodo del AST.
// Retorna el tipo de dato resultante de la expresion.
static DataType check_types(Node *node, SymbolTable *table) {
    if (!node) return TYPE_VOID;
    
    switch (node->type) {
        case NODE_NUMBER: {
            // Obtiene el string numerico desde la tabla de simbolos
            const char *num_str = symbol_table[node->symbol_index].name;
            // Retorna TYPE_FLOAT si contiene punto o notacion exponencial, sino TYPE_INTEGER
            return (strchr(num_str, '.') || strchr(num_str, 'e') || strchr(num_str, 'E'))
                   ? TYPE_FLOAT : TYPE_INTEGER;
        }
        
        case NODE_IDENTIFIER: {
            // Obtiene el nombre del identificador y lo busca en la tabla
            const char *id_name = symbol_table[node->symbol_index].name;
            SymbolInfo *info = lookup_symbol(table, id_name);
            if (!info) {
                fprintf(stderr, "Semantic Error: Undefined identifier '%s'\n", id_name);
                return TYPE_UNKNOWN;
            }
            return info->type;
        }
        
        case NODE_BINARY_OP: {
            // Comprueba los tipos de las subexpresiones y determina el tipo de la operacion
            DataType left_type = check_types(node->left, table);
            DataType right_type = check_types(node->right, table);
            
            if (left_type == TYPE_FLOAT || right_type == TYPE_FLOAT) {
                return TYPE_FLOAT;
            }
            return TYPE_INTEGER;
        }
        
        case NODE_FUNCTION_CALL: {
            // Obtiene el nombre de la funcion y verifica que sea una funcion
            const char *func_name = symbol_table[node->left->symbol_index].name;
            SymbolInfo *func = lookup_symbol(table, func_name);
            
            if (!func || !func->is_function) {
                fprintf(stderr, "Semantic Error: '%s' is not a function\n", func_name);
                return TYPE_UNKNOWN;
            }
            
            // Verifica los argumentos de la llamada a la funcion
            Node *arg = node->right;
            int arg_count = 0;
            while (arg) {
                DataType arg_type = check_types(arg, table);
                if (arg_count < func->param_count &&
                    arg_type != func->param_types[arg_count]) {
                    fprintf(stderr, "Semantic Error: Type mismatch in argument %d of '%s'\n",
                            arg_count + 1, func_name);
                }
                arg = arg->next;
                arg_count++;
            }
            
            if (arg_count != func->param_count) {
                fprintf(stderr, "Semantic Error: Wrong number of arguments for '%s'\n", func_name);
            }
            
            return func->return_type;
        }
        
        default:
            return TYPE_UNKNOWN;
    }
}

// Funcion: analyze_semantics
// ----------------------------
// Realiza el analisis semantico sobre el arbol de sintaxis abstracta (AST).
// Verifica declaraciones, asignaciones, llamadas a funciones y estructuras de control.
static void analyze_semantics(Node *root, SymbolTable *table) {
    if (!root) return;
    
    switch (root->type) {
        case NODE_FUNCTION: {
            // Procesa una definicion de funcion
            const char *func_name = symbol_table[root->symbol_index].name;
            DataType return_type = TYPE_VOID;
            add_function(table, func_name, return_type);
            
            // Procesa los parametros de la funcion
            Node *param = root->left;
            while (param) {
                const char *param_name = symbol_table[param->symbol_index].name;
                DataType param_type = TYPE_FLOAT;  // Se asume que el tipo de parametro es float
                add_symbol(table, param_name, param_type);
                param = param->next;
            }
            
            // Analiza el cuerpo de la funcion
            analyze_semantics(root->right, table);
            break;
        }
        
        case NODE_DECLARATION: {
            // Procesa una declaracion de variable
            const char *var_name = symbol_table[root->left->symbol_index].name;
            DataType expr_type = check_types(root->right, table);
            add_symbol(table, var_name, expr_type);
            break;
        }
        
        case NODE_ASSIGNMENT: {
            // Procesa una asignacion a una variable
            const char *var_name = symbol_table[root->left->symbol_index].name;
            SymbolInfo *var = lookup_symbol(table, var_name);
            
            if (!var) {
                fprintf(stderr, "Semantic Error: Assignment to undefined variable '%s'\n", var_name);
                break;
            }
            
            DataType expr_type = check_types(root->right, table);
            if (var->type != expr_type) {
                if (var->type == TYPE_FLOAT && expr_type == TYPE_INTEGER) {
                    // Conversion permitida de entero a float
                } else {
                    fprintf(stderr, "Semantic Error: Type mismatch in assignment to '%s'\n", var_name);
                }
            }
            break;
        }
        
        case NODE_IF:
        case NODE_WHILE: {
            // Procesa estructuras de control: if y while
            DataType cond_type = check_types(root->left, table);
            if (cond_type != TYPE_INTEGER && cond_type != TYPE_FLOAT) {
                fprintf(stderr, "Semantic Error: Condition must be numeric\n");
            }
            analyze_semantics(root->right, table);
            break;
        }
        
        case NODE_RETURN: {
            // Procesa una sentencia de retorno
            DataType return_type = check_types(root->left, table);
            break;
        }
    }
    
    if (root->next) {
        analyze_semantics(root->next, table);
    }
}

// Funcion: init_semantic_analysis
// -------------------------------
// Inicializa el analisis semantico del AST.
// Crea una tabla de simbolos, instala funciones predefinidas y analiza el arbol.
void init_semantic_analysis(Node *ast) {
    SymbolTable *table = create_symbol_table();
    add_function(table, "sqrt", TYPE_FLOAT);
    add_function(table, "power", TYPE_FLOAT);
    analyze_semantics(ast, table);
}
