import customtkinter
import pygame
import os
import sys
from mutagen.mp3 import MP3
from PIL import Image
import json
from tkinter import messagebox
import yt_dlp
import threading
import re
customtkinter.set_appearance_mode("dark")
def pasta_base_execucao():
    """Pasta onde o .exe (ou o main.py) está localizado. Usada para dados
    graváveis/externos: musicas/, ffmpeg/, playlists.json, estado.json."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
def caminho_recurso(caminho_relativo):
    """Localiza um recurso empacotado (ícones/imagens) tanto rodando como
    script normal quanto rodando dentro do .exe gerado pelo PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, caminho_relativo)
PASTA_MUSICAS = os.path.join(pasta_base_execucao(), 'musicas')
os.makedirs(PASTA_MUSICAS, exist_ok=True)
CAMINHO_FFMPEG = os.path.join(pasta_base_execucao(), 'ffmpeg', 'ffmpeg.exe')
COR_FUNDO = "#000000"
COR_FUNDO_SECUNDARIO = "#141414"
COR_ROXO = "#7C3AED"
COR_ROXO_HOVER = "#6D28D9"
COR_ROXO_ESCURO = "#2a1f3d"
menu_flyout_frame = None
menu_flyout_botao = None
indice_musica = 0
tocando = False
primeira = True
arrastando_slider = False
offset_tempo = 0
volume_antes_mute = None
ARQUIVO_PLAYLISTS = os.path.join(pasta_base_execucao(), 'playlists.json')
ARQUIVO_ESTADO = os.path.join(pasta_base_execucao(), 'estado.json')
playlist_atual = None
after_id_reproducao = None
after_id_progresso = None
icone_play = customtkinter.CTkImage(
    light_image=Image.open(caminho_recurso("imagem/botao_pause.png")),
    dark_image=Image.open(caminho_recurso("imagem/botao_pause.png")),
    size=(40, 40))
icone_pause = customtkinter.CTkImage(
    light_image=Image.open(caminho_recurso("imagem/botao_play.png")),
    dark_image=Image.open(caminho_recurso("imagem/botao_play.png")),
    size=(40, 40))
imagem_proxima = Image.open(caminho_recurso("imagem/botao_proxima.png"))
imagem_voltar = imagem_proxima.transpose(Image.FLIP_LEFT_RIGHT)
icone_proxima = customtkinter.CTkImage(
    light_image=imagem_proxima,
    dark_image=imagem_proxima,
    size=(30, 30))
icone_voltar = customtkinter.CTkImage(
    light_image=imagem_voltar,
    dark_image=imagem_voltar,
    size=(30, 30))
icone_volume = customtkinter.CTkImage(
    light_image=Image.open(caminho_recurso("imagem/icone_volume.png")),
    dark_image=Image.open(caminho_recurso("imagem/icone_volume.png")),
    size=(22, 22))
def elevar_janela(janela):
    janela.lift()
    janela.focus_force()
    janela.attributes('-topmost', True)
    janela.after(10, lambda: janela.attributes('-topmost', False))
def playlist():
    lista_de_musicas = []
    musicas = os.listdir(PASTA_MUSICAS)
    for musica in musicas:
        if musica.lower().endswith('.mp3'):
            lista_de_musicas.append(os.path.join(PASTA_MUSICAS, musica))
    return lista_de_musicas
def botao_play(lista_de_musica):
    global tocando
    global primeira
    global offset_tempo
    if not lista_de_musica:
        return
    if primeira == True:
        pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
        pygame.mixer.music.play()
        tocando = True
        primeira = False
        offset_tempo = 0
    else:
        if tocando == False:
            pygame.mixer.music.unpause()
            tocando = True
        else:
            pygame.mixer.music.pause()
            tocando = False
def botao_proximo(lista_de_musica, label_musica):
    global indice_musica, tocando, primeira, offset_tempo
    if not lista_de_musica:
        return
    indice_musica += 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    tocando = True
    primeira = False
    offset_tempo = 0
    exibir_nome_musica(label_musica, lista_de_musica)
def botao_voltar(lista_de_musica, label_musica):
    global indice_musica, offset_tempo
    if not lista_de_musica:
        return
    indice_musica -= 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    offset_tempo = 0
    exibir_nome_musica(label_musica, lista_de_musica)
def reconstruir_player(music_player, lista_de_musica, volume_inicial=1):
    music_player.configure(fg_color=COR_FUNDO)
    mostrar_imagem(music_player)
    global menu_flyout_botao
    fechar_menu_flyout()
    botao_playlists = customtkinter.CTkButton(
        music_player, text="☰", width=30, height=30,
        fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
        command=lambda: alternar_menu_flyout(music_player))
    botao_playlists.place(x=10, y=10)
    menu_flyout_botao = botao_playlists
    label_tempo = customtkinter.CTkLabel(music_player, text="00:00 / 00:00")
    label_tempo.grid(row=1, column=0, columnspan=3)
    slider_progresso = customtkinter.CTkSlider(
        music_player, from_=0, to=100,
        progress_color=COR_ROXO, button_color=COR_ROXO, button_hover_color=COR_ROXO_HOVER)
    slider_progresso.set(0)
    slider_progresso.grid(row=2, column=0, columnspan=3, pady=10)
    slider_progresso.bind("<Button-1>", lambda e: iniciar_arraste())
    slider_progresso.bind("<ButtonRelease-1>", lambda e: soltar_slider(lista_de_musica, slider_progresso))
    lista_vazia = len(lista_de_musica) == 0
    label_musica = customtkinter.CTkLabel(
        music_player,
        text="Nenhuma música encontrada" if lista_vazia else "Nenhuma música")
    label_musica.grid(row=3, column=0, columnspan=3)
    nome_playlist_exibir = playlist_atual if playlist_atual else "Todas as músicas"
    label_playlist = customtkinter.CTkLabel(
        music_player, text=nome_playlist_exibir,
        font=("", 11), text_color="gray")
    label_playlist.grid(row=4, column=0, columnspan=3)
    frame_controles = customtkinter.CTkFrame(music_player, fg_color="transparent")
    frame_controles.grid(row=5, column=0, columnspan=3)
    def alternar_play_pause():
        botao_play(lista_de_musica)
        layout_botao_play.configure(image=icone_pause if tocando else icone_play)
    layout_botao_voltar = customtkinter.CTkButton(
        frame_controles, text='', image=icone_voltar,
        command=lambda: botao_voltar(lista_de_musica, label_musica),
        fg_color="transparent", hover_color=COR_ROXO_ESCURO,
        width=45, height=45,
        state="disabled" if lista_vazia else "normal")
    layout_botao_voltar.pack(side="left", padx=10)
    layout_botao_play = customtkinter.CTkButton(
        frame_controles, text='', image=icone_play,
        command=alternar_play_pause,
        fg_color="transparent", hover_color=COR_ROXO_ESCURO,
        width=60, height=60,
        state="disabled" if lista_vazia else "normal")
    layout_botao_play.pack(side="left", padx=10)
    layout_botao_proximo = customtkinter.CTkButton(
        frame_controles, text='', image=icone_proxima,
        command=lambda: botao_proximo(lista_de_musica, label_musica),
        fg_color="transparent", hover_color=COR_ROXO_ESCURO,
        width=45, height=45,
        state="disabled" if lista_vazia else "normal")
    layout_botao_proximo.pack(side="left", padx=10)
    slider_volume = customtkinter.CTkSlider(
        music_player, from_=0, to=1,
        progress_color=COR_ROXO, button_color=COR_ROXO, button_hover_color=COR_ROXO_HOVER,
        command=lambda valor: pygame.mixer.music.set_volume(valor))
    slider_volume.set(volume_inicial)
    slider_volume.grid(row=6, column=1, columnspan=2, padx=(0, 10), pady=10, sticky="ew")
    def alternar_mute():
        global volume_antes_mute
        volume_atual = pygame.mixer.music.get_volume()
        if volume_atual > 0:
            volume_antes_mute = volume_atual
            pygame.mixer.music.set_volume(0)
            slider_volume.set(0)
        else:
            restaurar = volume_antes_mute if volume_antes_mute else 1
            pygame.mixer.music.set_volume(restaurar)
            slider_volume.set(restaurar)
    botao_mute = customtkinter.CTkButton(
        music_player, text='', image=icone_volume,
        command=alternar_mute,
        fg_color="transparent", hover_color=COR_ROXO_ESCURO,
        width=30, height=30)
    botao_mute.grid(row=6, column=0, padx=(15, 0))
    def ao_fechar():
        tempo_atual = 0
        if not primeira:
            tempo_atual = max((pygame.mixer.music.get_pos() / 1000) + offset_tempo, 0)
        salvar_estado(playlist_atual, indice_musica, tempo_atual, slider_volume.get())
        music_player.destroy()
    music_player.protocol("WM_DELETE_WINDOW", ao_fechar)
    if not lista_vazia:
        exibir_nome_musica(label_musica, lista_de_musica)
    reprodução_automatica(lista_de_musica, music_player, label_musica)
    atualizar_progresso_musica(lista_de_musica, slider_progresso, label_tempo, music_player)
def main():
    global indice_musica, tocando, primeira, offset_tempo, playlist_atual
    pygame.mixer.init()
    estado = carregar_estado()
    playlists = carregar_playlists()
    if estado and estado.get("playlist_atual") in playlists:
        playlist_atual = estado["playlist_atual"]
        lista_de_musica = playlists[playlist_atual]
    else:
        playlist_atual = None
        lista_de_musica = playlist()
    if estado and 0 <= estado.get("indice_musica", 0) < len(lista_de_musica):
        indice_musica = estado["indice_musica"]
    volume_inicial = estado.get("volume", 1) if estado else 1
    if estado and lista_de_musica:
        pygame.mixer.music.load(lista_de_musica[indice_musica])
        pygame.mixer.music.play()
        pygame.mixer.music.set_pos(estado.get("tempo_pausado", 0))
        pygame.mixer.music.pause()
        pygame.mixer.music.set_volume(volume_inicial)
        tocando = False
        primeira = False
        offset_tempo = estado.get("tempo_pausado", 0) - (pygame.mixer.music.get_pos() / 1000)
    music_player = customtkinter.CTk()
    music_player.grid_columnconfigure(0, weight=1)
    music_player.grid_columnconfigure(1, weight=1)
    music_player.grid_columnconfigure(2, weight=1)
    music_player.grid_rowconfigure(0, weight=1)
    music_player.title('Music Player')
    music_player.geometry('400x460')
    reconstruir_player(music_player, lista_de_musica, volume_inicial)
    music_player.bind_all("<Button-1>", clique_fora_menu, add="+")
    music_player.mainloop()
def reprodução_automatica(lista_de_musica, music_player, label_musica):
    global after_id_reproducao
    if lista_de_musica and pygame.mixer.music.get_busy() == False and tocando == True and primeira == False:
        botao_proximo(lista_de_musica, label_musica)
    after_id_reproducao = music_player.after(1000, lambda: reprodução_automatica(lista_de_musica, music_player, label_musica))
def exibir_nome_musica(label_musica, lista_de_musica):
    nome = os.path.basename(lista_de_musica[indice_musica]).replace(".mp3", "")
    label_musica.configure(text=nome)
def mostrar_imagem(music_player):
    imagem = Image.open(caminho_recurso('imagem/gato ouvindo musica.png'))
    ctkimagem = customtkinter.CTkImage(imagem, size=(150, 150))
    label_imagem = customtkinter.CTkLabel(music_player, image=ctkimagem, text='')
    label_imagem.grid(row=0, column=0, columnspan=3)
def formatar_tempo(segundos):
    minutos = int(segundos // 60)
    segundos_restantes = int(segundos % 60)
    return f'{minutos:02d}:{segundos_restantes:02d}'
def iniciar_arraste():
    global arrastando_slider
    arrastando_slider = True
def soltar_slider(lista_de_musica, slider_progresso):
    global arrastando_slider, indice_musica, offset_tempo
    if not lista_de_musica:
        arrastando_slider = False
        return
    duracao_total = MP3(lista_de_musica[indice_musica]).info.length
    posicao_segundos = (slider_progresso.get() / 100) * duracao_total
    pygame.mixer.music.set_pos(posicao_segundos)
    offset_tempo = posicao_segundos - (pygame.mixer.music.get_pos() / 1000)
    arrastando_slider = False
def atualizar_progresso_musica(lista_de_musica, slider_progresso, label_tempo, music_player):
    global indice_musica, arrastando_slider, offset_tempo, after_id_progresso
    if lista_de_musica and not arrastando_slider and not primeira:
        duracao_total = MP3(lista_de_musica[indice_musica]).info.length
        tempo_atual_ms = pygame.mixer.music.get_pos()
        tempo_atual_segundos = max((tempo_atual_ms / 1000) + offset_tempo, 0)
        porcentagem = min((tempo_atual_segundos / duracao_total) * 100, 100)
        slider_progresso.set(porcentagem)
        label_tempo.configure(text=f'{formatar_tempo(tempo_atual_segundos)} / {formatar_tempo(duracao_total)}')
    after_id_progresso = music_player.after(1000, lambda: atualizar_progresso_musica(lista_de_musica, slider_progresso, label_tempo, music_player))
def carregar_playlists():
    if os.path.exists(ARQUIVO_PLAYLISTS):
        with open(ARQUIVO_PLAYLISTS, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    return {}
def salvar_playlists(dados):
    with open(ARQUIVO_PLAYLISTS, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
def carregar_estado():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    return None
def salvar_estado(playlist_nome, indice, tempo, volume):
    dados = {
        "playlist_atual": playlist_nome,
        "indice_musica": indice,
        "tempo_pausado": tempo,
        "volume": volume
    }
    with open(ARQUIVO_ESTADO, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
def janela_criar_playlist(music_player_atual):
    checkboxes_musicas = {}
    estado_edicao = {"nome_original": None}
    todas_musicas = playlist()
    ordem_selecionada = []
    item_arrastando = {"caminho": None}
    janela = customtkinter.CTkToplevel(music_player_atual, fg_color=COR_FUNDO)
    janela.title("Playlists")
    janela.geometry("700x500")
    janela.grid_columnconfigure(0, weight=1)
    janela.grid_columnconfigure(1, weight=1)
    janela.grid_columnconfigure(2, weight=1)
    janela.grid_rowconfigure(0, weight=1)
    frame_todas = customtkinter.CTkScrollableFrame(janela, label_text="Todas as músicas", fg_color=COR_FUNDO_SECUNDARIO)
    frame_todas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    frame_selecionadas = customtkinter.CTkScrollableFrame(janela, label_text="Ordem da playlist (arraste)", fg_color=COR_FUNDO_SECUNDARIO)
    frame_selecionadas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    frame_playlists = customtkinter.CTkScrollableFrame(janela, label_text="Playlists salvas", fg_color=COR_FUNDO_SECUNDARIO)
    frame_playlists.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")
    entry_nome = customtkinter.CTkEntry(
        janela, placeholder_text="Nome da playlist",
        fg_color=COR_FUNDO_SECUNDARIO, border_color=COR_ROXO)
    entry_nome.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")
    label_aviso = customtkinter.CTkLabel(janela, text="", text_color="#e05555")
    label_aviso.grid(row=2, column=0, columnspan=2, padx=10, sticky="ew")
    def redesenhar_selecionadas():
        for widget in frame_selecionadas.winfo_children():
            widget.destroy()
        for caminho in ordem_selecionada:
            criar_item_arrastavel(caminho)
    def criar_item_arrastavel(caminho):
        nome = os.path.basename(caminho).replace(".mp3", "")
        item = customtkinter.CTkFrame(frame_selecionadas, fg_color=COR_ROXO_ESCURO)
        item.pack(fill="x", pady=2, padx=5)
        item.caminho = caminho
        label = customtkinter.CTkLabel(item, text=nome)
        label.pack(side="left", padx=8, pady=6)
        for widget in (item, label):
            widget.bind("<ButtonPress-1>", lambda e, c=caminho: iniciar_arraste_item(c))
            widget.bind("<B1-Motion>", arrastar_item)
            widget.bind("<ButtonRelease-1>", lambda e: soltar_item())
    def iniciar_arraste_item(caminho):
        item_arrastando["caminho"] = caminho
    def arrastar_item(event):
        if item_arrastando["caminho"] is None:
            return
        y_mouse = frame_selecionadas.winfo_pointery() - frame_selecionadas.winfo_rooty()
        filhos = frame_selecionadas.winfo_children()
        novo_indice = len(filhos) - 1
        for i, filho in enumerate(filhos):
            if y_mouse < filho.winfo_y() + filho.winfo_height() / 2:
                novo_indice = i
                break
        indice_atual = ordem_selecionada.index(item_arrastando["caminho"])
        if novo_indice != indice_atual:
            ordem_selecionada.pop(indice_atual)
            ordem_selecionada.insert(novo_indice, item_arrastando["caminho"])
            redesenhar_selecionadas()
    def soltar_item():
        item_arrastando["caminho"] = None
    for caminho in todas_musicas:
        nome = os.path.basename(caminho).replace(".mp3", "")
        def ao_marcar(caminho=caminho, var=None):
            if var.get():
                if caminho not in ordem_selecionada:
                    ordem_selecionada.append(caminho)
            else:
                if caminho in ordem_selecionada:
                    ordem_selecionada.remove(caminho)
            redesenhar_selecionadas()
        var = customtkinter.BooleanVar(value=False)
        checkbox = customtkinter.CTkCheckBox(
            frame_todas, text=nome, variable=var,
            fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
            command=lambda c=caminho, v=var: ao_marcar(c, v))
        checkbox.pack(anchor="w", padx=5, pady=3)
        checkboxes_musicas[caminho] = var
    def trocar_playlist_ativa_local(nome):
        global playlist_atual, indice_musica, tocando, primeira, offset_tempo
        playlists_atuais = carregar_playlists()
        musicas_da_playlist = playlists_atuais.get(nome, [])
        if not musicas_da_playlist:
            return
        volume_atual = pygame.mixer.music.get_volume()
        playlist_atual = nome
        indice_musica = 0
        pygame.mixer.music.load(musicas_da_playlist[0])
        pygame.mixer.music.play()
        tocando = True
        primeira = False
        offset_tempo = 0
        cancelar_after_pendentes(music_player_atual)
        for widget in music_player_atual.winfo_children():
            widget.destroy()
        reconstruir_player(music_player_atual, musicas_da_playlist, volume_atual)
    def ao_tocar(nome):
        trocar_playlist_ativa_local(nome)
        janela.destroy()
    def editar_playlist(nome):
        playlists_atuais = carregar_playlists()
        musicas = playlists_atuais.get(nome, [])
        estado_edicao["nome_original"] = nome
        entry_nome.delete(0, "end")
        entry_nome.insert(0, nome)
        ordem_selecionada.clear()
        ordem_selecionada.extend(musicas)
        for caminho, var in checkboxes_musicas.items():
            var.set(caminho in musicas)
        label_aviso.configure(text=f"Editando '{nome}'")
        redesenhar_selecionadas()
    def excluir_playlist(nome):
        confirmar = messagebox.askyesno("Excluir playlist", f"Tem certeza que deseja excluir a playlist '{nome}'?")
        if confirmar:
            playlists_atuais = carregar_playlists()
            if nome in playlists_atuais:
                del playlists_atuais[nome]
                salvar_playlists(playlists_atuais)
            if estado_edicao["nome_original"] == nome:
                estado_edicao["nome_original"] = None
                entry_nome.delete(0, "end")
                ordem_selecionada.clear()
                for var in checkboxes_musicas.values():
                    var.set(False)
                redesenhar_selecionadas()
            atualizar_lista_playlists()
    def atualizar_lista_playlists():
        for widget in frame_playlists.winfo_children():
            widget.destroy()
        playlists_atuais = carregar_playlists()
        for nome_playlist in playlists_atuais:
            linha = customtkinter.CTkFrame(frame_playlists, fg_color="transparent")
            linha.pack(fill="x", padx=5, pady=5)
            customtkinter.CTkLabel(linha, text=nome_playlist).pack(anchor="w", padx=5)
            botoes = customtkinter.CTkFrame(linha, fg_color="transparent")
            botoes.pack(fill="x", padx=5, pady=(2, 0))
            customtkinter.CTkButton(
                botoes, text="Tocar", width=60,
                fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
                command=lambda n=nome_playlist: ao_tocar(n)
            ).pack(side="left", padx=2)
            customtkinter.CTkButton(
                botoes, text="Editar", width=60,
                fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
                command=lambda n=nome_playlist: editar_playlist(n)
            ).pack(side="left", padx=2)
            customtkinter.CTkButton(
                botoes, text="Excluir", width=60, fg_color="#a33333", hover_color="#7a2626",
                command=lambda n=nome_playlist: excluir_playlist(n)
            ).pack(side="left", padx=2)
    def salvar_playlist():
        nome = entry_nome.get().strip()
        if not nome:
            label_aviso.configure(text="Digite um nome para a playlist.")
            return
        if not ordem_selecionada:
            label_aviso.configure(text="Selecione ao menos uma música.")
            return
        playlists_atuais = carregar_playlists()
        editando = estado_edicao["nome_original"]
        if nome != editando and nome in playlists_atuais:
            label_aviso.configure(text="Já existe uma playlist com esse nome.")
            return
        if editando and editando != nome and editando in playlists_atuais:
            del playlists_atuais[editando]
        playlists_atuais[nome] = list(ordem_selecionada)
        salvar_playlists(playlists_atuais)
        label_aviso.configure(text="")
        estado_edicao["nome_original"] = None
        entry_nome.delete(0, "end")
        ordem_selecionada.clear()
        for var in checkboxes_musicas.values():
            var.set(False)
        redesenhar_selecionadas()
        atualizar_lista_playlists()
    customtkinter.CTkButton(
        janela, text="Salvar playlist", command=salvar_playlist,
        fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER
    ).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
    atualizar_lista_playlists()
    elevar_janela(janela)
def cancelar_after_pendentes(music_player):
    global after_id_reproducao, after_id_progresso
    if after_id_reproducao is not None:
        try:
            music_player.after_cancel(after_id_reproducao)
        except Exception:
            pass
        after_id_reproducao = None
    if after_id_progresso is not None:
        try:
            music_player.after_cancel(after_id_progresso)
        except Exception:
            pass
        after_id_progresso = None
def sanitizar_nome_arquivo(nome):
    return re.sub(r'[\\/*?:"<>|]', '-', nome).strip()
def obter_caminho_disponivel(pasta, nome_base, extensao):
    caminho = os.path.join(pasta, f'{nome_base}{extensao}')
    contador = 1
    nome_final = nome_base
    while os.path.exists(caminho):
        nome_final = f'{nome_base} ({contador})'
        caminho = os.path.join(pasta, f'{nome_final}{extensao}')
        contador += 1
    return nome_final
def baixar_audio_youtube(link, estado):
    try:
        opcoes_info = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(opcoes_info) as ydl:
            info = ydl.extract_info(link, download=False)
        titulo = sanitizar_nome_arquivo(info.get('title', 'musica'))
        nome_final = obter_caminho_disponivel(PASTA_MUSICAS, titulo, '.mp3')
        def hook_progresso(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                baixado = d.get('downloaded_bytes', 0)
                if total:
                    estado['porcentagem'] = int(baixado / total * 100)
        opcoes = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(PASTA_MUSICAS, f'{nome_final}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': CAMINHO_FFMPEG,
            'progress_hooks': [hook_progresso],
            'quiet': True,
            'no_warnings': True,
            }
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([link])
        estado['status'] = 'concluido'
    except Exception:
        estado['erro'] = 'Não foi possível baixar esse link. Verifique se é um link válido do YouTube.'
        estado['status'] = 'erro'
def janela_progresso_download(link, janela_pai, callback_erro):
    estado = {"porcentagem": 0, "status": "baixando", "erro": None}
    janela = customtkinter.CTkToplevel(janela_pai, fg_color=COR_FUNDO)
    janela.title("Baixando música")
    janela.geometry("320x150")
    janela.grid_columnconfigure(0, weight=1)
    label_status = customtkinter.CTkLabel(janela, text="Baixando... 0%")
    label_status.grid(row=0, column=0, padx=20, pady=(25, 10))
    barra = customtkinter.CTkProgressBar(janela, width=250, progress_color=COR_ROXO)
    barra.set(0)
    barra.grid(row=1, column=0, padx=20, pady=10)
    thread = threading.Thread(target=baixar_audio_youtube, args=(link, estado), daemon=True)
    thread.start()
    def verificar_progresso():
        if estado["status"] == "erro":
            janela.destroy()
            callback_erro(estado["erro"])
            return
        if estado["status"] == "concluido":
            barra.set(1)
            label_status.configure(text="Download concluído!")
            janela.after(1500, janela.destroy)
            return
        barra.set(estado["porcentagem"] / 100)
        label_status.configure(text=f'Baixando... {estado["porcentagem"]}%')
        janela.after(200, verificar_progresso)
    verificar_progresso()
    elevar_janela(janela)
def janela_baixar_musica(music_player_atual):
    janela = customtkinter.CTkToplevel(music_player_atual, fg_color=COR_FUNDO)
    janela.title("Baixar música")
    janela.geometry("500x300")
    janela.grid_columnconfigure(0, weight=1)
    janela.grid_rowconfigure(0, weight=1)
    janela.grid_rowconfigure(4, weight=1)
    texto_instrucao = customtkinter.CTkLabel(
        janela,
        text="Cole abaixo o link de um vídeo do YouTube e clique em Enviar\n(ou pressione Enter) para baixar a música.",
        font=("", 15), wraplength=420, justify="center")
    texto_instrucao.grid(row=1, column=0, padx=20, pady=(10, 20))
    frame_link = customtkinter.CTkFrame(janela, fg_color="transparent")
    frame_link.grid(row=2, column=0, padx=20, pady=10)
    entry_link = customtkinter.CTkEntry(
        frame_link, placeholder_text="Cole o link aqui...", width=300,
        fg_color=COR_FUNDO_SECUNDARIO, border_color=COR_ROXO)
    entry_link.pack(side="left", padx=(0, 8))
    label_erro = customtkinter.CTkLabel(janela, text="", text_color="#e05555", wraplength=420)
    label_erro.grid(row=3, column=0, padx=20, pady=(5, 15))
    def mostrar_erro(msg):
        label_erro.configure(text=msg)
    def enviar(event=None):
        link = entry_link.get().strip()
        if not link:
            label_erro.configure(text="Cole um link antes de enviar.")
            return
        label_erro.configure(text="")
        janela_progresso_download(link, janela, mostrar_erro)
    botao_enviar = customtkinter.CTkButton(
        frame_link, text="Enviar", width=80, command=enviar,
        fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER
    )
    botao_enviar.pack(side="left")
    entry_link.bind("<Return>", enviar)
    elevar_janela(janela)
def fechar_menu_flyout():
    global menu_flyout_frame
    if menu_flyout_frame is not None:
        menu_flyout_frame.destroy()
        menu_flyout_frame = None
def alternar_menu_flyout(music_player):
    global menu_flyout_frame
    if menu_flyout_frame is not None:
        fechar_menu_flyout()
        return
    frame = customtkinter.CTkFrame(music_player, fg_color=COR_FUNDO_SECUNDARIO)
    frame.place(x=10, y=45)
    customtkinter.CTkButton(
        frame, text="Playlists", width=120,
        fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
        command=lambda: (fechar_menu_flyout(), janela_criar_playlist(music_player))
    ).pack(padx=5, pady=(5, 2))
    customtkinter.CTkButton(
        frame, text="Baixar música", width=120,
        fg_color=COR_ROXO, hover_color=COR_ROXO_HOVER,
        command=lambda: (fechar_menu_flyout(), janela_baixar_musica(music_player))
    ).pack(padx=5, pady=(2, 5))
    menu_flyout_frame = frame
def clique_fora_menu(event):
    global menu_flyout_frame, menu_flyout_botao
    if menu_flyout_frame is None:
        return
    widget = event.widget
    w = widget
    dentro = False
    while w is not None:
        if w in (menu_flyout_frame, menu_flyout_botao):
            dentro = True
            break
        w = getattr(w, "master", None)
    if not dentro:
        fechar_menu_flyout()
main()