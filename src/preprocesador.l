%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFFER 1000
char buffer[MAX_BUFFER];
char lib_content[MAX_BUFFER];
int import_active = 0;

void process_import(const char* lib_name);
%}

%option noyywrap

DIGIT    [0-9]
NUMBER   {DIGIT}+("."{DIGIT}+)?
ID       [a-zA-Z][a-zA-Z0-9_]*
WS       [ \t]
NL       \r|\n|\r\n
COMMENT  #[^\r\n]*{NL}?

%%

^"#import"[ ]*"<"[^>]*">"{NL}? {
    char lib_name[100];
    sscanf(yytext, "#import <%[^>]>", lib_name);
    process_import(lib_name);
}

{COMMENT}    { 
    printf("\n");
}

{WS}        { 
    if (import_active == 0) {
        ECHO; 
    }
}

{NL}        {
    if (import_active == 0) {
        printf("\n");
    }
}

.           { 
    if (import_active == 0) {
        ECHO; 
    }
}

%%

void process_import(const char* lib_name) {
    FILE* lib_file;
    char filename[120];
    
    snprintf(filename, sizeof(filename), "%s.lib", lib_name);
    
    lib_file = fopen(filename, "r");
    if (!lib_file) {
        fprintf(stderr, "Error: Cannot open library %s\n", filename);
        return;
    }
    
    import_active = 1;
    size_t n = fread(lib_content, 1, MAX_BUFFER - 1, lib_file);
    lib_content[n] = '\0';
    
    printf("%s\n\n", lib_content);
    
    import_active = 0;
    fclose(lib_file);
}

int main(int argc, char** argv) {
    // Require either one or two arguments.
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <input_file> [output_file]\n", argv[0]);
        return 1;
    }
    
    // Open the input file.
    FILE* input = fopen(argv[1], "r");
    if (!input) {
        fprintf(stderr, "Error: Cannot open input file %s\n", argv[1]);
        return 1;
    }
    yyin = input;
    
    // If an output file is provided, redirect stdout to it.
    if (argc == 3) {
        FILE* output = freopen(argv[2], "w", stdout);
        if (!output) {
            fprintf(stderr, "Error: Cannot open output file %s\n", argv[2]);
            return 1;
        }
    }
    
    // Run the lexer.
    yylex();
    
    fclose(yyin);
    return 0;
}
