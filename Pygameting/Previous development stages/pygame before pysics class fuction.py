import pygame
from pygame.locals import *
clock = pygame.time.Clock()
import random
import noise

pygame.init()
WINDOW_SIZE = (1200, 700)
run = True
mouse_click =  False
RED = (255,0,0)
GREEN = (0,255,0)
WHITE = (255,255,255)
text_colour = WHITE
menu_run = True
mountain_height = 4
pygame.display.set_caption("Space Invaders REMASTERED")
screen = pygame.display.set_mode(WINDOW_SIZE, 0,32)
enemies = []
#class_definitions----------------------------------
class button:
    def __init__(self,iscentrecoords, image_path, pressed_image_path, ispressed):
        self.coords = iscentrecoords
        self.image = pygame.image.load(image_path)
        self.pressed_image = pygame.image.load(pressed_image_path)
        self.status = self.image
        self.ispressed = ispressed
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        if self.coords == True:
            self.coords = [WINDOW_SIZE[0]/2-self.width/2, WINDOW_SIZE[1]/2-self.height/2]
        self.rect = pygame.Rect(self.coords[0], self.coords[1], self.width, self.height)
    def ispressed_check(self, colliding_with, activator):
        if self.rect.collidepoint(colliding_with) and activator:
            self.ispressed = True
        else:
            self.ispressed = False
            self.status = self.image
class entity:
    def __init__(self, location, vel, y_momentum, gravity_speed, terminal_vel, jump_height, collision_top_rebound, animation_speed, image_width, image_height, facing, action, frame, movement, running_animation_speed, moving_left, moving_right):
        self.location=location
        self.vel = vel
        self.y_momentum = y_momentum
        self.gravity_speed = gravity_speed
        self.terminal_vel = terminal_vel
        self.jump_height = jump_height
        self.collision_top_rebound = collision_top_rebound
        self.animation_speed = animation_speed
        self.image_width = image_width
        self.image_height = image_height
        self.facing = facing
        self.action = action
        self.frame = frame
        self.rect = pygame.Rect(self.location[0], self.location[1], self.image_width, self.image_height)
        self.movement = movement
        self.running_animation_speed = running_animation_speed
        self.moving_left = moving_left
        self.moving_right = moving_right
        


#buttons---------------
player = entity([50,50], 4, 0, 0.5, 10, 10, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False)
play_button = button(True, "play_button.png", "play_button_pressed.png", False )
exit_button_menu = button((play_button.rect.right + 30,play_button.rect.y+17),"quit_button.png", "quit_button_pressed.png", False)
moving_left = False
moving_right = False
jumping = False

menu_text = "Click here to start"
air_timer = 0
true_scroll = [0,0]
facing = 1
CHUNK_SIZE = 8
tile_height = -6
rocks_often = 9      # how often rocks appear, higher is less often

global animation_frames
animation_frames = {}



def generate_chunk(x,y):
    CHUNK_DATA =[]
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 #nothing
            height = int(noise.pnoise1(target_x * 0.08, repeat = 99999)*mountain_height)

            if target_y > 8-height +tile_height:
                tile_type = 2 # ground
            elif target_y == 8 - height +tile_height:
                tile_type = 1 # topground
            elif target_y ==8-height-1+tile_height:
                if random.randint(1,rocks_often) == 1:
                    tile_type = 3 # rocks
            if tile_type != 0:
                CHUNK_DATA.append([[target_x,target_y], tile_type])
    return CHUNK_DATA




def  load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split("/")[-1]
    animation_frame_data = []
    n = 1
    for frame in frame_durations:
        animation_frame_id = animation_name + str(n)
        image_loc = path + "/" + animation_frame_id + ".png"
        animation_image = pygame.image.load(image_loc)
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n+=1
    return animation_frame_data
def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

animation_database = {}
animation_database["run_left"] = load_animation("L", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed])
animation_database["run_right"] = load_animation("R", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,])
animation_database["idle_left"] = load_animation("idle/IL", [1])
animation_database["idle_right"] = load_animation("idle/IR",[1])
animation_database["idle"] = load_animation("idle/I", [1])
game_map = {}



background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
top_ground = pygame.image.load("topground.png")
ground = pygame.image.load("ground.png")
rocks = pygame.image.load("rocks.png")
tile_index = {1:top_ground,
              2:ground,
              3:rocks}

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {"top":False, "bottom":False, "right":False, "left":False}
    rect.x +=movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement [0] >0:
            rect.right = tile.left
            collision_types["right"] = True
        elif movement[0] <0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True

    return rect, collision_types 


true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])
#mainloop-----------------------------------------------------------------------------------------------------------------------------------
#mainloop-----------------------------------------------------------------------------------------------------------------------------------
#mainloop-----------------------------------------------------------------------------------------------------------------------------------
big_run = True
while big_run:
    menu_run = True


    while menu_run:


        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
            if event.type == MOUSEBUTTONUP:
                mouse_click = False
        mouse_coords = pygame.mouse.get_pos()
        screen.fill((0, 20, 150))
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(menu_text, True, text_colour)

        screen.blit(play_button.status, (play_button.coords[0], play_button.coords[1]))
        screen.blit(exit_button_menu.status, (exit_button_menu.coords[0], exit_button_menu.coords[1]))
        play_button.ispressed_check(mouse_coords,mouse_click)
        exit_button_menu.ispressed_check(mouse_coords,mouse_click)
        if play_button.ispressed:
            menu_run = False
            run = True
            play_button.status = play_button.pressed_image
            while mouse_click:
            #-------------------------------------------------
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        mouse_click = True
                    if event.type == MOUSEBUTTONUP:
                        mouse_click = False
           #---------------------------------------------------
                screen.fill((0, 20, 150))
                screen.blit(play_button.status, (play_button.coords[0], play_button.coords[1]))
                pygame.display.update()
                print("positive")

        elif exit_button_menu.ispressed:
            menu_run = False
            run = False
            big_run = False
            while mouse_click:
                # -------------------------------------------------
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        mouse_click = True
                    if event.type == MOUSEBUTTONUP:
                        mouse_click = False
                # ---------------------------------------------------
                #screen.fill((0, 20, 150))
                exit_button_menu.status = exit_button_menu.pressed_image
                screen.blit(exit_button_menu.status, (exit_button_menu.coords[0], exit_button_menu.coords[1]))
                pygame.display.update()



        else:
            pass
        pygame.display.update()
#-----------------------------------------------------------------------------------
    count = 0
    for i in range(3):

        enemies.append(entity([random.randint(scroll[0], scroll[0]+1200), 700],4, 0, 0.5, 10, 10, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False))
 
#-----------------------------------------------------------------------------------

    while run:
        

        fps = clock.get_fps()
        screen.fill((0,0,102))



        true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
        true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(screen, (0,125,146), obj_rect)
            else:
                pygame.draw.rect(screen, (0,46,76), obj_rect)
       #tiles---------------------------------------------
        tile_rects = []

        #tile_rendering-----------------------------------
        for y in range(4):
            for x in range(5):
                target_x = x - 1 + int(scroll[0]/(CHUNK_SIZE*66))
                target_y = y - 1 + int(scroll[1]/(CHUNK_SIZE*66))
                target_chunk = str(target_x) + ";" + str(target_y)
                if target_chunk not in game_map:
                    game_map[target_chunk] = generate_chunk(target_x, target_y)
                for tile in game_map[target_chunk]:
                    screen.blit(tile_index[tile[1]], (tile[0][0] * 66-scroll[0], tile[0][1]*66-scroll[1]))
                    if tile[1] in [1,2]:
                        tile_rects.append(pygame.Rect(tile[0][0]*66, tile[0][1]*66, 66, 66))

        player.movement = [0,0]


    #--------------------------------------------

        





        #drawing player character---------------------------------------------------
        if moving_right == True:
            player.movement[0] +=player.vel
        if moving_left == True:
            player.movement[0] -= player.vel
        player.movement[1] += player.y_momentum
        player.y_momentum += player.gravity_speed
        if player.y_momentum >player.terminal_vel:
            player.y_momentum = player.terminal_vel

        
        if moving_left:
            player.facing = -1
            player.action, player.frame  = change_action(player.action, player.frame,"run_left")
        elif moving_right:
            player.facing = 1
            player.action, player.frame  = change_action(player.action, player.frame,"run_right")
        elif player.facing == 1:
            player.action, player.frame = change_action(player.action, player.frame, "idle_right")
        else:
            player.action, player.frame = change_action(player.action, player.frame, "idle_left")
    #------------------


        
        
        player.rect, collision_types = move(player.rect, player.movement, tile_rects)
        if collision_types["bottom"]:
            player.y_momentum = 0
            air_timer=0
        else:
            air_timer+=1
        if collision_types["top"]:
            player.y_momentum +=player.collision_top_rebound


        player.frame += 1
        if player.frame >= len(animation_database[player.action]):
            player.frame = 0
        player_image_id = animation_database[player.action][player.frame]
        player_image = animation_frames[player_image_id]
        
        screen.blit(player_image, (player.rect.x -scroll[0], player.rect.y-scroll[1]))
        


    #------------------------------------------------

    #------------------------------------------------
        
     #event handling ---------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == QUIT:
                big_run = False
                run = False
            if event.type == KEYDOWN:
                if event.key == K_d:
                    moving_right = True
                if event.key == K_a:
                    moving_left = True
                if event.key == K_w :
                    if air_timer<6:
                        player.y_momentum  = -player.jump_height

            if event.type == KEYUP:
                if event.key == K_d:
                    moving_right = False
                if event.key == K_a:
                    moving_left = False
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
            if event.type == MOUSEBUTTONUP:
                mouse_click = False

        #fpscounter--------------------------------------------------

        myfont = pygame.font.SysFont('Gadugi', 30)
        textsurface = myfont.render(str(int(fps)), True, text_colour)
        screen.blit(textsurface, (0,0))
        #exit button-------------------------------------------------
        exit_button = button((1050,15), "exit_button.png", "exit_button_pressed.png", False)
        screen.blit(exit_button.status, exit_button.coords)
        mouse_coords = pygame.mouse.get_pos()
        exit_button.ispressed_check(mouse_coords,mouse_click)

        if exit_button.ispressed:
            run = False
            menu_run = True
            exit_button.status = exit_button.pressed_image
            while mouse_click:
            #-------------------------------------------------
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        mouse_click = True
                    if event.type == MOUSEBUTTONUP:
                        mouse_click = False
           #---------------------------------------------------
                #screen.fill((0, 20, 150))
                screen.blit(exit_button.status, (exit_button.coords[0], exit_button.coords[1]))
                pygame.display.update()
                print("positive loop")










        pygame.display.update()
        clock.tick(60)


pygame.quit()






    




