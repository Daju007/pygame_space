import pygame, random, noise, time, sys, math, json
pygame.init()
from pygame.locals import *

#variable tingamajig---------------------------------------------------------------------------------------------------------------------------------------------------
#variable tingamajig---------------------------------------------------------------------------------------------------------------------------------------------------
#variable tingamajig---------------------------------------------------------------------------------------------------------------------------------------------------
#variable tingamajig---------------------------------------------------------------------------------------------------------------------------------------------------
with open("data.json") as f:
    data = json.load(f)
def save_data():
  with open("data.json", "w") as f:
    json.dump(data, f)

place_holder_image = pygame.image.load("tile_frame.png")


CHUNK_SIZE = data["CHUNK_SIZE"]
mountain_height = data["mountain_height"]
tile_height = data["tile_height"]
rocks_often = data["rocks_often"]
enemies = data["enemies_list"]










#button-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#button-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#button-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#button-----------------------------------------------------------------------------------------------------------------------------------------------------------------

class button:
    def __init__(self,iscentrecoords, image_path, pressed_image_path, ispressed):
        self.coords = iscentrecoords
        self.image = pygame.image.load(image_path).convert_alpha()
        self.pressed_image = pygame.image.load(pressed_image_path).convert_alpha()
        self.status = self.image
        self.ispressed = ispressed
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        if self.coords == True:
            self.coords = [1200/2-self.width/2, 700/2-self.height/2]
        self.rect = pygame.Rect(self.coords[0], self.coords[1], self.width, self.height)
    def ispressed_check(self, colliding_with, activator):
        if self.rect.collidepoint(colliding_with) and activator:
            self.ispressed = True
        else:
            self.ispressed = False
            self.status = self.image







#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------

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
                enemies.append(entity([random.randint(x*CHUNK_SIZE*66, x*CHUNK_SIZE*66+(CHUNK_SIZE*66)),y*CHUNK_SIZE],2, 0, 0.5, 10, 13, 7, 5, 66, 66, 1, "idle", 0, [0,0], 5, False, False, i, 11,100,30, (255,0,0), 2,7, place_holder_image))
        data["enemies_list"] = 1


    save_data()
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
def calculate_bullet_radius(mouse_coords, player, scroll):
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
def blit_surf_at_player_hand(screen, surf, blit_point, angle, player, scroll):
    calcx = (player.rect.x+blit_point[0])-scroll[0]
    calcy = (player.rect.y+blit_point[1]) - scroll[1]
    if angle!= False:
        surf = pygame.transform.rotate(surf, angle)
    screen.blit(surf, (calcx - (surf.get_width()/2), calcy - (surf.get_height()/2)))


def make_particles(particle_list,xy, speed, particle_sizes, amount, depreciation_rate, colour):
    for i in range(amount):
        particle_list.append([[xy[0], xy[1]], [random.randint(-10, 10)/speed, random.randint(-10, 10)/speed], random.randint(particle_sizes[0], particle_sizes[1]), depreciation_rate, colour])

def handle_particles(particle_list, screen):
    for particle in particle_list:    # [x,y], [xvel, yvel], size, depreciation rate, colour
        if particle[2]<=0: 
            particle_list.remove(particle)
        pygame.draw.circle(screen, particle[4], particle[0], particle[2])
        particle[0][0]+= particle[1][0]
        particle[0][1]+= particle[1][1]
        particle[2]-=particle[3]

    

#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------
#starter_functions--------------------------------------------------------------------------------------------------------------------------------------------------------------










#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
class entity:
    def __init__(self, location, vel, y_momentum, gravity_speed, terminal_vel, jump_height, collision_top_rebound, animation_speed, image_width, image_height, facing, action, frame, movement, running_animation_speed, moving_left, moving_right, id,projectile_vel, projectile_fire_speed,health,health_bar_colour, sprint_vel, not_sprint_vel, place_holder_image):
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
        self.inventory_locs = [(4,4),(68,4),(133,4), (198,4), (264,4)]
        self.selected_inventory_slot = False
        self.selected_inventory_slot_index = 0
        self.gravity_speed_set = self.gravity_speed

    def apply_movement_physics(self, dt):
        if self.moving_right == True:
            self.movement[0] +=self.vel
        if self.moving_left == True:
            self.movement[0] -= self.vel
        self.movement[1] += self.y_momentum
        self.y_momentum += self.gravity_speed*dt
        if self.y_momentum >self.terminal_vel:
            self.y_momentum = self.terminal_vel
    


    def move(self, tiles, is_player, entity_rects, id, dt):
        self.collision_types = {"top":False, "bottom":False, "right":False, "left":False, "top_enitity" :False, "bottom_entity":False, "left_entity":False, "right_entity":False}
        self.rect.x +=self.movement[0]*dt
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
    

        
        self.rect.y += self.movement[1]*dt
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

    
    def generate_projectile(self, damage,angle, delta_vec, player,dt):
        if player ==True:
            if self.selected_inventory_slot != True and self.selected_inventory_slot != False:
                if self.selected_inventory_slot[0][1] == True:
            
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
            
    

    def handle_projectiles(self, display, scroll, projectile_image, projectile_image_flip, player, dt):
        if player == True:
            for projectile in self.projectiles:                     #loc,vel,facing,rect, damage, angle, delta_vec, projectile_vec
                #projectile[3].x+=self.projectile_vel*projectile[2]

                projectile[3].x += (projectile[6][0]*self.projectile_vel)*dt
                projectile[3].y += (projectile[6][1]*self.projectile_vel)*dt


                if projectile[3].x>scroll[0] and projectile[3].x<scroll[0]+1200:

                    display.blit(pygame.transform.rotate(projectile_image, projectile[5]),(projectile[3].x-scroll[0], projectile[3].y-scroll[1]) )
        else:
            

            for projectile in self.projectiles:
                projectile[3].x+=(self.projectile_vel*projectile[2])*dt

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
    def add_item(self, item_name, item_pic_path, isweapon, tile_number = False):
        item_pic = pygame.image.load(item_pic_path)
        if isweapon == True:
            self.items[item_name] = [item_pic, isweapon]
        elif isweapon ==False:
            self.items[item_name] = [item_pic, isweapon, tile_number ]


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
        
    
          
    def display_inventory(self, inventory_bar, screen, selector):
        self.inventory_bar_loc = ((screen.get_width()/2)-inventory_bar.get_width()/2, 600)
        screen.blit(inventory_bar, (self.inventory_bar_loc))
        for slot in self.inventory:
            if slot!=False:
                screen.blit(slot[0][0], ((self.inventory_bar_loc[0]+(self.inventory_locs[self.inventory.index(slot)][0])), 600+self.inventory_locs[self.inventory.index(slot)][1]))
        screen.blit(selector, ((self.inventory_bar_loc[0]+self.inventory_locs[self.selected_inventory_slot_index][0]),(600+ self.inventory_locs[self.selected_inventory_slot_index][1])))
    
    def change_selected_inventory(self, new_index, addorminus = False):
        if addorminus == False:
            self.selected_inventory_slot_index = new_index
            self.selected_inventory_slot = self.inventory[self.selected_inventory_slot_index]
        elif addorminus == 1:
            self.selected_inventory_slot_index+=1
            if self.selected_inventory_slot_index == 5:
                self.selected_inventory_slot_index = 0
            self.selected_inventory_slot = self.inventory[self.selected_inventory_slot_index]
        elif addorminus == -1:
            self.selected_inventory_slot_index -=1
            if self.selected_inventory_slot_index==-1:
                self.selected_inventory_slot_index =4
            self.selected_inventory_slot = self.inventory[self.selected_inventory_slot_index]
            
    def self_destruct(self, attack):
        self.health = -1
        attack.health = 0
        
        
        
    
        

save_data()
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------
#entity--------------------------------------------------------------------------------------------------------------------------------------------------------------


