import customtkinter
import pygame
import os
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
def botao_proximo(x):
    global indice_musica
    indice_musica += 1
    indice_musica %= len(x)
    pygame.mixer.music.load(f'{x[indice_musica]}')
    pygame.mixer.music.play()
    return x, indice_musica
def botao_voltar(x):
    global indice_musica
    indice_musica -= 1
    indice_musica %= len(x)
    pygame.mixer.music.load(f'{x[indice_musica]}')
    pygame.mixer.music.play()
    return x, indice_musica
def janela_music_player():
    lista_de_musica = playlist()
    music_player = customtkinter.CTk()
    music_player.title('Music Player')
    music_player.geometry('400x150')
    layout_botao_play = customtkinter.CTkButton(music_player, text ='play', command = lambda: botao_play(lista_de_musica), width = 60, height = 60)
    layout_botao_play.grid(row = 2, column = 2, padx = 75, pady = 75)
    layout_botao_proximo = customtkinter.CTkButton(music_player, text ='proxima', command = lambda: botao_proximo(lista_de_musica), width = 45, height = 45)
    layout_botao_proximo.grid(row = 2, column = 3, padx = 20, pady = 20)
    layout_botao_voltar = customtkinter.CTkButton(music_player, text ='anterior', command = lambda: botao_voltar(lista_de_musica), width = 45, height = 45)
    layout_botao_voltar.grid(row = 2, column = 1, padx = 20, pady = 20)
    reprodução_automatica(lista_de_musica)
    music_player.mainloop()
def main():
    pygame.mixer.init()
    janela_music_player()
def reprodução_automatica(x):
    if pygame.mixer.music.get_busy() == False and tocando == False and primeira == False:
        botao_proximo(x)
main()