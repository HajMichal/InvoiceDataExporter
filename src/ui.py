import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import datetime

from src.core.get_eur_to_pln_rate import get_eur_to_pln_rate_fallback
from src.core.ocr import extract_text_from_file
from src.core.ai_processor import gather_specific_data
from src.core.excel_exporter import export_to_excel

class ModernPDFProcessor:
    def __init__(self):
        self.selected_files = []
        self.is_processing = False
        self.current_rate = None
        self.setup_ui()
        self.fetch_current_rate()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Eksporter danych z faktur do Excela")
        self.root.geometry("800x1000")
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
        
        subtitle = tk.Label(header_frame, text="Pamiętaj, że aplikacja przetwarza tylko pliki PDF i TIFF", 
                           bg="#1e1e1e", fg="#cccccc", 
                           font=('Segoe UI', 11))
        subtitle.pack(pady=(5, 0))
    
    def fetch_current_rate(self):
        """Fetch current EUR/PLN rate in background"""
        def fetch_rate():
            try:
                rate = get_eur_to_pln_rate_fallback()
                self.current_rate = rate
                # Update UI on main thread - THIS is where update_rate_display gets called
                self.root.after(0, lambda: self.update_rate_display(rate))
            except Exception as e:
                print(f"Error fetching rate: {e}")
                self.current_rate = 4.8
                self.root.after(0, lambda: self.update_rate_display(4.8))
        
        # Run in background thread
        threading.Thread(target=fetch_rate, daemon=True).start()

    def update_rate_display(self, rate):
        """Update the rate display with current rate"""
        if hasattr(self, 'rate_display'):
            self.rate_display.config(text=f"{rate:.4f} PLN")
            
            # Update the info label
            if hasattr(self, 'rate_info_label'):
                current_time = datetime.datetime.now().strftime("%H:%M")
                self.rate_info_label.config(
                    text=f"Kurs z NBP (Narodowy Bank Polski) - ostatnia aktualizacja: {current_time}"
                )

    def refresh_exchange_rate(self):
        """Manually refresh the exchange rate"""
        if hasattr(self, 'rate_display'):
            self.rate_display.config(text="Ładowanie...")
        if hasattr(self, 'rate_info_label'):
            self.rate_info_label.config(text="Pobieranie aktualnego kursu...")
        self.fetch_current_rate()

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
        select_btn = tk.Button(file_card, text="Wybierz pliki PDF lub TIF", 
                              command=self.select_files,
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

        # Exchange rate display section (read-only)
        rate_card = tk.Frame(action_frame, bg="#2d2d2d", relief="flat", bd=1)
        rate_card.pack(fill="x", pady=(0, 20))
        
        rate_header = tk.Frame(rate_card, bg="#2d2d2d")
        rate_header.pack(fill="x", padx=25, pady=(15, 0))
        
        tk.Label(rate_header, text="💱 Aktualny kurs EUR → PLN", 
                bg="#2d2d2d", fg="#ffffff", 
                font=('Segoe UI', 12, 'bold')).pack(anchor="w")
        
        rate_content = tk.Frame(rate_card, bg="#2d2d2d")
        rate_content.pack(fill="x", padx=25, pady=(10, 15))
        
        # Display current rate (read-only)
        self.rate_display = tk.Label(rate_content, 
                                    text="Ładowanie kursu...", 
                                    bg="#1e1e1e", fg="#00ff88",
                                    font=('Segoe UI', 14, 'bold'),
                                    relief="flat", bd=5, pady=10)
        self.rate_display.pack(fill="x", pady=(0, 5))
        
        self.rate_info_label = tk.Label(rate_content, 
                                    text="Pobieranie aktualnego kursu z NBP...", 
                                    bg="#2d2d2d", fg="#888888", 
                                    font=('Segoe UI', 9))
        self.rate_info_label.pack(anchor="w")
        
        # Refresh rate button
        refresh_frame = tk.Frame(rate_content, bg="#2d2d2d")
        refresh_frame.pack(fill="x", pady=(5, 0))
        
        refresh_btn = tk.Button(refresh_frame, text="🔄 Odśwież kurs",
                            bg="#0078d4", fg="white",
                            font=('Segoe UI', 9),
                            relief="flat", bd=0,
                            padx=10, pady=5,
                            cursor="hand2",
                            command=self.refresh_exchange_rate)
        refresh_btn.pack(anchor="w")
        
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
        
        self.process_btn = tk.Button(button_container, text="⚡ Przetwórz pliki", 
                                    command=self.process_pdfs,
                                    bg="#107c10", fg="white", 
                                    font=('Segoe UI', 11, 'bold'),
                                    relief="flat", cursor="hand2",
                                    padx=20, pady=10, state="disabled")
        self.process_btn.pack(side="left")
        
    def select_files(self):
        if self.is_processing:
            return
            
        files = filedialog.askopenfilenames(
            title="Wybierz pliki PDF lub TIF",
            filetypes=[
                 ("Wszystkie obsługiwane", "*.pdf *.tif *.tiff"),
                ("Pliki PDF", "*.pdf"),
                   ("Pliki TIF", "*.tif *.tiff"),
                ("Wszystkie pliki", "*.*")
            ]
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
        self.process_btn.config(text="⚡ Przetwórz pliki")
        self.clear_btn.config(state="normal", bg="#404040")
        self.update_process_button()
        
    def process_pdfs_thread(self):
        """Run the actual processing in a separate thread"""
        try:
            all_extracted_text = []
            
            # Process each selected file
            for file_path in self.selected_files:
                try:
                    text = extract_text_from_file(file_path)
                    clean_text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])
                    all_extracted_text.append(clean_text)
                except ValueError as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
            
            if all_extracted_text:
                # Gather data using AI processor
                gathered_data = gather_specific_data(all_extracted_text)  
                
                # Use current rate if available, otherwise fallback
                eur_to_pln_rate = self.current_rate if self.current_rate else get_eur_to_pln_rate_fallback()
                
                # Export to Excel
                success = export_to_excel(gathered_data, eur_to_pln_rate)
                
                if success:
                    result_msg = f"Pomyślnie przetworzono {len(gathered_data)} faktury i wyeksportowano do pliku Excel."
                    self.root.after(0, lambda: self.processing_success(result_msg))
                else:
                    self.root.after(0, lambda: self.processing_error("Błąd podczas eksportowania do pliku Excel"))
            else:
                self.root.after(0, lambda: self.processing_error("Nie znaleziono prawidłowych plików do przetworzenia"))
                
        except Exception as e:
            error_msg = f"Błąd podczas przetwarzania: {str(e)}"
            self.root.after(0, lambda: self.processing_error(error_msg))
            
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