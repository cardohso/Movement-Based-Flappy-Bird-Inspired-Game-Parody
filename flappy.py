import random
import sys  # Sair do Programa
import pygame
from pygame.locals import *

# PoseDetector
from pose_detector import PoseDetector
import cv2
import mediapipe as mp


id_cotovelo_direito = 14
id_cotovelo_esquerdo = 13
id_mao_direita = 16
id_mao_esquerda = 15
id_ombro_direita = 12
id_ombro_esquerda = 11


# usa a web cam
cap = cv2.VideoCapture(0)

# pose detector instance
detector = PoseDetector()


FPS = 22
scr_width = 600
scr_height = 511
display_screen_window = pygame.display.set_mode((scr_width, scr_height))
play_ground = scr_height * 0.8
game_image = {}
game_audio_sound = {}
player = 'images/tareco.png'
bcg_image = 'images/background.png'
pipe_image = 'images/pipe.png'


def welcome_main_screen():
    p_x = int(scr_width / 5)
    p_y = int((scr_height - game_image['player'].get_height()) / 2)
    menu = 0
 
    while True:
        for event in pygame.event.get():
            # fechar o jogo
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()


            # selecionar opção no menu
            elif event.type == KEYDOWN and event.key == K_SPACE:

                if menu == 0: # iniciar
                    game_audio_sound['start'].play()
                    return
                elif menu == 1: # abrir créditos
                    menu = 3
                elif menu == 2: # sair
                    pygame.quit()
                    sys.exit()
                else: # fechar créditos
                    menu = 2
            
            # descer opção no menu
            elif event.type == KEYDOWN and event.key == K_DOWN:
                game_audio_sound['select'].play()
                if menu == 0:
                    menu = 1
                elif menu == 1:
                    menu = 2
                else:
                    menu = 0

            # subir opção no menu
            elif event.type == KEYDOWN and event.key == K_UP:
                game_audio_sound['select'].play()
                if menu == 1:
                    menu = 0
                elif menu == 2:
                    menu = 1
                else:
                    menu = 2
            

            else:
                display_screen_window.blit(game_image['background'], (0, 0))
                display_screen_window.blit(game_image['player'], (p_x, p_y))
                if menu == 0:
                    display_screen_window.blit(game_image['jogarMENU'], (0, 0))
                elif menu == 1:
                    display_screen_window.blit(game_image['creditosMENU'], (0, 0))
                elif menu == 2:
                    display_screen_window.blit(game_image['sairMENU'], (0, 0))
                else:
                    display_screen_window.blit(game_image['creditosMENU2'], (0,0))
                
                pygame.display.update()
                time_clock.tick(FPS)
                
                
                    
# core
def main_gameplay():    
    score = 0
    p_x = int(scr_width / 5)
    p_y = int(scr_width / 2)
    b_x = 0


    n_pip1 = get_Random_Pipes()


    up_pips = [
        {'x': scr_width + 200, 'y': n_pip1[0]['y']},
       
    ]

    low_pips = [
        {'x': scr_width + 200, 'y': n_pip1[1]['y']},
       
    ]

    pip_Vx = -4

    p_vx = -9
    p_mvx = 10
    
    # Velocidade Descida
    p_accuracy = 0.5

    p_flap_accuracy = -8
    p_flap = False

    braco_direito_em = "baixo"
    success, img = cap.read()
    img, p_landmarks, p_connections = detector.findPose(img, False)
    mp.solutions.drawing_utils.draw_landmarks(img, p_landmarks, p_connections)
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    coordenadas = detector.getPosition(img)

    while True:
        success, img = cap.read()
        img, p_landmarks, p_connections = detector.findPose(img, False)
        mp.solutions.drawing_utils.draw_landmarks(img, p_landmarks, p_connections)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        coordenadas = detector.getPosition(img)
        if coordenadas:
            if coordenadas[id_mao_direita][2] < coordenadas[id_cotovelo_direito][2] < coordenadas[id_ombro_direita][2]:
                print(braco_direito_em)
                braco_direito_em = "cima"
            elif coordenadas[id_mao_direita][2] > coordenadas[id_cotovelo_direito][2] > coordenadas[id_ombro_direita][2]:
                if braco_direito_em == "cima":                    
                    print("flap!")
                    p_vx = p_flap_accuracy
                    p_flap = True
                    game_audio_sound['wing'].play()
                braco_direito_em = "baixo"
                print(braco_direito_em)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if p_y > 0:
                    p_vx = p_flap_accuracy
                    p_flap = True
                    game_audio_sound['wing'].play()

        cr_tst = is_Colliding(p_x, p_y, up_pips,
                              low_pips)
        if cr_tst:
            return


        p_middle_positions = p_x + game_image['player'].get_width() / 2
        for pipe in up_pips:
            pip_middle_positions = pipe['x'] + game_image['pipe'][0].get_width() / 2
            if pip_middle_positions <= p_middle_positions < pip_middle_positions + 4:
                score += 1
                print(f"Pontuação:  {score}")
                game_audio_sound['point'].play()

        if p_vx < p_mvx and not p_flap:
            p_vx += p_accuracy

        if p_flap:
            p_flap = False
        p_height = game_image['player'].get_height()
        p_y = p_y + min(p_vx, play_ground - p_y - p_height)


        for pip_upper, pip_lower in zip(up_pips, low_pips):
            pip_upper['x'] += pip_Vx
            pip_lower['x'] += pip_Vx


        if 0 < up_pips[0]['x'] < 5:
            new_pip = get_Random_Pipes()
            up_pips.append(new_pip[0])
            low_pips.append(new_pip[1])


        if up_pips[0]['x'] < -game_image['pipe'][0].get_width():
            up_pips.pop(0)
            low_pips.pop(0)


        display_screen_window.blit(game_image['background'], (0, 0))
        for pip_upper, pip_lower in zip(up_pips, low_pips):
            display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
            display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))

        display_screen_window.blit(game_image['base'], (b_x, play_ground))
        display_screen_window.blit(game_image['player'], (p_x, p_y))
        d = [int(x) for x in list(str(score))]
        w = 0
        for digit in d:
            w += game_image['numbers'][digit].get_width()
        Xoffset = (scr_width - w) / 2

        for digit in d:
            display_screen_window.blit(game_image['numbers'][digit], (Xoffset, scr_height * 0.12))
            Xoffset += game_image['numbers'][digit].get_width()
        pygame.display.update()
        time_clock.tick(FPS)


def is_Colliding(p_x, p_y, up_pipes, low_pipes):
    """
    Verificar colisão
    """
    if p_y > play_ground - 25 or p_y < 0:
        game_audio_sound['hit'].play()
        return True

    for pipe in up_pipes:
        pip_h = game_image['pipe'][0].get_height()
        if (p_y < pip_h + pipe['y'] and abs(p_x - pipe['x']) < game_image['pipe'][0].get_width()):
            game_audio_sound['hit'].play()
            return True

    for pipe in low_pipes:
        if (p_y + game_image['player'].get_height() > pipe['y']) and abs(p_x - pipe['x']) < \
                game_image['pipe'][0].get_width():
            game_audio_sound['hit'].play()
            return True

    return False


def get_Random_Pipes():
    """
    Gera posições para os dois canos
    """
    pip_h = game_image['pipe'][0].get_height()
    off_s = int(scr_height / 2.5)
    yes2 = off_s + random.randrange(0, int(scr_height - game_image['base'].get_height() - 1.2 * off_s))
    pipeX = scr_width + 1
    y1 = pip_h - yes2 + off_s
    pipe = [
        {'x': pipeX, 'y': -y1},  # cano superior
        {'x': pipeX, 'y': yes2}  # cano inferior
    ]
    return pipe


if __name__ == "__main__":

    pygame.init()
    time_clock = pygame.time.Clock()
    pygame.display.set_caption('Tareco´s Magical Adventure')
    game_image['numbers'] = (
        pygame.image.load('images/0.png').convert_alpha(),
        pygame.image.load('images/1.png').convert_alpha(),
        pygame.image.load('images/2.png').convert_alpha(),
        pygame.image.load('images/3.png').convert_alpha(),
        pygame.image.load('images/4.png').convert_alpha(),
        pygame.image.load('images/5.png').convert_alpha(),
        pygame.image.load('images/6.png').convert_alpha(),
        pygame.image.load('images/7.png').convert_alpha(),
        pygame.image.load('images/8.png').convert_alpha(),
        pygame.image.load('images/9.png').convert_alpha(),
    )

    game_image['jogarMENU'] = pygame.image.load('images/jogarMENU.png').convert_alpha()
    game_image['creditosMENU'] = pygame.image.load('images/creditosMENU.png').convert_alpha()
    game_image['creditosMENU2'] = pygame.image.load('images/creditosMENU2.png').convert_alpha()
    game_image['sairMENU'] = pygame.image.load('images/sairMENU.png').convert_alpha()
    game_image['base'] = pygame.image.load('images/base.png').convert_alpha()
    game_image['pipe'] = (pygame.transform.rotate(pygame.image.load(pipe_image).convert_alpha(), 180),
                          pygame.image.load(pipe_image).convert_alpha()
                          )
    
    game_image['background'] = pygame.image.load(bcg_image).convert()
    game_image['player'] = pygame.image.load(player).convert_alpha()
    
    # Sons
    game_audio_sound['die'] = pygame.mixer.Sound('sounds/die.wav')
    game_audio_sound['hit'] = pygame.mixer.Sound('sounds/hit.wav')
    game_audio_sound['point'] = pygame.mixer.Sound('sounds/point.wav')
    game_audio_sound['wing'] = pygame.mixer.Sound('sounds/wing.wav')
    game_audio_sound['start'] = pygame.mixer.Sound('sounds/start.wav')
    game_audio_sound['select'] = pygame.mixer.Sound('sounds/select.flac')
    

    while True:
        welcome_main_screen()  # Mostra o menu principal
        main_gameplay()  # Inicia o jogo



        #Miguel Santos nº16 12ºE
        #Tiago Gregório nº23 12ºE
        #João Cardoso nº13 12ºA