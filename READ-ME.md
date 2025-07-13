
📘 Leitor de PDF com Áudio (Python)

Aplicação gráfica simples que permite:

✅ Ler arquivos PDF em voz alta
✅ Controlar a leitura com Play/Pause
✅ Navegar por páginas e escolher a linha exata onde a leitura começa
✅ Visualizar o conteúdo do PDF enquanto ouve


---

📦 Requisitos

Python 3.7+

Dependências:

pyttsx3 – leitura de texto em voz alta (offline)

PyPDF2 – leitura de conteúdo do PDF

tkinter – interface gráfica (já vem com Python)




---

🛠️ Instalação

1. Clone ou baixe o projeto:

git clone https://github.com//leitor-pdf-audio.git
cd leitor-pdf-audio


2. Instale as dependências:

pip install pyttsx3 PyPDF2



> 💡 O tkinter já está incluído com a maioria das instalações do Python. Se não estiver:

Ubuntu: sudo apt install python3-tk

Mac: já incluso

Windows: incluso no instalador oficial do Python





---

▶️ Como usar

1. Execute o script:

python leitor_pdf_audio.py


2. Na interface:

Clique em “Abrir PDF” e escolha o arquivo

Use os botões:

▶️ Play – lê a partir da página/linha atual

⏸ Pause – interrompe a leitura

⬅️ Página Anterior / ➡️ Próxima Página


Use os campos:

"Ir para página" – vá diretamente para uma página

"Ir para linha" – escolha de qual linha começar a leitura

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

    self.engine.say(line)

self.engine.runAndWait()
