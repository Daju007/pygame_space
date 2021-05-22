import pygame
import time
from random import randint
pygame.init()
run = True
screen_width = 1000
screen_height = 1000
win = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("wiggle")

#jumping---------------------------
isJump = False
Jumpcount = 10
jump_height = 0.5
#-----------------------------------

x=50
y=930
width = 40
height= 60
vel = 1
while run:
    win.fill((0,255,0))
    mx,my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
    #key presses ------------------------------------------------------------------------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and x>vel:
        x-=vel
    if keys[pygame.K_d] and x<screen_width-width-vel:
        x+=vel
    if not(isJump):
        if keys[pygame.K_SPACE]:
            isJump = True
    else:
        if Jumpcount>= -10:
            neg=1
            if Jumpcount<0:
                neg= -1

            y-=(Jumpcount**2)*jump_height*neg
            Jumpcount -=1
            time.sleep(0.02)
            
        else:
            isJump = False
            Jumpcount = 10

    #--------------------------------------------------------------------------------------
    pygame.draw.rect(win, (0,0,255), (x, y, width, height))
    pygame.image.load("C:\Users\Daniel\Desktop\Python programs\Pygameting\Sprite_still.png")
    
    
    pygame.display.update()
pygame.quit()