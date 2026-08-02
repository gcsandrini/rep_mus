import customtkinter
import pygame
import os
from mutagen.mp3 import MP3
from PIL import Image
import json
from tkinter import messagebox
indice_musica = 0
tocando = False
primeira = True
arrastando_slider = False
offset_tempo = 0
ARQUIVO_PLAYLISTS = 'playlists.json'
ARQUIVO_ESTADO = 'estado.json'
playlist_atual = None
after_id_reproducao = None
after_id_progresso = None
icone_play = customtkinter.CTkImage(
    light_image=Image.open("imagem/botao_pause.png"),
    dark_image=Image.open("imagem/botao_pause.png"),
    size=(40, 40))
icone_pause = customtkinter.CTkImage(
    light_image=Image.open("imagem/botao_play.png"),
    dark_image=Image.open("imagem/botao_play.png"),
    size=(40, 40))
imagem_proxima = Image.open("imagem/botao_proxima.png")
imagem_voltar = imagem_proxima.transpose(Image.FLIP_LEFT_RIGHT)
icone_proxima = customtkinter.CTkImage(
    light_image=imagem_proxima,
    dark_image=imagem_proxima,
    size=(30, 30))
icone_voltar = customtkinter.CTkImage(
    light_image=imagem_voltar,
    dark_image=imagem_voltar,
    size=(30, 30))
def playlist():
    lista_de_musicas = []
    musicas = os.listdir('musicas')
    for musica in musicas:
        lista_de_musicas.append("musicas/" + musica)
    return lista_de_musicas
def botao_play(lista_de_musica):
    global tocando
    global primeira
    global offset_tempo
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
def botao_proximo(lista_de_musica,label_musica):
    global indice_musica, tocando, primeira, offset_tempo
    indice_musica += 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    tocando = True
    primeira = False
    offset_tempo = 0
    exibir_nome_musica(label_musica,lista_de_musica)
def botao_voltar(lista_de_musica,label_musica):
    global indice_musica, offset_tempo
    indice_musica -= 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    offset_tempo = 0
    exibir_nome_musica(label_musica,lista_de_musica)
def reconstruir_player(music_player, lista_de_musica, volume_inicial=1):
    mostrar_imagem(music_player)

    botao_playlists = customtkinter.CTkButton(
        music_player, text="☰", width=30, height=30,
        command=lambda: janela_criar_playlist(music_player)
    )
    botao_playlists.place(x=10, y=10)

    label_tempo = customtkinter.CTkLabel(music_player, text="00:00 / 00:00")
    label_tempo.grid(row=1, column=0, columnspan=3)

    slider_progresso = customtkinter.CTkSlider(music_player, from_=0, to=100)
    slider_progresso.set(0)
    slider_progresso.grid(row=2, column=0, columnspan=3, pady=10)
    slider_progresso.bind("<Button-1>", lambda e: iniciar_arraste())
    slider_progresso.bind("<ButtonRelease-1>", lambda e: soltar_slider(lista_de_musica, slider_progresso))

    label_musica = customtkinter.CTkLabel(music_player, text="Nenhuma música")
    label_musica.grid(row=3, column=0, columnspan=3)

    nome_playlist_exibir = playlist_atual if playlist_atual else "Todas as músicas"
    label_playlist = customtkinter.CTkLabel(
        music_player, text=nome_playlist_exibir,
        font=("", 11), text_color="gray"
    )
    label_playlist.grid(row=4, column=0, columnspan=3)

    def alternar_play_pause():
        botao_play(lista_de_musica)
        layout_botao_play.configure(image=icone_pause if tocando else icone_play)
    layout_botao_play = customtkinter.CTkButton(
        music_player, text='', image=icone_play,
        command=alternar_play_pause,
        fg_color="transparent", hover_color="#2a2a2a",
        width=60, height=60)
    layout_botao_play.grid(row=5, column=1)

    layout_botao_proximo = customtkinter.CTkButton(
        music_player, text='', image=icone_proxima,
        command=lambda: botao_proximo(lista_de_musica, label_musica),
        fg_color="transparent", hover_color="#2a2a2a",
        width=45, height=45)
    layout_botao_proximo.grid(row=5, column=2)

    layout_botao_voltar = customtkinter.CTkButton(
        music_player, text='', image=icone_voltar,
        command=lambda: botao_voltar(lista_de_musica, label_musica),
        fg_color="transparent", hover_color="#2a2a2a",
        width=45, height=45)
    layout_botao_voltar.grid(row=5, column=0)

    slider_volume = customtkinter.CTkSlider(
        music_player, from_=0, to=1,
        command=lambda valor: pygame.mixer.music.set_volume(valor))
    slider_volume.set(volume_inicial)
    slider_volume.grid(row=6, column=0, columnspan=3, pady=10)

    def ao_fechar():
        tempo_atual = 0
        if not primeira:
            tempo_atual = max((pygame.mixer.music.get_pos() / 1000) + offset_tempo, 0)
        salvar_estado(playlist_atual, indice_musica, tempo_atual, slider_volume.get())
        music_player.destroy()
    music_player.protocol("WM_DELETE_WINDOW", ao_fechar)

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

    music_player.mainloop()
def reprodução_automatica(lista_de_musica, music_player, label_musica):
    global after_id_reproducao
    if pygame.mixer.music.get_busy() == False and tocando == True and primeira == False:
        botao_proximo(lista_de_musica, label_musica)
    after_id_reproducao = music_player.after(1000, lambda: reprodução_automatica(lista_de_musica, music_player, label_musica))
def exibir_nome_musica(label_musica,lista_de_musica):
    nome = os.path.basename(lista_de_musica[indice_musica]).replace(".mp3", "")
    label_musica.configure(text=nome)
def mostrar_imagem(music_player):
    imagem = Image.open('imagem/gato ouvindo musica.png')
    ctkimagem = customtkinter.CTkImage(imagem,size= (150, 150))
    label_imagem = customtkinter.CTkLabel(music_player,image=ctkimagem, text= '')
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
    duracao_total = MP3(lista_de_musica[indice_musica]).info.length
    posicao_segundos = (slider_progresso.get() / 100) * duracao_total
    pygame.mixer.music.set_pos(posicao_segundos)
    offset_tempo = posicao_segundos - (pygame.mixer.music.get_pos() / 1000)
    arrastando_slider = False
def atualizar_progresso_musica(lista_de_musica, slider_progresso, label_tempo, music_player):
    global indice_musica, arrastando_slider, offset_tempo, after_id_progresso
    if not arrastando_slider and not primeira:
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

    janela = customtkinter.CTkToplevel(music_player_atual)
    janela.title("Playlists")
    janela.geometry("700x500")
    janela.grid_columnconfigure(0, weight=1)
    janela.grid_columnconfigure(1, weight=1)
    janela.grid_columnconfigure(2, weight=1)
    janela.grid_rowconfigure(0, weight=1)

    frame_todas = customtkinter.CTkScrollableFrame(janela, label_text="Todas as músicas")
    frame_todas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    frame_selecionadas = customtkinter.CTkScrollableFrame(janela, label_text="Ordem da playlist (arraste)")
    frame_selecionadas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    frame_playlists = customtkinter.CTkScrollableFrame(janela, label_text="Playlists salvas")
    frame_playlists.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")

    entry_nome = customtkinter.CTkEntry(janela, placeholder_text="Nome da playlist")
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
        item = customtkinter.CTkFrame(frame_selecionadas, fg_color="#2a2a2a")
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
                command=lambda n=nome_playlist: ao_tocar(n)
            ).pack(side="left", padx=2)
            customtkinter.CTkButton(
                botoes, text="Editar", width=60,
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

    customtkinter.CTkButton(janela, text="Salvar playlist", command=salvar_playlist).grid(
        row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    atualizar_lista_playlists()
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
main()