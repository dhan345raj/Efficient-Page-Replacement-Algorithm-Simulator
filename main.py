import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import deque, OrderedDict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tip_window, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Algorithm Simulator")
        self.current_result = None
        self.page_sequence = []
        self.num_frames = 0
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=3)
        main_frame.columnconfigure(0, weight=1)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Simulation Parameters")
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Page Sequence Input
        ttk.Label(input_frame, text="Page Sequence:").grid(row=0, column=0, sticky="w")
        self.page_entry = ttk.Entry(input_frame, width=40)
        self.page_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # File Buttons
        file_btn_frame = ttk.Frame(input_frame)
        file_btn_frame.grid(row=0, column=2, padx=5)
        ttk.Button(file_btn_frame, text="Load", command=self.load_from_file).pack(side=tk.LEFT)
        ttk.Button(file_btn_frame, text="Save", command=self.save_results).pack(side=tk.LEFT, padx=5)

        # Frame Count Input
        ttk.Label(input_frame, text="Number of Frames:").grid(row=1, column=0, sticky="w")
        self.frame_entry = ttk.Entry(input_frame, width=10)
        self.frame_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Algorithm Selection
        ttk.Label(input_frame, text="Algorithm:").grid(row=2, column=0, sticky="w")
        self.algorithm_var = tk.StringVar()
        algorithms = ["FIFO", "LRU", "Clock"]
        self.algorithm_menu = ttk.Combobox(input_frame, textvariable=self.algorithm_var, values=algorithms)
        self.algorithm_menu.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.algorithm_menu.current(0)

        # Control Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=5)
        ttk.Button(btn_frame, text="Run", command=self.run_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Compare All", command=self.compare_algorithms).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Performance Graph", command=self.show_performance_graph).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_inputs).pack(side=tk.LEFT, padx=2)

        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Simulation Results")
        results_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # Results Table
        self.tree = ttk.Treeview(results_frame, columns=("Step", "Page", "Frames", "Fault"), 
                               show="headings", height=8)
        self.tree_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.column("Step", width=80, anchor=tk.CENTER)
        self.tree.column("Page", width=80, anchor=tk.CENTER)
        self.tree.column("Frames", width=200, anchor=tk.CENTER)
        self.tree.column("Fault", width=100, anchor=tk.CENTER)
        
        for col in ["Step", "Page", "Frames", "Fault"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80 if col != "Frames" else 150, anchor=tk.CENTER)
            self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.tag_configure('fault', background='#ffcccc')

        # Statistics
        self.stats_label = ttk.Label(results_frame, text="", font=('Arial', 10, 'bold'))
        self.stats_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Add tooltips
        ToolTip(self.page_entry, "Enter comma-separated page numbers\nExample: 1,2,3,4,1,2")
        ToolTip(self.frame_entry, "Enter number of available frames\nMust be a positive integer")
        ToolTip(self.algorithm_menu, "Select page replacement algorithm to simulate")

    def validate_inputs(self):
        try:
            pages = self.page_entry.get().strip()
            if not pages:
                raise ValueError("Please enter page sequence")
            self.page_sequence = [int(p.strip()) for p in pages.split(',') if p.strip()]
            
            self.num_frames = int(self.frame_entry.get())
            if self.num_frames <= 0:
                raise ValueError("Frame count must be ≥ 1")
            return True
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input:\n{str(e)}")
            return False

    def run_simulation(self):
        if not self.validate_inputs():
            return

        algo = self.algorithm_var.get()
        result = getattr(self, algo.lower())()
        self.display_results(result, algo)
        self.current_result = result

    def compare_algorithms(self):
        if not self.validate_inputs():
            return

        results = {}
        for algo in ["FIFO", "LRU", "Clock"]:
            results[algo] = getattr(self, algo.lower())()
        self.plot_comparison(results)

    def fifo(self):
        frames = []
        queue = deque()
        faults = 0
        result = []

        for idx, page in enumerate(self.page_sequence):
            fault = False
            if page not in frames:
                fault = True
                faults += 1
                if len(frames) >= self.num_frames:
                    removed = queue.popleft()
                    frames.remove(removed)
                frames.append(page)
                queue.append(page)
            result.append(self.create_step(idx+1, page, frames.copy(), fault))
        return {"data": result, "faults": faults}

    def lru(self):
        frames = OrderedDict()
        faults = 0
        result = []

        for idx, page in enumerate(self.page_sequence):
            fault = False
            if page not in frames:
                fault = True
                faults += 1
                if len(frames) >= self.num_frames:
                    frames.popitem(last=False)
                frames[page] = None
            else:
                frames.move_to_end(page)
            result.append(self.create_step(idx+1, page, list(frames.keys()), fault))
        return {"data": result, "faults": faults}

    def clock(self):
        frames = [None] * self.num_frames
        ref_bits = [0] * self.num_frames
        ptr = 0
        faults = 0
        result = []

        for idx, page in enumerate(self.page_sequence):
            fault = False
            if page in frames:
                ref_bits[frames.index(page)] = 1
            else:
                fault = True
                faults += 1
                while True:
                    if ref_bits[ptr] == 0:
                        frames[ptr] = page
                        ref_bits[ptr] = 1
                        ptr = (ptr + 1) % self.num_frames
                        break
                    else:
                        ref_bits[ptr] = 0
                        ptr = (ptr + 1) % self.num_frames
            result.append(self.create_step(idx+1, page, [p for p in frames if p is not None], fault))
        return {"data": result, "faults": faults}
        def create_step(self, step, page, frames, fault):
        return {
            "step": step,
            "page": page,
            "frames": frames + [''] * (self.num_frames - len(frames)),
            "fault": "Yes" if fault else "No"
        }

    def display_results(self, result, algorithm):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for entry in result["data"]:
            tags = ('fault',) if entry["fault"] == "Yes" else ()
            self.tree.insert("", "end", values=(
                entry["step"],
                entry["page"],
                " | ".join(map(str, entry["frames"])),
                entry["fault"]
            ), tags=tags)
        
        total = len(self.page_sequence)
        stats = (f"{algorithm} - Page Faults: {result['faults']}/{total} | "
                f"Hit Ratio: {(total - result['faults'])/total:.1%}")
        self.stats_label.config(text=stats, font=('Arial', 12, 'bold'))
        self.current_result = result

    def show_performance_graph(self):
        if not self.current_result:
            messagebox.showwarning("No Data", "Please run a simulation first!")
            return

        fig = plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        cumulative_faults = []
        current_faults = 0
        for entry in self.current_result["data"]:
            if entry['fault'] == "Yes":
                current_faults += 1
            cumulative_faults.append(current_faults)
        
        ax.plot(range(1, len(self.current_result["data"])+1), cumulative_faults, 
               marker='o', markersize=5, linestyle='-', linewidth=1.5, color='#2196F3')
        ax.set_title("Page Faults Over Time", fontsize=14)
        ax.set_xlabel("Step Number", fontsize=12)
        ax.set_ylabel("Cumulative Page Faults", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Performance Graph")
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_comparison(self, results):
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        algos = list(results.keys())
        faults = [results[a]['faults'] for a in algos]
        
        bars = ax.bar(algos, faults, color=['#4CAF50', '#2196F3', '#FF9800'])
        ax.set_title("Algorithm Comparison", fontsize=16, pad=20)
        ax.set_ylabel("Page Faults", fontsize=14)
        ax.tick_params(axis='both', labelsize=12)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}', ha='center', va='bottom', fontsize=12)
        
        top = tk.Toplevel()
        top.title("Algorithm Comparison")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_from_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'r') as f:
                content = f.read().strip().replace('\n', ',')
                self.page_entry.delete(0, tk.END)
                self.page_entry.insert(0, content)

    def save_results(self):
        if not self.current_result:
            messagebox.showwarning("Save Error", "No results to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.stats_label.cget('text') + "\n\n")
                    f.write(f"{'Step':<5} | {'Page':<5} | {'Frames':<20} | {'Fault'}\n")
                    f.write("-"*50 + "\n")
                    
                    for item in self.tree.get_children():
                        values = self.tree.item(item, 'values')
                        f.write(f"{values[0]:<5} | {values[1]:<5} | {values[2]:<20} | {values[3]}\n")
                
                messagebox.showinfo("Save Successful", "Results saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving file: {str(e)}")

    def clear_inputs(self):
        self.page_entry.delete(0, tk.END)
        self.frame_entry.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.stats_label.config(text="")
        self.current_result = None

if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()
