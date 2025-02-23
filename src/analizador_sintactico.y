%{
#include <stdio.h>
#include <stdlib.h>
#include "ast.h"
#include "analizador_semantico.h"
#include "intermediate_code.h" 

extern int yylex();
extern FILE* yyin;
extern int yylineno;
void yyerror(const char *s);

Node* ast_root = NULL;
%}

%define parse.error verbose

%union {
    int symbol_index;
    struct Node *node;
}

%token <symbol_index> TOKEN_ID TOKEN_NUMBER
%token TOKEN_FUN TOKEN_RET TOKEN_IF TOKEN_WHILE TOKEN_ENT TOKEN_FLO
%token TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE
%token TOKEN_PLUS TOKEN_MINUS TOKEN_MULT TOKEN_DIV TOKEN_ASSIGN
%token TOKEN_SEMICOLON TOKEN_COMMA TOKEN_LPAREN TOKEN_RPAREN TOKEN_LBRACE TOKEN_RBRACE
%type <symbol_index> relop

%type <node> program function_list function param_list param
%type <node> block statement_list statement declaration_stmt assignment_stmt
%type <node> if_stmt while_stmt return_stmt condition expr arg_list

%left TOKEN_PLUS TOKEN_MINUS
%left TOKEN_MULT TOKEN_DIV
%nonassoc TOKEN_RELOP_LT TOKEN_RELOP_LE TOKEN_RELOP_EQ TOKEN_RELOP_NE TOKEN_RELOP_GT TOKEN_RELOP_GE

%%

program 
    : function_list    { 
        $$ = create_node(NODE_PROGRAM, $1, NULL);
        ast_root = $$;
    }
    ;

function_list
    : function                        { $$ = $1; }
    | function_list function          { 
                                        $$ = $1;
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $2;
                                     }
    ;

function
    : TOKEN_FUN TOKEN_ID TOKEN_LPAREN param_list TOKEN_RPAREN block
                                     { 
                                        Node *func = create_node(NODE_FUNCTION, $4, $6);
                                        func->symbol_index = $2;
                                        $$ = func;
                                     }
    ;

param_list
    : /* empty */                     { $$ = NULL; }
    | param                           { $$ = $1; }
    | param_list TOKEN_COMMA param    {
                                        $$ = $1;
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $3;
                                     }
    ;

param
    : type TOKEN_ID                   {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $2;
                                        $$ = id;
                                     }
    ;

type
    : TOKEN_ENT
    | TOKEN_FLO
    ;

block
    : TOKEN_LBRACE statement_list TOKEN_RBRACE
                                     { $$ = create_node(NODE_BLOCK, $2, NULL); }
    ;

statement_list
    : /* empty */                     { $$ = NULL; }
    | statement_list statement        {
                                        if ($1 == NULL) {
                                            $$ = $2;
                                        } else {
                                            $$ = $1;
                                            Node *last = $1;
                                            while(last->next) last = last->next;
                                            last->next = $2;
                                        }
                                     }
    ;

statement
    : declaration_stmt
    | assignment_stmt
    | if_stmt
    | while_stmt
    | return_stmt
    ;

declaration_stmt
    : type TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON
                                     {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $2;
                                        $$ = create_node(NODE_DECLARATION, id, $4);
                                     }
    ;

assignment_stmt
    : TOKEN_ID TOKEN_ASSIGN expr TOKEN_SEMICOLON
                                     {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $1;
                                        $$ = create_node(NODE_ASSIGNMENT, id, $3);
                                     }
    ;

if_stmt
    : TOKEN_IF TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_IF, $3, $5); }
    ;

while_stmt
    : TOKEN_WHILE TOKEN_LPAREN condition TOKEN_RPAREN block
                                     { $$ = create_node(NODE_WHILE, $3, $5); }
    ;

return_stmt
    : TOKEN_RET expr TOKEN_SEMICOLON  { $$ = create_node(NODE_RETURN, $2, NULL); }
    ;

condition
    : expr relop expr                { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = $2;
                                     }
    ;

relop
    : TOKEN_RELOP_LT                 { $$ = TOKEN_RELOP_LT; }
    | TOKEN_RELOP_LE                 { $$ = TOKEN_RELOP_LE; }
    | TOKEN_RELOP_EQ                 { $$ = TOKEN_RELOP_EQ; }
    | TOKEN_RELOP_NE                 { $$ = TOKEN_RELOP_NE; }
    | TOKEN_RELOP_GT                 { $$ = TOKEN_RELOP_GT; }
    | TOKEN_RELOP_GE                 { $$ = TOKEN_RELOP_GE; }
    ;

expr
    : TOKEN_ID                        {
                                        $$ = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        $$->symbol_index = $1;
                                     }
    | TOKEN_NUMBER                    {
                                        $$ = create_node(NODE_NUMBER, NULL, NULL);
                                        $$->symbol_index = $1;
                                     }
    | TOKEN_ID TOKEN_LPAREN arg_list TOKEN_RPAREN
                                     {
                                        Node *id = create_node(NODE_IDENTIFIER, NULL, NULL);
                                        id->symbol_index = $1;
                                        $$ = create_node(NODE_FUNCTION_CALL, id, $3);
                                     }
    | expr TOKEN_PLUS expr           { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3); 
                                        $$->symbol_index = TOKEN_PLUS;
                                     }
    | expr TOKEN_MINUS expr          { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = TOKEN_MINUS;
                                     }
    | expr TOKEN_MULT expr           { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = TOKEN_MULT;
                                     }
    | expr TOKEN_DIV expr            { 
                                        $$ = create_node(NODE_BINARY_OP, $1, $3);
                                        $$->symbol_index = TOKEN_DIV;
                                     }
    | TOKEN_LPAREN expr TOKEN_RPAREN { $$ = $2; }
    ;

arg_list
    : /* empty */                     { $$ = NULL; }
    | expr                            { $$ = $1; }
    | arg_list TOKEN_COMMA expr       {
                                        $$ = $1;
                                        Node *last = $1;
                                        while(last->next) last = last->next;
                                        last->next = $3;
                                     }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Error: %s at line %d\n", s, yylineno);
}

int main(int argc, char **argv) {
    if (argc > 1) {
        if (!(yyin = fopen(argv[1], "r"))) {
            perror(argv[1]);
            return 1;
        }
    }
    
    if (yyparse() == 0) {
        if (ast_root) {
            init_semantic_analysis(ast_root);
            generate_intermediate_code(ast_root, "output.tac");
        }
    }
    
    return 0;
}