#!/usr/bin/python3
import subprocess
import sys
import os
from pathlib import Path

# Get the project root directory (where this script is located)
PROJECT_ROOT = Path(__file__).parent.parent

# Define important paths
PIPELINE_DIR = PROJECT_ROOT / "pipeline"
COMPILADOS_DIR = PROJECT_ROOT / "compilados"
SRC_DIR = PROJECT_ROOT / "src"

# Define paths to source and executable files
PREPROCESSOR_SOURCE = SRC_DIR / "preprocessor.l"
ANALYZER_SOURCE = SRC_DIR / "analizador.l"
ASSEMBLER_SOURCE = SRC_DIR / "ensamblador.l"
PARSER_SOURCE = SRC_DIR / "parser.y"
SYMBOL_TABLE_SOURCE = SRC_DIR / "symbol_table.c"

PREPROCESSOR_PATH = COMPILADOS_DIR / "preprocessor.exe"
# The lexical analyzer executable will only be compiled if no parser exists
LEXICAL_ANALYZER_PATH = COMPILADOS_DIR / "analizador.exe"
ASSEMBLER_PATH = COMPILADOS_DIR / "ensamblador.exe"
COMPILER_PATH = COMPILADOS_DIR / "compiler.exe"  # Parser (compiler) executable

# Pipeline files
SOURCE_FILE = PIPELINE_DIR / "source.txt"
PREPROCESSOR_OUTPUT = PIPELINE_DIR / "output_preprocessor.txt"
LEXICAL_OUTPUT = PIPELINE_DIR / "output_lexical_analyzer.txt"

def compile_flex_file(flex_file, output_exe):
    """
    Compile a Flex file to an executable.
    Adds the src folder to the include path so that any headers in SRC_DIR (like parser.tab.h) can be found.
    """
    try:
        print(f"Compiling {flex_file.name}...")
        
        # Generate C file using flex
        lex_yy_c = flex_file.parent / "lex.yy.c"
        subprocess.run(['flex', str(flex_file)], 
                       check=True,
                       shell=True)
        
        # Compile the generated C file with an include flag for SRC_DIR
        subprocess.run(['gcc', '-I', str(SRC_DIR), 'lex.yy.c', '-o', str(output_exe)],
                       check=True,
                       shell=True)
        
        # Clean up the intermediate file
        if lex_yy_c.exists():
            lex_yy_c.unlink()
            
        print(f"Successfully compiled {flex_file.name} to {output_exe.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {flex_file.name}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error compiling {flex_file.name}: {e}")
        sys.exit(1)

def compile_parser():
    """
    Compile the parser using Bison and GCC.
    Command sequence:
      bison -v -d parser.y -Wcounterexamples
      flex analizador.l
      gcc lex.yy.c parser.tab.c symbol_table.c -o compiler
    """
    try:
        print("Compiling parser...")
        # Use SRC_DIR as working directory for these steps
        parser_dir = SRC_DIR
        
        # Run bison to generate parser files (parser.tab.c and parser.tab.h)
        subprocess.run(['bison', '-v', '-d', str(PARSER_SOURCE), '-Wcounterexamples'], 
                       check=True, shell=True, cwd=str(parser_dir))
        
        # Run flex on the analyzer source to generate lex.yy.c
        subprocess.run(['flex', str(ANALYZER_SOURCE)], 
                       check=True, shell=True, cwd=str(parser_dir))
        
        # Compile the generated files and symbol_table.c with gcc
        subprocess.run(['gcc', 'lex.yy.c', 'parser.tab.c', 'symbol_table.c', '-o', str(COMPILER_PATH)],
                       check=True, shell=True, cwd=str(parser_dir))
        
        # Clean up the intermediate lex.yy.c file
        lex_file = parser_dir / "lex.yy.c"
        if lex_file.exists():
            lex_file.unlink()
        
        print(f"Successfully compiled parser to {COMPILER_PATH.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error compiling parser: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error compiling parser: {e}")
        sys.exit(1)

def compile_all_sources():
    """
    Compile all source files.
    If a parser exists (parser.y and symbol_table.c), compile it (which uses analizador.l internally)
    and skip compiling analizador.l separately.
    """
    print("Compiling source files...")
    
    # Ensure compilados directory exists
    COMPILADOS_DIR.mkdir(exist_ok=True)
    
    # Compile preprocessor
    if PREPROCESSOR_SOURCE.exists():
        compile_flex_file(PREPROCESSOR_SOURCE, PREPROCESSOR_PATH)
    
    # If parser exists, compile it (which will process analizador.l); otherwise, compile analizador.l separately.
    if PARSER_SOURCE.exists() and SYMBOL_TABLE_SOURCE.exists():
        compile_parser()
    elif ANALYZER_SOURCE.exists():
        compile_flex_file(ANALYZER_SOURCE, LEXICAL_ANALYZER_PATH)
    
    # Compile assembler
    if ASSEMBLER_SOURCE.exists():
        compile_flex_file(ASSEMBLER_SOURCE, ASSEMBLER_PATH)

def ensure_pipeline_directory():
    """
    Create pipeline directory and required files if they don't exist.
    """
    PIPELINE_DIR.mkdir(exist_ok=True)
    if not SOURCE_FILE.exists():
        SOURCE_FILE.write_text("# Write your high level language code here\n")
        print(f"Created empty source file at {SOURCE_FILE}")

def run_preprocessor():
    """
    Run the preprocessor on the source file.
    """
    try:
        print(f"Running preprocessor on {SOURCE_FILE}")
        result = subprocess.run([str(PREPROCESSOR_PATH), str(SOURCE_FILE)], 
                                capture_output=True, 
                                text=True,
                                check=True,
                                shell=True)
        
        # Write the preprocessor output to file
        PREPROCESSOR_OUTPUT.write_text(result.stdout)
        print(f"Preprocessor output saved to {PREPROCESSOR_OUTPUT}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running preprocessor: {e}")
        print(f"Preprocessor stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error running preprocessor: {e}")
        sys.exit(1)

def run_lexical_analyzer():
    """
    Run the lexical analyzer on the preprocessed file.
    This step is executed only if the separate lexical analyzer executable exists.
    """
    if not LEXICAL_ANALYZER_PATH.exists():
        print("Lexical analyzer executable not found; skipping lexical analyzer step.")
        return

    try:
        print(f"Running lexical analyzer on {PREPROCESSOR_OUTPUT}")
        # Redirect output to file using shell redirection
        with open(LEXICAL_OUTPUT, 'w') as f:
            subprocess.run([str(LEXICAL_ANALYZER_PATH), str(PREPROCESSOR_OUTPUT)],
                           stdout=f,
                           text=True,
                           check=True,
                           shell=True)
        
        print(f"Lexical analyzer output saved to {LEXICAL_OUTPUT}")
        
        # Print the content of the output file
        print("\nLexical Analyzer Output:")
        print(LEXICAL_OUTPUT.read_text())
        
    except subprocess.CalledProcessError as e:
        print(f"Error running lexical analyzer: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error running lexical analyzer: {e}")
        sys.exit(1)

def run_parser():
    """
    Run the parser (compiler) on the file generated by the preprocessor.
    Final test now uses the preprocessor output file (output_preprocessor.txt).
    Command: .\compiler.exe <pipeline/output_preprocessor.txt>
    """
    try:
        print(f"Running parser on preprocessor output {PREPROCESSOR_OUTPUT}")
        result = subprocess.run([str(COMPILER_PATH), str(PREPROCESSOR_OUTPUT)], 
                                  capture_output=True, 
                                  text=True,
                                  check=True,
                                  shell=True)
        print("Parser output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running parser: {e}")
        print(f"Parser stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error running parser: {e}")
        sys.exit(1)

def check_requirements():
    """
    Check if required programs (flex, gcc, bison) are installed.
    """
    try:
        subprocess.run(['flex', '--version'], capture_output=True, shell=True)
        subprocess.run(['gcc', '--version'], capture_output=True, shell=True)
        subprocess.run(['bison', '--version'], capture_output=True, shell=True)
    except subprocess.CalledProcessError:
        print("Error: flex, gcc, or bison not found. Please ensure all are installed and in your PATH.")
        sys.exit(1)

def main():
    print("Starting compilation pipeline...")
    
    # Check if required programs are installed
    check_requirements()
    
    # Compile all source files
    compile_all_sources()
    
    # Ensure pipeline directory and files exist
    ensure_pipeline_directory()
    
    if not SOURCE_FILE.exists():
        print(f"Error: Source file not found at {SOURCE_FILE}")
        print("Please create the file and add your code before running the pipeline.")
        sys.exit(1)
    
    # Run the pipeline steps
    print(f"\nStep 1: Running preprocessor...")
    run_preprocessor()
    
    # Only run the lexical analyzer if its executable exists
    print(f"\nStep 2: Running lexical analyzer...")
    run_lexical_analyzer()
    
    print(f"\nStep 3: Running parser on preprocessor output...")
    run_parser()
    
    print("\nPipeline execution complete!")
    print(f"\nFiles generated:")
    print(f"1. Preprocessor output: {PREPROCESSOR_OUTPUT}")
    print(f"2. Lexical analyzer output: {LEXICAL_OUTPUT}")
    print(f"3. Parser executable: {COMPILER_PATH}")

if __name__ == "__main__":
    main()
