import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import threading

class ModernPDFProcessor:
    def __init__(self):
        self.selected_files = []
        self.is_processing = False
        self.setup_ui()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Eksporter danych z faktur do Excela")
        self.root.geometry("700x700")
        self.root.configure(bg="#1e1e1e")
        
        # Configure modern dark theme
        self.setup_styles()
        
        # Main container
        self.main_container = tk.Frame(self.root, bg="#1e1e1e")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        self.create_header()
        self.create_file_section()
        self.create_action_section()
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure dark theme styles
        style.configure('Dark.TFrame', background="#1e1e1e")
        style.configure('Dark.TLabel', background="#1e1e1e", foreground="#ffffff", font=('Segoe UI', 10))
        style.configure('Title.TLabel', background="#1e1e1e", foreground="#ffffff", font=('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel', background="#1e1e1e", foreground="#cccccc", font=('Segoe UI', 11))
        
        # Modern button styles
        style.configure('Primary.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 10))
        style.configure('Secondary.TButton', 
                       font=('Segoe UI', 10),
                       padding=(15, 8))
        
    def create_header(self):
        header_frame = tk.Frame(self.main_container, bg="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 40))
        
        title = tk.Label(header_frame, text="Eksportuj dane z faktur do Excela", 
                        bg="#1e1e1e", fg="#ffffff", 
                        font=('Segoe UI', 24, 'bold'))
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Pamiętaj, że aplikacja przetwarza tylko pliki PDF", 
                           bg="#1e1e1e", fg="#cccccc", 
                           font=('Segoe UI', 11))
        subtitle.pack(pady=(5, 0))
        
    def create_file_section(self):
        # File selection card
        file_card = tk.Frame(self.main_container, bg="#2d2d2d", relief="flat", bd=1)
        file_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Card header
        card_header = tk.Frame(file_card, bg="#2d2d2d")
        card_header.pack(fill="x", padx=25, pady=(20, 0))
        
        tk.Label(card_header, text="📁 Wybór plików", 
                bg="#2d2d2d", fg="#ffffff", 
                font=('Segoe UI', 14, 'bold')).pack(anchor="w")
        
        # Select button
        select_btn = tk.Button(file_card, text="Wybierz pliki PDF", 
                              command=self.select_pdfs,
                              bg="#0078d4", fg="white", 
                              font=('Segoe UI', 11, 'bold'),
                              relief="flat", cursor="hand2",
                              padx=20, pady=10)
        select_btn.pack(pady=20)
        
        # File list
        list_container = tk.Frame(file_card, bg="#2d2d2d")
        list_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        tk.Label(list_container, text="Wybrane pliki (kliknij dwukrotnie aby usunąć):", 
                bg="#2d2d2d", fg="#cccccc", 
                font=('Segoe UI', 10)).pack(anchor="w", pady=(0, 5))
        
        list_frame = tk.Frame(list_container, bg="#1e1e1e")
        list_frame.pack(fill="both", expand=True)
        
        self.file_list = tk.Listbox(list_frame, 
                                   bg="#1e1e1e", fg="#ffffff",
                                   selectbackground="#0078d4",
                                   font=('Segoe UI', 9),
                                   relief="flat", bd=0)
        scrollbar = tk.Scrollbar(list_frame, bg="#2d2d2d")
        
        self.file_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.file_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.file_list.yview)

        self.file_list.bind("<Double-Button-1>", self.on_file_double_click)
        
    def on_file_double_click(self, event):
        """Handle double-click on file list item to remove it"""
        if self.is_processing:
            return
            
        selection = self.file_list.curselection()
        if selection:
            index = selection[0]
            # Remove from both the visual list and the selected_files list
            self.file_list.delete(index)
            if index < len(self.selected_files):
                self.selected_files.pop(index)
            self.update_process_button()


    def create_action_section(self):
        action_frame = tk.Frame(self.main_container, bg="#1e1e1e")
        action_frame.pack(fill="x")
        
        # Status and progress container
        self.status_container = tk.Frame(action_frame, bg="#1e1e1e")
        
        # Status label
        self.status_label = tk.Label(self.status_container, text="", 
                                    bg="#1e1e1e", fg="#cccccc", 
                                    font=('Segoe UI', 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.status_container, mode='indeterminate')
        
        # Buttons
        button_container = tk.Frame(action_frame, bg="#1e1e1e")
        button_container.pack(pady=10)
        
        self.clear_btn = tk.Button(button_container, text="Wyczyść Listę", 
                                  command=self.clear_files,
                                  bg="#404040", fg="white", 
                                  font=('Segoe UI', 10),
                                  relief="flat", cursor="hand2",
                                  padx=15, pady=8)
        self.clear_btn.pack(side="left", padx=(0, 10))
        
        self.process_btn = tk.Button(button_container, text="⚡ Przetwórz PDF'y", 
                                    command=self.process_pdfs,
                                    bg="#107c10", fg="white", 
                                    font=('Segoe UI', 11, 'bold'),
                                    relief="flat", cursor="hand2",
                                    padx=20, pady=10, state="disabled")
        self.process_btn.pack(side="left")
        
    def select_pdfs(self):
        if self.is_processing:
            return
            
        files = filedialog.askopenfilenames(
            title="Wybierz pliki PDF",
            filetypes=[("Pliki PDF", "*.pdf")]
        )
        if files:
            self.file_list.delete(0, tk.END)
            self.selected_files.clear()
            for file in files:
                self.file_list.insert(tk.END, os.path.basename(file))
            self.selected_files.extend(files)
            self.update_process_button()
            
    def update_process_button(self):
        if self.selected_files and not self.is_processing:
            self.process_btn.config(state="normal", bg="#107c10")
        else:
            self.process_btn.config(state="disabled", bg="#404040")
            
    def show_processing_state(self):
        self.is_processing = True
        self.status_container.pack(fill="x", pady=(0, 10))
        self.status_label.config(text="🤖 Odczytywanie, przetwarzanie oraz eksportowanie danych...")
        self.status_label.pack(pady=(0, 5))
        self.progress.pack(fill="x")
        self.progress.start()
        
        # Update button text and disable it
        self.process_btn.config(text="⏳ Przetwarzanie...", state="disabled", bg="#404040")
        self.clear_btn.config(state="disabled", bg="#2d2d2d")
        
        self.root.update()
        
    def hide_processing_state(self):
        self.is_processing = False
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.pack_forget()
        self.status_container.pack_forget()
        
        # Reset button text and state
        self.process_btn.config(text="⚡ Eksportuj PDF'y")
        self.clear_btn.config(state="normal", bg="#404040")
        self.update_process_button()
        
    def process_pdfs_thread(self):
        """Run the actual processing in a separate thread"""
        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
            main_script = os.path.join(app_dir, "main.py")
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.dirname(__file__))
            main_script = os.path.join(app_dir, "main.py")
        
        command = ["python3", main_script] + self.selected_files
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=app_dir)
            # Schedule UI updates on main thread
            self.root.after(0, lambda: self.processing_success(result.stdout))
        except subprocess.CalledProcessError as e:
            # Schedule UI updates on main thread
            self.root.after(0, lambda: self.processing_error(e.stderr))
            
    def processing_success(self, output):
        self.hide_processing_state()
        messagebox.showinfo("Success", output)
        self.clear_files()
        
    def processing_error(self, error):
        self.hide_processing_state()
        messagebox.showerror("Error", error)
            
    def process_pdfs(self):
        if not self.selected_files or self.is_processing:
            return
            
        self.show_processing_state()
        
        # Run processing in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.process_pdfs_thread, daemon=True)
        thread.start()
                
    def clear_files(self):
        if self.is_processing:
            return
            
        self.selected_files.clear()
        self.file_list.delete(0, tk.END)
        self.update_process_button()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernPDFProcessor()
    app.run()