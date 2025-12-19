import re
import subprocess
import os
import tkinter as tk
from tkinter import ttk, scrolledtext




# ==============================================================================================
# COMPILER SIMULATOR GUI (Python Frontend)
# ==============================================================================================
# This application serves as the visual front-end for the C++ Compiler Engine.
# It allows users to:
#   1. Input source code and regex patterns.
#   2. Visualize Lexical Analysis (Tokens).
#   3. View dynamically generated NFA and DFA state diagrams.
#   4. Step through the Syntax Analysis (PDA) process.
# ==============================================================================================

class CompilerSimulatorGUI:
    """
    Main GUI Class for the Compiler Simulator.
    Handles window creation, layout management, and interaction with the C++ backend.
    """
    def __init__(self, root):
        """
        Initialize the application window and design themes.
        """
        self.root = root
        self.root.title("Compiler Front-End Simulator")
        self.root.geometry("1400x900")  # Large default size for better visibility
        # Color palette (black/white shades)
        self.colors = {
            'bg_main': '#1e1e1e',      # Darker background like VS Code
            'panel_bg': '#252526',     # Slightly lighter panel
            'card_bg': '#1e1e1e',      # Same as main for seamless look
            'text_fg': '#cccccc',      # Softer white
            'muted': '#858585',        # Muted text
            'accent': '#007acc',       # VS Code Blue
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
            'node_fill': '#2d2d2d',
            'node_outline': '#007acc'
        }
        self.ui_font = ('Segoe UI', 10)
        self.header_font = ('Segoe UI', 12, 'bold')
        self.title_font = ('Segoe UI', 24, 'bold')
        self.code_font = ('Consolas', 10)
        
        self.root.configure(bg=self.colors['bg_main'])
        
        # Create main container
        self.create_widgets()
 
        
    
    def create_widgets(self):
        """
        Sets up the entire UI layout, including the title bar, side panels, and content area.
        """
        # Title
        title_frame = tk.Frame(self.root, bg=self.colors['panel_bg'], height=80)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_frame.pack_propagate(False)

        # Left-justified title occupying two lines
        title_label = tk.Label(title_frame, text="Compiler Front-End Simulator", 
                      font=self.title_font, fg=self.colors['text_fg'], bg=self.colors['panel_bg'], anchor='w', justify='left')
        title_label.pack(anchor='w', padx=20, pady=(12,0))

        subtitle = tk.Label(title_frame, text="Lexical Analysis (NFA/DFA)  •  Syntax Analysis (PDA)", 
                   font=self.ui_font, fg=self.colors['muted'], bg=self.colors['panel_bg'], anchor='w', justify='left')
        subtitle.pack(anchor='w', padx=20, pady=(0,12))

        # Main content split
        main_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=(10,20))

        left_frame = tk.Frame(main_frame, bg=self.colors['bg_main'])
        left_frame.pack(side='left', fill='both', expand=True)

        right_panel = tk.Frame(main_frame, bg=self.colors['panel_bg'], width=320)
        right_panel.pack(side='right', fill='y', padx=(15,0), pady=0)
        right_panel.pack_propagate(False)

        input_label = tk.Label(right_panel, text="Input Expression:", 
                              font=self.header_font, bg=self.colors['panel_bg'], fg=self.colors['text_fg'])
        input_label.pack(anchor='n', pady=(20,6), padx=12)

        # Example Dropdown (New)
        self.create_example_menu(right_panel)

        self.input_entry = tk.Entry(right_panel, font=self.code_font, 
                        relief='solid', borderwidth=2, bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.input_entry.pack(fill='x', padx=12, pady=(0, 12))

        # Create rounded run button (10px radius)
        self.run_button = self.create_rounded_button(right_panel, text="▶ Run Analysis", command=self.run_analysis,
                                 font=('Segoe UI', 12, 'bold'), height=40)
        self.run_button.pack(pady=(12,8), padx=12, anchor='n', fill='x')
        # Content area (left) where frames are shown
        content_area = tk.Frame(left_frame, bg=self.colors['bg_main'])
        content_area.pack(side='left', fill='both', expand=True, padx=(10,0))

        # Create content frames (acts like notebook pages)
        self.lexical_frame = self.create_lexical_tab(content_area)
        self.nfa_frame = self.create_nfa_tab(content_area)
        self.dfa_frame = self.create_dfa_tab(content_area)
        self.pda_frame = self.create_pda_tab(content_area)
        self.tester_frame = self.create_tester_tab(content_area) # New Tab
        self.pdalab_frame = self.create_pdalab_tab(content_area) # PDA Lab Tab
        self.log_frame = self.create_log_tab(content_area)

        # Pack views (stacked); we'll lift the active one
        for f in (self.lexical_frame, self.nfa_frame, self.dfa_frame, self.pda_frame, self.tester_frame, self.pdalab_frame, self.log_frame):
            f.place(in_=content_area, x=0, y=0, relwidth=1, relheight=1)

        # Navigation buttons moved to the right panel below the input
        nav_frame = tk.Frame(right_panel, bg=self.colors['panel_bg'])
        # place the nav_frame centered vertically in the right panel
        nav_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Smaller gaps and slightly larger buttons but packed close together
        self.create_rounded_button(nav_frame, text='Lexical Analysis', command=lambda: self.show_view('lexical'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='NFA Diagram', command=lambda: self.show_view('nfa'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='DFA Diagram', command=lambda: self.show_view('dfa'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        # self.create_rounded_button(nav_frame, text='Syntax (PDA)', command=lambda: self.show_view('pda'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='Regex Tester', command=lambda: self.show_view('tester'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4) # New Button
        self.create_rounded_button(nav_frame, text='General PDA Lab', command=lambda: self.show_view('pdalab'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4) 
        self.create_rounded_button(nav_frame, text='Compilation Log', command=lambda: self.show_view('log'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)

        # map names to frames and show default
        self.views = {'lexical': self.lexical_frame, 'nfa': self.nfa_frame, 'dfa': self.dfa_frame, 'pda': self.pda_frame, 'tester': self.tester_frame, 'pdalab': self.pdalab_frame, 'log': self.log_frame}
        self.show_view('lexical')

    def create_lexical_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])

        title = tk.Label(frame, text="Token Recognition", 
                        font=('Arial', 16, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)

        self.lexical_text = scrolledtext.ScrolledText(frame, font=('Courier', 11), 
                                                      height=25, wrap='word', bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.lexical_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        return frame
    
    def create_nfa_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])

        title = tk.Label(frame, text="NFA Simulation (Thompson's Construction)", 
                        font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)

        # Diagram canvas
        diagram_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='solid', borderwidth=2)
        diagram_frame.pack(fill='x', padx=20, pady=(0, 15))



        diagram_label = tk.Label(diagram_frame, text="NFA State Diagram", 
                                font=('Segoe UI', 10), bg=self.colors['card_bg'], fg=self.colors['muted'])
        diagram_label.pack(pady=5)

        # Diagram canvas container with scrollbar
        # Diagram canvas container with scrollbar
        canvas_container = tk.Frame(diagram_frame, bg=self.colors['card_bg'])
        canvas_container.pack(fill='x', padx=20, pady=(0, 15))

        self.nfa_canvas = tk.Canvas(canvas_container, height=200, bg=self.colors['card_bg'], highlightthickness=0)
        
        # Scrollbars - Pack Y first to maximize height, then X
        nfa_scroll_y = ttk.Scrollbar(canvas_container, orient='vertical', command=self.nfa_canvas.yview)
        nfa_scroll_y.pack(side='right', fill='y')
        
        nfa_scroll_x = ttk.Scrollbar(canvas_container, orient='horizontal', command=self.nfa_canvas.xview)
        nfa_scroll_x.pack(side='bottom', fill='x')
        
        self.nfa_canvas.configure(xscrollcommand=nfa_scroll_x.set, yscrollcommand=nfa_scroll_y.set)
        self.nfa_canvas.pack(side='left', fill='both', expand=True)

        # Steps text
        steps_label = tk.Label(frame, text="Transition Steps:", 
                              font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        steps_label.pack(anchor='w', padx=20, pady=(10, 5))

        self.nfa_text = scrolledtext.ScrolledText(frame, font=self.code_font, 
                                                 height=15, wrap='word', bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.nfa_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        return frame
    
    def create_dfa_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])

        title = tk.Label(frame, text="DFA Simulation (Optimized)", 
                        font=('Arial', 16, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)

        # Diagram canvas
        diagram_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='solid', borderwidth=2)
        diagram_frame.pack(fill='x', padx=20, pady=(0, 15))

        diagram_label = tk.Label(diagram_frame, text="DFA State Diagram", 
                                font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], fg=self.colors['muted'])
        diagram_label.pack(pady=10)

        # Diagram canvas container with scrollbar
        # Diagram canvas container with scrollbar
        canvas_container = tk.Frame(diagram_frame, bg=self.colors['card_bg'])
        canvas_container.pack(fill='x', padx=20, pady=(0, 15))

        self.dfa_canvas = tk.Canvas(canvas_container, height=200, bg=self.colors['card_bg'], highlightthickness=0)
        
        # Scrollbars - Pack Y first to maximize height, then X
        dfa_scroll_y = ttk.Scrollbar(canvas_container, orient='vertical', command=self.dfa_canvas.yview)
        dfa_scroll_y.pack(side='right', fill='y')
        
        dfa_scroll_x = ttk.Scrollbar(canvas_container, orient='horizontal', command=self.dfa_canvas.xview)
        dfa_scroll_x.pack(side='bottom', fill='x')
        
        self.dfa_canvas.configure(xscrollcommand=dfa_scroll_x.set, yscrollcommand=dfa_scroll_y.set)
        self.dfa_canvas.pack(side='left', fill='both', expand=True)

        # Steps text
        steps_label = tk.Label(frame, text="Transition Steps:", 
                              font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        steps_label.pack(anchor='w', padx=20, pady=(10, 5))

        self.dfa_text = scrolledtext.ScrolledText(frame, font=('Courier', 10), 
                                                 height=15, wrap='word', bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.dfa_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        return frame
    
    def create_pda_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        
        title = tk.Label(frame, text="Pushdown Automaton (PDA)", 
                        font=('Arial', 16, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)
        
        # Result frame
        self.result_frame = tk.Frame(frame, relief='solid', borderwidth=2, bg=self.colors['card_bg'])
        self.result_frame.pack(fill='x', padx=20, pady=(0, 15))

        self.result_label = tk.Label(self.result_frame, text="", 
                         font=('Arial', 12, 'bold'), 
                         pady=15, bg=self.colors['card_bg'], fg=self.colors['text_fg'], anchor='center', justify='center')
        self.result_label.pack(fill='x', padx=10)
        
        # Visualization Section
        viz_frame = tk.Frame(frame, bg=self.colors['card_bg'], relief='solid', borderwidth=2)
        viz_frame.pack(fill='x', padx=20, pady=(0, 15))

        # Header with Toggle
        header_frame = tk.Frame(viz_frame, bg=self.colors['card_bg'])
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="PDA Visualization", font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['muted']).pack(side='left')

        toggle_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
        toggle_frame.pack(side='right')
        
        # Parse Tree Header
        tk.Label(toggle_frame, text="Parse Tree Visualization", font=self.ui_font, bg=self.colors['card_bg'], fg=self.colors['muted']).pack(side='right', padx=5)
        
        # Sub-container for Tree and Stack
        viz_container = tk.Frame(viz_frame, bg=self.colors['card_bg'])
        viz_container.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # 1. Parse Tree Canvas (Left)
        tree_frame = tk.Frame(viz_container, bg=self.colors['card_bg'], width=400)
        tree_frame.pack(side='left', fill='both', expand=True)
        tk.Label(tree_frame, text="Parse Tree", font=('Segoe UI', 9, 'bold'), bg=self.colors['card_bg'], fg=self.colors['muted']).pack(anchor='n')
        
        self.pda_canvas = tk.Canvas(tree_frame, height=250, bg=self.colors['card_bg'], highlightthickness=0)
        
        pda_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.pda_canvas.yview)
        pda_scroll_y.pack(side='right', fill='y')
        pda_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.pda_canvas.xview)
        pda_scroll_x.pack(side='bottom', fill='x')
        
        self.pda_canvas.configure(xscrollcommand=pda_scroll_x.set, yscrollcommand=pda_scroll_y.set)
        self.pda_canvas.pack(side='left', fill='both', expand=True)

        # 2. Stack Viz Canvas (Right)
        stack_frame = tk.Frame(viz_container, bg=self.colors['card_bg'], width=200)
        stack_frame.pack(side='right', fill='y', padx=(10, 0))
        tk.Label(stack_frame, text="PDA Stack", font=('Segoe UI', 9, 'bold'), bg=self.colors['card_bg'], fg=self.colors['muted']).pack(anchor='n')

        self.stack_canvas = tk.Canvas(stack_frame, width=150, height=250, bg=self.colors['panel_bg'], highlightthickness=1, highlightbackground='#3c3c3c')
        self.stack_canvas.pack(fill='y', expand=True)

        # Controls
        controls_frame = tk.Frame(frame, bg=self.colors['card_bg'])
        controls_frame.pack(fill='x', padx=20, pady=5)
        
        self.step_label = tk.Label(controls_frame, text="Step: 0 / 0", font=('Consolas', 10), bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        self.step_label.pack(side='left', padx=10)

        self.btn_prev = tk.Button(controls_frame, text="<< Prev", command=self.prev_step, bg=self.colors['button_bg'], fg=self.colors['button_fg'], relief='flat')
        self.btn_prev.pack(side='left', padx=5)
        
        self.btn_next = tk.Button(controls_frame, text="Next >>", command=self.next_step, bg=self.colors['button_bg'], fg=self.colors['button_fg'], relief='flat')
        self.btn_next.pack(side='left', padx=5)

        self.btn_reset = tk.Button(controls_frame, text="Reset", command=self.reset_steps, bg=self.colors['button_bg'], fg=self.colors['button_fg'], relief='flat')
        self.btn_reset.pack(side='left', padx=5)

        # Steps Text Log
        steps_label = tk.Label(frame, text="PDA Execution Trace:", 
                              font=('Arial', 12, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        steps_label.pack(anchor='w', padx=20, pady=(10, 5))
        
        self.pda_text = scrolledtext.ScrolledText(frame, font=('Courier', 10), 
                                                 height=10, wrap='word', bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.pda_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        return frame

    def create_log_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        
        title = tk.Label(frame, text="Compilation Process Log", 
                        font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)
        
        self.log_text = scrolledtext.ScrolledText(frame, font=self.code_font, 
                                                 height=20, wrap='word', bg=self.colors['card_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['text_fg'])
        self.log_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        return frame

    def create_tester_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])
        
        title = tk.Label(frame, text="Regex Tester (NFA Simulator)", 
                        font=self.header_font, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(anchor='w', padx=20, pady=15)
        
        # Regex Input
        tk.Label(frame, text="Regex Pattern:", font=('Segoe UI', 10, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg']).pack(anchor='w', padx=20)
        self.tester_regex = tk.Entry(frame, font=('Consolas', 11), bg=self.colors['panel_bg'], fg=self.colors['text_fg'], insertbackground='white')
        self.tester_regex.pack(fill='x', padx=20, pady=(0, 5))
        self.tester_regex.bind('<KeyRelease>', self.validate_regex_input)
        
        self.tester_error_label = tk.Label(frame, text="", font=('Segoe UI', 9), bg=self.colors['card_bg'], fg='#f44336')
        self.tester_error_label.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Test Strings Input
        tk.Label(frame, text="Test Strings (one per line or comma/space separated):", font=('Segoe UI', 10, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg']).pack(anchor='w', padx=20)
        self.tester_input = scrolledtext.ScrolledText(frame, font=('Consolas', 11), height=6, bg=self.colors['panel_bg'], fg=self.colors['text_fg'], insertbackground='white')
        self.tester_input.pack(fill='x', padx=20, pady=(0, 15))
        
        # Run Button
        self.create_rounded_button(frame, text="✅ Validate Strings", command=self.run_tester, font=('Segoe UI', 11, 'bold'), height=40).pack(fill='x', padx=20, pady=(0,15))
        
        # Results Area
        tk.Label(frame, text="Validation Results:", font=('Segoe UI', 10, 'bold'), bg=self.colors['card_bg'], fg=self.colors['text_fg']).pack(anchor='w', padx=20)
        self.tester_results = scrolledtext.ScrolledText(frame, font=('Consolas', 11), height=10, bg=self.colors['panel_bg'], fg=self.colors['text_fg'], state='disabled')
        self.tester_results.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        return frame

    def run_tester(self):
        pattern = self.tester_regex.get().strip()
        raw_input = self.tester_input.get("1.0", tk.END).strip()
        
        if not pattern:
             self.tester_results.config(state='normal')
             self.tester_results.delete('1.0', tk.END)
             self.tester_results.insert('1.0', "Error: Please enter a regex pattern.")
             self.tester_results.config(state='disabled')
             return

        # Split input into lines or words
        # Be robust: replace commas with spaces, then split
        norm_input = raw_input.replace(',', ' ').replace('\n', ' ')
        test_strings = [s.strip() for s in norm_input.split() if s.strip()]
        
        if not test_strings:
             self.tester_results.config(state='normal')
             self.tester_results.delete('1.0', tk.END)
             self.tester_results.insert('1.0', "Error: Please enter at least one test string.")
             self.tester_results.config(state='disabled')
             return
             
        # Call Backend
        try:
            # Use new advanced engine
            binary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'regex_engine.exe')
            if not os.path.exists(binary_path):
                # Fallback or error
                 binary_path = 'compiler_engine.exe' # Old one if new doesn't exist?
            
            cmd = [binary_path, 'TEST', pattern] + test_strings
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Use subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
            
            output = result.stdout
            
            self.tester_results.config(state='normal')
            self.tester_results.delete('1.0', tk.END)
            
            if "ERROR|" in output: # Format: ERROR|Msg|Pos
                 self.tester_results.insert('1.0', f"System Error: {output}")
            elif "ERROR: Invalid Regex" in output:
                self.tester_results.insert('1.0', f"Invalid Regex Pattern: {pattern}\n Check syntax.")
            else:
                for line in output.split('\n'):
                    if line.startswith("RESULT:"):
                        # line format: RESULT: string -> Accepted/Rejected
                        content = line.replace("RESULT:", "").strip()
                        if "-> Accepted" in content:
                            self.tester_results.insert(tk.END, content + "\n", 'accepted')
                        else:
                            self.tester_results.insert(tk.END, content + "\n", 'rejected')

            # Tag config
            self.tester_results.tag_config('accepted', foreground='#4caf50') # Green
            self.tester_results.tag_config('rejected', foreground='#f44336') # Red
            
            self.tester_results.config(state='disabled')
            
        except Exception as e:
            self.tester_results.config(state='normal')
            self.tester_results.insert(tk.END, f"System Error: {e}")
            self.tester_results.config(state='disabled')

    def validate_regex_input(self, event=None):
        pattern = self.tester_regex.get().strip()
        if not pattern:
            self.tester_error_label.config(text="")
            self.tester_regex.config(bg=self.colors['panel_bg'])
            return

        try:
            binary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'regex_engine.exe')
            if not os.path.exists(binary_path): return

            cmd = [binary_path, 'VALIDATE', pattern]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Use subprocess (fast check)
            # Startupinfo to hide window on Windows if needed, but simple run is ok for now
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
            output = result.stdout.strip()
            
            if output == "VALID":
                self.tester_error_label.config(text="✓ Valid Regex", fg='#4caf50')
                self.tester_regex.config(bg=self.colors['panel_bg'])
            elif output.startswith("ERROR|"):
                # ERROR|Msg|Pos
                parts = output.split('|')
                if len(parts) >= 3:
                    msg = parts[1]
                    # pos = int(parts[2]) # Parsing pos if we want to underline
                    self.tester_error_label.config(text=f"✗ {msg}", fg='#f44336')
                    self.tester_regex.config(bg='#3ed1cfcf') # Slight red tint? Or just rely on label
                else:
                    self.tester_error_label.config(text="✗ Invalid Regex", fg='#f44336')
        except:
            pass

    
    def draw_nfa_diagram(self, transitions, final_states):
        """Renders the NFA Graph using the custom layout engine."""
        self.draw_dynamic_graph(self.nfa_canvas, transitions, "NFA", final_states)

    def draw_dfa_diagram(self, transitions, final_states):
        self.draw_dynamic_graph(self.dfa_canvas, transitions, "DFA", final_states)

    def draw_dynamic_graph(self, canvas, transitions, title, final_states):
        """
        A custom graph layout engine (DAG-based) to visualize Automata.
        It ranks nodes by depth (Topological-like sort) and minimizes edge crossing.
        """
        canvas.delete('all')
        if not transitions:
            return

        # 1. Build Adjacency List
        adj = {}
        nodes = set()
        for t in transitions:
            u, v = t['from'], t['to']
            nodes.add(u)
            nodes.add(v)
            if u not in adj: adj[u] = []
            adj[u].append((v, t['label']))
            
        # 2. Heuristic Layout: Longest Path Layering (Ranked)
        # Identify start node
        start_node = next((n for n in nodes if n in ['q0', '0', 'S0']), list(nodes)[0])
        
        # Detect Back Edges (DFS) to break cycles for ranking
        visited = set()
        recursion_stack = set()
        back_edges = set() # (u, v)
        
        def dfs_detect_cycles(u):
            visited.add(u)
            recursion_stack.add(u)
            if u in adj:
                for v, _ in adj[u]:
                    if v not in visited:
                        dfs_detect_cycles(v)
                    elif v in recursion_stack:
                        back_edges.add((u, v))
            recursion_stack.remove(u)
            
        dfs_detect_cycles(start_node)
        
        # Calculate Ranks (Longest Path using forward edges only)
        ranks = {n: 0 for n in nodes}
        # Relax edges multiple times (Bellman-Ford-like since DAG)
        # Since we removed back edges, we have a DAG. 
        # But we might have disconnected components or cross edges.
        # Simple iteration for depth:
        for _ in range(len(nodes) + 1):
            changed = False
            for u in nodes:
                if u in adj:
                    for v, _ in adj[u]:
                        if (u, v) in back_edges: continue
                        if ranks[v] < ranks[u] + 1:
                            ranks[v] = ranks[u] + 1
                            changed = True
            if not changed: break
            
        # Group by Rank
        layers = {}
        for n, r in ranks.items():
            if r not in layers: layers[r] = []
            layers[r].append(n)
            
        # 3. Calculate Coordinates
        # Sort nodes within layers to minimize crossings? (Heuristic: sort by neighbor average?)
        # For simplicity, sort by name or keep stable
        for r in layers:
            layers[r].sort(key=lambda x: str(x))

        # Calculate required height based on max nodes in a layer
        max_nodes_in_layer = max((len(nodes) for nodes in layers.values()), default=1)
        
        c_width = max(800, len(layers) * 120 + 200)
        # Dynamic height calculation
        required_height = max_nodes_in_layer * 80 + 100
        c_height = max(300, required_height)
        
        x_gap = 120
        y_gap = 70
        start_x = 80
        center_y = c_height // 2
        
        node_pos = {}
        
        for r in sorted(layers.keys()):
            n_list = layers[r]
            x = start_x + r * x_gap
            total_h = (len(n_list) - 1) * y_gap
            start_y = center_y - total_h // 2
            
            for i, node in enumerate(n_list):
                y = start_y + i * y_gap
                node_pos[node] = (x, y)

        # 4. Draw Edges
        for u in adj:
            if u not in node_pos: continue
            xu, yu = node_pos[u]
            for v, label in adj[u]:
                if v not in node_pos: continue
                xv, yv = node_pos[v]
                
                # Check for Self Loop
                if u == v:
                    # Draw a loop above the node
                    canvas.create_arc(xu-20, yu-40, xu+20, yu, start=0, extent=180, 
                                    style='arc', outline=self.colors['muted'], width=1.5)
                    # Label above loop
                    canvas.create_text(xu, yu-48, text=label, fill=self.colors['text_fg'], font=('Consolas', 9))
                
                # Check for Back Edge (Curve below)
                elif (u, v) in back_edges or ranks[u] >= ranks[v]:
                    # Curve downwards
                    mid_x = (xu + xv) // 2
                    mid_y = max(yu, yv) + 50 + abs(xu-xv)//5
                    canvas.create_line(xu, yu+20, mid_x, mid_y, xv, yv+20, smooth=True, 
                                     arrow='last', arrowshape=(10, 12, 4), fill=self.colors['muted'], width=1.5)
                    canvas.create_text(mid_x, mid_y+14, text=label, fill=self.colors['text_fg'], font=('Consolas', 9))
                
                # Long Forward Edge (Curve Up)
                elif ranks[v] - ranks[u] > 1:
                    # Curve upwards to avoid crossing through nodes
                    mid_x = (xu + xv) // 2
                    mid_y = min(yu, yv) - 50 - abs(xu-xv)//5
                    canvas.create_line(xu, yu-20, mid_x, mid_y, xv, yv-20, smooth=True, 
                                     arrow='last', arrowshape=(10, 12, 4), fill=self.colors['muted'], width=1.5)
                    canvas.create_text(mid_x, mid_y-14, text=label, fill=self.colors['text_fg'], font=('Consolas', 9))

                # Adjacent Forward Edge (Straight)
                else:
                    canvas.create_line(xu+25, yu, xv-25, yv, arrow='last', arrowshape=(10, 12, 4), fill=self.colors['muted'], width=1.5)
                    xm, ym = (xu+xv)//2, (yu+yv)//2
                    # Offset label slightly to avoid clutter
                    canvas.create_rectangle(xm-10, ym-10, xm+10, ym+5, fill=self.colors['card_bg'], outline="") # Clear bg for text
                    canvas.create_text(xm, ym-8, text=label, fill=self.colors['text_fg'], font=('Consolas', 9))


        # 5. Draw Nodes
        node_radius = 24
        for node, (x, y) in node_pos.items():
            fill = self.colors['node_fill']
            outline = self.colors['node_outline']
            width = 2
            
            # Highlight accept
            # Highlight accept
            # Check explicit final states list (converting to str to match node keys)
            is_accept = str(node) in [str(x) for x in final_states]
            
            if is_accept:
                # Double circle effect
                canvas.create_oval(x-(node_radius+4), y-(node_radius+4), x+(node_radius+4), y+(node_radius+4), outline=self.colors['node_outline'], width=2)
                
            canvas.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, fill=fill, outline=outline, width=width)
            
            # Ensure text contrast
            canvas.create_text(x, y, text=str(node), fill=self.colors['text_fg'], font=('Segoe UI', 9, 'bold'))
            
            # Label Start
            if node == start_node:
                canvas.create_text(x-35, y, text="START", fill=self.colors['muted'], font=('Segoe UI', 8), anchor='e')
                canvas.create_line(x-30, y, x-node_radius-2, y, arrow='last', fill=self.colors['muted'], width=1)
        
        # Update Scroll Region (MOVED: Do this AFTER drawing nodes to include them!)
        # Calculate bounding box of all items
        x0, y0, x1, y1 = canvas.bbox("all") or (0,0,0,0)
        # Add some padding
        canvas.configure(scrollregion=(0, 0, x1 + 50, max(c_height, y1 + 50)))

    def draw_pda_tree(self, root_node):
        canvas = self.pda_canvas
        canvas.delete('all')
        
        if not root_node: return

        # 1. Assign Coordinates (Reingold-Tilford simplifed)
        # Recursively determine width of each node
        level_y_gap = 60
        sibling_x_gap = 20
        
        def iter_width(node):
            if not node['children']:
                node['width'] = 40
            else:
                w = 0
                for c in node['children']:
                    w += iter_width(c)
                node['width'] = max(40, w + (len(node['children'])-1)*sibling_x_gap)
            return node['width']
            
        iter_width(root_node)
        
        # 2. Assign positions
        node_positions = [] # (x, y, label)
        edges = [] # (x1, y1, x2, y2)
        
        def assign_pos(node, x, y):
            node_positions.append((x, y, node['label']))
            
            # center children under x
            if node['children']:
                total_w = node['width']
                start_x = x - total_w / 2
                current_x = start_x
                
                for c in node['children']:
                    child_x = current_x + c['width']/2
                    child_y = y + level_y_gap
                    edges.append((x, y + 15, child_x, child_y - 15))
                    assign_pos(c, child_x, child_y)
                    current_x += c['width'] + sibling_x_gap

        assign_pos(root_node, 400, 40) # Start centerish
        
        # 3. Draw
        # Draw edges first
        for (x1, y1, x2, y2) in edges:
            canvas.create_line(x1, y1, x2, y2, fill='#555555', width=2)
            
        # Draw nodes
        for (x, y, label) in node_positions:
            r = 18
            # Color coding
            fill = '#2d2d2d'
            outline = '#007acc'
            text_col = '#ffffff'
            
            if label in ['+', '-', '*', '/', '=']:
                fill = '#3c3c3c'
                outline = '#ff9800' # Orange for ops
            elif label.isdigit() or label.replace('.', '').isdigit():
                fill = '#3c3c3c'
                outline = '#4caf50' # Green for numbers
                
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=2)
            canvas.create_text(x, y, text=label, fill=text_col, font=('Segoe UI', 9, 'bold'))
            
        # Scroll region
        x0, y0, x1, y1 = canvas.bbox("all") or (0,0,0,0)
        canvas.configure(scrollregion=(0, 0, x1 + 50, y1 + 50))
    


    def run_analysis(self):
        input_text = self.input_entry.get()
        
        # Run C++ executable
        try:
            # Ensure we operate relative to this script's directory so
            # the C++ source/binary are found even if user runs Python elsewhere.
            script_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(script_dir, 'compiler_engine')

            # Compile if needed (for first run)
            # if not os.path.exists(exe_path):
            #     self.compile_cpp(script_dir)

            # ---------------------------------------------------------------------------------
            # RUN C++ BACKEND
            # ---------------------------------------------------------------------------------
            # We execute the compiled C++ binary ('compiler_engine.exe') as a subprocess.
            # The C++ engine takes the input string and performs all the heavy lifting:
            # parsing regex, generating NFA/DFA, and running the PDA.
            # ---------------------------------------------------------------------------------
            # Run the executable with input (use absolute path)
            # result = subprocess.run([exe_path], 
            #                       input=input_text, 
            #                       capture_output=True, 
            #                       text=True, cwd=script_dir)
            
            # Parse output (simplified version - in real app, parse JSON properly)
            # output_lines = result.stdout.split('\n')
            
            # For this demo, we'll simulate the output
            self.simulate_analysis(input_text)
            
        except Exception as e:
            self.lexical_text.delete('1.0', tk.END)
            self.lexical_text.insert('1.0', f"Error running analysis: {str(e)}\n\n")
            self.lexical_text.insert(tk.END, "Note: Make sure compiler_engine.cpp is compiled.\n")
            self.lexical_text.insert(tk.END, "Run: g++ -o compiler_engine compiler_engine.cpp -std=c++11")

    def show_view(self, name):
        # Lift the requested view (frame) to the top of the stack
        frame = self.views.get(name)
        if frame:
            frame.lift()

    def create_rounded_button(self, parent, text, command=None, font=('Arial',12,'bold'), height=44, radius=10):
        """Create a Canvas-based rounded button. Returns the Canvas widget.

        - `height` in pixels controls the button height.
        - `radius` is corner radius in pixels.
        """
        bg = parent.cget('bg') if isinstance(parent, tk.Widget) else self.colors['panel_bg']
        canvas = tk.Canvas(parent, height=height, bg=bg, highlightthickness=0)

        fill = self.colors['button_bg']
        fg = self.colors['button_fg']
        hover_fill = self.colors['card_bg']

        def _draw(fill_color=fill, text_color=fg):
            canvas.delete('all')
            w = canvas.winfo_width() or (parent.winfo_width() or 200)
            h = height
            r = radius
            x1, y1, x2, y2 = 4, 4, max(w-4, 60), h-4
            # center rectangle and corner ovals to form rounded rect
            canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=fill_color, outline='')
            canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=fill_color, outline='')
            canvas.create_oval(x1, y1, x1+2*r, y1+2*r, fill=fill_color, outline='')
            canvas.create_oval(x2-2*r, y1, x2, y1+2*r, fill=fill_color, outline='')
            canvas.create_oval(x1, y2-2*r, x1+2*r, y2, fill=fill_color, outline='')
            canvas.create_oval(x2-2*r, y2-2*r, x2, y2, fill=fill_color, outline='')
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, font=font, fill=text_color)

        def _on_enter(e):
            _draw(hover_fill, self.colors['text_fg'])

        def _on_leave(e):
            _draw(fill, fg)

        def _on_click(e):
            if command:
                command()

        # Initial draw after widget appears
        canvas.bind('<Configure>', lambda e: _draw())
        canvas.bind('<Enter>', _on_enter)
        canvas.bind('<Leave>', _on_leave)
        canvas.bind('<Button-1>', _on_click)

        return canvas
    
    def create_example_menu(self, parent):
        # Create a Menubutton for examples
        mb = tk.Menubutton(parent, text="", 
                          bg=self.colors['panel_bg'], fg=self.colors['accent'],
                          font=('Segoe UI', 10), activebackground=self.colors['panel_bg'], activeforeground=self.colors['text_fg'],
                          relief='flat')
        mb.pack(anchor='e', padx=12, pady=(0, 5))
        
        self.example_menu = tk.Menu(mb, tearoff=0, bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        mb.config(menu=self.example_menu)
        
        examples = [
            ("Simple Identifier (Regex Demo)", "my_variable_123"),
            ("Decimal Number", "3.14159"),
            ("Calculator Expression", "x + 5 * (y - 2)"),
            ("Nested Parentheses (PDA Demo)", "((a + b) * c)"),
            ("Complex Statement", "total / (count + 1) * 100")
        ]
        
        for label, text in examples:
            self.example_menu.add_command(label=label, command=lambda t=text: self.load_example(t))
            
    def load_example(self, text):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)
    
    def compile_cpp(self):
        """Compile the C++ code"""
        # Compile using the script directory as working directory so the
        # compiler finds `compiler_engine.cpp` even if current working
        # directory differs from the script location.
        script_dir = None
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            script_dir = os.getcwd()

        subprocess.run(['g++', '-o', 'compiler_engine', 'compiler_engine.cpp', '-std=c++11'], cwd=script_dir)
    
    def simulate_analysis(self, input_text):
        """
        Perform the actual analysis by bridging with the C++ backend.
        Captures stdout from the C++ program and parses it to update the GUI.
        """
        import re
        
        # Clear all tabs
        self.lexical_text.delete('1.0', tk.END)
        self.nfa_text.delete('1.0', tk.END)
        self.dfa_text.delete('1.0', tk.END)
        self.pda_text.delete('1.0', tk.END)
        self.log_text.delete('1.0', tk.END)
        self.nfa_canvas.delete('all')
        self.dfa_canvas.delete('all')
        self.stack_canvas.delete('all')
        
        # Reset Stepper functionality
        self.pda_steps = [] # List of {step_num, action, stack (list), desc}
        self.current_step_index = -1
        
        log_lines = []
        log_lines.append("=== COMPILATION STARTED ===\n")
        log_lines.append(f"Source Code Input: \"{input_text}\"\n")
        
        # Display Grammar Info (UI Static)
        grammar_info = (
            "Regular Language Definitions:\n"
            "-----------------------------\n"
            "Identifier -> [a-zA-Z_][a-zA-Z0-9_]*\n"
            "Number     -> [0-9]+(\\.[0-9]+)?\n"
            "Grammar    -> Identifier -> letter IdentifierTail\n"
            "              IdentifierTail -> letter IdentifierTail | digit IdentifierTail | ε\n"
            "-----------------------------\n\n"
        )
        self.lexical_text.insert('1.0', grammar_info)
        
        # -------------------------------------------------------------
        # 1. PREPARE INPUT and CALL BACKEND
        # -------------------------------------------------------------
        # Use the input text as the regex pattern for this demo
        current_regex = input_text.strip()
        
        cpp_exe = "compiler_engine.exe"
        if os.path.exists(cpp_exe):
            log_lines.append(f"SYSTEM: Found C++ Backend '{cpp_exe}'. Executing...\n")
            try:
                # Run C++ Engine with Input AND Regex Pattern
                process = subprocess.Popen([cpp_exe, input_text, current_regex], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
                stdout, stderr = process.communicate()
                
                output_lines = stdout.replace('\r\n', '\n').split('\n')
                
                # Parsing State Containers
                nfa_transitions = []
                nfa_final = []
                dfa_transitions = []
                dfa_final = []
                
                # Parse Tree Simulation Stack
                # Store node objects: {'label': str, 'children': [node, node...]}
                tree_stack = []
                pda_final_tree = None
                

                # -------------------------------------------------------------
                # 2. PARSE OUTPUT
                # -------------------------------------------------------------
                # The C++ engine outputs specific markers (e.g., "NFA_EDGE:", "PDA_STEP:")
                # which we intercept here to build the data structures for visualization.
                # -------------------------------------------------------------

                for line in output_lines:
                    # 1. Scanner Output
                    if "SCANNER: Found" in line:
                         parts = line.split("SCANNER: Found")
                         if len(parts) > 1:
                             self.lexical_text.insert(tk.END, parts[1].strip() + "\n")
                             log_lines.append(line + "\n")
                    
                    # 2. NFA Output
                    elif "NFA_EDGE:" in line:
                        # Format: NFA_EDGE: 0 --(a)--> 1
                        m = re.search(r'(\d+)\s+--\((.*?)\)-->\s+(\d+)', line)
                        if m:
                            u, label, v = m.groups()
                            nfa_transitions.append({'from': u, 'to': v, 'label': label})
                            self.nfa_text.insert(tk.END, f"{u} --({label})--> {v}\n")
                    elif "NFA_FINAL:" in line:
                        state_id = line.split(":")[1].strip()
                        nfa_final.append(state_id)
                        
                    # 3. DFA Output
                    elif "DFA_EDGE:" in line:
                         m = re.search(r'(\d+)\s+--\((.*?)\)-->\s+(\d+)', line)
                         if m:
                            u, label, v = m.groups()
                            dfa_transitions.append({'from': u, 'to': v, 'label': label})
                            self.dfa_text.insert(tk.END, f"{u} --({label})--> {v}\n")
                    elif "DFA_FINAL:" in line:
                         state_id = line.split(":")[1].strip()
                         dfa_final.append(state_id)

                    # 4. PDA Output


                    elif "PDA_STEP:" in line:
                        # Format: PDA_STEP: 1 | ACTION | [stack] | desc
                        parts = line.split("|")
                        if len(parts) >= 4:
                            step_num = parts[0].replace("PDA_STEP:", "").strip()
                            action = parts[1].strip()
                            stack_content = parts[2].strip()
                            desc = parts[3].strip()
                            
                            self.pda_text.insert(tk.END, f"Step {step_num}:\n")
                            self.pda_text.insert(tk.END, f"  Action: {action}\n")
                            self.pda_text.insert(tk.END, f"  Stack:  {stack_content}\n")
                            self.pda_text.insert(tk.END, f"  Desc:   {desc}\n")
                            self.pda_text.insert(tk.END, "-"*30 + "\n")
                            
                            # Parse stack string "[a, b]" -> ["a", "b"]
                            stack_list = []
                            if stack_content.strip() and stack_content != "[]":
                                # Simple splitting for this demo (handle brackets)
                                raw = stack_content.replace("[", "").replace("]", "")
                                if raw.strip():
                                    stack_list = [s.strip() for s in raw.split(',')]
                            
                            self.pda_steps.append({
                                'step': int(step_num),
                                'action': action,
                                'stack': stack_list,
                                'desc': desc
                            })

                            

                            
                            # --- TREE CONSTRUCTION LOGIC ---
                            # The PDA output from C++ is a flat sequence of steps (Shift, Reduce, etc.).
                            # To visualize this as a tree, we must reconstruct the hierarchy.
                            # We maintain a 'tree_stack' of nodes. When a REDUCE action happens (e.g., T -> T * F),
                            # we pop the corresponding children from the stack and create a new parent node.
                            try:
                                if action == "SHIFT":
                                    # Read operand 3 -> Label "3"
                                    # Read variable x -> Label "x"
                                    # Read function f -> Label "f"
                                    label = desc
                                    for prefix in ["Read operand", "Read variable", "Read function"]:
                                        label = label.replace(prefix, "")
                                    label = label.strip()
                                    
                                    tree_stack.append({'label': label, 'children': []})
                                elif action == "PUSH":
                                    # Push operator + -> Label "+"
                                    # Push '(' -> Label "("
                                    label = desc.replace("Push operator", "").replace("Push", "").replace("'", "").strip()
                                    tree_stack.append({'label': label, 'children': []})
                                elif action == "POP/REDUCE":
                                    # Apply T -> T * F
                                    # format: Apply LHS -> RHS
                                    if "->" in desc:
                                        rule = desc.replace("Apply", "").strip()
                                        lhs, rhs = rule.split("->")
                                        lhs = lhs.strip()
                                        rhs_parts = rhs.strip().split()
                                        
                                        # Pop N items from stack where N = len(rhs_parts)
                                        # C++ logic might have minimal stack ops, so we heuristically pop
                                        # based on the rule length.
                                        children = []
                                        count = len(rhs_parts)
                                        if count > len(tree_stack): count = len(tree_stack) # Safety
                                        
                                        if count > 0:
                                            children = tree_stack[-count:]
                                            tree_stack = tree_stack[:-count]
                                        
                                        node = {'label': lhs, 'children': children}
                                        tree_stack.append(node)
                                        
                                elif action == "POP" and "Match" in desc:
                                    # Match '('
                                    # This usually means we close a parenthesis group.
                                    # Structure on stack might be: '(', 'E'
                                    # We want to reduce this to 'F' or similar, but the log just says "Match '('".
                                    # We'll pop the current top (expression) and the '(' below it.
                                    if len(tree_stack) >= 2:
                                        expr = tree_stack.pop()
                                        lparen = tree_stack.pop()
                                        # Synthesize a parent node (e.g. Factor)
                                        node = {'label': 'F', 'children': [lparen, expr, {'label': ')', 'children': []}]}
                                        tree_stack.append(node)
                                    
                            except Exception as e:
                                print(f"Tree build error: {e}")
                                
                            if action == "ACCEPT":
                                self.result_label.config(text="✓ SYNTAX CORRECT", fg="#4caf50")
                                log_lines.append("RESULT: Syntax Accepted.\n")
                                if tree_stack:
                                    pda_final_tree = tree_stack[0] # Root
                            elif action == "REJECT":
                                self.result_label.config(text="✗ SYNTAX ERROR (REJECTED)", fg="#f44336")
                                log_lines.append("RESULT: Syntax Rejected by PDA.\n")

                if nfa_transitions: self.draw_nfa_diagram(nfa_transitions, nfa_final)
                if dfa_transitions: self.draw_dfa_diagram(dfa_transitions, dfa_final)
                
                if pda_final_tree:
                    self.draw_pda_tree(pda_final_tree)
                else:
                    self.pda_canvas.delete('all')
                    self.pda_canvas.create_text(400, 100, text="No Parse Tree Available", fill=self.colors['muted'], font=('Segoe UI', 12))

            except Exception as e:
                log_lines.append(f"SYSTEM ERROR: Failed to run C++ engine: {e}\n")
                self.lexical_text.insert(tk.END, f"Error: {str(e)}\n", 'error')
        else:
            log_lines.append("SYSTEM ERROR: C++ Executable 'compiler_engine.exe' NOT FOUND.\n")
            log_lines.append("Please compile the project using g++.\n")
            self.result_label.config(text="⚠ COMPILER MISSING", fg="#ff9800")
            self.lexical_text.insert(tk.END, "CRITICAL ERROR: C++ Backend Not Found.\n", 'error')
            self.lexical_text.insert(tk.END, "The simulator requires the C++ executable to run.\n")
            self.lexical_text.insert(tk.END, "Please fix your C++ compiler (MinGW) and compile the project.\n")

        # Write Log
        for line in log_lines:
            self.log_text.insert(tk.END, line)

        # After parsing all logs
        if self.pda_steps:
             self.current_step_index = 0
             self.update_pda_viz()
        else:
             self.step_label.config(text="Step: 0 / 0")

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_pda_viz()

    def next_step(self):
        if self.current_step_index < len(self.pda_steps) - 1:
            self.current_step_index += 1
            self.update_pda_viz()
            
    def reset_steps(self):
        if self.pda_steps:
            self.current_step_index = 0
            self.update_pda_viz()
            
    def update_pda_viz(self):
        if not self.pda_steps or self.current_step_index < 0:
            return
            
        step = self.pda_steps[self.current_step_index]
        self.step_label.config(text=f"Step: {step['step']} / {len(self.pda_steps)}")
        
        # 1. Update Stack Viz
        self.draw_stack(step['stack'])
        
        # 2. Highlight text log (optional - simple scroll to end for now)
        # self.pda_text.see(tk.END) 
        
    def draw_stack(self, stack_items):
        canvas = self.stack_canvas
        canvas.delete('all')
        
        w = int(canvas['width'])
        h = int(canvas['height'])
        item_h = 30
        margin_bottom = 10
        
        # Draw base
        canvas.create_line(10, h-5, w-10, h-5, width=3, fill='#555')
        
        for i, item in enumerate(stack_items):
            # Bottom-up
            y2 = h - margin_bottom - (i * item_h)
            y1 = y2 - item_h
            x1 = 20
            x2 = w - 20
            
            # Color code
            fill = '#2d2d2d'
            if item in ['(', ')']: fill = '#3c3c3c'
            elif item in ['+', '-', '*', '/']: fill = '#3e3e42' 
            
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline='#007acc')
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=item, fill='white', font=('Consolas', 10, 'bold'))
        
        # Label Top
        if stack_items:
             y_top = h - margin_bottom - (len(stack_items) * item_h)
             canvas.create_text(w//2, y_top - 10, text="TOP", fill='#007acc', font=('Segoe UI', 8))




    # ==============================================================================================
    # PDA LAB TAB (New)
    # ==============================================================================================


    def create_pdalab_tab(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card_bg'])

        # Top Bar: Title and Controls
        top_bar = tk.Frame(frame, bg=self.colors['card_bg'])
        top_bar.pack(fill='x', padx=20, pady=15)

        title = tk.Label(top_bar, text="General PDA Simulator (a^n b^n)", font=self.header_font, 
                        bg=self.colors['card_bg'], fg=self.colors['text_fg'])
        title.pack(side='left')

        # Control Group (Regex + Input)
        input_group = tk.Frame(top_bar, bg=self.colors['card_bg'])
        input_group.pack(side='left', padx=20)

        # Row 1: Regex
        row1 = tk.Frame(input_group, bg=self.colors['card_bg'])
        row1.pack(fill='x', pady=2)
        tk.Label(row1, text="Regex:", width=8, anchor='e', bg=self.colors['card_bg'], fg=self.colors['text_fg']).pack(side='left')
        self.pdalab_regex = tk.Entry(row1, font=self.code_font, width=25)
        self.pdalab_regex.pack(side='left', padx=5)
        self.pdalab_regex.bind('<KeyRelease>', self.validate_pdalab_regex)
        
        self.pdalab_error_label = tk.Label(row1, text="", font=('Segoe UI', 8), bg=self.colors['card_bg'], fg='#f44336')
        self.pdalab_error_label.pack(side='left', padx=5)

        # Row 2: String
        row2 = tk.Frame(input_group, bg=self.colors['card_bg'])
        row2.pack(fill='x', pady=2)
        tk.Label(row2, text="String:", width=8, anchor='e', bg=self.colors['card_bg'], fg=self.colors['text_fg']).pack(side='left')
        self.pdalab_input = tk.Entry(row2, font=self.code_font, width=25)
        self.pdalab_input.pack(side='left', padx=5)
        self.pdalab_input.insert(0, "aabb")

        run_btn = self.create_rounded_button(top_bar, text="Run Simulation", command=self.run_pdalab, height=50)
        run_btn.pack(side='left', padx=10)

        # Content Split
        content_split = tk.Frame(frame, bg=self.colors['bg_main'])
        content_split.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Left Panel: Text Log
        left_panel = tk.Frame(content_split, bg=self.colors['bg_main'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        tk.Label(left_panel, text="Execution Log", bg=self.colors['bg_main'], fg=self.colors['muted'], font=self.ui_font).pack(anchor='w', pady=(0,5))
        self.pdalab_output = scrolledtext.ScrolledText(left_panel, font=('Consolas', 10), 
                                                      bg='#1e1e1e', fg='#cccccc', insertbackground='white')
        self.pdalab_output.pack(fill='both', expand=True)
        
        # Tags for highlighting
        self.pdalab_output.tag_config('action', foreground='#4ec9b0') 
        self.pdalab_output.tag_config('stack', foreground='#ce9178')
        self.pdalab_output.tag_config('success', foreground='#6a9955')
        self.pdalab_output.tag_config('fail', foreground='#f44747')
        self.pdalab_output.tag_config('highlight', background='#264f78')


        # Right Panel: Stack Visualization
        right_panel = tk.Frame(content_split, bg=self.colors['panel_bg'], width=300)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        right_panel.pack_propagate(False)

        self.pdalab_stack_label = tk.Label(right_panel, text="Stack Visualization", bg=self.colors['panel_bg'], fg=self.colors['text_fg'], font=self.header_font)
        self.pdalab_stack_label.pack(pady=10)

        # Canvas
        # Canvas
        self.pdalab_canvas = tk.Canvas(right_panel, bg='#1e1e1e', highlightthickness=0)
        self.pdalab_canvas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bind resize event to redraw
        self.pdalab_canvas.bind('<Configure>', lambda e: self.update_pdalab_viz())

        # Playback Controls
        ctrl_frame = tk.Frame(right_panel, bg=self.colors['panel_bg'])
        ctrl_frame.pack(fill='x', pady=10, padx=10)
        
        self.btn_prev = self.create_rounded_button(ctrl_frame, text="< Prev", command=self.pdalab_prev, height=30)
        self.btn_prev.grid(row=0, column=0, sticky='ew', padx=2)
        
        self.btn_reset = self.create_rounded_button(ctrl_frame, text="Reset", command=self.reset_pdalab_view, height=30)
        self.btn_reset.grid(row=0, column=1, sticky='ew', padx=2)

        self.btn_next = self.create_rounded_button(ctrl_frame, text="Next >", command=self.pdalab_next, height=30)
        self.btn_next.grid(row=0, column=2, sticky='ew', padx=2)

        ctrl_frame.grid_columnconfigure(0, weight=1)
        ctrl_frame.grid_columnconfigure(1, weight=1)
        ctrl_frame.grid_columnconfigure(2, weight=1)

        self.pdalab_lbl_step = tk.Label(right_panel, text="Step: 0 / 0", bg=self.colors['panel_bg'], fg=self.colors['muted'])
        self.pdalab_lbl_step.pack(pady=5)

        # State Variables
        self.pdalab_trace = [] # List of (action, stack_str)
        self.pdalab_step_idx = 0

        return frame

    def run_pdalab(self):
        input_str = self.pdalab_input.get().strip()
        regex_str = self.pdalab_regex.get().strip()
        
        self.pdalab_output.delete('1.0', tk.END)
        self.pdalab_output.insert(tk.END, f"Running PDA Lab...\n")
        if regex_str:
            self.pdalab_output.insert(tk.END, f"Regex:  {regex_str}\n")
            self.pdalab_stack_label.config(text="Stack (Unused in Regex Mode)")
        else:
            self.pdalab_stack_label.config(text="Stack Visualization")
            
        self.pdalab_output.insert(tk.END, f"Input:  '{input_str}'\n\n")
        
        self.pdalab_trace = []
        self.pdalab_step_idx = 0

        try:
            exe_path = "bin/pda_lab.exe"
            if not os.path.exists(exe_path):
                 exe_path = "pda_lab.exe" # local

            # Pass both input and regex if regex is present
            # Protocol: pda_lab.exe <input> [regex]
            cmd = [exe_path, input_str]
            if regex_str:
                 cmd.append(regex_str)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                # Log to text area
                if "ACCEPTED" in line:
                    self.pdalab_output.insert(tk.END, line + "\n", 'success')
                elif "REJECTED" in line:
                    self.pdalab_output.insert(tk.END, line + "\n", 'fail')
                elif "Action:" in line:
                    # Parse: "Action: a | Transition to q_push, Stack: $AA"
                    parts = line.split("|")
                    if len(parts) >= 2:
                        action_part = parts[0]
                        desc_stack_part = "|".join(parts[1:]) 
                        
                        # Extract stack content
                        # desc_stack_part might be " Transition to q_push, Stack: $AA"
                        stack_part = desc_stack_part.split("Stack:")[-1].strip()
                        
                        # Extract State: " Transition to q_push,"
                        state_part = "?"
                        if "Transition to " in desc_stack_part:
                            try:
                                state_part = desc_stack_part.split("Transition to ")[1].split(",")[0].strip()
                            except: pass
                        
                        # Calculate Input Index
                        # If action is NOT 'EPS' (and NOT 'Step 0'), we consumed a char.
                        # We need to know the PREVIOUS index.
                        prev_idx = 0
                        if self.pdalab_trace:
                             # Last item is tuple idx 3
                             # But wait, self.pdalab_trace[-1] might be different format if we changed it.
                             # It is (line, stack, state, idx) now.
                             if len(self.pdalab_trace[-1]) >= 4:
                                 prev_idx = self.pdalab_trace[-1][3]
                        
                        new_idx = prev_idx
                        # Clean action part "Action: a "
                        act = action_part.replace("Action:", "").replace("|", "").strip()
                        if act != "EPS" and act != "":
                            new_idx += 1

                        self.pdalab_trace.append( (action_part + "|" + desc_stack_part, stack_part, state_part, new_idx) )
                        
                        self.pdalab_output.insert(tk.END, action_part, 'action')
                        self.pdalab_output.insert(tk.END, "|" + desc_stack_part + "\n", 'stack')
                    else:
                        self.pdalab_output.insert(tk.END, line + "\n")
                elif "Step 0:" in line:
                     # Parse start state. "Step 0: Start | Stack: $"
                     # "Step 0: Start" -> State is "Start" or "q0" (implicit)
                     stack_part = line.split("Stack:")[-1].strip()
                     self.pdalab_trace.append( (line, stack_part, "Start", 0) ) # 0 is start index
                     self.pdalab_output.insert(tk.END, line + "\n")
                elif "DEBUG" in line:
                     self.pdalab_output.insert(tk.END, line + "\n", 'fail') 
                else:
                    self.pdalab_output.insert(tk.END, line + "\n")
            
            if result.returncode != 0:
                 self.pdalab_output.insert(tk.END, f"\nError: Process exited with code {result.returncode}\n")
            
        except Exception as e:
            self.pdalab_output.insert(tk.END, f"\nError running simulation: {e}\n", 'fail')
            # DEBUG: Print traceback
            import traceback
            traceback.print_exc()

        self.pdalab_output.see(tk.END)
        self.pdalab_trace_len = len(self.pdalab_trace)
        self.pdalab_step_idx = 0
        if self.pdalab_trace_len > 0:
            self.update_pdalab_viz()

    def reset_pdalab_view(self):
        self.pdalab_step_idx = 0
        self.update_pdalab_viz()

    def pdalab_next(self):
        if self.pdalab_step_idx < len(self.pdalab_trace) - 1:
            self.pdalab_step_idx += 1
            self.update_pdalab_viz()
            
    def pdalab_prev(self):
        if self.pdalab_step_idx > 0:
            self.pdalab_step_idx -= 1
            self.update_pdalab_viz()

    def update_pdalab_viz(self):
         if not self.pdalab_trace:
             return
         
         # Force update to get correct dimensions
         self.pdalab_canvas.update_idletasks()

         # item format: (full_desc, stack_str, state_str, input_idx)
         # Using try-except for backward compat is messy if we just changed it.
         # But let's be safe.
         
         trace_item = self.pdalab_trace[self.pdalab_step_idx]
         current_input_idx = 0
         
         if len(trace_item) == 4:
             current_info, current_stack_str, current_state, current_input_idx = trace_item
         elif len(trace_item) == 3:
              current_info, current_stack_str, current_state = trace_item
         else:
             # Fallback
             current_info = trace_item[0] if len(trace_item)>0 else ""
             current_stack_str = ""
             current_state = "?"

         # Draw Stack (Only if NO Regex is present, per user request)
         # "do not connect the Regex input field on the stack Visualization"
         # This implies: If Regex is active, Stack Viz should be hidden/cleared.
         regex_val = self.pdalab_regex.get().strip()
         
         if not regex_val:
             # Default Mode: Show Stack
             stack_list = list(current_stack_str)
             self.draw_stack_on_canvas(self.pdalab_canvas, stack_list)
         else:
             # Regex Mode: Clear Stack area / Show nothing for stack
             # We just don't draw the stack rectangles.
             pass
         
         # Draw State
         self.draw_state_on_canvas(self.pdalab_canvas, current_state)
         
         # Draw Input Tape
         # We need the full input string. We can store it in self.pdalab_current_input_str
         input_val = self.pdalab_input.get() # Get from UI directly or store it
         self.draw_input_tape(self.pdalab_canvas, input_val, current_input_idx)
         
         # Update Label logic
         self.pdalab_lbl_step.config(text=f"Step: {self.pdalab_step_idx} / {len(self.pdalab_trace)-1}")

    def validate_pdalab_regex(self, event=None):
        pattern = self.pdalab_regex.get().strip()
        if not pattern:
            self.pdalab_error_label.config(text="")
            self.pdalab_regex.config(bg=self.colors['panel_bg'])
            return

        try:
            binary_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'regex_engine.exe')
            if not os.path.exists(binary_path):
                 # Fallback to local if bin not found
                 binary_path = 'regex_engine.exe'
            if not os.path.exists(binary_path): return

            cmd = [binary_path, 'VALIDATE', pattern]
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
            output = result.stdout.strip()
            
            if output == "VALID":
                self.pdalab_error_label.config(text="✓", fg='#4caf50')
                self.pdalab_regex.config(bg=self.colors['panel_bg'])
            elif output.startswith("ERROR|"):
                self.pdalab_error_label.config(text="✗ Invalid", fg='#f44336')
            else:
                self.pdalab_error_label.config(text="✗", fg='#f44336')
        except:
            pass
         
         # Highlight line in text logic (optional, but nice)
         # Requires keeping track of line indices. Simpler: Update label.

    def draw_stack_on_canvas(self, canvas, stack_items):
        canvas.delete('all')
        w = canvas.winfo_width() or 300
        h = canvas.winfo_height() or 400
        item_h = 40
        item_w = 80
        center_x = w // 2
        margin_bottom = 20
        
        # Draw base
        canvas.create_line(center_x - item_w//2 - 10, h - margin_bottom, 
                           center_x + item_w//2 + 10, h - margin_bottom, fill='#555', width=3)

        for i, item in enumerate(stack_items):
            # i=0 is bottom ($).
            y_btm = h - margin_bottom - (i * item_h)
            y_top = y_btm - item_h
            x1 = center_x - item_w // 2
            x2 = center_x + item_w // 2
            
            fill = '#2d2d2d'
            if item == '$': fill = '#553333'
            
            canvas.create_rectangle(x1, y_top, x2, y_btm, fill=fill, outline='#007acc', width=2)
            canvas.create_text(center_x, (y_top+y_btm)//2, text=item, fill='white', font=('Consolas', 12, 'bold'))
        
        # Label TOP
        if stack_items:
             y_top_label = h - margin_bottom - (len(stack_items) * item_h) - 10
             canvas.create_text(center_x, y_top_label, text=f"TOP ({len(stack_items)})", fill='#007acc', font=('Segoe UI', 9))
             
    def draw_state_on_canvas(self, canvas, state_name):
        # Draw State Name at the top
        w = canvas.winfo_width() or 300
        center_x = w // 2
        y_pos = 40
        
        # Box for state
        # State names can be long, auto-width?
        text_w = len(state_name) * 10 
        x1 = center_x - max(40, text_w//2)
        x2 = center_x + max(40, text_w//2)
        y1 = y_pos - 15
        y2 = y_pos + 15
        
        canvas.create_rectangle(x1, y1, x2, y2, fill='#252526', outline='#4ec9b0', width=2)
        canvas.create_text(center_x, y_pos, text=f"State: {state_name}", fill='#4ec9b0', font=('Segoe UI', 10, 'bold'))
        
        # Arrow pointing down to stack?
        canvas.create_line(center_x, y2, center_x, y2+20, arrow='last', fill='#555')

    def draw_input_tape(self, canvas, input_str, current_idx):
        # Draw Tape at the bottom or top? Let's put it below the state, above stack?
        # Or at the very top.
        
        w = canvas.winfo_width() or 300
        center_x = w // 2
        y_pos = 90 # Below state box (40 +/- 15)
        
        cell_size = 25
        tape_w = len(input_str) * cell_size
        start_x = center_x - tape_w // 2
        
        # Label
        canvas.create_text(center_x, y_pos - 20, text="Input Tape", fill='#888', font=('Segoe UI', 8))

        for i, char in enumerate(input_str):
            x1 = start_x + i * cell_size
            x2 = x1 + cell_size
            y1 = y_pos
            y2 = y1 + cell_size
            
            # Highlight current
            bg = '#2d2d2d'
            fg = 'white'
            if i == current_idx:
                bg = '#007acc'
                fg = 'white'
            elif i < current_idx:
                bg = '#1e1e1e'
                fg = '#555' # Processed
            
            canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline='#555')
            canvas.create_text((x1+x2)//2, (y1+y2)//2, text=char, fill=fg, font=('Consolas', 10, 'bold'))
            
        # Arrow pointing to current
        if current_idx < len(input_str):
            curr_x = start_x + current_idx * cell_size + cell_size//2
            canvas.create_line(curr_x, y_pos + cell_size + 5, curr_x, y_pos + cell_size, arrow='last', fill='#007acc')


if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerSimulatorGUI(root)
    root.mainloop()