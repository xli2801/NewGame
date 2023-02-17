import pygame, sys
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 512)  # able to add sound into the game
mixer.init()
pygame.init()

# font
font = pygame.font.SysFont('bauhaus 93', 60)
font2 = pygame.font.SysFont('bauhaus 93', 30)
white = (255, 255, 255)

# game variable
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 500
SPEED = 3
running = True
game_over = False
score = 0
HIGH_SCORE_FILE = open("data/high_score.txt", "r")
high_score = int(HIGH_SCORE_FILE.read())
thorn_frequency = 1500
last_spine = pygame.time.get_ticks() - thorn_frequency
main_menu = True

# create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # size of the screen
clock = pygame.time.Clock()  # frame rate
pygame.display.set_caption("adventure")  # Name the screen


# ___________load images_________
bg_img = pygame.image.load("resources/graphics/background.jpg").convert()
reset_button_img = pygame.image.load("resources/graphics/reset.png").convert()
reset_button_img.set_colorkey((255, 255, 255))
start_button_img = pygame.image.load("resources/graphics/start.png").convert()
exit_button_img = pygame.image.load("resources/graphics/exit.png").convert()
set_button = 0

# ___________load sounds_________
pygame.mixer.music.load("resources/music/background.mp3")
pygame.mixer.music.play(-1, 0.0, 500)
pygame.mixer.music.set_volume(0.3)
coin_fx = pygame.mixer.Sound("resources/sound/coin.mp3")
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound("resources/sound/jump.wav")
jump_fx.set_volume(0.3)
game_over_fx = pygame.mixer.Sound("resources/sound/game_over.mp3")
game_over_fx.set_volume(0.3)
button_fx = pygame.mixer.Sound("resources/sound/click.wav")
button_fx.set_volume(0.3)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))



def reset_game():
    boy.rect.x = 200
    boy.rect.y = 320
    boy.image = pygame.image.load("resources/graphics/character1.png")
    boy.image.set_colorkey((255, 255, 255))  # remove background color
    score = 0
    return score

# _______________classes________________
class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("resources/graphics/floor.jpg").convert()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.floor_x_pos = 0
        self.floor_speed = SPEED

    def update(self):
        if running == True and game_over == False:
            self.rect.x -= self.floor_speed  # floor
            if self.rect.x <= -600:
                self.rect.x = 0


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img = pygame.image.load(f"resources/graphics/character{num}.png")
            img.set_colorkey((255, 255, 255))  # remove background color
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel = 0
        self.clicked = False
        self.jumpCounter = 0

    def update(self):

        if running == True and game_over == False:
            # gravity
            self.vel += 0.25
            if self.rect.y > 320:
                self.rect.y = 320
            self.rect.y += self.vel
            if pygame.sprite.groupcollide(character_group, floor_group, False, False):
                self.vel = 0

            # jump
            key = pygame.key.get_pressed()
            if key[pygame.K_RSHIFT] and self.clicked == False and self.jumpCounter < 1:
                jump_fx.play()
                self.vel = -8
                self.jumpCounter += 1
                self.clicked = True
            if pygame.key.get_pressed()[pygame.K_RSHIFT] == 0:
                self.clicked = False
            if self.rect.y >= 320 and game_over == False:
                self.jumpCounter = 0



            # animation of character
            if self.rect.bottom >= 350 and running == True:  # when the character is on the ground it keeps walking
                self.counter += 1
                walk_cool_down = 8
                if self.counter > walk_cool_down:
                    self.counter = 0
                    self.index += 1
                    if self.index >= len(self.images):
                        self.index = 0
                self.image = self.images[self.index]

            # rotate the character
            self.image = pygame.transform.rotate(self.images[self.index], self.vel*-1)
        elif game_over == True:
            self.image = pygame.image.load("resources/graphics/ghost.png")
            self.image.set_colorkey((255, 255, 255))  # remove background color
            self.rect.y -= 3


class Thorn (pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("resources/graphics/spine.png").convert()
        self.rect = self.image.get_rect(center=(x, y))


    def update(self):
        if running == True:
            self.rect.x -= SPEED
            if self.rect.right < 0:  # delete the spines that have passed
                self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("resources/graphics/coin.png").convert()
        self.image.set_colorkey((0, 0, 0))  # remove background color
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if running == True:
            self.rect.x -= SPEED
            if self.rect.right < 0:  # delete the coins that have passed
                self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                button_fx.play()
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

# _____________ end of class ____________________


character_group = pygame.sprite.Group()
thorn_group = pygame.sprite.Group()
floor_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

boy = Character(200, 320)
character_group.add(boy)
floor = Floor(0, 350)
floor_group.add(floor)

reset_button = Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20, reset_button_img)
start_button = Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20, start_button_img)
exit_button = Button(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60, exit_button_img)

# run the game
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(bg_img, (0, 0))  # background image

    if main_menu == True:
        draw_text("Highest Score: " + str(high_score), font, white, SCREEN_WIDTH / 4, 20)
        draw_text("ADVENTURE", font, (55, 92, 210), 170, 140)
        draw_text("Press shift to jump...", font2, (55, 200, 210), 200, 180)
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            run = False

    else:
        floor_group.draw(screen)
        floor_group.update()  # draw the floor
        draw_text(str(score), font, white, SCREEN_WIDTH / 2, 20)

        # collision
        if pygame.sprite.groupcollide(character_group, thorn_group, False, False):
            game_over_fx.play()
            game_over = True
            running = False

        if running == True and game_over == False and pygame.sprite.groupcollide(character_group, coin_group, False, True):
            coin_fx.play()
            score += 1

        # check for game over and reset
        if game_over == True:
            draw_text("Game Over", font, (55, 92, 210), 185, 140)
            if score > high_score:
                high_score = score
                f = open("data/high_score.txt", "w")
                f.write(str(high_score))
            draw_text("Highest Score: " + str(high_score), font2, white, 240, 60)
            thorn_group.empty()
            coin_group.empty()
            if exit_button.draw():
                    run = False
            if reset_button.draw():
                game_over = False
                running = True
                score = reset_game()



        if running == True and game_over == False:
            # generate the thorns
            time_now = pygame.time.get_ticks()
            if time_now - last_spine > thorn_frequency:
                thorn = Thorn(SCREEN_WIDTH + 100, 345)
                coin = Coin(SCREEN_WIDTH + random.randint(0, 200), 300 - random.randint(0, 200))
                thorn_frequency = random.randint(500, 1500)
                thorn_group.add(thorn)
                coin_group.add(coin)
                last_spine = time_now


        coin_group.draw(screen)  # coin
        coin_group.update()
        thorn_group.draw(screen)  # spine
        thorn_group.update()
        character_group.draw(screen)  # character
        character_group.update()
    pygame.display.update()
    clock.tick(100)




