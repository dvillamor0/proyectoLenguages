#include "symbol_table.h"

SymbolTable* create_symbol_table() {
    SymbolTable *table = (SymbolTable*)malloc(sizeof(SymbolTable));
    table->head = NULL;
    table->current_scope = 0;
    return table;
}

void enter_scope(SymbolTable *table) {
    table->current_scope++;
}

void exit_scope(SymbolTable *table) {
    // Eliminar símbolos del ámbito actual
    Symbol *current = table->head;
    Symbol *prev = NULL;

    while (current != NULL) {
        if (current->scope == table->current_scope) {
            Symbol *to_delete = current;
            if (prev == NULL) {
                table->head = current->next;
                current = table->head;
            } else {
                prev->next = current->next;
                current = current->next;
            }
            free(to_delete->name);
            free(to_delete);
        } else {
            prev = current;
            current = current->next;
        }
    }
    table->current_scope--;
}

Symbol* insert_symbol(SymbolTable *table, const char *name, SymbolType type) {
    Symbol *existing = lookup_symbol_in_scope(table, name, table->current_scope);
    if (existing != NULL) {
        printf("Error: Variable '%s' ya declarada en este ambito\n", name);
        return NULL;
    }

    Symbol *symbol = (Symbol*)malloc(sizeof(Symbol));
    symbol->name = strdup(name);
    symbol->type = type;
    symbol->scope = table->current_scope;
    symbol->next = table->head;
    table->head = symbol;
    
    return symbol;
}

Symbol* lookup_symbol(SymbolTable *table, const char *name) {
    // Buscar desde el ámbito actual hacia abajo
    for (int scope = table->current_scope; scope >= 0; scope--) {
        Symbol *symbol = lookup_symbol_in_scope(table, name, scope);
        if (symbol != NULL) {
            return symbol;
        }
    }
    return NULL;
}

Symbol* lookup_symbol_in_scope(SymbolTable *table, const char *name, int scope) {
    Symbol *current = table->head;
    while (current != NULL) {
        if (current->scope == scope && strcmp(current->name, name) == 0) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

void delete_symbol_table(SymbolTable *table) {
    Symbol *current = table->head;
    while (current != NULL) {
        Symbol *next = current->next;
        free(current->name);
        free(current);
        current = next;
    }
    free(table);
}

// Helper function to add debugging for type names
const char* get_type_name(SymbolType type) {
    switch (type) {
        case TYPE_INT: return "entero";
        case TYPE_STRING: return "cadena";
        case TYPE_LIST: return "lista";
        default: return "desconocido";
    }
}

void print_symbol_table(SymbolTable *table) {
    printf("\n=== Tabla de Simbolos ===\n");
    printf("Ambito actual: %d\n", table->current_scope);
    printf("Nombre\tTipo\tAmbito\n");
    printf("------------------------\n");
    
    Symbol *current = table->head;
    while (current != NULL) {
        printf("%s\t%s\t%d\n", 
               current->name, 
               get_type_name(current->type), 
               current->scope);
        current = current->next;
    }
    printf("========================\n\n");
}