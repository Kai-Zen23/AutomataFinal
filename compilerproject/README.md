# Automata Simulator & Compiler Front-End

A comprehensive tool for simulating Automata (NFA, DFA, PDA) and visualizing Compiler Front-End phases (Lexical Analysis, Syntax Analysis).

## 1. Prerequisites

Before running the project, ensure you have the following installed:

*   **Python 3.x**: Required for the GUI (`tkinter`).
*   **G++ Compiler**: Required to compile the C++ backend engines.
    *   **Windows**: Install MinGW.
    *   **Linux/Mac**: Install via your package manager (e.g., `sudo apt install g++`).

## 2. Compilation Instructions

You need to compile the C++ backend executables before running the GUI. Open your terminal in the project root (`compilerproject/`) and run:

### A. Compile the PDA Lab Simulator
This engine powers the "General PDA Lab" tab.
```bash
g++ -o bin/pda_lab.exe tools/pda_lab.cpp src/lexer_regex.cpp src/parser_regex.cpp src/nfa.cpp src/dfa.cpp -I include -std=c++17
```

### B. Compile the Regex Engine (Validator)
This engine powers the "Regex Tester" and real-time validation.
```bash
g++ -o bin/regex_engine.exe src/main.cpp src/regex_validator.cpp src/lexer_regex.cpp src/parser_regex.cpp src/nfa.cpp src/dfa.cpp src/minimize.cpp src/pda_wrapper.cpp -I include -std=c++17
```

### C. Compile the Main Compiler Engine (Legacy)
This engine powers the main "Compiler Front-End" tab.
```bash
g++ -o bin/compiler_engine.exe compiler_engine.cpp -std=c++17
```

## 3. Running the Application

Once compiled, start the Graphical User Interface (GUI) using Python:

```bash
python tkinter_gui.py
```

## 4. Usage Guide

### Tab 1: Compiler Front-End
*   **Purpose**: Visualize the full pipeline (Lexer -> PDA).
*   **Usage**: Enter code and click "Run Analysis".

### Tab 2: Regex Tester
*   **Purpose**: Test and Validate Regex patterns.
*   **Usage**:
    *   Enter a Regex (e.g., `(a|b)*abb`).
    *   Add Test Strings.
    *   Click "Run Regex Tests" to see Pass/Fail results.

### Tab 3: General PDA Lab (New!)
This is the advanced simulation features.

#### A. Regex Mode (NFA Simulation)
*   **How**: Enter a Regex in the "Regex" field (e.g., `(a|b)*abb`).
*   **Description**: Simulates the Regex using a Finite Automaton.
*   **Visualization**:
    *   **State Box**: Shows the current active state (e.g., `State: 0`).
    *   **Input Tape**: Shows the string being read with the current character highlighted.
    *   **Stack**: **Hidden** (Finite Automata do not use a stack).

#### B. Default Mode (Standard PDA)
*   **How**: **Clear the Regex field** (leave it empty). Enter a string (e.g., `aabb`).
*   **Description**: Runs the built-in PDA for the language $a^n b^n$.
*   **Visualization**:
    *   **Stack**: **Visible** and active (shows Push/Pop operations).
    *   **State**: Shows simulation progress.

## Troubleshooting
*   **White Screen / Crash**: Ensure all `.exe` files exist in the `bin/` folder.
*   **Validation Errors**: Ensure you compiled `regex_engine.exe` correctly.
