#info:
#screen = 1200x714
#widths/heights for sprites are x2 because of scaling



import pygame
import time
from random import randint
from pygame.locals import *
pygame.init()
top_ground = pygame.image.load("topground.png")
ground = pygame.image.load("ground.png")

game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','2','2','2','2','2','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['2','2','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','2','2'],
            ['1','1','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]

#defining functions------------------------------------------------------------------------------------------------------------------------------------------------------

def scale_images(images, scale_factor):
    scaled_images = []
    for image in images:
        scaled_image = pygame.transform.scale(image, (image.get_width() * scale_factor, image.get_height() * scale_factor))
        scaled_images.append(scaled_image)
    return scaled_images
def scale_image(image, scale_factor):
    scaled_image = pygame.transform.scale(image, (image.get_width() * scale_factor, image.get_height() * scale_factor))
    return scaled_image
#--------------------------

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {"top":False, "bottom":False, "right":False, "left":False}
    rect.x +=movement[0]
    hit_list = collision_test(rect, tile)
    for tile in hit_list:
        if movement [0] >0:
            rect.right = tile.left
            collision_types["right"] = True
        elif movement[0] <0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tile)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True

    return rect, collision_types 

    






#class defenitions-------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class player(object):
    def __init__(self, x,y, width, height): 
        
        self.x = x
        self.y = y
        self.position = [self.x, self.y]
        self.width = width*2
        self.height = height *2
        self.vel = 5
        self.isjump = False
        self.Jumpcount = 8
        self.moving_left = False
        self.moving_right = False
        self.walkcount = 0
        self.standing = True
        self.hitbox = (self.x , self.y, self.width, self,height)

        

  
        
    

class projectile(object):
    def __init__(self, x, y, radius, colour, facing):
        self.x = x
        self.y=y
        self.radius = radius
        self.colour = colour
        self.facing = facing
        self.vel = 8 * facing
    def draw(self,win):
        pygame.draw.circle(win, self.colour, (self.x,self.y), self.radius)

class enemy(object):
    Ewalk_left_original = [pygame.image.load("EL1.png"), pygame.image.load("EL2.png"), pygame.image.load("EL3.png"), pygame.image.load("EL4.png"), pygame.image.load("EL5.png"), pygame.image.load("EL6.png")]
    Ewalk_right_original = [pygame.image.load("ER1.png"), pygame.image.load("ER2.png"), pygame.image.load("ER3.png"), pygame.image.load("ER4.png"), pygame.image.load("ER5.png"), pygame.image.load("ER6.png")]
    Ewalk_left = scale_images(Ewalk_left_original,2)
    Ewalk_right = scale_images(Ewalk_right_original, 2)

    def __init__(self, x,y, width, height, end):
        self.x = x
        self.y = y
        self.width = width*2
        self.height = height*2
        self.end = end 
        self.walkcount = 0
        self.vel = 3
        self.path = [self.x, self.end]
        self.hitbox = (self.x , self.y, self.width, self,height)

    def draw(self,win):
        self.move()
        
        
        if self.walkcount +1 >= 18:
            self.walkcount = 0

        if self.vel>0:
            win.blit(self.Ewalk_right[self.walkcount//3], (self.x,self.y))
            self.walkcount+=1
        else:
            win.blit(self.Ewalk_left[self.walkcount//3], (self.x,self.y))
            self.walkcount+=1
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win,(255,0,0), self.hitbox, 2)
        
 
        

    def move(self):
        if self.vel >0:
            if self.x + self.vel<self.path[1] :
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.walkcount = 0
        else:
            if self.x - self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.walkcount = 0

    def hit(self):
        print("hit")


#IMPORTING Sprite--------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
walk_right_original = [pygame.image.load("R1.png"),pygame.image.load("R2.png"),pygame.image.load("R3.png"),pygame.image.load("R4.png"),pygame.image.load("R5.png"),pygame.image.load("R6.png")]
walk_left_original = [pygame.image.load("L1.png"), pygame.image.load("L2.png"),pygame.image.load("L3.png"),pygame.image.load("L4.png"),pygame.image.load("L5.png"),pygame.image.load("L6.png")]
char = pygame.image.load("still.png")
bg = pygame.image.load("backround.png")



walk_right = scale_images(walk_right_original, 2)
walk_left = scale_images(walk_left_original, 2)
char = scale_image(char, 2)
bg = scale_image(bg, 2)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
run = True
screen_width = bg.get_width()
screen_height = bg.get_height()
win = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("wiggle")
clock = pygame.time.Clock()
#drawing-----------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
def redrawGameWindow():
    win.blit(bg,(0,0))

    #space_man------------------------
    win.blit(char, (space_man.x, space_man.y))
    #---------------------------------
    alien.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    #-----tile----------------
    tile_rects = []
    tile_y=0
    for row in game_map:
        tile_x=0
        for tile in row:
            if tile == "1":
                win.blit(ground, (tile_x*66, tile_y * 66))
            if tile == "2":
                win.blit(top_ground, (tile_x*66, tile_y*66))
            if tile != "0":
                tile_rects.append(pygame.Rect(tile_x*66, tile_y*66, 66,66))
            tile_x +=1 
        tile_y+=1
    #------------------------------------


     
    pygame.display.update()

    
#jumping---------------------------
jump_height = 0.45
#-----------------------------------


#mainloop----------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------
space_man = player(900,100,33,33)
alien = enemy(50,100,33, 33,1000)
bullets = []
bullet_limit = 2



while run:
    clock.tick(40)
    print(clock.get_fps())    
    mx,my = pygame.mouse.get_pos()
    #collisions------------------------------------------------
    player_movement = [0,0]
    

   
    #---------tiles---------------------------------------------------
    tile_rects = []
    tile_y=0
    for row in game_map:
        tile_x=0
        for tile in row:
            if tile == "1":
                win.blit(ground, (tile_x*66, tile_y * 66))
            if tile == "2":
                win.blit(top_ground, (tile_x*66, tile_y*66))
            if tile != "0":
                tile_rects.append(pygame.Rect(tile_x*66, tile_y*66, 66,66))
            tile_x +=1 
        tile_y+=1
    


    #----------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
    
    for bullet in bullets:
        if bullet.x < 1200 and bullet.x >0:
            bullet.x +=bullet.vel
        else:
            bullets.pop(bullets.index(bullet))

    #key presses ------------------------------------------------------------------------

    keys = pygame.key.get_pressed()
    KEYDOWN = pygame.KEYDOWN
    KEYUP = pygame.KEYUP
    for event in pygame.event.get():
        if keys[pygame.K_SPACE]:
            if space_man.moving_left:
                facing = -1
            else:
                facing = 1
            if len(bullets) < bullet_limit:
                bullets.append(projectile(round(space_man.x + space_man.width //2), round(space_man.y + space_man.height //2), 6, (255,0,0), facing )) 
        
        if event.type == pygame.KEYDOWN:
            if event.key == K_d:
                space_man.moving_right = True
            if event.key == K_a:
                space_man.moving_left = True
    #movement-------------------------------------------------------------------------------
    if space_man.moving_left:
        space_man.x -= space_man.vel
    if space_man.moving_right:
        space_man.x +=space_man.vel

    redrawGameWindow()

    #--------------------------------------------------------------------------------------
    
pygame.quit()