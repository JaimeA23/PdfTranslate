import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from googletrans import Translator

class PDFPagedViewer:
    def __init__(self, root):
        self.root = root
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.page_texts = []
        self.translator = Translator()
        self.languages = [
            ('Inglés', 'en'),
            ('Español', 'es'),
            ('Francés', 'fr'),
            ('Alemán', 'de'),
            ('Italiano', 'it'),
            ('Portugués', 'pt'),
            ('Chino', 'zh-cn'),
            ('Japonés', 'ja'),
            ('Ruso', 'ru'),
            ('Árabe', 'ar')
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # Barra de herramientas superior
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        
        # Botones en la barra superior
        ttk.Button(self.toolbar, text="Abrir PDF", 
                 command=self.load_pdf_dialog).pack(side=tk.LEFT)
        
        self.language_var = tk.StringVar()
        self.lang_combobox = ttk.Combobox(self.toolbar,
                                        textvariable=self.language_var,
                                        values=[lang[0] for lang in self.languages],
                                        state="readonly",
                                        width=15)
        self.lang_combobox.set('Inglés')
        self.lang_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.toolbar, text="Traducir", 
                 command=self.translate_page).pack(side=tk.LEFT, padx=5)
        
        self.page_label = ttk.Label(self.toolbar, text="Página: 0/0")
        self.page_label.pack(side=tk.RIGHT, padx=10)
        
        # Área principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Componentes del área de texto
        self.text_widget = tk.Text(self.main_frame, wrap="word", 
                                 font=("Helvetica", 10), padx=10, pady=10)
        
        # Barra de scroll vertical
        self.scrollbar = ttk.Scrollbar(self.main_frame, 
                                     command=self.on_scroll)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)
        
        # Barra de progreso de páginas
        self.page_progress = ttk.Scale(self.main_frame, 
                                     orient=tk.VERTICAL,
                                     from_=1,
                                     to=1,
                                     command=self.on_progress_move)
        self.page_progress.set(1)
        
        # Distribución de elementos
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.page_progress.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Configuración de eventos
        self.text_widget.bind("<MouseWheel>", self.on_mousewheel)
        self.text_widget.bind("<Button-4>", self.on_mousewheel)
        self.text_widget.bind("<Button-5>", self.on_mousewheel)
        
        self.update_text_display("Abra un archivo PDF para comenzar")
    
    def on_progress_move(self, value):
        new_page = int(float(value)) - 1
        if 0 <= new_page < self.total_pages and new_page != self.current_page:
            self.current_page = new_page
            self.show_page()
    
    def get_language_code(self):
        selected_lang = self.language_var.get()
        for lang in self.languages:
            if lang[0] == selected_lang:
                return lang[1]
        return 'en'
    
    def load_pdf_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, path: str):
        self.doc = fitz.open(path)
        self.total_pages = len(self.doc)
        self.page_texts = []
        
        for page in self.doc:
            self.page_texts.append(page.get_text("text"))
        
        self.current_page = 0
        self.page_progress.config(from_=1, to=self.total_pages)
        self.show_page()
    
    def show_page(self):
        if not self.page_texts:
            return
            
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, self.page_texts[self.current_page])
        self.text_widget.configure(state="disabled")
        
        self.page_label.config(text=f"Página: {self.current_page + 1}/{self.total_pages}")
        self.page_progress.set(self.current_page + 1)
        self.text_widget.yview_moveto(0)
    
    def translate_page(self):
        if not self.page_texts:
            return
            
        try:
            target_lang = self.get_language_code()
            original_text = self.page_texts[self.current_page]
            translated = self.translator.translate(original_text, dest=target_lang).text
            
            self.text_widget.configure(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, translated)
            self.text_widget.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo traducir: {str(e)}")
    
    def update_text_display(self, message: str):
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, message)
        self.text_widget.configure(state="disabled")
    
    def on_scroll(self, action, *args):
        if action == "scroll":
            self.change_page(1 if args[0] == "1" else -1)
    
    def on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.change_page(-1)
        else:
            self.change_page(1)
    
    def change_page(self, delta: int):
        new_page = self.current_page + delta
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            self.show_page()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Visor de PDF con Navegación Avanzada")
    root.geometry("800x600")
    
    app = PDFPagedViewer(root)
    root.mainloop()