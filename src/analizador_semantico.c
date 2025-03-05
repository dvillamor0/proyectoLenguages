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
        unsigned int natural_value;
    } value;
} symbol_table[];

// Enumeracion de tipos de datos
typedef enum {
    TYPE_UNKNOWN,
    TYPE_INTEGER,
    TYPE_FLOAT,
    TYPE_NATURAL,
    TYPE_VOID,
    TYPE_ARRAY_INTEGER,  
    TYPE_ARRAY_FLOAT,    
    TYPE_ARRAY_NATURAL,
    TYPE_BIGRAPH,        // Tipo para bigrafos
    TYPE_STRING          // Tipo para strings
} DataType;

// Estructura que contiene la informacion de un simbolo
typedef struct {
    char *name;
    DataType type;
    int is_function;
    DataType return_type;
    DataType *param_types;
    int param_count;
    int array_size;     
    DataType element_type; 
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
    table->entries[table->size].array_size = 0;  
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

static void add_array_symbol(SymbolTable *table, const char *name, DataType elemType, int size) {
    if (table->size >= table->capacity) {
        table->capacity *= 2;
        table->entries = realloc(table->entries, sizeof(SymbolInfo) * table->capacity);
    }
    
    // Determine array type based on element type
    DataType arrayType;
    switch (elemType) {
        case TYPE_INTEGER:
            arrayType = TYPE_ARRAY_INTEGER;
            break;
        case TYPE_FLOAT:
            arrayType = TYPE_ARRAY_FLOAT;
            break;
        case TYPE_NATURAL:
            arrayType = TYPE_ARRAY_NATURAL;
            break;
        default:
            fprintf(stderr, "Semantic Error: Cannot create array of type %d\n", elemType);
            arrayType = TYPE_UNKNOWN;
    }
    
    table->entries[table->size].name = strdup(name);
    table->entries[table->size].type = arrayType;
    table->entries[table->size].element_type = elemType;
    table->entries[table->size].is_function = 0;
    table->entries[table->size].array_size = size;
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
        case TOKEN_NAT:
            return TYPE_NATURAL;
        default:
            return TYPE_UNKNOWN;
    }
}

static DataType get_element_type(DataType arrayType) {
    switch (arrayType) {
        case TYPE_ARRAY_INTEGER:
            return TYPE_INTEGER;
        case TYPE_ARRAY_FLOAT:
            return TYPE_FLOAT;
        case TYPE_ARRAY_NATURAL:
            return TYPE_NATURAL;
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
            if (symbol_table[node->symbol_index].type == 3) {  
                return TYPE_NATURAL;
            }
            
            // Otherwise, check for float or integer as before
            const char *num_str = symbol_table[node->symbol_index].name;
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

        case NODE_ARRAY_ACCESS: {
            // Check that the identifier is an array
            const char *id_name = symbol_table[node->left->symbol_index].name;
            SymbolInfo *info = lookup_symbol(table, id_name);
            if (!info) {
                fprintf(stderr, "Semantic Error: Undefined identifier '%s'\n", id_name);
                return TYPE_UNKNOWN;
            }
            
            // Verify it's an array type
            if (info->type != TYPE_ARRAY_INTEGER && 
                info->type != TYPE_ARRAY_FLOAT && 
                info->type != TYPE_ARRAY_NATURAL) {
                fprintf(stderr, "Semantic Error: '%s' is not an array\n", id_name);
                return TYPE_UNKNOWN;
            }
            
            // Check that the index is an integer or natural
            DataType index_type = check_types(node->right, table);
            if (index_type != TYPE_INTEGER && index_type != TYPE_NATURAL) {
                fprintf(stderr, "Semantic Error: Array index must be integer or natural, got %d\n", index_type);
            }
            
            // Return the element type of the array
            return info->element_type;
        }
        
        case NODE_ARRAY_LITERAL: {
            // Check that all elements have the same type
            DataType element_type = TYPE_UNKNOWN;
            Node *element = node->left;
            
            if (element) {
                element_type = check_types(element, table);
                element = element->next;
                
                while (element) {
                    DataType current_type = check_types(element, table);
                    if (current_type != element_type) {
                        fprintf(stderr, "Semantic Error: Array elements must have the same type\n");
                        break;
                    }
                    element = element->next;
                }
            }
            
            // Return the appropriate array type based on element type
            switch (element_type) {
                case TYPE_INTEGER:
                    return TYPE_ARRAY_INTEGER;
                case TYPE_FLOAT:
                    return TYPE_ARRAY_FLOAT;
                case TYPE_NATURAL:
                    return TYPE_ARRAY_NATURAL;
                default:
                    return TYPE_UNKNOWN;
            }
        }
        
        case NODE_ARRAY_ASSIGNMENT: {
            // Check the array access
            DataType element_type = check_types(node->left, table);
            
            // Check the value being assigned
            DataType value_type = check_types(node->right, table);
            
            // Check type compatibility
            if (element_type != value_type) {
                fprintf(stderr, "Semantic Error: Type mismatch in array assignment\n");
            }
            
            return element_type;
        }
        
        default:
            return TYPE_UNKNOWN;
    }
}

// Añadimos funciones de verificación para operaciones de bigrafo
static void check_bigraph_operation(Node *node, SymbolTable *table) {
    if (!node) return;
    
    char *bigraph_id = symbol_table[node->symbol_index].name;
    SymbolInfo *info = lookup_symbol(table, bigraph_id);
    
    if (!info) {
        printf("Error semántico: El bigrafo '%s' no ha sido declarado.\n", bigraph_id);
        return;
    }
    
    if (info->type != TYPE_BIGRAPH) {
        printf("Error semántico: '%s' no es un bigrafo.\n", bigraph_id);
        return;
    }
    
    // Verificaciones específicas según la operación
    switch (node->type) {
        case NODE_BIGRAPH_ADD_NODE:
        case NODE_BIGRAPH_REMOVE_NODE:
            // Comprobar que el argumento es una cadena
            if (node->left && node->left->type == NODE_STRING_LITERAL) {
                // El argumento es una cadena, correcto
            } else {
                printf("Error semántico: Se esperaba una cadena como nombre de nodo en operación sobre bigrafo '%s'.\n", bigraph_id);
            }
            break;
            
        case NODE_BIGRAPH_REPLACE_NODE:
            // Comprobar que ambos argumentos son cadenas
            if (node->left && node->left->type == NODE_STRING_LITERAL &&
                node->right && node->right->type == NODE_STRING_LITERAL) {
                // Ambos argumentos son cadenas, correcto
            } else {
                printf("Error semántico: Se esperaban dos cadenas como nombres de nodos en operación de reemplazo sobre bigrafo '%s'.\n", bigraph_id);
            }
            break;
            
        case NODE_BIGRAPH_ADD_EDGE:
        case NODE_BIGRAPH_REMOVE_EDGE:
        case NODE_BIGRAPH_ADD_PARENT:
            // Comprobar expresiones para los nodos
            if (node->left) check_types(node->left, table);
            if (node->right) check_types(node->right, table);
            break;
            
        case NODE_BIGRAPH_ADD_TYPE:
        case NODE_BIGRAPH_REMOVE_TYPE:
            // Comprobar que el primer argumento es una cadena
            if (node->left && node->left->type == NODE_STRING_LITERAL) {
                // El primer argumento es una cadena, correcto
                if (node->right) check_types(node->right, table);
            } else {
                printf("Error semántico: Se esperaba una cadena como tipo en operación sobre bigrafo '%s'.\n", bigraph_id);
            }
            break;
            
        case NODE_BIGRAPH_SET_LINK:
            // Comprobar que primer argumento es un nodo y el segundo es un número (natural)
            if (node->left) check_types(node->left, table);
            if (node->right) {
                DataType right_type = check_types(node->right, table);
                if (right_type != TYPE_INTEGER && right_type != TYPE_NATURAL) {
                    printf("Error semántico: Se esperaba un número natural para el límite de enlace en bigrafo '%s'.\n", bigraph_id);
                }
            }
            break;
            
        case NODE_BIGRAPH_REMOVE_LINK:
            // Comprobar que el argumento es un nodo
            if (node->left) check_types(node->left, table);
            break;
            
        case NODE_BIGRAPH_COMPOSE:
            // Comprobar que los argumentos son bigrafos
            if (node->left && node->left->type == NODE_IDENTIFIER) {
                char *left_id = symbol_table[node->left->symbol_index].name;
                SymbolInfo *left_info = lookup_symbol(table, left_id);
                if (!left_info || left_info->type != TYPE_BIGRAPH) {
                    printf("Error semántico: '%s' no es un bigrafo válido para composición.\n", left_id);
                }
            }
            
            if (node->right && node->right->type == NODE_IDENTIFIER) {
                char *right_id = symbol_table[node->right->symbol_index].name;
                SymbolInfo *right_info = lookup_symbol(table, right_id);
                if (!right_info || right_info->type != TYPE_BIGRAPH) {
                    printf("Error semántico: '%s' no es un bigrafo válido para composición.\n", right_id);
                }
            }
            break;
            
        default:
            break;
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
        
        case NODE_ARRAY_DECL: {
            const char *array_name = symbol_table[root->left->symbol_index].name;
            
            // Check if this is a declaration with initialization
            if (root->right && root->right->type == NODE_ARRAY_INIT) {
                // Get the type and size
                Node *size_and_type = root->right->left;
                Node *init_value = root->right->right;
                
                // Check the size expression
                DataType size_type = check_types(size_and_type->left, table);
                if (size_type != TYPE_INTEGER && size_type != TYPE_NATURAL) {
                    fprintf(stderr, "Semantic Error: Array size must be an integer or natural\n");
                }
                
                // Get the element type from the NODE_ARRAY_TYPE node
                DataType elem_type = get_type_from_token(size_and_type->right->symbol_index);
                
                // Check the initializer
                DataType init_type = check_types(init_value, table);
                
                // Determine expected array type based on element type
                DataType expected_array_type;
                switch (elem_type) {
                    case TYPE_INTEGER:
                        expected_array_type = TYPE_ARRAY_INTEGER;
                        break;
                    case TYPE_FLOAT:
                        expected_array_type = TYPE_ARRAY_FLOAT;
                        break;
                    case TYPE_NATURAL:
                        expected_array_type = TYPE_ARRAY_NATURAL;
                        break;
                    default:
                        expected_array_type = TYPE_UNKNOWN;
                }
                
                // Check if initializer type matches expected array type
                if (init_type != expected_array_type) {
                    fprintf(stderr, "Semantic Error: Array initializer type mismatch\n");
                }
                
                // Add the array to the symbol table
                // For simplicity, we're not calculating exact size at compile time
                add_array_symbol(table, array_name, elem_type, 0);
            } else {
                // Simple array declaration without initialization
                DataType elem_type = get_type_from_token(root->right->symbol_index);
                
                // Check the size expression
                DataType size_type = check_types(root->right, table);
                if (size_type != TYPE_INTEGER && size_type != TYPE_NATURAL) {
                    fprintf(stderr, "Semantic Error: Array size must be an integer or natural\n");
                }
                
                // Add the array to the symbol table
                add_array_symbol(table, array_name, elem_type, 0);
            }
            break;
        }
        
        case NODE_ARRAY_ASSIGNMENT: {
            // The array access semantics are checked in check_types
            check_types(root, table);
            break;
        }
        
        case NODE_IF:
        case NODE_WHILE: {
            DataType cond_type = check_types(root->left, table);
            if (cond_type != TYPE_INTEGER && cond_type != TYPE_FLOAT) {
                fprintf(stderr, "Semantic Error: Condition must be numeric\n");
            }
            analyze_semantics(root->right, table);
            break;
        }
        
        case NODE_RETURN: {
            DataType return_type = check_types(root->left, table);
            break;
        }
        
        case NODE_BIGRAPH_DECL: {
            // Declaración de bigrafo
            char *name = symbol_table[root->symbol_index].name;
            SymbolInfo *info = lookup_symbol(table, name);
            
            if (info) {
                printf("Error semántico: El bigrafo '%s' ya ha sido declarado.\n", name);
            } else {
                add_symbol(table, name, TYPE_BIGRAPH);
                
                // Si hay nodos iniciales (bigrafo con array de nodos)
                if (root->left) {
                    Node *current = root->left;
                    while (current) {
                        if (current->type != NODE_STRING_LITERAL) {
                            printf("Error semántico: Los nodos iniciales de un bigrafo deben ser cadenas de texto.\n");
                        }
                        current = current->next;
                    }
                }
            }
            break;
        }
        
        case NODE_BIGRAPH_ADD_NODE:
        case NODE_BIGRAPH_REPLACE_NODE:
        case NODE_BIGRAPH_REMOVE_NODE:
        case NODE_BIGRAPH_ADD_EDGE:
        case NODE_BIGRAPH_REMOVE_EDGE:
        case NODE_BIGRAPH_ADD_TYPE:
        case NODE_BIGRAPH_REMOVE_TYPE:
        case NODE_BIGRAPH_ADD_PARENT:
        case NODE_BIGRAPH_SET_LINK:
        case NODE_BIGRAPH_REMOVE_LINK:
        case NODE_BIGRAPH_COMPOSE:
            check_bigraph_operation(root, table);
            break;
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
