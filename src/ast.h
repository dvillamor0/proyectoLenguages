#ifndef AST_H
#define AST_H

typedef enum {
    NODE_PROGRAM,
    NODE_FUNCTION,
    NODE_BLOCK,
    NODE_DECLARATION,
    NODE_ASSIGNMENT,
    NODE_IF,
    NODE_WHILE,
    NODE_RETURN,
    NODE_BINARY_OP,
    NODE_FUNCTION_CALL,
    NODE_IDENTIFIER,
    NODE_NUMBER,
    NODE_ADD,
    NODE_SUB,
    NODE_MUL,
    NODE_DIV,
    NODE_ARRAY_TYPE,
    NODE_ARRAY_DECL,
    NODE_ARRAY_ACCESS,
    NODE_ARRAY_ASSIGNMENT,
    NODE_ARRAY_LITERAL,
    NODE_ARRAY_INIT,
    NODE_ARRAY_SIZE,
    
    // Bigraph node types
    NODE_BIGRAPH_DECL,         // Bigraph declaration
    NODE_BIGRAPH_ADD_NODE,     // Add node to bigraph
    NODE_BIGRAPH_REPLACE_NODE, // Replace node in bigraph
    NODE_BIGRAPH_REMOVE_NODE,  // Remove node from bigraph
    NODE_BIGRAPH_ADD_EDGE,     // Add edge between nodes
    NODE_BIGRAPH_REMOVE_EDGE,  // Remove edge between nodes
    NODE_BIGRAPH_ADD_TYPE,     // Add type relation
    NODE_BIGRAPH_REMOVE_TYPE,  // Remove type relation
    NODE_BIGRAPH_ADD_PARENT,   // Add parent-child relation
    NODE_BIGRAPH_SET_LINK,     // Set link count for a node
    NODE_BIGRAPH_REMOVE_LINK,  // Remove link count for a node
    NODE_BIGRAPH_COMPOSE,      // Compose two bigraphs
    NODE_STRING_LITERAL       // String literal for node names
} NodeType;


typedef struct Node {
    NodeType type;
    int symbol_index;  
    struct Node *left;
    struct Node *right;
    struct Node *next;  
} Node;

Node* create_node(NodeType type, Node* left, Node* right);

#endif /* AST_H */