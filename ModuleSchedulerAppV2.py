import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------
# Module Definitions
# -------------------------
class Module:
    def __init__(self, code, name, tracks, prerequisites=None, credits=3):
        self.code = code
        self.name = name
        self.tracks = tracks  # list of applicable course tracks
        self.prerequisites = prerequisites or []  # list of module codes
        self.credits = credits  # default to 3 credits if not specified
# -------------------------
# Load Modules Catalogue from JSON
# -------------------------
def load_modules_catalog(filename="modules.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            catalog = {}
            for entry in data:
                catalog[entry["code"]] = Module(
                    code=entry["code"],
                    name=entry["name"],
                    tracks=entry["tracks"],
                    prerequisites=entry.get("prerequisites", []),
                    credits=entry.get("credits", 3)  # Default to 3 if not specified
                )
            return catalog
    except Exception as e:
        messagebox.showerror("Error", f"Error loading modules catalog: {e}")
        return {}
    
# -------------------------
# Student Class Definition
# -------------------------
class Student:
    def __init__(self, student_id, name, course, year, semester, completed):
        self.student_id = student_id
        self.name = name
        self.course = course
        self.year = year
        self.semester = semester
        self.completed = {}  # modules already completed: key=module code, value=Module instance

def load_students(filename="students.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading student data: {e}")
        return []

# -------------------------
# Related Courses Mapping
# -------------------------
# Courses in similar fields can share modules.
related_courses = {
    "Data Science": ["Mathematics", "Electric Engineering", "Computer Science", "Economics"],
    "Mathematics": ["Data Science", "Electric Engineering", "Computer Science", "Economics"],
    "Electric Engineering": ["Data Science", "Mathematics", "Computer Science"],
    "Computer Science": ["Data Science", "Mathematics", "Electric Engineering"],
    "Linguistics": ["English", "Philosophy", "Sociology", "History"],
    "Microbiology": ["Biology", "Chemistry", "Medicine"],
    "Physiology": ["Biology", "Medicine"],
    "English": ["Linguistics", "History", "Philosophy"],
    "History": ["English", "Philosophy", "Sociology", "Linguistics"],
    "Economics": ["Business", "Mathematics", "Data Science", "Law"],
    "Business": ["Economics", "Law", "Sociology"],
    "Philosophy": ["Linguistics", "English", "History", "Sociology"],
    "Sociology": ["History", "Philosophy", "Psychology", "Business", "Linguistics"],
    "Art": ["History", "English"],
    "Biology": ["Chemistry", "Medicine", "Microbiology", "Physiology"],
    "Chemistry": ["Biology", "Medicine", "Microbiology"],
    "Psychology": ["Sociology", "Medicine", "Philosophy"],
    "Law": ["Economics", "Business"],
    "Medicine": ["Nursing", "Biology", "Physiology", "Chemistry", "Psychology"],
    "Nursing": ["Medicine", "Psychology"]
}

# -------------------------
# Cycle Detection (DFS-based)
# -------------------------
def detect_cycle(selected_modules):
    """
    Detect cycles in the module prerequisites graph using DFS.
    Returns a list representing the cycle if found, None otherwise.
    """
    graph = defaultdict(list)
    for code, mod in selected_modules.items():
        for pre in mod.prerequisites:
            if pre in selected_modules:
                graph[pre].append(code)
    
    visited = set()
    rec_stack = set()
    cycle_found = None

    def dfs(node, path):
        nonlocal cycle_found
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                cycle_index = path.index(neighbor)
                cycle_found = path[cycle_index:]
                return True
        rec_stack.remove(node)
        path.pop()
        return False

    for node in selected_modules:
        if node not in visited:
            if dfs(node, []):
                break
    return cycle_found

# -------------------------
# Topological Sorting with Kahn's Algorithm & Cycle Reporting
# -------------------------
def topological_sort(selected_modules):
    graph = defaultdict(list)
    in_degree = {code: 0 for code in selected_modules}
    
    # Build the graph and calculate in-degrees
    for code, mod in selected_modules.items():
        for pre in mod.prerequisites:
            if pre in selected_modules:
                graph[pre].append(code)
                in_degree[code] += 1
    
    # Start with nodes that have no prerequisites
    queue = deque([code for code, deg in in_degree.items() if deg == 0])
    ordering = []
    
    # Process the queue
    while queue:
        node = queue.popleft()
        ordering.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check if we processed all modules
    if len(ordering) != len(selected_modules):
        # Find and report the cycle
        cycle = detect_cycle(selected_modules)
        return None, cycle
    return ordering, None

# -------------------------
# Main Application GUI
# -------------------------
class ModuleSchedulerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Module Scheduler App")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # Set a theme
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')  # Use clam if available, otherwise default
        
        # Define colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a7abc"
        self.text_color = "#333333"
        self.header_color = "#2a4d7f"
        
        # Configure styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), foreground=self.header_color)
        self.style.configure('TLabel', font=('Helvetica', 12), foreground=self.text_color)
        self.style.configure('TButton', font=('Helvetica', 12))
        
        # Load data
        self.modules_catalog = load_modules_catalog()
        self.students_data = load_students()
        
        # Current student
        self.current_student = None
        
        # Explicitly initialize the displayed_frame variable first
        self._displayed_frame = None
        
        # Set up the frames
        self.setup_frames()
        
        # Initialize with login frame
        self.show_login_frame()
        
    def setup_frames(self):
        # Main container
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        # Create frames but don't pack them yet
        self.login_frame = self.create_login_frame()
        self.main_menu_frame = self.create_main_menu_frame()
        self.completed_modules_frame = self.create_completed_modules_frame()
        self.upcoming_modules_frame = self.create_upcoming_modules_frame()
        self.module_graph_frame = self.create_module_graph_frame()
        self.progress_dashboard_frame = self.create_progress_dashboard_frame()
        self.simulation_frame = self.create_simulation_frame()
        self.search_frame = self.create_module_search_frame()
        self.eligible_modules_frame = self.create_eligible_modules_frame()
        self.credit_planner_frame = self.create_credit_planner_frame()

    def show_frame(self, frame):
        # Hide the current frame
        if hasattr(self, '_displayed_frame') and self._displayed_frame is not None:
            self._displayed_frame.pack_forget()
        
        # Show the new frame
        frame.pack(fill="both", expand=True)
        self._displayed_frame = frame
        
        # Update the frame content if needed
        if frame == self.completed_modules_frame:
            self.update_completed_modules_list()
        elif frame == self.upcoming_modules_frame:
            self.update_upcoming_modules_list()
        elif frame == self.module_graph_frame:
            self.update_module_graph()
        elif frame == self.progress_dashboard_frame:
            self.update_progress_dashboard()
        elif frame == self.eligible_modules_frame:
            self.update_eligible_modules_list()
    
    def show_login_frame(self):
        self.show_frame(self.login_frame)
    
    def show_main_menu(self):
        # Update welcome message with student info
        if self.current_student:
            welcome_text = f"Welcome {self.current_student.name}!\nCourse: {self.current_student.course}, Year: {self.current_student.year}, Semester: {self.current_student.semester}"
            self.welcome_label.config(text=welcome_text)
        self.show_frame(self.main_menu_frame)
    
    # -------------------------
    # Login Frame
    # -------------------------
    def create_login_frame(self):
        frame = ttk.Frame(self.container)
        
        # Create a header
        header = ttk.Label(frame, text="Student Module Scheduler", style='Header.TLabel')
        header.pack(pady=(20, 40))
        
        # Login form
        login_container = ttk.Frame(frame)
        login_container.pack(pady=20)
        
        ttk.Label(login_container, text="Enter your 6-digit student ID:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.student_id_entry = ttk.Entry(login_container, width=20)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Login button
        login_btn = ttk.Button(login_container, text="Login", command=self.login)
        login_btn.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Demo accounts info
        ttk.Label(frame, text="Demo student IDs for testing:").pack(pady=(40, 5))
        # Create scrolled text for displaying all IDs
        id_display = scrolledtext.ScrolledText(frame, height=10, width=50)
        id_display.pack(padx=10, pady=5)

        # Insert all the IDs
        for s in self.students_data:
            id_display.insert(tk.END, f"{s['student_id']}: {s['name']} ({s['course']})\n")

        # Make it read-only
        id_display.config(state=tk.DISABLED)
        
        return frame
        
    def login(self):
        student_id = self.student_id_entry.get().strip()
        
        if not (student_id.isdigit() and len(student_id) == 6):
            messagebox.showerror("Invalid ID", "Please enter a valid 6-digit student ID.")
            return
        
        student_info = next((s for s in self.students_data if s["student_id"] == student_id), None)
        if not student_info:
            messagebox.showerror("Not Found", "Student not found. Please try again.")
            return
        
        # Create student object
        student = Student(
            student_id=student_info["student_id"],
            name=student_info["name"],
            course=student_info["course"],
            year=student_info["year"],
            semester=student_info["semester"],
            completed=student_info.get("completed", [])
        )
        
        # Load completed modules
        for mod_code in student_info.get("completed", []):
            if mod_code in self.modules_catalog:
                student.completed[mod_code] = self.modules_catalog[mod_code]
        
        self.current_student = student
        self.show_main_menu()
    
    # -------------------------
    # Main Menu Frame
    # -------------------------
    def create_main_menu_frame(self):
        frame = ttk.Frame(self.container)
        
        # Welcome header
        self.welcome_label = ttk.Label(frame, text="Welcome!", style='Header.TLabel')
        self.welcome_label.pack(pady=(20, 40))
        
        # Reminder notification
        reminder = ttk.Label(frame, text="Reminder: Registration deadlines are approaching soon!", 
                           foreground="red", font=('Helvetica', 12, 'italic'))
        reminder.pack(pady=(0, 30))
        
        # Menu buttons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill="both", expand=True)
        
        # Define the menu options
        menu_options = [
            ("View Completed Modules", lambda: self.show_frame(self.completed_modules_frame)),
            ("View Upcoming Core Modules", lambda: self.show_frame(self.upcoming_modules_frame)),
            ("View Module Dependency Graph", lambda: self.show_frame(self.module_graph_frame)),
            ("View Progress Dashboard", lambda: self.show_frame(self.progress_dashboard_frame)),
            ("Simulate Course Path", lambda: self.show_frame(self.simulation_frame)),
            ("Credit Semester Planner", lambda: self.show_frame(self.credit_planner_frame)),
            ("Search for Modules", lambda: self.show_frame(self.search_frame)),
            ("Search for Eligible Modules", lambda: self.show_frame(self.eligible_modules_frame)),
            ("Logout", self.logout)
        ]
        
        # Create the buttons in a grid
        for i, (text, command) in enumerate(menu_options):
            row, col = divmod(i, 2)
            button = ttk.Button(buttons_frame, text=text, command=command, width=25)
            button.grid(row=row, column=col, padx=20, pady=15, sticky="nsew")
        
        # Configure the grid
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        return frame
    
    def logout(self):
        self.current_student = None
        self.student_id_entry.delete(0, tk.END)
        self.show_login_frame()
    
    # -------------------------
    # Completed Modules Frame
    # -------------------------
    def create_completed_modules_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Completed Modules", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for displaying modules
        self.completed_modules_tree = ttk.Treeview(
            tree_frame, 
            columns=("Code", "Name", "Track", "Credits"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.completed_modules_tree.heading("Code", text="Module Code")
        self.completed_modules_tree.heading("Name", text="Module Name")
        self.completed_modules_tree.heading("Track", text="Tracks")
        self.completed_modules_tree.heading("Credits", text="Credits")
        
        # Set column widths
        self.completed_modules_tree.column("Code", width=100, anchor=tk.CENTER)
        self.completed_modules_tree.column("Name", width=250)
        self.completed_modules_tree.column("Track", width=250)
        self.completed_modules_tree.column("Credits", width=70, anchor=tk.CENTER)
        
        self.completed_modules_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.completed_modules_tree.yview)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame
    
    def update_completed_modules_list(self):
        # Clear existing items
        for item in self.completed_modules_tree.get_children():
            self.completed_modules_tree.delete(item)
        
        # Add completed modules to the treeview
        if self.current_student and self.current_student.completed:
            total_credits = 0
            for code, mod in self.current_student.completed.items():
                tracks_str = ", ".join(mod.tracks)
                self.completed_modules_tree.insert("", "end", values=(code, mod.name, tracks_str, f"{mod.credits}"))
                total_credits += mod.credits
                
            # Add a total credits row
            self.completed_modules_tree.insert("", "end", values=("", "TOTAL CREDITS", "", f"{total_credits}"))
        else:
            self.completed_modules_tree.insert("", "end", values=("", "No completed modules found", "", ""))
        
    # -------------------------
    # Upcoming Modules Frame
    # -------------------------
    def create_upcoming_modules_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Upcoming Core Modules", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Subheader explaining topological sort
        subheader = ttk.Label(frame, text="Modules are ordered using topological sorting algorithm")
        subheader.pack(pady=(0, 20))
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for displaying modules
        self.upcoming_modules_tree = ttk.Treeview(
            tree_frame, 
            columns=("Order", "Code", "Name", "Prerequisites"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.upcoming_modules_tree.heading("Order", text="Order")
        self.upcoming_modules_tree.heading("Code", text="Module Code")
        self.upcoming_modules_tree.heading("Name", text="Module Name")
        self.upcoming_modules_tree.heading("Prerequisites", text="Prerequisites")
        
        # Set column widths
        self.upcoming_modules_tree.column("Order", width=50, anchor=tk.CENTER)
        self.upcoming_modules_tree.column("Code", width=100, anchor=tk.CENTER)
        self.upcoming_modules_tree.column("Name", width=250)
        self.upcoming_modules_tree.column("Prerequisites", width=300)
        
        self.upcoming_modules_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.upcoming_modules_tree.yview)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame
    
    def update_completed_modules_list(self):
        # Clear existing items
        for item in self.completed_modules_tree.get_children():
            self.completed_modules_tree.delete(item)
        
        # Add completed modules to the treeview
        if self.current_student and self.current_student.completed:
            for code, mod in self.current_student.completed.items():
                tracks_str = ", ".join(mod.tracks)
                self.completed_modules_tree.insert("", "end", values=(code, mod.name, tracks_str))
        else:
            self.completed_modules_tree.insert("", "end", values=("", "No completed modules found", ""))
    
    # -------------------------
    # Upcoming Modules Frame
    # -------------------------
    def create_upcoming_modules_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Upcoming Core Modules", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Subheader explaining topological sort
        subheader = ttk.Label(frame, text="Modules are ordered using topological sorting algorithm")
        subheader.pack(pady=(0, 20))
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for displaying modules
        self.upcoming_modules_tree = ttk.Treeview(
            tree_frame, 
            columns=("Order", "Code", "Name", "Prerequisites"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.upcoming_modules_tree.heading("Order", text="Order")
        self.upcoming_modules_tree.heading("Code", text="Module Code")
        self.upcoming_modules_tree.heading("Name", text="Module Name")
        self.upcoming_modules_tree.heading("Prerequisites", text="Prerequisites")
        
        # Set column widths
        self.upcoming_modules_tree.column("Order", width=50, anchor=tk.CENTER)
        self.upcoming_modules_tree.column("Code", width=100, anchor=tk.CENTER)
        self.upcoming_modules_tree.column("Name", width=250)
        self.upcoming_modules_tree.column("Prerequisites", width=300)
        
        self.upcoming_modules_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.upcoming_modules_tree.yview)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame
    
    def update_upcoming_modules_list(self):
        # Clear existing items
        for item in self.upcoming_modules_tree.get_children():
            self.upcoming_modules_tree.delete(item)
        
        if not self.current_student:
            return
        
        # Get all core modules for this course
        core_modules_dict = self.get_core_modules_for_course(self.current_student.course)
        if not core_modules_dict:
            self.upcoming_modules_tree.insert("", "end", values=("", "", "No core modules found for this course", ""))
            return
        
        # Filter out completed modules and create a dictionary of eligible modules
        eligible_modules = {}
        for code, mod in core_modules_dict.items():
            if code not in self.current_student.completed:
                if all(pre in self.current_student.completed for pre in mod.prerequisites):
                    eligible_modules[code] = mod
        
        if not eligible_modules:
            self.upcoming_modules_tree.insert("", "end", values=("", "", "No eligible modules found. Check prerequisites.", ""))
            return
        
        # Get the topological sort order
        topo_order, cycle = topological_sort(eligible_modules)
        
        if cycle:
            # If a cycle was detected
            self.upcoming_modules_tree.insert("", "end", values=("", "", f"Error: Cycle detected in prerequisites: {' -> '.join(cycle)}", ""))
            return
        
        # Add modules in topological order
        for i, code in enumerate(topo_order, start=1):
            mod = eligible_modules[code]
            prereqs = ", ".join(mod.prerequisites) if mod.prerequisites else "None"
            self.upcoming_modules_tree.insert("", "end", values=(i, code, mod.name, prereqs))
    
    def get_core_modules_for_course(self, course):
        """Get all core modules for a specific course from the catalog"""
        # For this demo version, we'll consider all modules that have the course in their tracks
        core_modules_dict = {}
        for code, mod in self.modules_catalog.items():
            if course in mod.tracks:
                core_modules_dict[code] = mod
        return core_modules_dict
    
    # -------------------------
    # Module Graph Frame 
    # -------------------------
    def update_module_graph(self):
    # Clear existing content
        for widget in self.graph_container.winfo_children():
            widget.destroy()
        
        if not self.current_student:
            return
        
        # Get modules for this course
        course_modules = self.get_core_modules_for_course(self.current_student.course)
        if not course_modules:
            msg_label = ttk.Label(self.graph_container, text="No modules found for this course")
            msg_label.pack(pady=50)
            return
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Get completed modules for coloring
        completed_modules = set(self.current_student.completed.keys())
        
        # Filter modules based on selection
        filter_type = self.graph_filter_var.get()
        filtered_modules = {}
        
        if filter_type == "next":
            # Find modules that student has completed or can take next
            for code, mod in course_modules.items():
                if code in completed_modules:
                    filtered_modules[code] = mod
                elif all(pre in completed_modules for pre in mod.prerequisites):
                    filtered_modules[code] = mod
            
            # Add one level of upcoming modules to show future path
            next_level = {}
            for code, mod in course_modules.items():
                if code not in filtered_modules and not code in completed_modules:
                    if any(pre in filtered_modules and pre not in completed_modules for pre in mod.prerequisites):
                        next_level[code] = mod
            
            # Combine both sets
            filtered_modules.update(next_level)
            
        elif filter_type == "eligible":
            # Only show modules the student can take now (all prerequisites completed)
            for code, mod in course_modules.items():
                if code not in completed_modules and all(pre in completed_modules for pre in mod.prerequisites):
                    filtered_modules[code] = mod
                    # Also include completed prerequisites for context
                    for pre in mod.prerequisites:
                        if pre in course_modules:
                            filtered_modules[pre] = course_modules[pre]
        else:
            # "all" option - use all course modules
            filtered_modules = course_modules
        
        # Make sure we have modules to display
        if not filtered_modules:
            msg_label = ttk.Label(self.graph_container, text="No modules to display with current filter")
            msg_label.pack(pady=50)
            return
        
        # Add nodes and edges for the filtered modules
        for code, mod in filtered_modules.items():
            # Add the node
            G.add_node(code, label=mod.name)
            
            # Add edges for prerequisites (only if both modules are in filtered set)
            for pre in mod.prerequisites:
                if pre in filtered_modules:
                    G.add_edge(pre, code)
        
        # Check if graph has any nodes
        if not G.nodes():
            msg_label = ttk.Label(self.graph_container, text="No dependencies to visualize with current filter")
            msg_label.pack(pady=50)
            return
        
        # Get topological sorting if possible (use filtered modules)
        topo_order, cycle = topological_sort(filtered_modules)
        
        if cycle:
            # Cycle detected, display the graph but warn the user
            fig = plt.figure(figsize=(8, 6))
            fig.suptitle("Module Dependency Graph (Cycle Detected)", fontsize=14)
            
            # Draw the graph
            pos = nx.spring_layout(G, seed=42)
            nx.draw(G, pos, with_labels=True, labels={node: node for node in G.nodes()},
                node_color=["green" if n in completed_modules else "skyblue" for n in G.nodes()],
                node_size=1000, font_size=8, font_weight="bold", arrows=True)
            
            # Display the graph in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            warning_label = ttk.Label(self.graph_container, 
                                text="Warning: Cycle detected in module dependencies. Topological ordering not possible.",
                                foreground="red")
            warning_label.pack(pady=10)
            return
        
        # Create figure with smaller size that fits better
        fig = plt.figure(figsize=(8, 6))
        fig.suptitle(f"Core Module Dependency Graph: {self.current_student.course}", fontsize=14)
        
        # Draw the graph with better spacing
        pos = nx.spring_layout(G, seed=42, k=1.5)  # Increase k for more spacing
        nx.draw(G, pos, with_labels=True, labels={node: node for node in G.nodes()},
            node_color=["green" if n in completed_modules else "skyblue" for n in G.nodes()],
            node_size=800, font_size=8, font_weight="bold", arrows=True)
        
        # Add order numbers and module names with adjusted positioning
        if topo_order:
            for i, code in enumerate(topo_order):
                if code in G.nodes():  # Only add if the node is in our filtered graph
                    x, y = pos[code]
                    plt.text(x, y + 0.07, f'{i+1}', fontsize=8, ha="center", color="red")
                    # Shorten module names to prevent overlap
                    short_name = filtered_modules[code].name[:15] + "..." if len(filtered_modules[code].name) > 15 else filtered_modules[code].name
                    plt.text(x, y - 0.07, short_name, fontsize=6, ha="center")
        
        # Add legend
        green_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Completed')
        blue_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markersize=10, label='Not Completed')
        
        plt.legend(handles=[green_patch, blue_patch], loc='upper left')
        
        # Create a tight layout to make better use of space
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout, leaving space for the title
        
        # Embed the Matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add filter info
        if filter_type == "next":
            info_text = "Showing completed modules and next available modules"
        elif filter_type == "eligible":
            info_text = "Showing only modules where all prerequisites are met"
        else:
            info_text = "Showing all course modules"
            
        info_label = ttk.Label(self.graph_container, text=info_text, font=('Helvetica', 10, 'italic'))
        info_label.pack(pady=5)
        
        

    # Make sure to update the create_module_graph_frame method to include a back button
    def create_module_graph_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Module Dependency Graph", style='Header.TLabel')
        header.pack(pady=(20, 10))

        # Add a filter option
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(filter_frame, text="Display:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.graph_filter_var = tk.StringVar(value="all")
        filter_options = [
            ("All Modules", "all"),
            ("Current + Next Semester", "next"),
            ("Eligible Modules Only", "eligible")
        ]
    
        # Create radio buttons for filtering
        for text, value in filter_options:
            ttk.Radiobutton(filter_frame, text=text, value=value, 
                       variable=self.graph_filter_var,
                       command=self.update_module_graph).pack(side=tk.LEFT, padx=10)
    
        
        # Frame for the graph
        self.graph_container = ttk.Frame(frame)
        self.graph_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Back button - MAKE SURE THIS IS INCLUDED
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=10)
        
        return frame    # -------------------------
    # Progress Dashboard Frame
    # -------------------------
    # Find this method in your code
    def create_progress_dashboard_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Progress Dashboard", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Create main content area
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Progress summary
        self.progress_frame = ttk.LabelFrame(content_frame, text="Overall Progress")
        self.progress_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Right side - Recommended modules
        self.recommended_frame = ttk.LabelFrame(content_frame, text="Recommended Modules for Next Semester")
        self.recommended_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=(10, 0), pady=10)
        
        # Create a treeview for recommended modules
        # Scrollbar for recommended modules
        scrollbar = ttk.Scrollbar(self.recommended_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.recommended_tree = ttk.Treeview(
            self.recommended_frame, 
            columns=("Order", "Code", "Name"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.recommended_tree.heading("Order", text="#")
        self.recommended_tree.heading("Code", text="Code")
        self.recommended_tree.heading("Name", text="Module Name")
        
        # Set column widths
        self.recommended_tree.column("Order", width=40, anchor=tk.CENTER)
        self.recommended_tree.column("Code", width=80, anchor=tk.CENTER)
        self.recommended_tree.column("Name", width=250)
        
        self.recommended_tree.pack(fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.recommended_tree.yview)
        
        # ADD THIS: Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame 

    def update_progress_dashboard(self):
        # Clear existing content in the frames
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        for item in self.recommended_tree.get_children():
            self.recommended_tree.delete(item)
        
        if not self.current_student:
            return
        
        # Get all modules for this course
        course_modules = self.get_core_modules_for_course(self.current_student.course)
        if not course_modules:
            ttk.Label(self.progress_frame, text="No modules found for this course").pack(pady=20)
            return
        
        # Calculate progress statistics
        total_course_modules = len(course_modules)
        completed_count = len(self.current_student.completed)
        
        # Calculate credit statistics
        total_credits = sum(mod.credits for mod in course_modules.values())
        completed_credits = sum(mod.credits for mod in self.current_student.completed.values())
        
        # Create a progress summary
        progress_summary = f"Course: {self.current_student.course}\n"
        progress_summary += f"Year: {self.current_student.year}, Semester: {self.current_student.semester}\n\n"
        progress_summary += f"Total Core Modules: {total_course_modules}\n"
        progress_summary += f"Modules Completed: {completed_count}\n"
        progress_summary += f"Remaining Modules: {total_course_modules - completed_count}\n"
        
        # Add credit information
        progress_summary += f"Total Credits Required: {total_credits}\n"
        progress_summary += f"Credits Completed: {completed_credits}\n"
        progress_summary += f"Credits Remaining: {total_credits - completed_credits}\n"
        
        if total_course_modules > 0:
            progress_percentage = (completed_count / total_course_modules) * 100
            progress_summary += f"Progress: {progress_percentage:.1f}%"
        
        # Display the summary
        summary_label = ttk.Label(self.progress_frame, text=progress_summary, justify=tk.LEFT)
        summary_label.pack(anchor=tk.W, padx=20, pady=20)
           
        # Create a simple progress bar 
        if total_course_modules > 0:
            progress_text = "Progress: ["
            filled_slots = int((completed_count / total_course_modules) * 20)
            progress_text += "■" * filled_slots
            progress_text += "□" * (20 - filled_slots)
            progress_text += f"] {progress_percentage:.1f}%"
            
            progress_bar_label = ttk.Label(self.progress_frame, text=progress_text, font=('Courier', 12))
            progress_bar_label.pack(anchor=tk.W, padx=20, pady=10)
        
        # Get recommended modules (not completed and all prerequisites met)
        recommended_modules = {}
        for code, mod in course_modules.items():
            if code not in self.current_student.completed:
                if all(pre in self.current_student.completed for pre in mod.prerequisites):
                    recommended_modules[code] = mod
        
        # Display recommended modules in topological order
        if recommended_modules:
            topo_order, cycle = topological_sort(recommended_modules)
            
            if cycle:
                self.recommended_tree.insert("", "end", values=("", "", f"Cycle detected in prerequisites"))
            else:
                for i, code in enumerate(topo_order, start=1):
                    mod = recommended_modules[code]
                    self.recommended_tree.insert("", "end", values=(i, code, mod.name))
        else:
            self.recommended_tree.insert("", "end", values=("", "", "No eligible modules found. Check prerequisites."))
    
    # -------------------------
    # Simulation Frame - What-if Analysis
    # -------------------------
    def create_simulation_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Simulate Course Path", style='Header.TLabel')
        header.pack(pady=(20, 10))
        
        # Subheader
        subheader = ttk.Label(frame, text="Enter module codes separated by commas to simulate a course path")
        subheader.pack(pady=(0, 20))
        
        # Input section
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(input_frame, text="Module Codes:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.simulation_entry = ttk.Entry(input_frame, width=50)
        self.simulation_entry.pack(side=tk.LEFT, padx=5)
        
        simulate_btn = ttk.Button(input_frame, text="Simulate", command=self.run_simulation)
        simulate_btn.pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_frame = ttk.LabelFrame(frame, text="Simulation Results")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Simulation output text area
        self.simulation_output = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.simulation_output.pack(fill="both", expand=True, padx=10, pady=10)
        self.simulation_output.config(state=tk.DISABLED)  # Make read-only
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame
    
    def run_simulation(self):
        if not self.current_student:
            return
        
        # Get the entered module codes
        module_input = self.simulation_entry.get().strip()
        if not module_input:
            messagebox.showinfo("Input Required", "Please enter module codes to simulate.")
            return
        
        # Parse the input
        module_codes = [code.strip() for code in module_input.split(",")]
        
        # Clear previous results
        self.simulation_output.config(state=tk.NORMAL)
        self.simulation_output.delete(1.0, tk.END)
        
        # Perform the simulation
        self.simulation_output.insert(tk.END, "--- Simulation Results ---\n\n")
        
        # Start with current completed modules
        simulated_completed = set(self.current_student.completed.keys())
        valid_path = True
        
        # Check each module in the path
        for code in module_codes:
            mod = self.modules_catalog.get(code)
            if not mod:
                self.simulation_output.insert(tk.END, f"❌ Module {code} not found in catalogue.\n")
                valid_path = False
                continue
            
            # Check if prerequisites are met
            missing = [pre for pre in mod.prerequisites if pre not in simulated_completed]
            if missing:
                self.simulation_output.insert(tk.END, f"❌ Cannot take {code} - missing prerequisites: {', '.join(missing)}\n")
                valid_path = False
            else:
                self.simulation_output.insert(tk.END, f"✓ {code} ({mod.name}) is eligible to be taken.\n")
                simulated_completed.add(code)
         # Calculate credits for the simulation
        total_simulation_credits = sum(self.modules_catalog[code].credits for code in module_codes if code in self.modules_catalog)
        
        # Add to simulation results
        self.simulation_output.insert(tk.END, f"\nTotal Credits: {total_simulation_credits}\n")
        
        # Suggest semester balance
        semester_suggestion = ""
        if total_simulation_credits > 20:
            semester_suggestion = "Warning: This course load may be heavy for a single semester."
        elif total_simulation_credits < 10:
            semester_suggestion = "Note: This course load is lighter than a typical semester."
        else:
            semester_suggestion = "This appears to be a well-balanced semester."
        
        self.simulation_output.insert(tk.END, semester_suggestion + "\n")

        # Overall result
        self.simulation_output.insert(tk.END, "\nSummary:\n")
        if valid_path:
            self.simulation_output.insert(tk.END, "The simulated course path is valid! You can take these modules in this order.\n")
        else:
            self.simulation_output.insert(tk.END, "The simulated course path has issues. Please review the prerequisites.\n")
        
        self.simulation_output.config(state=tk.DISABLED)
    
    def create_credit_planner_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Credit Planner", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Set target credits per semester
        planner_frame = ttk.Frame(frame)
        planner_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ttk.Label(planner_frame, text="Target credits per semester:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.target_credits_var = tk.StringVar(value="15")
        target_credits_entry = ttk.Entry(planner_frame, textvariable=self.target_credits_var, width=5)
        target_credits_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        plan_btn = ttk.Button(planner_frame, text="Generate Plan", command=self.generate_credit_plan)
        plan_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Semester Plan")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.plan_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.plan_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame

    def generate_credit_plan(self):
        if not self.current_student:
            return
        
        try:
            target_credits = int(self.target_credits_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for target credits.")
            return
        
        # Clear previous plan
        self.plan_text.config(state=tk.NORMAL)
        self.plan_text.delete(1.0, tk.END)
        
        # Get eligible modules in topological order
        remaining_modules = {}
        for code, mod in self.get_core_modules_for_course(self.current_student.course).items():
            if code not in self.current_student.completed:
                remaining_modules[code] = mod
        
        if not remaining_modules:
            self.plan_text.insert(tk.END, "You have completed all core modules!")
            self.plan_text.config(state=tk.DISABLED)
            return
        
        topo_order, cycle = topological_sort(remaining_modules)
        
        if cycle:
            self.plan_text.insert(tk.END, "Error: Cannot generate plan due to cycle in prerequisites.")
            self.plan_text.config(state=tk.DISABLED)
            return
        
        # Generate plan
        semesters = []
        current_semester = []
        current_credits = 0
        
        # Track which modules are eligible (all prerequisites satisfied)
        eligible_modules = {}
        completed_set = set(self.current_student.completed.keys())
        
        for code in topo_order:
            mod = remaining_modules[code]
            # Check if prerequisites are met
            if all(pre in completed_set for pre in mod.prerequisites):
                eligible_modules[code] = mod
        
        # Build semesters
        while eligible_modules:
            best_fit = None
            for code, mod in eligible_modules.items():
                # Find module that fits best in current semester
                if current_credits + mod.credits <= target_credits:
                    best_fit = code
                    break
            
            if best_fit:
                # Add module to current semester
                current_semester.append(best_fit)
                current_credits += eligible_modules[best_fit].credits
                completed_set.add(best_fit)
                
                # Remove from eligible and check for newly eligible modules
                del eligible_modules[best_fit]
                
                # Update eligible modules
                for code, mod in remaining_modules.items():
                    if code not in completed_set and code not in eligible_modules:
                        if all(pre in completed_set for pre in mod.prerequisites):
                            eligible_modules[code] = mod
            else:
                # Start a new semester
                if current_semester:
                    semesters.append(current_semester)
                    current_semester = []
                    current_credits = 0
                else:
                    # Impossible to fit any remaining module
                    break
        
        # Add the last semester if not empty
        if current_semester:
            semesters.append(current_semester)
        
        # Display the plan
        for i, semester in enumerate(semesters, start=1):
            self.plan_text.insert(tk.END, f"Semester {i}:\n")
            semester_credits = 0
            
            for code in semester:
                mod = remaining_modules[code]
                self.plan_text.insert(tk.END, f"  {code}: {mod.name} ({mod.credits} credits)\n")
                semester_credits += mod.credits
            
            self.plan_text.insert(tk.END, f"  Total: {semester_credits} credits\n\n")
        
        # Make read-only
        self.plan_text.config(state=tk.DISABLED)
        
        # -------------------------
        # Search Frame
        # -------------------------
    def create_module_search_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Module Search", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Search section
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(search_frame, text="Search by code or name:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_modules)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Results section
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for search results
        self.search_results_tree = ttk.Treeview(
            results_frame, 
            columns=("Code", "Name", "Tracks", "Prerequisites"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.search_results_tree.heading("Code", text="Module Code")
        self.search_results_tree.heading("Name", text="Module Name")
        self.search_results_tree.heading("Tracks", text="Tracks")
        self.search_results_tree.heading("Prerequisites", text="Prerequisites")
        
        # Set column widths
        self.search_results_tree.column("Code", width=80, anchor=tk.CENTER)
        self.search_results_tree.column("Name", width=200)
        self.search_results_tree.column("Tracks", width=200)
        self.search_results_tree.column("Prerequisites", width=200)
        
        self.search_results_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.search_results_tree.yview)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame
        
    def search_modules(self):
        # Get search query
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showinfo("Input Required", "Please enter a search term.")
            return
        
        # Clear previous results
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        # Perform search
        results = []
        for code, mod in self.modules_catalog.items():
            if query in code.lower() or query in mod.name.lower():
                results.append(mod)
        
        # Display results
        if results:
            for mod in results:
                tracks_str = ", ".join(mod.tracks)
                prereqs_str = ", ".join(mod.prerequisites) if mod.prerequisites else "None"
                self.search_results_tree.insert("", "end", values=(mod.code, mod.name, tracks_str, prereqs_str))
        else:
            self.search_results_tree.insert("", "end", values=("", "No modules found matching the query", "", ""))

    # -------------------------
    # Eligible Modules Frame
    # -------------------------
    def create_eligible_modules_frame(self):
        frame = ttk.Frame(self.container)
        
        # Header
        header = ttk.Label(frame, text="Eligible Modules for Your Course", style='Header.TLabel')
        header.pack(pady=(20, 20))
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview for displaying modules
        self.eligible_modules_tree = ttk.Treeview(
            tree_frame, 
            columns=("Code", "Name", "Tracks"),
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Set column headings
        self.eligible_modules_tree.heading("Code", text="Module Code")
        self.eligible_modules_tree.heading("Name", text="Module Name")
        self.eligible_modules_tree.heading("Tracks", text="Tracks")
        
        # Set column widths
        self.eligible_modules_tree.column("Code", width=100, anchor=tk.CENTER)
        self.eligible_modules_tree.column("Name", width=300)
        self.eligible_modules_tree.column("Tracks", width=300)
        
        self.eligible_modules_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Connect scrollbar to treeview
        scrollbar.config(command=self.eligible_modules_tree.yview)
        
        # Back button
        back_btn = ttk.Button(frame, text="Back to Menu", command=self.show_main_menu)
        back_btn.pack(pady=20)
        
        return frame

    def update_eligible_modules_list(self):
        # Clear existing items
        for item in self.eligible_modules_tree.get_children():
            self.eligible_modules_tree.delete(item)
        
        if not self.current_student:
            return
        
        # A module is eligible if it's in the student's course or any related course
        # and all prerequisites are met
        eligible = []
        related = related_courses.get(self.current_student.course, [])
        
        for code, mod in self.modules_catalog.items():
            if self.current_student.course in mod.tracks or any(r in mod.tracks for r in related):
                if code in self.current_student.completed:
                    continue
                if all(pre in self.current_student.completed for pre in mod.prerequisites):
                    eligible.append(mod)
        
        # Display eligible modules
        if eligible:
            for mod in eligible:
                tracks_str = ", ".join(mod.tracks)
                self.eligible_modules_tree.insert("", "end", values=(mod.code, mod.name, tracks_str))
        else:
            self.eligible_modules_tree.insert("", "end", values=("", "No eligible modules found. Check if prerequisites are met.", ""))

    # -------------------------
    # Main Application Entry Point
    # -------------------------
def main():
    app = ModuleSchedulerApp()    
    app.mainloop()

if __name__ == "__main__":
        main()