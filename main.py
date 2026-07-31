import customtkinter
import pygame
import os
from PIL import Image
indice_musica = 0
tocando = False
primeira = True
icone_play = customtkinter.CTkImage(
    light_image=Image.open("imagem/botao_play.png"),
    dark_image=Image.open("imagem/botao_play.png"),
    size=(40, 40))
icone_pause = customtkinter.CTkImage(
    light_image=Image.open("imagem/botao_pause.png"),
    dark_image=Image.open("imagem/botao_pause.png"),
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
    if primeira == True:
        pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
        pygame.mixer.music.play()
        tocando = True
        primeira = False
    else:
        if tocando == False:
            pygame.mixer.music.unpause()
            tocando = True
        else:
            pygame.mixer.music.pause()
            tocando = False
def botao_proximo(lista_de_musica,label_musica):
    global indice_musica, tocando, primeira
    indice_musica += 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    tocando = True
    primeira = False
    exibir_nome_musica(label_musica,lista_de_musica)
def botao_voltar(lista_de_musica,label_musica):
    global indice_musica
    indice_musica -= 1
    indice_musica %= len(lista_de_musica)
    pygame.mixer.music.load(f'{lista_de_musica[indice_musica]}')
    pygame.mixer.music.play()
    exibir_nome_musica(label_musica,lista_de_musica)
def janela_music_player():
    lista_de_musica = playlist()
    music_player = customtkinter.CTk()
    music_player.grid_columnconfigure(0, weight=1)
    music_player.grid_columnconfigure(1, weight=1)
    music_player.grid_columnconfigure(2, weight=1)
    music_player.grid_rowconfigure(0, weight=1)
    music_player.title('Music Player')
    music_player.geometry('400x325')
    mostrar_imagem(music_player)
    label_musica = customtkinter.CTkLabel(music_player, text="Nenhuma música")
    label_musica.grid(row=1, column=0, columnspan=3)
    def alternar_play_pause():
        botao_play(lista_de_musica)
        layout_botao_play.configure(image=icone_pause if tocando else icone_play)
    layout_botao_play = customtkinter.CTkButton(
        music_player, text='', image=icone_play,
        command=alternar_play_pause,
        fg_color="transparent", hover_color="#2a2a2a",
        width=60, height=60)
    layout_botao_play.grid(row=2, column=1)
    layout_botao_proximo = customtkinter.CTkButton(
        music_player, text='', image=icone_proxima,
        command=lambda: botao_proximo(lista_de_musica, label_musica),
        fg_color="transparent", hover_color="#2a2a2a",
        width=45, height=45)
    layout_botao_proximo.grid(row=2, column=2)
    layout_botao_voltar = customtkinter.CTkButton(
        music_player, text='', image=icone_voltar,
        command=lambda: botao_voltar(lista_de_musica, label_musica),
        fg_color="transparent", hover_color="#2a2a2a",
        width=45, height=45)
    layout_botao_voltar.grid(row=2, column=0)
    exibir_nome_musica(label_musica, lista_de_musica)
    reprodução_automatica(lista_de_musica, music_player, label_musica)
    music_player.mainloop()
def main():
    pygame.mixer.init()
    janela_music_player()
def reprodução_automatica(lista_de_musica, music_player,label_musica):
    if pygame.mixer.music.get_busy() == False and tocando == True and primeira == False:
        botao_proximo(lista_de_musica,label_musica)
    music_player.after(1000, lambda: reprodução_automatica(lista_de_musica, music_player, label_musica))
def exibir_nome_musica(label_musica,lista_de_musica):
    nome = os.path.basename(lista_de_musica[indice_musica]).replace(".mp3", "")
    label_musica.configure(text=nome)
def mostrar_imagem(music_player):
    imagem = Image.open('imagem/gato ouvindo musica.png')
    ctkimagem = customtkinter.CTkImage(imagem,size= (150, 150))
    label_imagem = customtkinter.CTkLabel(music_player,image=ctkimagem, text= '')
    label_imagem.grid(row=0, column=0, columnspan=3)
main()