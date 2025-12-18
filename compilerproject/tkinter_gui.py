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
        self.log_frame = self.create_log_tab(content_area)

        # Pack views (stacked); we'll lift the active one
        for f in (self.lexical_frame, self.nfa_frame, self.dfa_frame, self.pda_frame, self.log_frame):
            f.place(in_=content_area, x=0, y=0, relwidth=1, relheight=1)

        # Navigation buttons moved to the right panel below the input
        nav_frame = tk.Frame(right_panel, bg=self.colors['panel_bg'])
        # place the nav_frame centered vertically in the right panel
        nav_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Smaller gaps and slightly larger buttons but packed close together
        self.create_rounded_button(nav_frame, text='Lexical Analysis', command=lambda: self.show_view('lexical'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='NFA Diagram', command=lambda: self.show_view('nfa'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='DFA Diagram', command=lambda: self.show_view('dfa'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='Syntax (PDA)', command=lambda: self.show_view('pda'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)
        self.create_rounded_button(nav_frame, text='Compilation Log', command=lambda: self.show_view('log'), font=('Segoe UI', 11), height=45).pack(fill='x', pady=4)

        # map names to frames and show default
        self.views = {'lexical': self.lexical_frame, 'nfa': self.nfa_frame, 'dfa': self.dfa_frame, 'pda': self.pda_frame, 'log': self.log_frame}
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
        
        pda_canvas_container = tk.Frame(viz_frame, bg=self.colors['card_bg'])
        pda_canvas_container.pack(fill='x', padx=20, pady=(0, 15))
        
        self.pda_canvas = tk.Canvas(pda_canvas_container, height=250, bg=self.colors['card_bg'], highlightthickness=0)
        
        pda_scroll_y = ttk.Scrollbar(pda_canvas_container, orient='vertical', command=self.pda_canvas.yview)
        pda_scroll_y.pack(side='right', fill='y')
        pda_scroll_x = ttk.Scrollbar(pda_canvas_container, orient='horizontal', command=self.pda_canvas.xview)
        pda_scroll_x.pack(side='bottom', fill='x')
        
        self.pda_canvas.configure(xscrollcommand=pda_scroll_x.set, yscrollcommand=pda_scroll_y.set)
        self.pda_canvas.pack(side='left', fill='both', expand=True)

        # Steps
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




if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerSimulatorGUI(root)
    root.mainloop()