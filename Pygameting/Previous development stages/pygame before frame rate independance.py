"""
NOTES:

>when laser hits aliens make aliens explode into particles
"""



import pygame, random, noise, time
from pygame.locals import *
clock = pygame.time.Clock()
place_holder_image = pygame.image.load("player_laser.png")

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
pygame.display.set_caption("Space Game Thingamajiggery")
screen = pygame.display.set_mode(WINDOW_SIZE, 0,32)
framerate = 60
last_time = time.time()
enemies = []
enemies_rects = []
enemies_id = []

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
    def __init__(self, location, vel, y_momentum, gravity_speed, terminal_vel, jump_height, collision_top_rebound, animation_speed, image_width, image_height, facing, action, frame, movement, running_animation_speed, moving_left, moving_right, id,projectile_vel, projectile_fire_speed,health,health_bar_colour):
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

    def apply_movement_physics(self):
        if self.moving_right == True:
            self.movement[0] +=self.vel
        if self.moving_left == True:
            self.movement[0] -= self.vel
        self.movement[1] += self.y_momentum
        self.y_momentum += self.gravity_speed
        if self.y_momentum >self.terminal_vel:
            self.y_momentum = self.terminal_vel
    


    def move(self, tiles, is_player, entity_rects, id):
        self.collision_types = {"top":False, "bottom":False, "right":False, "left":False, "top_enitity" :False, "bottom_entity":False, "left_entity":False, "right_entity":False}
        self.rect.x +=self.movement[0]
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
    

        
        self.rect.y += self.movement[1]
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
            self.animation_image = pygame.image.load(self.image_loc)
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

    
    def generate_projectile(self, damage):
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

    

    def handle_projectiles(self, display, scroll, projectile_image, projectile_image_flip):
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
        





            



        
        






#buttons---------------

play_button = button(True, "play_button.png", "play_button_pressed.png", False )
exit_button_menu = button((play_button.rect.right + 30,play_button.rect.y+17),"quit_button.png", "quit_button_pressed.png", False)


#----entities---------------------------------------------------------------------------------------
player = entity([50,50], 4, 0, 0.5, 10, 10, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False, 1, 11,10, 100, (255,0,110))
player.projectile_image = pygame.image.load("player_laser.png")
player.projectile_image_flipped = pygame.image.load("player_laser_flipped.png")


true_scroll = [0,0]
true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])
def load_enemy_laser_image():
    for enemy in enemies:
        if enemy.laser_image_load_check == False:
            enemy.projectile_image = pygame.image.load("enemy_laser.png")
            enemy.projectile_image_flipped = pygame.image.load("enemy_laser_flipped.png")
            enemy.laser_image_load_check = True


#----------------------------------------------------------------------------------------------------
menu_text = "Click here to start"
air_timer = 0
true_scroll = [0,0]
CHUNK_SIZE = 8
tile_height = -6
rocks_often = 9      # how often rocks appear, higher is less often




def generate_chunk(x,y):
    CHUNK_DATA =[]
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 #nothing
            height = int(noise.pnoise1(target_x * 0.08, repeat = 999999999)*mountain_height)
            if target_y > 8-height +tile_height:
                tile_type = 2 # ground
            elif target_y == 8 - height +tile_height:
                tile_type = 1 # topground
            elif target_y ==8-height-1+tile_height:
                if random.randint(1,rocks_often) == 1:
                    tile_type = 3 # rocks
            if tile_type != 0:
                CHUNK_DATA.append([[target_x,target_y], tile_type]) 
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
                enemies.append(entity([random.randint(x*CHUNK_SIZE*66, x*CHUNK_SIZE*66+(CHUNK_SIZE*66)),y*CHUNK_SIZE],2, 0, 0.5, 10, 13, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False, i, 11,100,30, (255,0,0)))


    
    return CHUNK_DATA

def collision_test(rect, tiles):
    hit_list = []
    entity_hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    
    return hit_list
    

player.animation_database["run_left"] = player.load_animation("L", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed])
player.animation_database["run_right"] = player.load_animation("R", [player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,player.running_animation_speed,])
player.animation_database["idle_left"] = player.load_animation("idle/IL", [1])
player.animation_database["idle_right"] = player.load_animation("idle/IR",[1])
player.animation_database["idle"] = player.load_animation("idle/I", [1])

def load_enemy_animations():
    for enemy in enemies:
        if enemy.load_animation_check ==False:
            enemy.animation_database["run_left"] = enemy.load_animation("EL", [enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed])
            enemy.animation_database["run_right"] = enemy.load_animation("ER", [enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed,enemy.running_animation_speed])
            enemy.animation_database["idle_left"] = enemy.load_animation("Eidle/IL", [1])
            enemy.animation_database["idle_right"] = enemy.load_animation("Eidle/IR", [1])
            enemy.load_animation_check = True

game_map = {}



background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]
top_ground = pygame.image.load("topground.png")
ground = pygame.image.load("ground.png")
rocks = pygame.image.load("rocks.png")
tile_index = {1:top_ground,
              2:ground,
              3:rocks}







true_scroll[0]+= (player.rect.x - true_scroll[0]-584)/20
true_scroll[1]+= (player.rect.y - true_scroll[1] - 366)/20



scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])


#loading_images---------------------------------------------
player.health_bar_frame = pygame.image.load("player_health_frame.png")
def load_enemy_health_bar_frame():
    for enemy in enemies:
        if enemy.health_bar_load_check==False:
            enemy.health_bar_frame = pygame.image.load("enemy_health_frame.png")
            enemy.health_bar_load_check = True

player.health_bar_frame_loc = [40,0]
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
                menu_run=False
                big_run = False
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





        pygame.display.update()
#-----------------------------------------------------------------------------------

 
#-----------------------------------------------------------------------------------

    while run:
        

        fps = clock.get_fps()
        d_t = time.time() - last_time
        d_t *= framerate
        last_time = time.time()
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

        load_enemy_animations()
        load_enemy_health_bar_frame()
        load_enemy_laser_image()
    #--------------------------------------------

        





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
            run = False



        player.apply_movement_physics()

    #---animation_stuff----------------------------------
        if player.moving_left:
            player.facing = -1
            player.action, player.frame  = player.change_action(player.action, player.frame,"run_left")
        elif player.moving_right:
            player.facing = 1
            player.action, player.frame  = player.change_action(player.action, player.frame,"run_right")
        elif player.facing == 1:
            player.action, player.frame = player.change_action(player.action, player.frame, "idle_right")
        else:
            player.action, player.frame = player.change_action(player.action, player.frame, "idle_left")
    #------------------


        
        
        player.rect, player.collision_types = player.move(tile_rects, True, enemies_rects, player.id)
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
            player.generate_projectile(7)
        player.handle_projectiles(screen, scroll, player.projectile_image, player.projectile_image_flipped)
        
        #--------------------------------------------------
        player.generate_health_bar(3, 0)
        player.render_health_bar(screen)

        
        
 
        
        screen.blit(player.image, (player.rect.x -scroll[0], player.rect.y-scroll[1]))






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




                enemy.apply_movement_physics()

                enemy.rect, enemy.collision_types = enemy.move(tile_rects, False, enemies_rects, enemy.id)

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

                    enemy.generate_projectile(4)
                enemy.handle_projectiles(screen, scroll, enemy.projectile_image, enemy.projectile_image_flipped)
                
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
                if event.key == K_SPACE:
                    player.fire = False
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


        pygame.display.update()
        clock.tick(60)


pygame.quit()







    




