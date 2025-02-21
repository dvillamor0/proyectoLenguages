%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
%}

%option noyywrap
%option yylineno

%%

POWER\([ \t]*[0-9]+[ \t]*,[ \t]*[0-9]+[ \t]*\) {
    int base, exponent;
    if (sscanf(yytext, "POWER( %d , %d )", &base, &exponent) != 2) {
        fprintf(stderr, "Error parsing POWER macro: %s\n", yytext);
    }
    printf("int result = %d;\n", base);
    printf("int i = 1;\n");
    printf("while (i < %d) {\n", exponent);
    printf("    result = result * %d;\n", base);
    printf("    i = i + 1;\n");
    printf("}\n");
}

SQUAREROOT\([ \t]*[0-9]+[ \t]*\) {
    int number;
    if (sscanf(yytext, "SQUAREROOT( %d )", &number) != 1) {
        fprintf(stderr, "Error parsing SQUAREROOT macro: %s\n", yytext);
    }
    printf("int x = %d;\n", number);
    printf("int guess = x / 2;\n");
    printf("int lastGuess = 0;\n");
    printf("while (guess != lastGuess) {\n");
    printf("    lastGuess = guess;\n");
    printf("    guess = (guess + x / guess) / 2;\n");
    printf("}\n");
}

"#".*    { /* Discard single-line comments */ }

\"\"\"(.|\n)*?\"\"\" {
    for(int i = 0; i < yyleng; i++) {
        if(yytext[i] == '\n')
            putchar('\n');
    }
}

"'''"(.|\n)*?"'''" {
    for(int i = 0; i < yyleng; i++) {
        if(yytext[i] == '\n')
            putchar('\n');
    }
}

\n      { putchar('\n'); }  
.       { putchar(yytext[0]); }  

%%

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error opening file");
        return 1;
    }

    yyin = file;
    yylex();
    fclose(file);
    return 0;
}