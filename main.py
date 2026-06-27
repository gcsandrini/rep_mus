import customtkinter
import pygame
import os
from PIL import Image
indice_musica = 0
tocando = False
primeira = True
def playlist():
    lista_de_musicas = []
    musicas = os.listdir('musicas')
    for musica in musicas:
        lista_de_musicas.append("musicas/" + musica)
    return lista_de_musicas
def botao_play(x):
    global tocando
    global primeira
    if primeira == True:
        pygame.mixer.music.load(f'{x[indice_musica]}')
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
def botao_proximo(x,y,z):
    global indice_musica
    indice_musica += 1
    indice_musica %= len(x)
    pygame.mixer.music.load(f'{x[indice_musica]}')
    pygame.mixer.music.play()
    exibir_nome_musica(y,z)
    return x, indice_musica
def botao_voltar(x,y,z):
    global indice_musica
    indice_musica -= 1
    indice_musica %= len(x)
    pygame.mixer.music.load(f'{x[indice_musica]}')
    pygame.mixer.music.play()
    exibir_nome_musica(y,z)
    return x, indice_musica
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
    layout_botao_play = customtkinter.CTkButton(music_player, text ='play', command = lambda: botao_play(lista_de_musica), width = 60, height = 60)
    layout_botao_play.grid(row=2, column=1)
    layout_botao_proximo = customtkinter.CTkButton(music_player, text ='proxima', command = lambda: botao_proximo(lista_de_musica,label_musica,lista_de_musica), width = 45, height = 45)
    layout_botao_proximo.grid(row=2, column=2)
    layout_botao_voltar = customtkinter.CTkButton(music_player, text ='anterior', command = lambda: botao_voltar(lista_de_musica,label_musica,lista_de_musica), width = 45, height = 45)
    layout_botao_voltar.grid(row=2, column=0)
    exibir_nome_musica(label_musica,lista_de_musica)
    reprodução_automatica(lista_de_musica, music_player)
    music_player.mainloop()
def main():
    pygame.mixer.init()
    janela_music_player()
def reprodução_automatica(x,y):
    if pygame.mixer.music.get_busy() == False and tocando == True and primeira == False:
        botao_proximo(x)
    y.after(1000, lambda: reprodução_automatica(x,y))
def exibir_nome_musica(x,y):
    x.configure(text="Nome da música aqui")
    nome = os.path.basename(y[indice_musica]).replace(".mp3", "")
    x.configure(text=nome)
def mostrar_imagem(x):
    imagem = Image.open('imagem/gato ouvindo musica.png')
    ctkimagem = customtkinter.CTkImage(imagem,size= (150, 150))
    label_imagem = customtkinter.CTkLabel(x,image=ctkimagem, text= '')
    label_imagem.grid(row=0, column=0, columnspan=3)
main()