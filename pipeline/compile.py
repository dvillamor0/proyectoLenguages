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

PREPROCESSOR_PATH = COMPILADOS_DIR / "preprocessor.exe"
LEXICAL_ANALYZER_PATH = COMPILADOS_DIR / "analizador.exe"
ASSEMBLER_PATH = COMPILADOS_DIR / "ensamblador.exe"

# Pipeline files
SOURCE_FILE = PIPELINE_DIR / "source.txt"
PREPROCESSOR_OUTPUT = PIPELINE_DIR / "output_preprocessor.txt"
LEXICAL_OUTPUT = PIPELINE_DIR / "output_lexical_analyzer.txt"

def compile_flex_file(flex_file, output_exe):
    """
    Compile a Flex file to an executable
    """
    try:
        print(f"Compiling {flex_file.name}...")
        
        # Generate C file using flex
        lex_yy_c = flex_file.parent / "lex.yy.c"
        subprocess.run(['flex', str(flex_file)], 
                      check=True,
                      shell=True)
        
        # Compile C file using gcc
        subprocess.run(['gcc', 'lex.yy.c', '-o', str(output_exe)],
                      check=True,
                      shell=True)
        
        # Clean up intermediate file
        if lex_yy_c.exists():
            lex_yy_c.unlink()
            
        print(f"Successfully compiled {flex_file.name} to {output_exe.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {flex_file.name}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error compiling {flex_file.name}: {e}")
        sys.exit(1)

def compile_all_sources():
    """
    Compile all Flex source files
    """
    print("Compiling source files...")
    
    # Ensure compilados directory exists
    COMPILADOS_DIR.mkdir(exist_ok=True)
    
    # Compile preprocessor
    if PREPROCESSOR_SOURCE.exists():
        compile_flex_file(PREPROCESSOR_SOURCE, PREPROCESSOR_PATH)
    
    # Compile lexical analyzer
    if ANALYZER_SOURCE.exists():
        compile_flex_file(ANALYZER_SOURCE, LEXICAL_ANALYZER_PATH)
    
    # Compile assembler
    if ASSEMBLER_SOURCE.exists():
        compile_flex_file(ASSEMBLER_SOURCE, ASSEMBLER_PATH)

def ensure_pipeline_directory():
    """
    Create pipeline directory and required files if they don't exist
    """
    PIPELINE_DIR.mkdir(exist_ok=True)
    if not SOURCE_FILE.exists():
        SOURCE_FILE.write_text("# Write your high level language code here\n")
        print(f"Created empty source file at {SOURCE_FILE}")

def run_preprocessor():
    """
    Run the preprocessor on the source file
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
    Run the lexical analyzer on the preprocessed file
    """
    try:
        print(f"Running lexical analyzer on {PREPROCESSOR_OUTPUT}")
        # Redirect output to file using shell redirection
        with open(LEXICAL_OUTPUT, 'w') as f:
            result = subprocess.run([str(LEXICAL_ANALYZER_PATH), str(PREPROCESSOR_OUTPUT)],
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

def check_requirements():
    """
    Check if required programs (flex, gcc) are installed
    """
    try:
        subprocess.run(['flex', '--version'], 
                      capture_output=True,
                      shell=True)
        subprocess.run(['gcc', '--version'],
                      capture_output=True,
                      shell=True)
    except subprocess.CalledProcessError:
        print("Error: flex or gcc not found. Please ensure both are installed and in your PATH.")
        sys.exit(1)

def main():
    print("Starting compilation pipeline...")
    
    # Check if flex and gcc are installed
    check_requirements()
    
    # Compile all source files first
    compile_all_sources()
    
    # Ensure pipeline directory and files exist
    ensure_pipeline_directory()
    
    if not SOURCE_FILE.exists():
        print(f"Error: Source file not found at {SOURCE_FILE}")
        print("Please create the file and add your code before running the pipeline.")
        sys.exit(1)
    
    # Run the pipeline
    print(f"\nStep 1: Running preprocessor...")
    run_preprocessor()
    
    print(f"\nStep 2: Running lexical analyzer...")
    run_lexical_analyzer()
    
    print("\nPipeline execution complete!")
    print(f"\nFiles generated:")
    print(f"1. Preprocessor output: {PREPROCESSOR_OUTPUT}")
    print(f"2. Lexical analyzer output: {LEXICAL_OUTPUT}")

if __name__ == "__main__":
    main()