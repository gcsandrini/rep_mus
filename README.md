# 🎵 Music Player em Python

Um reprodutor de música simples feito com **Python**, usando **CustomTkinter**, **Pygame** e **Pillow**.  
O projeto permite tocar músicas de uma pasta local com interface gráfica e controles básicos de reprodução.

---

## 🚀 Funcionalidades

- ▶️ Play / Pause de músicas
- ⏭️ Próxima música
- ⏮️ Música anterior
- 🔁 Reprodução automática ao finalizar a música
- 📃 Exibição do nome da música atual
- 🖼️ Interface gráfica com imagem ilustrativa
- 📁 Leitura automática de músicas da pasta `musicas/`

---

## 🛠️ Tecnologias usadas

- Python 3
- CustomTkinter
- Pygame
- Pillow (PIL)
- OS (biblioteca padrão)

---

## 📂 Estrutura do projeto
projeto/
│
├── main.py
├── musicas/
│ ├── musica1.mp3
│ ├── musica2.mp3
│
├── imagem/
│ └── gato ouvindo musica.png


---

## ▶️ Como executar

### 1. Instale as dependências:

```bash
pip install customtkinter pygame pillow
2. Adicione músicas

Coloque arquivos .mp3 dentro da pasta:

musicas/
3. Execute o projeto
python main.py
⚙️ Como funciona
O programa lê automaticamente todas as músicas da pasta musicas/
Usa o pygame.mixer para tocar áudio
Interface construída com customtkinter
Um loop com .after() verifica quando a música termina e chama a próxima automaticamente
📌 Observações
Funciona melhor com arquivos .mp3
A ordem das músicas segue a ordem da pasta
O autoplay depende do pygame.mixer.music.get_busy()
📈 Possíveis melhorias futuras
🔀 Shuffle (aleatório)
🔁 Repeat (repetir música)
📊 Barra de progresso da música
🎧 Playlists múltiplas
🌐 Integração com Spotify API
👨‍💻 Autor: Gabriel Sandrini

Projeto desenvolvido como estudo de: Gabriel Sandrini

Python GUI
Manipulação de áudio
Estruturação de projetos
