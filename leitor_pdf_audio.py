import tkinter as tk
from tkinter import filedialog
import pyttsx3
import PyPDF2
import threading
import re
import time

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de PDF com Áudio")
        self.last_line_index = 0  # Para retomar leitura
        self.reading_thread = None  # Para controlar o thread
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.voices = self.engine.getProperty('voices')
        self.voice_names = [v.name for v in self.voices]
        self.selected_voice_index = tk.IntVar(value=0)

        self.is_reading = False
        self.pdf_reader = None
        self.current_page = 0
        self.pages_text = []

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Lista de páginas (lado esquerdo)
        self.page_listbox = tk.Listbox(main_frame, width=8, height=25)
        self.page_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.page_listbox.bind('<<ListboxSelect>>', self.on_page_select)

        # Caixa de texto (lado direito)
        self.text_box = tk.Text(main_frame, wrap='word', height=25, width=90)
        self.text_box.tag_configure("highlight", underline=True, background="#ffffaa")
        self.text_box.bind("<ButtonRelease-1>", self.on_text_click)
        self.text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Interface
        #self.text_box = tk.Text(root, wrap='word', height=25, width=90)
        #self.text_box.tag_configure("highlight", underline=True, background="#ffffaa")
        #self.text_box.pack(padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Abrir PDF", command=self.load_pdf).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Play", command=self.start_reading_thread).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Pause", command=self.pause_reading).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Página Anterior", command=self.prev_page).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Próxima Página", command=self.next_page).grid(row=0, column=4, padx=5)
        
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=5)

        tk.Label(nav_frame, text="Ir para página:").grid(row=0, column=0)
        self.page_entry = tk.Entry(nav_frame, width=5)
        self.page_entry.grid(row=0, column=1)
        tk.Button(nav_frame, text="Ir", command=self.go_to_page).grid(row=0, column=2, padx=5)

        tk.Label(nav_frame, text="Ir para linha:").grid(row=0, column=3)
        self.line_entry = tk.Entry(nav_frame, width=5)
        self.line_entry.grid(row=0, column=4)

        # Controle de volume
        volume_frame = tk.Frame(root)
        volume_frame.pack(pady=5)
        tk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT, padx=5)

        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.volume_slider.set(100)  # Volume inicial em 100%
        self.volume_slider.pack(side=tk.LEFT)

        # Escolha da voz
        voice_frame = tk.Frame(root)
        voice_frame.pack(pady=5)
        tk.Label(voice_frame, text="Escolha a voz:").pack(side=tk.LEFT, padx=5)
        self.voice_menu = tk.OptionMenu(voice_frame, self.selected_voice_index, *range(len(self.voice_names)))
        self.voice_menu.pack(side=tk.LEFT)

        tk.Label(voice_frame, text="(Índice de voz, veja lista no terminal)").pack(side=tk.LEFT)

        # Exibe vozes disponíveis no terminal
        print("\n--- Vozes disponíveis ---")
        for i, voice in enumerate(self.voices):
            print(f"[{i}] {voice.name} - {voice.languages}")
        print("--------------------------\n")

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            with open(file_path, 'rb') as f:
                self.pdf_reader = PyPDF2.PdfReader(f)
                self.pages_text = [p.extract_text() or "" for p in self.pdf_reader.pages]
                self.current_page = 0
                self.display_page()

                self.page_listbox.delete(0, tk.END)
                for i in range(len(self.pages_text)):
                    self.page_listbox.insert(tk.END, f"Página {i + 1}")

    def display_page(self):
        if 0 <= self.current_page < len(self.pages_text):
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, self.pages_text[self.current_page])

    def start_reading_thread(self):
        if not self.is_reading:
            self.reading_thread = threading.Thread(target=self.read_text, daemon=True)
            self.reading_thread.start()

    def read_text(self):
        if self.pages_text:
            self.is_reading = True

            # Define a voz
            voice_index = self.selected_voice_index.get()
            if 0 <= voice_index < len(self.voices):
                self.engine.setProperty('voice', self.voices[voice_index].id)

            # Define volume
            volume = self.volume_slider.get() / 100
            self.engine.setProperty('volume', volume)
            
            text = self.pages_text[self.current_page]
            lines = text.split('\n')

            try:
                entry_line = int(self.line_entry.get()) - 1
            except ValueError:
                entry_line = 0

            start_line = max(self.last_line_index, entry_line)

            for i in range(start_line, len(lines)):
                if not self.is_reading:
                    self.last_line_index = i
                    self.engine.stop()
                    break

                line = lines[i].strip()
                if not line:
                    continue

                if (
                    line.count('/') > 3 or
                    '.sc' in line.lower() or
                    re.search(r'[a-z]\.sc', line.lower())
                ):
                    continue

                #self.highlight_line_in_text(line)
                self.engine.say(line)

            self.engine.runAndWait()





    def highlight_line_in_text(self, line):
        self.text_box.tag_remove("highlight", "1.0", tk.END)

        # Procura a linha no texto exibido e aplica a tag
        start_idx = self.text_box.search(line, "1.0", tk.END, nocase=True)
        if start_idx:
            end_idx = f"{start_idx} + {len(line)}c"
            self.text_box.tag_add("highlight", start_idx, end_idx)

            # Rolagem automática até a linha
            self.text_box.see(start_idx)
    def on_text_click(self, event):
        # Pega o índice da posição do clique, ex: "5.0" (linha 5, coluna 0)
        index = self.text_box.index("@%d,%d" % (event.x, event.y))
        line_number = int(index.split('.')[0])
        
        # Atualiza os campos página e linha
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))  # +1 pois página é 1-based
        self.line_entry.delete(0, tk.END)
        self.line_entry.insert(0, str(line_number))

    def on_page_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.current_page = index
            self.pause_reading()
            self.display_page()

    def pause_reading(self):
        if self.is_reading:
            self.is_reading = False  # sinaliza para o loop parar
            self.engine.stop()       # para o engine de voz imediatamente


    def next_page(self):
        if self.current_page < len(self.pages_text) - 1:
            self.current_page += 1
            self.pause_reading()
            self.display_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.pause_reading()
            self.display_page()

    def go_to_page(self):
        try:
            page = int(self.page_entry.get()) - 1
            if 0 <= page < len(self.pages_text):
                self.current_page = page
                self.pause_reading()
                self.display_page()
        except ValueError:
            pass

# Inicia a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()
