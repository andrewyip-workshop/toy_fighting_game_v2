import pygame 
pygame.init()
import math 
import random 
import json 
import os
from os.path import isfile 
import sys

clicking = False 

#Functions 
def load_image(img, scale): 
    img = pygame.image.load(img)
    width = img.get_width() 
    height = img.get_height() 
    ratio = width / height 
    img = pygame.transform.scale(img, (int(width * scale), int(width * scale/ratio)))
    return img 

def scale_image(img, scale): 
    width = img.get_width() 
    height = img.get_height() 
    ratio = width / height 
    img = pygame.transform.scale(img, (width * scale, (width * scale/ratio)))
    return img    

def draw(): 
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    screen_3.fill(TRANSPARENT)    

    for player in all_players: 
        p_img = scale_image(player.animation["static"][0], 0.5)
        screen.blit(p_img, (10, OFFSET_Y-p_img.get_height()))
        header_text_1 = SMALL_FONT.render(player.name, 1, WHITE)
        screen.blit(header_text_1, (200, 30))        
        pygame.draw.rect(screen_3, LIGHTRED_ALPHA, (200, 50, 240, 20))
        pygame.draw.rect(screen_3, LIGHTGREEN, (200, 50, 240 * player.health/player.max_health, 20))  
    total_enemy_health = 0 
    total_enemy_max_health = 0
    pos_x = SCREEN_WIDTH - 10
    for enemy in all_enemies: 
        e_img = pygame.transform.flip(scale_image(enemy.animation["static"][0], 0.5), True, False)
        screen.blit(e_img, (pos_x - e_img.get_width(), OFFSET_Y - e_img.get_height()))
        pos_x -= 100
        total_enemy_health += enemy.health
        total_enemy_max_health += enemy.max_health 
        header_text_2 = SMALL_FONT.render("Enemies", 1, WHITE)
        screen.blit(header_text_2, (SCREEN_WIDTH - 200 - header_text_2.get_width(), 30))
        pygame.draw.rect(screen_3, LIGHTRED_ALPHA, (460, 50, 240, 20))
        pygame.draw.rect(screen_3, LIGHTGREEN, (460 + 240 * (1- total_enemy_health/total_enemy_max_health ), 50, 240 * total_enemy_health/total_enemy_max_health, 20))  
    
    header_text_3 = BIG_FONT.render(f"Stage {gameboard.stage}", 1, WHITE)
    screen.blit(header_text_3, (SCREEN_WIDTH // 2 - header_text_3.get_width() //2, 10))


    if gameboard.turn == "enemy": 
        message_text = SMALL_FONT.render("Enemies are moving...", 1, WHITE)
        screen.blit(message_text, (100, SCREEN_HEIGHT - 75))

    elif gameboard.turn =="player": 
        if gameboard.selected_l == None: 
            selected_unit_text = SMALL_FONT.render("[Left click] to select your unit.", 1, WHITE)        
        if gameboard.selected_r != None: 
            selected_unit_text = SMALL_FONT.render(f"[Right click] select a place to attack. There are {gameboard.avail_targets} targets!", 1, WHITE)        
        elif gameboard.selected_l != None:             
            selected_unit_text = SMALL_FONT.render("[Left click] select a place to move.", 1, WHITE)
        
        screen.blit(selected_unit_text, (100, SCREEN_HEIGHT - 75))

    exit_button = (SCREEN_WIDTH - 110, SCREEN_HEIGHT - 80, 100, 50)
    change_button = (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 80, 100, 50)   
    mpos = pygame.mouse.get_pos()
    if pygame.Rect(exit_button).collidepoint(mpos): 
        if clicking == True: 
            pygame.quit()
            sys.exit()
        else: 
            pygame.draw.rect(screen_3, LIGHTRED, exit_button)
    else: 
        pygame.draw.rect(screen_3, LIGHTRED_ALPHA, exit_button)
    
    if pygame.Rect(change_button).collidepoint(mpos): 
        if clicking == True:
            for player in all_players: 
                player.health = 0
        else:  
            pygame.draw.rect(screen_3, LIGHTBLUE, change_button)
    else: 
        pygame.draw.rect(screen_3, LIGHTBLUE_ALPHA, change_button)        
    
    button_text_1 = SMALL_FONT.render("Exit", 1, WHITE)
    button_text_2 = SMALL_FONT.render("Change unit", 1, WHITE)
    screen_3.blit(button_text_1, (SCREEN_WIDTH - 110+10, SCREEN_HEIGHT - 80+15))
    screen_3.blit(button_text_2, (SCREEN_WIDTH - 220+10, SCREEN_HEIGHT - 80+15))
    screen.blit(screen_3, (0,0))

    gameboard.draw()
    pygame.display.update()

def get_grid_pos(pos): 
    x, y = pos 
    col = (x - OFFSET_X) // SQUARE_SIZE
    row = (y - OFFSET_Y)  // SQUARE_SIZE
    return row, col

def load_data(player_choice, enemy_num):
    df = open("units/all_units.json", "r")
    units_data = json.load(df)
    df.close() 
    units_list = list(units_data)
    #player_choice = random.choice(units_list)
    player = Unit("player", 5, 3, units_data[player_choice][0], units_data[player_choice][1], units_data[player_choice][2], units_data[player_choice][3], units_data[player_choice][4])
    all_units.add(player)
    all_players.add(player)
    gameboard.board[player.row][player.col] = player      
    for i in range(min(enemy_num, 7)): 
        pos_row = [2,3,4,5,6,7,8]
        pos_col = [6,5,6,5,6,5,6]    
        enemy_choice = random.choice(units_list)
        enemy = Unit("enemy", pos_row[i], pos_col[i], units_data[enemy_choice][0], units_data[enemy_choice][1], units_data[enemy_choice][2], units_data[enemy_choice][3], units_data[enemy_choice][4])
        all_units.add(enemy)
        all_enemies.add(enemy)
        gameboard.board[enemy.row][enemy.col] = enemy
        gameboard.num_of_enemies += 1
    return player 


def load_animation(short_name): 
    path = os.path.join("units/" + short_name + "/")
    unit_animation = {}
    unit_animation["static"] = [] 
    unit_animation["idle"] = [] 
    unit_animation["move"] = []
    unit_animation["attack"] = [] 
    stat_img = pygame.image.load(os.path.join(path + "static/" + "static.png") )
    unit_animation["static"].append(scale_image(stat_img, 1))
    for f in os.listdir(os.path.join(path + "idle/")):
        if isfile(path + "idle/" + f) and f.endswith(".png"): 
            file_path = os.path.join(path + "idle/" + f)
            unit_animation["idle"].append(load_image(file_path, 1)) 

    for f in os.listdir(os.path.join(path + "attack/")):
        if isfile(path + "attack/" + f)and f.endswith(".png"):
            file_path = os.path.join(path + "attack/" + f) 
            unit_animation["attack"].append(load_image(file_path, 1)) 

    for f in os.listdir(os.path.join(path + "move/")):
        if isfile(path + "move/" + f) and f.endswith(".png"): 
            file_path = os.path.join(path + "move/" + f)
            unit_animation["move"].append(load_image(file_path, 1)) 

    return unit_animation 

def sortie_page(): 
    player_choice = 0
    df = open("units/all_units.json", "r")
    units_data = json.load(df)
    df.close() 
    units_list = list(units_data)
    waiting = True 

    while waiting: 
        clock.tick(FPS)
        screen.fill(BLACK)
        screen.blit(background_img, (0, 0))
        intro_text_1 = HUGE_FONT.render("TOYS WAR GAME", 1, SILVER)
        screen.blit(intro_text_1, (SCREEN_WIDTH //2 - intro_text_1.get_width()//2, SCREEN_HEIGHT //4 - 50))
        intro_text_2 = BIG_FONT.render("Sortie Preparations", 1, SILVER)
        screen.blit(intro_text_2, (SCREEN_WIDTH //2 - intro_text_2.get_width()//2, SCREEN_HEIGHT //4 ))
        path = os.path.join("units/" + units_list[player_choice] + "/static/static.png") 
        player_img = pygame.image.load(path)
        screen.blit(player_img, (150, 475 - player_img.get_height()))        
        player_text_1 = SMALL_FONT.render(f"Unit Name :  {units_data[units_list[player_choice]][1]}", 1, WHITE) 
        screen.blit(player_text_1, (400, 400 ))
        player_text_2 = SMALL_FONT.render(f"Mobility :  {units_data[units_list[player_choice]][2]}", 1, WHITE) 
        screen.blit(player_text_2, (400, 420 ))
        player_text_3 = SMALL_FONT.render(f"Weapon Range :  {units_data[units_list[player_choice]][3]}", 1, WHITE) 
        screen.blit(player_text_3, (400, 440 ))
        player_text_4 = SMALL_FONT.render(f"Health :  {units_data[units_list[player_choice]][4]}", 1, WHITE) 
        screen.blit(player_text_4, (400, 460 ))
        intro_text_3 = BIG_FONT.render("[UP] [DOWN] to select unit, [SPACE] to start...", 1, WHITE)
        screen.blit(intro_text_3, (SCREEN_WIDTH //2 - intro_text_3.get_width()//2, 600 ))

        pygame.display.update()
        
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_SPACE:
                    waiting = False
                if event.key == pygame.K_UP:
                    player_choice = (player_choice - 1) % len(units_list)  
                if event.key == pygame.K_DOWN:
                    player_choice = (player_choice + 1) % len(units_list)  

    return units_list[player_choice]

# setup screen
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Toys War") 
screen_2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
screen_shake = 0 
screen_3 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)


#Set game variables 
ROWS = 10
COLS= 10
SQUARE_SIZE = 70
OFFSET_X = ( SCREEN_WIDTH - SQUARE_SIZE * COLS ) // 2 
OFFSET_Y = ( SCREEN_HEIGHT - SQUARE_SIZE * ROWS ) // 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SILVER = (165, 169, 180)
RED_ALPHA = (255, 0, 0, 100)
BLUE_ALPHA = (0, 0, 255, 100)
GREEN_ALPHA = (0, 255, 0, 100)
TRANSPARENT = (0, 0, 0, 0)
LIGHTGREEN = (144, 238, 144)
LIGHTGREEN_ALPHA = (144, 238, 144, 100)
LIGHTRED = (255, 127, 127)
LIGHTRED_ALPHA = (255, 127, 127, 100)
LIGHTBLUE = (159, 195, 233)
LIGHTBLUE_ALPHA = (159, 195, 233, 100)
HUGE_FONT = pygame.font.SysFont("comicsans", 35)
BIG_FONT = pygame.font.SysFont("comicsans", 25)
SMALL_FONT = pygame.font.SysFont("comicsans", 15)



#set frame rate 
clock = pygame.time.Clock() 
FPS = 60 

#load game images 
background_img = pygame.image.load("img/background.jpg")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
pointer_img = pygame.image.load("img/pointer.png")

#load images 
bullet_animation = [] 
for i in  range (13): 
    bullet_img = pygame.image.load(f"img/bullet/{i}.png")
    bullet_animation.append(scale_image(bullet_img, 0.2)) 
explosion_animation = [] 
for i in  range (15): 
    explosion_img = pygame.image.load(f"img/explosion/{i}.png")
    explosion_animation.append(scale_image(explosion_img, 0.3)) 
slash_animation = [] 
for i in  range (7): 
    slash_img = pygame.image.load(f"img/slash/{i}.png")
    slash_animation.append(scale_image(slash_img, 0.5)) 
for i in  range (7): 
    slash_img = pygame.image.load(f"img/slash/{i}.png")
    slash_img = pygame.transform.flip(slash_img, True, False)
    slash_animation.append(scale_image(slash_img, 0.5))




#Classes 
class Board:
    def __init__(self):
        self.board = [] 
        self.create_board()
        self.selected_l = None
        self.selected_r = None 
        self.avail_move = []
        self.avail_shoot = []
        self.avail_targets = 0
        self.enemy_avail_moves = [] 
        self.enemy_avail_shoots = [] 
        self.ai_moving = False 
        self.turn = "player"
        self.change_turn_counter = 0 
        self.restart_counter = 0
        self.restart = False 
        self.stage = 1 
        self.next_stage_counter = 0
        self.next_stage = False 
        self.num_of_enemies = 0

     
    def draw(self): 

        screen_2.fill(TRANSPARENT)
        for row in range(ROWS): 
            for col in range(COLS): 
                pygame.draw.rect(screen, WHITE, (col*SQUARE_SIZE+OFFSET_X, row*SQUARE_SIZE+OFFSET_Y, SQUARE_SIZE, SQUARE_SIZE), 1)
                unit = gameboard.board[row][col] 
                if unit != 0:
                    x = col * SQUARE_SIZE + OFFSET_X
                    y = row * SQUARE_SIZE + OFFSET_Y
                    pygame.draw.rect(screen_2, GREEN_ALPHA, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        
        if len(self.avail_move) != 0: 
            for pos in self.avail_move:
                row, col = pos 
                x = col * SQUARE_SIZE + OFFSET_X
                y = row * SQUARE_SIZE + OFFSET_Y
                pygame.draw.rect(screen_2, RED_ALPHA, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            mpos = pygame.mouse.get_pos()
            m_x, m_y = mpos  
            unit_mask = pygame.mask.from_surface(self.selected_l.image)
            unit_shadow = unit_mask.to_surface(setcolor = (0, 0, 0, 180), unsetcolor = (0, 0, 0, 0))
            screen_2.blit(unit_shadow, (m_x - self.selected_l.image.get_width() //2, m_y - self.selected_l.image.get_height()//2) )
        if len(self.avail_shoot) != 0: 
            for pos in self.avail_shoot:
                row, col = pos 
                x = col * SQUARE_SIZE + OFFSET_X
                y = row * SQUARE_SIZE + OFFSET_Y
                pygame.draw.rect(screen_2, BLUE_ALPHA, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                if row < ROWS and col < COLS and self.board[row][col] != 0: 
                    pygame.draw.rect(screen_2, WHITE, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            mpos = pygame.mouse.get_pos()
            m_x, m_y = mpos 
            screen_2.blit(pointer_img, (m_x - pointer_img.get_width() //2, m_y - pointer_img.get_height()//2) ) 


        if len(self.enemy_avail_moves) != 0: 
            for pos in self.enemy_avail_moves:
                row, col = pos 
                x = col * SQUARE_SIZE + OFFSET_X
                y = row * SQUARE_SIZE + OFFSET_Y
                pygame.draw.rect(screen_2, RED_ALPHA, (x, y, SQUARE_SIZE, SQUARE_SIZE))
        if len(self.enemy_avail_shoots) != 0: 
            for pos in self.enemy_avail_shoots:
                row, col = pos 
                x = col * SQUARE_SIZE + OFFSET_X
                y = row * SQUARE_SIZE + OFFSET_Y
                pygame.draw.rect(screen_2, BLUE_ALPHA, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        all_flyings.draw(screen_2)

        for row in range (ROWS):
            for col in range (COLS): 
                unit = gameboard.board[row][col] 
                if unit != 0:
                    unit.draw_unit() 
        
        all_bullets.draw(screen_2)
        all_slashes.draw(screen_2)
        for beam in all_beams: 
            beam.draw()         
        all_explosions.draw(screen_2)

        screen_shake_offset = (random.random() * screen_shake - screen_shake/2, random.random() * screen_shake - screen_shake/2)
        screen.blit(screen_2, (screen_shake_offset))


    def create_board(self): 
        for row in range(ROWS): 
            self.board.append([])
            for col in range (COLS):
                self.board[row].append(0) 

    def clear_board(self):
        for row in range(ROWS): 
            for col in range (COLS):
                self.board[row][col] = 0          
        self.selected_l = None
        self.selected_r = None 
        self.avail_move = []
        self.avail_shoot = []
        self.enemy_avail_moves = [] 
        self.enemy_avail_shoots = [] 
        self.ai_moving = False 
        self.turn = "player"
        self.change_turn_counter = 0 


    def select_unit(self, row, col): 
        if self.selected_l:   #check if this is the second click
            self.place_unit(self.selected_l, row, col)
        else:   # else if this is the first click 
            unit = self.board[row][col]
            if unit != 0 and unit.type == "player": 
                self.selected_l = unit
                self.selected_r = None
                self.avail_shoot = []   
                self.avail_move = self.selected_l.calc_avail_move()
                self.board[row][col].frame = 0
                self.board[row][col].action = "move"
                
    def place_unit(self, unit, row, col): 
        if row < ROWS: 
            if (row, col) in unit.avail_move and self.board[row][col] == 0: 
                flying = Flying(unit, unit.row, unit.col, row, col)
                all_flyings.add(flying)
                self.board[unit.row][unit.col], self.board[row][col] = self.board[row][col], self.board[unit.row][unit.col] # this is copy only, not change the row, col , x , y data yet
                self.board[row][col].move(row, col)
                self.board[row][col].avail_move = [] 
                self.board[row][col].frame = 0
                self.board[row][col].action = "idle"
                self.avail_move = [] 
                self.before_shoot(unit.row, unit.col) 
            elif row == unit.row and col == unit.col: 
                self.board[row][col].avail_move = [] 
                self.board[row][col].frame = 0
                self.board[row][col].action = "idle"
                self.avail_move = [] 
                self.before_shoot(unit.row, unit.col)     
                              
            else: 
                self.board[unit.row][unit.col].frame = 0
                self.board[unit.row][unit.col].action = "idle"
                self.selected_l = None 
                self.avail_move = [] 

        else: 
            self.board[unit.row][unit.col].frame = 0
            self.board[unit.row][unit.col].action = "idle"
            self.selected_l = None 
            self.avail_move = [] 


    def before_shoot(self, row, col): 
        if self.selected_r and self.avail_targets == 0: 
            self.board[self.selected_r.row][self.selected_r.col].frame = 0
            self.board[self.selected_r.row][self.selected_r.col].action = "idle"            
            self.selected_r = None
            self.selected_l = None 
            self.avail_shoot = []
            self.turn = "enemy" 
        elif self.selected_r:  
            self.shoot(self.selected_r, row, col) 
        else:   
            unit = self.board[row][col]
            if unit != 0 and unit.type == "player": 
                self.selected_r = unit 
                #self.selected_l = None
                self.avail_move = []  
                self.avail_targets = 0 
                self.avail_shoot = self.selected_r.calc_avail_shoot()
                for pos in self.avail_shoot:
                    t_row, t_col = pos
                    if t_row < ROWS and t_col < COLS and self.board[t_row][t_col] != 0:
                        self.avail_targets += 1
                self.board[row][col].frame = 0
                self.board[row][col].action = "attack"


    def shoot(self, unit, row, col): 
        if row < ROWS:         
            if (row, col) in unit.avail_shoot: 
                if unit.range == 3: 
                    beam = Beam(unit.row, unit.col, row, col)
                    all_beams.append(beam)
                elif unit.range == 1: 
                    slash = Slash(row, col)
                    all_slashes.add(slash)
                else: 
                    bullet = Bullet(unit.row, unit.col, row, col)
                    all_bullets.add(bullet)                
                self.board[unit.row][unit.col].frame = 0
                self.board[unit.row][unit.col].action = "idle"
                self.avail_shoot = [] 
                self.selected_r = None
                self.selected_l = None  
                self.turn = "enemy"

    
    
    def ai_before_move(self): 
        for enemy in all_enemies: 
            enemy_avail_move = enemy.calc_avail_move()
            self.enemy_avail_moves.extend(enemy_avail_move)
            self.board[enemy.row][enemy.col].frame = 0 
            self.board[enemy.row][enemy.col].action = "move" 
    
    def ai_move(self): 
        for enemy in all_enemies: 
            enemy_avail_move = enemy.calc_avail_move()
            t_row, t_col = random.choice(enemy_avail_move)
            if t_row >= 0 and t_row < ROWS and t_col >=0 and t_col < COLS:
                if self.board[t_row][t_col] == 0:  
                    flying = Flying(enemy, enemy.row, enemy.col, t_row, t_col)
                    all_flyings.add(flying)
                    self.board[enemy.row][enemy.col], self.board[t_row][t_col] = self.board[t_row][t_col], self.board[enemy.row][enemy.col]
                    self.board[t_row][t_col].move(t_row, t_col)
        self.enemy_avail_moves = [] 

    def ai_before_shoot(self): 
        for enemy in all_enemies: 
            enemy_avail_shoot = enemy.calc_avail_shoot()
            self.enemy_avail_shoots.extend(enemy_avail_shoot)
            self.board[enemy.row][enemy.col].frame = 0 
            self.board[enemy.row][enemy.col].action = "attack"         

    def ai_shoot(self): 
        for enemy in all_enemies: 
            enemy_avail_shoot = enemy.calc_avail_shoot()
            if (player.row, player.col) in enemy_avail_shoot: 
                if enemy.range == 3: 
                    beam = Beam(enemy.row, enemy.col, player.row, player.col)
                    all_beams.append(beam)
                elif enemy.range == 1: 
                    slash = Slash(player.row, player.col)
                    all_slashes.add(slash)
                else: 
                    bullet = Bullet(enemy.row, enemy.col, player.row, player.col)
                    all_bullets.add(bullet)                  
                self.board[enemy.row][enemy.col].frame = 0
                self.board[enemy.row][enemy.col].action = "idle"
            else: 
                self.board[enemy.row][enemy.col].frame = 0
                self.board[enemy.row][enemy.col].action = "idle"     
        self.enemy_avail_shoots = []           
    
    def restart_process(self):
        self.turn = "player"
        self.restart = True
        self.restart_counter += 1 
        if self.restart_counter <= 100: 
            message_text = BIG_FONT.render("Game over...", 1, WHITE)
            screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width()//2 , SCREEN_HEIGHT // 2 - message_text.get_height()//2 - 50))
        elif self.restart_counter > 100: 
            message_text = BIG_FONT.render("Restarting...", 1, WHITE)
            screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width()//2 , SCREEN_HEIGHT // 2 - message_text.get_height()//2 - 50))        
        if self.restart_counter == 150: 
            self.restart = False 
            self.restart_counter = 0
            self.clear_board()
            self.num_of_enemies = 0
            self.stage = 1 
            for enemy in all_enemies: 
                enemy.kill()             
            return True
        
        pygame.display.update()

    def next_stage_process(self):
        self.turn = "player"
        self.next_stage = True
        self.next_stage_counter += 1 
        if self.next_stage_counter <= 100: 
            message_text = BIG_FONT.render("Stage clear...", 1, WHITE)
            screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width()//2 , SCREEN_HEIGHT // 2 - message_text.get_height()//2 - 50))
        elif self.next_stage_counter > 100: 
            message_text = BIG_FONT.render("Next Stage...", 1, WHITE)
            screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width()//2 , SCREEN_HEIGHT // 2 - message_text.get_height()//2 - 50))
        if self.next_stage_counter == 150:  
            self.next_stage = False 
            self.next_stage_counter = 0
            self.clear_board()          
            self.num_of_enemies = 0 
            self.stage += 1
            for player in all_players:
                player.kill()
            player = load_data(player_choice, self.stage)
            return player 

        pygame.display.update()

      
    def enemies_process(self):
        self.change_turn_counter += 1 
        if self.change_turn_counter == 25: 
            self.ai_before_move()
        if self.change_turn_counter == 50: 
            self.ai_move()
        if self.change_turn_counter == 75: 
            self.ai_before_shoot()        
        if self.change_turn_counter == 100: 
            self.change_turn_counter = 0 
            self.ai_shoot()            
            self.turn = "player" 


class Unit(pygame.sprite.Sprite): 
    def __init__(self, type, row, col, short_name, name, speed, range, health):
        pygame.sprite.Sprite.__init__(self)         
        self.type = type
        self.short_name = short_name
        self.animation = load_animation(self.short_name) 
        self.action = "idle"
        self.image = self.animation[self.action][0]
        self.rect = self.image.get_rect() 
        self.move(row, col) 
        self.name = name 
        self.speed = speed
        self.avail_move = []
        self.health = health 
        self.max_health = health  
        self.range = range
        self.avail_shoot = [] 
        self.frame = 0
        self.last_update = pygame.time.get_ticks()  

    def update(self):  
        if len(self.animation[self.action]) == 1: 
            if self.col + 1 <= COLS//2 :
                self.image = pygame.transform.flip(self.animation[self.action][0], True, False)
                self.calc_pos()          
            elif self.col + 1 > COLS//2 : 
                self.image = self.animation[self.action][0]
                self.calc_pos()
        elif len(self.animation[self.action]) > 1: 
            now = pygame.time.get_ticks() 
            if now - self.last_update > 80: 
                self.last_update = now         
                self.frame += 1
                if self.frame == len(self.animation[self.action]): 
                    self.frame = 0              
                else: 
                    if self.col + 1 <= COLS//2 :
                        self.image = pygame.transform.flip(self.animation[self.action][self.frame], True, False)
                        self.calc_pos()          
                    elif self.col + 1 > COLS//2 : 
                        self.image = self.animation[self.action][self.frame]
                        self.calc_pos()
        
        if self.health <=0: 
            expl = Explosion(self.rect.centerx, self.rect.centery)
            all_explosions.add(expl)
            gameboard.board[self.row][self.col] = 0 
            if self.type == "enemy":
                gameboard.num_of_enemies -= 1
                self.kill()
            elif self.type == "player":
                self.kill()           

    def calc_pos(self): 
        self.rect.x = self.col * SQUARE_SIZE + OFFSET_X - (self.image.get_width()-SQUARE_SIZE)//2
        self.rect.y = self.row * SQUARE_SIZE + OFFSET_Y - (self.image.get_height()-SQUARE_SIZE)

    def draw_unit(self): 
        screen_2.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen_2, LIGHTRED_ALPHA, (self.rect.centerx-25, self.rect.y - 5, 50, 3))
        pygame.draw.rect(screen_2, LIGHTGREEN, (self.rect.centerx-25, self.rect.y - 5, 50 * self.health/self.max_health, 3))  

    def move(self, t_row, t_col): 
        self.row = t_row 
        self.col = t_col 
        self.calc_pos() 

    def calc_avail_move(self): 
        self.avail_move = []
        if self.speed == 1: 
            avail_move_temp  = [(self.row -1, self.col), (self.row+1, self.col), (self.row, self.col-1), (self.row, self.col+1), (self.row, self.col) ]
            for pos in avail_move_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_move.append(pos)          
        elif self.speed == 2: 
            avail_move_temp  = [(self.row -1, self.col), (self.row+1, self.col), (self.row, self.col-1), (self.row, self.col+1), (self.row, self.col), 
                                (self.row -2, self.col), (self.row+2, self.col), (self.row, self.col-2), (self.row, self.col+2), 
                                (self.row -1, self.col-1), (self.row+1, self.col-1), (self.row-1, self.col+1), (self.row+1, self.col+1)
                                ]            
            for pos in avail_move_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_move.append(pos)          
        else: 
            avail_move_temp  = [(self.row -1, self.col), (self.row+1, self.col), (self.row, self.col-1), (self.row, self.col+1), (self.row, self.col), 
                                (self.row -2, self.col), (self.row+2, self.col), (self.row, self.col-2), (self.row, self.col+2), 
                                (self.row -1, self.col-1), (self.row+1, self.col-1), (self.row-1, self.col+1), (self.row+1, self.col+1), 
                                (self.row -3, self.col), (self.row+3, self.col), (self.row, self.col-3), (self.row, self.col+3), 
                                (self.row -1, self.col-2), (self.row-2, self.col-1), 
                                (self.row -1, self.col+2), (self.row-2, self.col+1),
                                (self.row+2, self.col-1), (self.row+1, self.col-2),
                                (self.row+2, self.col+1), (self.row+1, self.col+2)
                                ]            
            for pos in avail_move_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_move.append(pos)    
        return self.avail_move

    def calc_avail_shoot(self): 
        self.avail_shoot = [] 
        if self.range == 1: 
            avail_shoot_temp  = [(self.row -1, self.col), (self.row+1, self.col), (self.row, self.col-1), (self.row, self.col+1) ]
            for pos in avail_shoot_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_shoot.append(pos)  
        elif self.range == 2: 
            avail_shoot_temp  = [(self.row -2, self.col), (self.row+2, self.col), (self.row, self.col-2), (self.row, self.col+2), 
                                (self.row -1, self.col-1), (self.row+1, self.col-1), (self.row-1, self.col+1), (self.row+1, self.col+1)
                                ]            
            for pos in avail_shoot_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_shoot.append(pos)          
        else: 
            avail_shoot_temp  = [(self.row -3, self.col), (self.row+3, self.col), (self.row, self.col-3), (self.row, self.col+3), 
                                (self.row -1, self.col-2), (self.row-2, self.col-1), 
                                (self.row -1, self.col+2), (self.row-2, self.col+1), 
                                (self.row+2, self.col-1), (self.row+1, self.col-2),
                                (self.row+2, self.col+1), (self.row+1, self.col+2)
                                ]            
            for pos in avail_shoot_temp: 
                if pos[1] * SQUARE_SIZE + OFFSET_X >= 0 + OFFSET_X  and pos[1] * SQUARE_SIZE + OFFSET_X < SCREEN_WIDTH - OFFSET_X and pos[0] * SQUARE_SIZE + OFFSET_Y >= 0 + OFFSET_Y and pos[0] * SQUARE_SIZE + OFFSET_Y < SCREEN_HEIGHT - OFFSET_Y: 
                    self.avail_shoot.append(pos)    
        return self.avail_shoot
        

class Flying(pygame.sprite.Sprite):
    def __init__ (self, unit, row, col, t_row, t_col):
        pygame.sprite.Sprite.__init__(self)
        self.row = row 
        self.col = col
        self.t_row = t_row
        self.t_col = t_col 
        self.animation = unit.animation["move"]
        self.o_image = self.animation[0]
        unit_mask = pygame.mask.from_surface(self.o_image)
        self.image = unit_mask.to_surface(setcolor = (0, 0, 0, 180), unsetcolor = (0, 0, 0, 0))
        self.frame = 0 
        self.rect = self.o_image.get_rect() 
        self.speed = 10
        self.rect.x = int(self.col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 - self.o_image.get_width()//2)
        self.rect.y = int(self.row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 - self.o_image.get_height()//2)
        self.t_x = int(self.t_col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 - self.o_image.get_width()//2) 
        self.t_y = int(self.t_row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 - self.o_image.get_height()//2)
        self.angle = 0 


    def update(self): 

        x_diff = self.t_x - self.rect.x 
        y_diff = self.t_y - self.rect.y 
        angle_radians = math.atan2(y_diff, x_diff)
        move_x = math.cos(angle_radians) * self.speed
        move_y = math.sin(angle_radians) * self.speed
        self.rect.y += move_y 
        self.rect.x += move_x 

        if abs(self.t_y - self.rect.y) < self.speed:
            self.t_y = self.rect.y
        if abs(self.t_x - self.rect.x) < self.speed:
            self.t_x = self.rect.x             

        if self.t_y == self.rect.y and self.t_x == self.rect.x: 
            self.kill() 

        self.frame += 1
        if self.frame == len(self.animation):
            self.frame = 0 
        else: 
            self.o_image = self.animation[self.frame]
            unit_mask = pygame.mask.from_surface(self.o_image)
            self.image = unit_mask.to_surface(setcolor = (0, 0, 0, 180), unsetcolor = (0, 0, 0, 0))


class Bullet(pygame.sprite.Sprite): 

    def __init__ (self, row, col, t_row, t_col):
        pygame.sprite.Sprite.__init__(self)
        self.row = row 
        self.col = col
        self.t_row = t_row
        self.t_col = t_col 
        self.image = bullet_animation[0]
        self.frame = 0 
        self.rect = self.image.get_rect() 
        self.speed = 10
        self.rect.x = int(self.col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 - self.image.get_width()//2)
        self.rect.y = int(self.row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 - self.image.get_height()//2)
        self.t_x = int(self.t_col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 - self.image.get_width()//2) 
        self.t_y = int(self.t_row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 - self.image.get_height()//2)
        self.angle = 0 

    def update(self): 

        x_diff = self.t_x - self.rect.x 
        y_diff = self.t_y - self.rect.y 
        angle_radians = math.atan2(y_diff, x_diff)
        move_x = math.cos(angle_radians) * self.speed
        move_y = math.sin(angle_radians) * self.speed
        self.rect.y += move_y 
        self.rect.x += move_x 

        if abs(self.t_y - self.rect.y) < self.speed:
            self.t_y = self.rect.y
        if abs(self.t_x - self.rect.x) < self.speed:
            self.t_x = self.rect.x             

        if self.t_y == self.rect.y and self.t_x == self.rect.x: 
            if gameboard.board[self.t_row][self.t_col] != 0: 
                gameboard.board[self.t_row][self.t_col].health -= 30
                expl = Explosion(self.rect.centerx, self.rect.centery)
                all_explosions.add(expl)
            self.kill() 

        self.frame += 1
        if self.frame == len(bullet_animation):
            self.frame = 0 
        else: 
            self.image = bullet_animation[self.frame]


class Beam(): 

    def __init__ (self, row, col, t_row, t_col):
        pygame.sprite.Sprite.__init__(self)
        self.row = row 
        self.col = col
        self.t_row = t_row
        self.t_col = t_col 
        self.speed = 15
        self.x = int(self.col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 )
        self.y = int(self.row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 )
        self.t_x = int(self.t_col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 ) 
        self.t_y = int(self.t_row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 )
        self.angle = 0 

    def update(self): 

        x_diff = self.t_x - self.x 
        y_diff = self.t_y - self.y 
        angle_radians = math.atan2(y_diff, x_diff)
        move_x = math.cos(angle_radians) * self.speed
        move_y = math.sin(angle_radians) * self.speed
        self.y += move_y 
        self.x += move_x 

        if abs(self.t_y - self.y) < self.speed:
            self.t_y = self.y
        if abs(self.t_x - self.x) < self.speed:
            self.t_x = self.x             

        if self.t_y == self.y and self.t_x == self.x: 
            if gameboard.board[self.t_row][self.t_col] != 0: 
                gameboard.board[self.t_row][self.t_col].health -= 50
                expl = Explosion(self.x, self.y)
                all_explosions.add(expl)
            all_beams.remove(self)

    def draw(self): 
        pygame.draw.line(screen_2, RED_ALPHA, (self.x, self.y), (self.t_x, self.t_y), 15)
        pygame.draw.line(screen_2, WHITE, (self.x, self.y), (self.t_x, self.t_y), 5)


class Slash(pygame.sprite.Sprite): 

    def __init__ (self, t_row, t_col):
        pygame.sprite.Sprite.__init__(self)
        self.row = t_row
        self.col = t_col 
        self.image = slash_animation[0]
        self.frame = 0 
        self.rect = self.image.get_rect() 
        self.rect.x = int(self.col * SQUARE_SIZE + OFFSET_X + SQUARE_SIZE //2 - self.image.get_width()//2)
        self.rect.y = int(self.row * SQUARE_SIZE + OFFSET_Y + SQUARE_SIZE //2 - self.image.get_height()//2)

    def update(self):         
        self.frame += 1
        if self.frame == len(slash_animation):
            if gameboard.board[self.row][self.col] != 0: 
                gameboard.board[self.row][self.col].health -= 40
                expl = Explosion(self.rect.centerx, self.rect.centery)
                all_explosions.add(expl)            
            self.frame = 0 
            self.kill()
        else:             
            self.image = slash_animation[self.frame]
        

class Explosion(pygame.sprite.Sprite):
    def __init__ (self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = explosion_animation[0]
        self.rect = self.image.get_rect() 
        self.rect.centerx = x
        self.rect.centery = y
        self.frame = 0 
    
    def update(self):
        self.frame += 1
        if self.frame == len(explosion_animation):
            self.kill() 
            return True 
        else: 
            self.image = explosion_animation[self.frame]        



#Sprite Group 
all_flyings = pygame.sprite.Group() 
all_units = pygame.sprite.Group() 
all_players = pygame.sprite.Group() 
all_enemies = pygame.sprite.Group() 
all_bullets = pygame.sprite.Group()
all_explosions = pygame.sprite.Group()
all_slashes = pygame.sprite.Group() 

#list group 
all_beams = [] 

    

gameboard = Board() 

#game loop 
run = True 
sortie = True 
while run:

    if sortie == True: 
        player_choice = sortie_page()
        sortie = False
        player = load_data(player_choice, gameboard.stage) 

    clock.tick(FPS) 
    all_units.update()
    all_flyings.update()    
    all_bullets.update()
    all_slashes.update()
    for beam in all_beams:
        beam.update() 
    all_explosions.update()

    if len(all_explosions) != 0 and screen_shake == 0: 
        screen_shake = 50 
    screen_shake = max (0, screen_shake - 1)

    if gameboard.turn == "enemy": 
        gameboard.enemies_process()    

    if player not in all_players and gameboard.next_stage == False: 
        sortie = gameboard.restart_process() 
    elif gameboard.num_of_enemies == 0 and gameboard.restart == False: 
        player = gameboard.next_stage_process()

    draw()


    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            run = False 

        if event.type == pygame.MOUSEBUTTONDOWN and gameboard.turn == "player": 
            if event.button == 1 and gameboard.selected_r == None: 
                clicking = True
                mpos = pygame.mouse.get_pos() 
                row, col = get_grid_pos(mpos)
                if row < ROWS: 
                    gameboard.select_unit(row, col) 

            if event.button == 3 and gameboard.selected_l != None:                 
                pos = pygame.mouse.get_pos() 
                row, col = get_grid_pos(pos)
                if row < ROWS: 
                    gameboard.before_shoot(row, col)

        if event.type == pygame.MOUSEBUTTONUP:
            clicking = False 

pygame.quit() 

#Copyright © 2025 by futuristickids (Instagram), Futuristic Kids(Facebook), ay.parentingworkshop@yahoo.com, andrewyip-workshop, Andrew Yip
#All rights reserved
