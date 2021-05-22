"""
NOTES:

>when laser hits aliens make aliens explode into particles
"""
#aa


import pygame, random, noise, time, sys, math, json
import engine as e
from pygame.locals import *
clock = pygame.time.Clock()
pygame.init()
WINDOW_SIZE = (1200, 700)
screen = pygame.display.set_mode(WINDOW_SIZE, 0,32)
place_holder_image = pygame.image.load("assets\Weapons\player_laser.png").convert_alpha()





mouse_click =  False
RED = (255,0,0)
GREEN = (0,255,0)
WHITE = (255,255,255)
text_colour = WHITE
menu_run = True
run = True
mountain_height = 4
pygame.display.set_caption("Space Game Thingamajiggery")
cursor_image_white = pygame.image.load("assets/Cursor/cursor.png").convert_alpha()
cursor_image_red = pygame.image.load("assets/Cursor/cursor_red.png").convert_alpha()
cursor_image = cursor_image_white


framerate = 50
framerate_cap =1000000
last_time = time.time()
enemies = []
enemies_rects = []
enemies_id = []
mouse_click_left = False
game_map_for_stuff = {}


#class_definitions----------------------------------





class entity:
    def __init__(self, location, vel, y_momentum, gravity_speed, terminal_vel, jump_height, collision_top_rebound, animation_speed, image_width, image_height, facing, action, frame, movement, running_animation_speed, moving_left, moving_right, id,projectile_vel, projectile_fire_speed,health,health_bar_colour, sprint_vel, not_sprint_vel):
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
        self.id = id
        self.animation_frames = {}
        self.animation_database = {}
        self.projectiles = []
        self.projectile_vel = projectile_vel
        self.projectile_count = 0
        self.fire = False
        self.projectile_image = 0
        self.projectile_image_flipped = 0
        self.projectile_cooldown_count = 0
        self.projectile_fire_speed = projectile_fire_speed
        self.health = health
        self.health_bar_frame = place_holder_image
        self.health_bar = 0
        self.health_bar_frame_loc = []
        self.health_bar_loc = [0,0]
        self.health_bar_colour = health_bar_colour
        self.load_animation_check = False
        self.health_bar_load_check = False
        self.laser_image_load_check = False
        self.sprint = False
        self.sprint_vel = sprint_vel
        self.not_sprint_vel = not_sprint_vel
        self.inventory = [False,False,False,False,False]
        self.vec = False
        self.items = {}
        self.inventory_locs = [(4,4),(66,4),(132,4), (198,4), (262,4)]
        self.selected_inventory_slot = 0

    def apply_movement_physics(self):
        if self.moving_right == True:
            self.movement[0] +=self.vel
        if self.moving_left == True:
            self.movement[0] -= self.vel
        self.movement[1] += self.y_momentum
        self.y_momentum += self.gravity_speed
        if self.y_momentum >self.terminal_vel:
            self.y_momentum = self.terminal_vel
    


    def move(self, tiles, is_player, entity_rects, id, dt):
        self.collision_types = {"top":False, "bottom":False, "right":False, "left":False, "top_enitity" :False, "bottom_entity":False, "left_entity":False, "right_entity":False}
        self.rect.x +=self.movement[0]*d_t
        hit_list = collision_test(self.rect, tiles)
        for tile in hit_list:
            if self.movement [0] >0:
                self.rect.right = tile.left
                self.collision_types["right"] = True
            elif self.movement[0] <0:
                self.rect.left = tile.right
                self.collision_types["left"] = True
        
        if is_player==False:
            hit_list = collision_test(self.rect, entity_rects)
            for rect in hit_list:
                if rect != self.rect:
                    if self.movement [0] >0:
                        self.rect.right = rect.left
                        self.collision_types["right_entity"] = True
                    elif self.movement[0] <0:
                        self.rect.left = rect.right
                        self.collision_types["left_entity"] = True
    

        
        self.rect.y += self.movement[1]*d_t
        hit_list = collision_test(self.rect,tiles)
        for tile in hit_list:
            if self.movement[1] > 0:
                self.rect.bottom = tile.top
                self.collision_types["bottom"] = True
            elif self.movement[1] < 0:
                self.rect.top = tile.bottom
                self.collision_types["top"] = True
        
        if is_player==False:
            hit_list = collision_test(self.rect, entity_rects)
            for rect in hit_list:
                if rect != self.rect:
                    if self.movement [1] >0:
                        self.rect.bottom = rect.top
                        self.collision_types["bottom_entity"] = True
                    elif self.movement[1] <0:
                        self.rect.top = rect.bottom
                        self.collision_types["top_entity"] = True

        return self.rect, self.collision_types 

    def  load_animation(self,path, frame_durations):
        self.animation_name = path.split("/")[-1]
        self.animation_frame_data = []
        n = 1
        for frame in frame_durations:
            self.animation_frame_id = self.animation_name + str(n)
            self.image_loc = path + "/" + self.animation_frame_id + ".png"
            self.animation_image = pygame.image.load(self.image_loc).convert_alpha()
            self.animation_frames[self.animation_frame_id] = self.animation_image.copy()
            for i in range(frame):
                self.animation_frame_data.append(self.animation_frame_id)
            n+=1
        return self.animation_frame_data
    def change_action(self,action_var, frame, new_value):
        if action_var != new_value:
            action_var = new_value
            frame = 0
        return action_var, frame

    
    def generate_projectile(self, damage,angle, delta_vec, player):
        if player ==True:
        
            self.projectile_cooldown_count +=1
            if self.projectile_cooldown_count == self.projectile_fire_speed:
                self.projectile_cooldown_count = 0
            if self.projectile_cooldown_count ==0:  
                self.projectile_count +=1
                self.centre = [self.rect.centerx, self.rect.centery]
                projectile_vec = pygame.math.Vector2([self.centre[0], self.centre[1]])
 


                
                self.projectiles.append([[self.centre[0], self.centre[1]], self.projectile_vel, self.facing, pygame.Rect(self.centre[0], self.centre[1]+20, 40 ,18), damage,angle,delta_vec, projectile_vec])
        else:
            self.projectile_cooldown_count +=1
            if self.projectile_cooldown_count == self.projectile_fire_speed:
                self.projectile_cooldown_count = 0
            if self.projectile_cooldown_count ==0:  
                self.projectile_count +=1
                if self.facing ==1:
                    self.centre = [self.rect.x+65, self.rect.y+33]
                if self.facing ==-1:
                    self.centre = [self.rect.x, self.rect.y+33]
                self.projectiles.append([[self.centre[0], self.centre[1]], self.projectile_vel, self.facing, pygame.Rect(self.centre[0], self.centre[1], 40 ,18), damage])
            
    

    def handle_projectiles(self, display, scroll, projectile_image, projectile_image_flip, player):
        if player == True:
            for projectile in self.projectiles:                     #loc,vel,facing,rect, damage, angle, delta_vec, projectile_vec
                #projectile[3].x+=self.projectile_vel*projectile[2]

                projectile[3].x += projectile[6][0]*self.projectile_vel*d_t
                projectile[3].y += projectile[6][1]*self.projectile_vel


                if projectile[3].x>scroll[0] and projectile[3].x<scroll[0]+1200:

                    display.blit(pygame.transform.rotate(projectile_image, projectile[5]),(projectile[3].x-scroll[0], projectile[3].y-scroll[1]) )
        else:
            

            for projectile in self.projectiles:
                projectile[3].x+=self.projectile_vel*projectile[2]

                if projectile[3].x>scroll[0] and projectile[3].x<scroll[0]+1200:

                    if projectile[2]== 1:
                        display.blit(projectile_image, (projectile[3].x-scroll[0], projectile[3].y-scroll[1]))
                    if projectile[2]==-1:#
                        display.blit(projectile_image_flip, (projectile[3].x-scroll[0], projectile[3].y-scroll[1]))



                else:
                    self.projectiles.remove(projectile)
                    self.projectile_count -=1
                    
                    
    def generate_health_bar(self, health_bar_multiplier,addition_number):
        self.health_bar_loc[0] = self.health_bar_frame_loc[0]+(self.health_bar_frame.get_width()/52)+addition_number
        self.health_bar_loc[1] = self.health_bar_frame_loc[1]+(self.health_bar_frame.get_height()/2.8)
        self.health_bar = pygame.Rect(self.health_bar_loc[0], self.health_bar_loc[1], self.health*health_bar_multiplier,8*health_bar_multiplier )
    
    def render_health_bar(self, display):
        display.blit(self.health_bar_frame, (self.health_bar_frame_loc[0], self.health_bar_frame_loc[1]))
        pygame.draw.rect(display, self.health_bar_colour, (self.health_bar.x, self.health_bar.y , self.health_bar.width, self.health_bar.height))
    def add_item(self, item_name, item_pic_path, isweapon):
        item_pic = pygame.image.load(item_pic_path)
        self.items[item_name] = [item_pic, isweapon]

    def add_inventory(self, item_name, number):
        if self.items[item_name] not in self.inventory:#figure something out:
            if self.items[item_name][1] == False:
                if self.inventory[0] == False:
                    self.inventory[0] = [self.items[item_name], number]
                elif self.inventory[1] == False:
                    self.inventory[1] = [self.items[item_name], number]
                elif self.inventory[2] == False:
                    self.inventory[2] = [self.items[item_name], number]
                elif self.inventory[3] == False:
                    self.inventory[3] = [self.items[item_name], number]
                elif self.inventory[4] == False:
                    self.inventory[4] = [self.items[item_name], number]
                #if item is a weapon do same without number
            elif self.items[item_name][1]==True:
                if self.inventory[0] == False:
                    self.inventory[0] = [self.items[item_name]]
                elif self.inventory[1] == False:
                    self.inventory[1] = [self.items[item_name]]
                elif self.inventory[2] == False:
                    self.inventory[2] = [self.items[item_name]]
                elif self.inventory[3] == False:
                    self.inventory[3] = [self.items[item_name]]
                elif self.inventory[4] == False:
                    self.inventory[4] = [self.items[item_name]]
    def remove_inventory(self, item_nameorslotnumber):
        item_nameorslotnumber = i_d
        if isinstance(i_d, str):
            for slot in self.inventory:
                if slot[0] == self.items[i_d]:
                    slot = False
        elif isinstance(i_d, int):
            self.inventory[i_d] = False
        
    

    
        
tile_frames = {}


for i in range(100):
    num = str(i+1)
    path = "tile_frame/tile_frame"+num +".png"
    print(path)
    tile_frames[num] = pygame.image.load(path).convert_alpha()
    

      



        
        






#buttons---------------

play_button = e.button(True, "assets/Buttons/play_button.png", "assets/Buttons/play_button_pressed.png", False )
exit_button_menu = e.button((play_button.rect.right + 30,play_button.rect.y+17),"assets/Buttons/quit_button.png", "assets/Buttons/quit_button_pressed.png", False)


#----entities---------------------------------------------------------------------------------------
player = e.entity([0,0], 4, 0, 0.3, 10, 12, 7, 5, 63, 66, 1, "idle", 0, [0,0], 5, False, False, 1, 20,10, 100, (255,0,110), 15, 4, place_holder_image)
player.projectile_image = pygame.image.load("assets/Weapons/player_laser.png").convert_alpha()
player.projectile_image_flipped = pygame.image.load("assets/Weapons/player_laser_flipped.png").convert_alpha()


true_scroll = [0,0]
true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])
def load_enemy_laser_image():
    for enemy in enemies:
        if enemy.laser_image_load_check == False:
            enemy.projectile_image = pygame.image.load("assets/Alien/enemy_laser.png").convert_alpha()
            enemy.projectile_image_flipped = pygame.image.load("assets/Alien/enemy_laser_flipped.png").convert_alpha()
            enemy.laser_image_load_check = True
            


#----------------------------------------------------------------------------------------------------

air_timer = 0
true_scroll = [0,0]
CHUNK_SIZE = 8
tile_height = -6
rocks_often = 9      # how often rocks appear, higher is less often

def set_story_chunks(startx, starty, width, height):
    story_area_chunks = []
    current_x = startx
    current_y = starty
    for x in range(width):

        for y in range(height):
 
            story_area_chunks.append(str(current_x) + ";" + str(current_y))
            current_y+=1
        current_x+=1
        current_y=starty
            

    return story_area_chunks



def generate_chunk(x,y):
    CHUNK_DATA =[]
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 #nothing
            tile_health = 0
            height = int(noise.pnoise1(target_x * 0.08, repeat = 999999999)*mountain_height)
            if target_y > 8-height +tile_height:
                tile_type = 2 # ground
                tile_health = 10
            elif target_y == 8 - height +tile_height:
                tile_type = 1 # topground
                tile_health = 10
            elif target_y ==8-height-1+tile_height:
                if random.randint(1,rocks_often) == 1:
                    tile_type = 3 # rocks
                    tile_health = 20
            tile_current_health = tile_health

            CHUNK_DATA.append([[target_x,target_y], tile_type, True, tile_health, tile_current_health]) 
    spawnable = []
    for tile_data in CHUNK_DATA:
        if tile_data[1]==1:
            spawnable.append(True)
    if True in spawnable:
        #a = random.randint(0,1)
        a=random.randint(0,1)
        if a==1:
            enemy_spawn_number = random.randint(1,3)
            for i in range(enemy_spawn_number):
                enemies.append(e.entity([random.randint(x*CHUNK_SIZE*66, x*CHUNK_SIZE*66+(CHUNK_SIZE*66)),y*CHUNK_SIZE],2, 0, 0.5, 10, 13, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False, i, 11,100,30, (255,0,0), 2,7, place_holder_image))


    
    return CHUNK_DATA

def generate_story_chunk(x,y):
    CHUNK_DATA =[]
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 #nothing
            tile_health = 0
            if target_y > 2:
                tile_type = 2 # ground
                tile_health = 10
            elif target_y == 2:
                tile_type = 1 # topground
                tile_health = 10
            tile_current_health =tile_health

            CHUNK_DATA.append([[target_x,target_y], tile_type, True, tile_health, tile_current_health]) 

    return CHUNK_DATA


    
def collision_test(rect, tiles):
    hit_list = []
    entity_hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    
    return hit_list

def calculate_distance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist
def find_percentage(numerator, denominator):
    if denominator!= 0:
        scaler = 100/denominator
        percentage = int(numerator*scaler)
    else:
        percentage = 0
    return percentage
def calculate_bullet_radius(mouse_coords):
    x1 = int(mouse_coords[0] )
    y1 = int(mouse_coords[1])
    radius = math.sqrt((player.rect.centerx-scroll[0] - x1)**2 + (player.rect.centery-scroll[1] - y1)**2)
    top_point = [player.rect.centerx-scroll[0], player.rect.centery-scroll[1] - radius]
    chord = math.sqrt((top_point[0] - x1)**2 + (top_point[1] - y1)**2)
    O = chord/2
    H = radius
    if O !=0:
        half_angle = math.asin((O/H))
        angle = half_angle*2
    else:
        angle = 0
    actual_angle = math.degrees(angle)
    dx = (x1+scroll[0]) - player.rect.centerx
    dy = (y1+scroll[1]) - player.rect.centery
    
    
    player.vec = pygame.math.Vector2(player.rect.centerx, player.rect.centery)
    mouse_vec = pygame.math.Vector2(mouse_coords[0], mouse_coords[1])
    delta_vec = pygame.math.Vector2(dx, dy)
    delta_vec =delta_vec.normalize()


    
        
    return int(actual_angle), delta_vec

def center_img_on_surf(img, surf, rot_point):
    surf_centre = (surf.get_width()/2, surf.get_height()/2)

    surf.set_colorkey((0,0,0))
    surf.blit(img, (surf_centre[0] - rot_point[0], surf_centre[1] - rot_point[1]))
    return surf
def blit_surf_at_player_hand(screen, surf, blit_point, angle):
    calcx = (player.rect.x+blit_point[0])-scroll[0]
    calcy = (player.rect.y+blit_point[1]) - scroll[1]
    if angle!= False:
        surf = pygame.transform.rotate(surf, angle)
    screen.blit(surf, (calcx - (surf.get_width()/2), calcy - (surf.get_height()/2)))
    

player.add_item("laser_gun", "assets/Weapons/laser_gun_inventory.png", True)  
player.add_item("test", "assets/Tiles/test_ting.png", False)
player.add_inventory("laser_gun", False)  

    
        
   
    

    
    

    
    
    



        
        
    

player.animation_database["run_left"] = player.load_animation("assets/Player/L", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed])
player.animation_database["run_right"] = player.load_animation("assets/Player/R", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,])
player.animation_database["run_left_reverse"] = player.load_animation("assets/Player/RL",[player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,] )
player.animation_database["run_right_reverse"] = player.load_animation("assets/Player/RR",[player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,] )
player.animation_database["idle_left"] = player.load_animation("assets/Player/idle/IL", [1])
player.animation_database["idle_right"] = player.load_animation("assets/Player/idle/IR",[1])
player.animation_database["idle"] = player.load_animation("assets/Player/idle/I", [1])

def load_enemy_animations():
    for enemy in enemies:
        if enemy.load_animation_check ==False:
            enemy.animation_database["run_left"] = enemy.load_animation("assets/Alien/EL", [enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed])
            enemy.animation_database["run_right"] = enemy.load_animation("assets/Alien/ER", [enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed])
            enemy.animation_database["idle_left"] = enemy.load_animation("assets/Alien/Eidle/IL", [1])
            enemy.animation_database["idle_right"] = enemy.load_animation("assets/Alien/Eidle/IR", [1])
            enemy.load_animation_check = True

game_map = {}

story_area_chunks = set_story_chunks(-2, -2, 4, 4)
pygame.mouse.set_visible(False)



background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
top_ground = pygame.image.load("assets/Tiles/topground.png").convert_alpha()
ground = pygame.image.load("assets/Tiles/ground.png").convert_alpha()
rocks = pygame.image.load("assets/Tiles/rocks.png").convert_alpha()
tile_index = {1:top_ground,
              2:ground,
              3:rocks}

#functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
def print_cursor(image, display):
    mouse_coords = pygame.mouse.get_pos()
    coords_ = [mouse_coords[0]-image.get_width()/2, mouse_coords[1]-image.get_height()/2]
    display.blit(image, coords_)
    mouse_rect = pygame.Rect(mouse_coords[0], mouse_coords[1], image.get_width(), image.get_height())
    return mouse_rect
    
def start_menu(mouse_click, run, menu_run, big_run):
    
    menu_run = True

    while menu_run:

    


        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
                menu_run=False
                big_run = False
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
            if event.type == MOUSEBUTTONUP:
                mouse_click = False
        mouse_coords = pygame.mouse.get_pos()
        screen.fill((0, 20, 150))



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

                exit_button_menu.status = exit_button_menu.pressed_image
                screen.blit(exit_button_menu.status, (exit_button_menu.coords[0], exit_button_menu.coords[1]))
                pygame.display.update()

        print_cursor(cursor_image, screen)

        pygame.display.update()
        
    return run, big_run, menu_run


    
player.items["laser_gun"] = []





true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])
mouse_rect = print_cursor(cursor_image, screen)

#loading_images---------------------------------------------
player.health_bar_frame = pygame.image.load("assets/Player/player_health_frame.png").convert_alpha()
def load_enemy_health_bar_frame():
    for enemy in enemies:
        if enemy.health_bar_load_check==False:
            enemy.health_bar_frame = pygame.image.load("assets/Alien/enemy_health_frame.png").convert_alpha()
            enemy.health_bar_load_check = True

player.health_bar_frame_loc = [40,0]
tile_frame = pygame.image.load("tile_frame.png").convert_alpha()
laser_gun = pygame.image.load("assets/Weapons/laser_gun.png").convert_alpha()
laser_gun_surface = pygame.Surface((laser_gun.get_width()*2, laser_gun.get_height()*2))
center_img_on_surf(laser_gun, laser_gun_surface, (50,4))
inventory_bar = pygame.image.load("inventory_bar.png").convert_alpha()
background = pygame.image.load("background.png").convert_alpha()

#mainloop-----------------------------------------------------------------------------------------------------------------------------------

#mainloop-----------------------------------------------------------------------------------------------------------------------------------
#mainloop-----------------------------------------------------------------------------------------------------------------------------------
big_run = True



while big_run:
    run, menu_run, big_run =  start_menu(False, run, menu_run, big_run)


 
#-----------------------------------------------------------------------------------

    while run:
        mx,my = pygame.mouse.get_pos()
     

        

        fps = clock.get_fps()
        d_t = time.time() - last_time
        d_t *= framerate
        last_time = time.time()
        screen.blit(background, (0,0))
        #screen.fill((255,0,0))




        true_scroll[0]+= ((player.rect.x - true_scroll[0]-584)/20)
        true_scroll[1]+= ((player.rect.y - true_scroll[1] - 366)/20)



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

        #tile_rendering---------------------------------------------------------------------------------------------------------------------
        for y in range(4):
            for x in range(5):
                target_x = x - 1 + int(scroll[0]/(CHUNK_SIZE*66))
                target_y = y - 1 + int(scroll[1]/(CHUNK_SIZE*66))
                target_chunk = str(target_x) + ";" + str(target_y)
                if target_chunk not in game_map and target_chunk not in story_area_chunks:
                    game_map[target_chunk] = generate_chunk(target_x, target_y)
                elif target_chunk not in game_map and target_chunk in story_area_chunks:
 
                    game_map[target_chunk] = generate_story_chunk(target_x, target_y)
                game_map_for_stuff[target_chunk] = game_map[target_chunk]

                for tile in game_map[target_chunk]:

                    if tile[1]!= 0: 
                        screen.blit(tile_index[tile[1]], (tile[0][0] * 66-scroll[0], tile[0][1]*66-scroll[1]))

                    if tile[1] in [1,2]:
                        tile_rects.append(pygame.Rect(tile[0][0]*66, tile[0][1]*66, 66, 66))

 
                    
#----------------------------------------------------------------------------------------------------------------------------------------

        
        for chunk in game_map_for_stuff:
            for tile in game_map[chunk]:

                
                tile_adjusted_rect = pygame.Rect(tile[0][0]*66- scroll[0], tile[0][1]*66- scroll[1], 66,66)
                #pygame.draw.rect(screen, (255,0,0), tile_adjusted_rect, 1)
                tile_distance_line = calculate_distance(player.rect.centerx -scroll[0], player.rect.centery-scroll[1], pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
                if tile_adjusted_rect.collidepoint(pygame.mouse.get_pos()) and mouse_click==True:
                    if tile_distance_line<200:
                        tile[4]-=0.5*d_t
                        if tile[4]<0:
                            if tile[1] ==3:
                                player.add_inventory("test", 1)
                            tile[1] = 0                           
                    else:
                        tile[4] = tile[3]
                tile[2] = find_percentage(tile[4], tile[3])
                if tile[2]!=0 and tile[2]>0:
                    tile_frame = tile_frames[str(100-tile[2]+1)]
                else:
                    tile_frame = tile_frame
                if tile_adjusted_rect.collidepoint(pygame.mouse.get_pos()):
                    screen.blit(tile_frame, (tile_adjusted_rect.x, tile_adjusted_rect.y))
                if tile_distance_line<200:    
                    if tile_adjusted_rect.collidepoint(pygame.mouse.get_pos()) and mouse_click_left==True and tile[1]==0:
                        if not player.rect.colliderect(tile_adjusted_rect.x+scroll[0], tile_adjusted_rect.y+scroll[1], tile_adjusted_rect.width, tile_adjusted_rect.height):
                            for chunk_ in game_map_for_stuff:
                                for check_tile in game_map[chunk_]:
                                    if (check_tile[0][0] == tile[0][0]+1 and check_tile[0][1] == tile[0][1]) or (check_tile[0][0] == tile[0][0]-1 and check_tile[0][1] == tile[0][1]) or (check_tile[0][0] == tile[0][0] and check_tile[0][1] == tile[0][1]+1) or (check_tile[0][0] == tile[0][0] and check_tile[0][1] == tile[0][1]-1):
                                        if check_tile[1]==1 or check_tile[1] ==2:
                                            tile[1] = 2
                                            tile[3] = 10
                                            tile[4] = tile[3]
                                        
                                    
            

        bullet_angle, delta_vec  =calculate_bullet_radius((mx,my))

        if player.facing ==1:
            bullet_angle = bullet_angle
        elif player.facing ==-1:
            bullet_angle = 180+(180-bullet_angle)
        
        bullet_angle = 360-bullet_angle

        if bullet_angle<=270:
            bullet_angle+=90
        else:
            bullet_angle = bullet_angle-270

        


        
        
        
        
        player.movement = [0,0]


    #--------------------------------------------

        load_enemy_animations()
        load_enemy_health_bar_frame()
        load_enemy_laser_image()
    #--------------------------------------------

        if mx >player.rect.centerx-scroll[0]:

            player.facing = 1
        elif mx<player.rect.centerx -scroll[0]:

            player.facing = -1






        #drawing player character---------------------------------------------------
        for enemy in enemies:
            for projectile in enemy.projectiles:
                if projectile[3].colliderect(player.rect):
                    enemy.projectiles.remove(projectile)
                    player.health-=projectile[4]
            if player.rect.colliderect(enemy.rect):
                player.y_momentum-=1
                player.health-=0.01
        if player.health<0:
            print("dead")
        if player.sprint == True:
            player.vel = player.sprint_vel
        else:
            player.vel = player.not_sprint_vel
            



        player.apply_movement_physics(d_t)

    #---animation_stuff----------------------------------
        if player.moving_left and player.facing==-1:

            player.action, player.frame  = player.change_action(player.action, player.frame,"run_left")
        elif player.moving_right and player.facing ==1:
            player.action, player.frame  = player.change_action(player.action, player.frame,"run_right")
        elif player.moving_right and player.facing ==-1:
            player.action, player.frame  = player.change_action(player.action, player.frame,"run_left_reverse")
        elif player.moving_left and player.facing==1:
            player.action, player.frame  = player.change_action(player.action, player.frame,"run_right_reverse")
            
        elif player.facing == 1:
            player.action, player.frame = player.change_action(player.action, player.frame, "idle_right")
        elif player.facing == -1:
            player.action, player.frame = player.change_action(player.action, player.frame, "idle_left")
    #------------------

        
        
        
        player.rect, player.collision_types = player.move(tile_rects, True, enemies_rects, player.id, d_t)
        if player.collision_types["bottom"]:
            player.y_momentum = 0
            air_timer=0
        else:
            air_timer+=1
        if player.collision_types["top"]:
            player.y_momentum +=player.collision_top_rebound


        player.frame += 1
        if player.frame >= len(player.animation_database[player.action]):
            player.frame = 0
        player.image_id = player.animation_database[player.action][player.frame]
        player.image = player.animation_frames[player.image_id]
        #------------------------------------------------
        if player.projectile_count<100 and player.fire==True:
            player.generate_projectile(7, bullet_angle, delta_vec, True, d_t)
        player.handle_projectiles(screen, scroll, player.projectile_image, player.projectile_image_flipped, True, d_t)
        
        #--------------------------------------------------
        player.generate_health_bar(3, 0)
        player.render_health_bar(screen)

        
        
 
        
        screen.blit(player.image, (player.rect.x -scroll[0], player.rect.y-scroll[1]))

        if player.facing==-1:
            gun_angle = bullet_angle-180
            blit_surf_at_player_hand(screen, laser_gun_surface, (54,46), gun_angle)
        elif player.facing == 1:
            blit_surf_at_player_hand(screen, pygame.transform.flip(laser_gun_surface, True, False), (11,47), bullet_angle)

        

        player.display_inventory( inventory_bar, screen)



     #------------------------------------------------
        enemy_count = 0
        screen_rect = pygame.Rect(scroll[0], scroll[1], 1200,700)

        for enemy in enemies:
            if enemy.rect.colliderect(screen_rect):
                enemy.movement = [0,0]
                for projectile in player.projectiles:
                    if enemy.rect.colliderect(projectile[3]):
                        enemy.health -= projectile[4]
                        player.projectiles.remove(projectile)
                if enemy.rect.colliderect((mouse_rect.x +scroll[0], mouse_rect.y+scroll[1], mouse_rect.width, mouse_rect.height)):
                    cursor_image = cursor_image_red
                else: 
                    cursor_image = cursor_image_white
                    
                if enemy.health<0:
                    enemies.remove(enemy)
                enemy.health_bar_frame_loc = [enemy.rect.x-scroll[0], enemy.rect.y-20-scroll[1]]
                enemy.generate_health_bar(1,2)
                enemy.render_health_bar(screen)
                


                enemy_count+=1


                if player.rect.x-66>enemy.rect.x:
                    enemy.moving_right = True
                    enemy.moving_left = False
                elif player.rect.x+66<enemy.rect.x:
                    enemy.moving_right = False
                    enemy.moving_left = True
                else:
                    enemy.moving_right = False
                    enemy.moving_left = False
                if player.rect.x>enemy.rect.x:
                    if ((player.rect.x-66)-enemy.rect.x)<600:
                        enemy.fire=True
                elif player.rect.x<enemy.rect.x:
                    if (enemy.rect.x-(player.rect.x+66))<600:
                        enemy.fire=True
                else: 
                    enemy.fire= False




                enemy.apply_movement_physics(d_t)

                enemy.rect, enemy.collision_types = enemy.move(tile_rects, False, enemies_rects, enemy.id, d_t)

                if enemy.collision_types["bottom"]:
                    enemy.y_momentum = 0
                if enemy.collision_types["top"]:
                    enemy.y_momentum += enemy.collision_top_rebound
                if enemy.collision_types["left"] or enemy.collision_types["right"]:
                    enemy.y_momentum = -enemy.jump_height
    

                if enemy.collision_types["bottom_entity"]:
                    enemy.vel = 4
                else:
                    enemy.vel =2
                
                
                #-------------------
                if enemy.projectile_count<7 and enemy.fire==True:

                    enemy.generate_projectile(4,0, False, False, d_t)
                enemy.handle_projectiles(screen, scroll, enemy.projectile_image, enemy.projectile_image_flipped, False, d_t)
                
                #animation----------


                if enemy.moving_left:
                    enemy.facing = -1
                    enemy.action, enemy.frame  = enemy.change_action(enemy.action, enemy.frame,"run_left")
                elif enemy.moving_right:
                    enemy.facing = 1
                    enemy.action, enemy.frame  = enemy.change_action(enemy.action, enemy.frame,"run_right")
                elif enemy.facing == 1:
                    enemy.action, enemy.frame = enemy.change_action(enemy.action, enemy.frame, "idle_right")
                else:
                    enemy.action, enemy.frame = enemy.change_action(enemy.action, enemy.frame, "idle_left")

                enemy.frame += 1
                if enemy.frame >= len(enemy.animation_database[enemy.action]):
                    enemy.frame = 0
                enemy.image_id = enemy.animation_database[enemy.action][enemy.frame]
                enemy.image = enemy.animation_frames[enemy.image_id]


                        

                
                screen.blit(enemy.image,(enemy.rect.x - scroll[0], enemy.rect.y - scroll[1]))

                enemies_rects.append(enemy.rect)
                enemies_id.append(enemy.id)


        enemies_rects = []
        

            



    #------------------------------------------------
        
     #event handling ---------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == QUIT:
                big_run = False
                run = False
            if event.type == KEYDOWN:
                if event.key == K_d:
                    player.moving_right = True
                if event.key == K_a:
                    player.moving_left = True
                if event.key == K_LSHIFT:
                    player.sprint = True
                if event.key == K_w :
                    if air_timer<6:
                        player.y_momentum  = -player.jump_height
                if event.key == K_SPACE:
                    player.fire = True
                    

            if event.type == KEYUP:
                if event.key == K_d:
                    player.moving_right = False
                if event.key == K_a:
                    player.moving_left = False
                if event.key == K_LSHIFT:
                    player.sprint = False
                if event.key == K_SPACE:
                    player.fire = False
            if event.type == MOUSEBUTTONDOWN and event.button ==1:
                mouse_click = True
                
            if event.type == MOUSEBUTTONUP and event.button ==1:
                mouse_click = False
            if event.type == MOUSEBUTTONDOWN and event.button ==3:
                mouse_click_left = True
            if event.type == MOUSEBUTTONUP and event.button ==3:
                mouse_click_left = False
            if event.type == MOUSEBUTTONDOWN and event.button ==4:
                print("up")
            if event.type ==MOUSEBUTTONDOWN and event.button ==5:
                print("down")
            


        #fpscounter--------------------------------------------------

        myfont = pygame.font.SysFont('Gadugi', 30)
        textsurface = myfont.render(str(int(fps)), True, text_colour)
        screen.blit(textsurface, (0,0))
        #exit button-------------------------------------------------
        exit_button = e.button((1050,15), "assets/Buttons/exit_button.png", "assets/Buttons/exit_button_pressed.png", False)
        screen.blit(exit_button.status, exit_button.coords)
        mouse_coords = pygame.mouse.get_pos()
        exit_button.ispressed_check(mouse_coords,mouse_click)

        if exit_button.ispressed:
            run = False
            menu_run = True
            big_run = True
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

        game_map_for_stuff = {}
        mouse_rect = print_cursor(cursor_image, screen)
        cursor_image = cursor_image_white


        pygame.display.update()
        clock.tick(framerate_cap)


pygame.quit()







    




