import pygame, sys
from os.path import join

from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if  self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

         # Zorg ervoor dat de speler niet uit het scherm kan
        self.rect.centerx = max(self.rect.width // 2, min(self.rect.centerx, WINDOW_WIDTH - self.rect.width // 2))
        self.rect.centery = max(self.rect.height // 2, min(self.rect.centery, WINDOW_HEIGHT - self.rect.height // 2))

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
         
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.scale = uniform(0.5, 1.5)
        self.original_surf = pygame.transform.rotozoom(surf, 0, self.scale)
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play() 

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)
    
    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False
    
    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

def collisions():
    global running
    global current_score

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        for meteor in meteor_sprites:
            meteor.kill()
        running = False


    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            current_score += 1

def display_score():
    global current_score

    text_surf = font.render(str(current_score), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def get_font(size):
    return pygame.font.Font(join('images', 'Oxanium-bold.ttf'), size)

# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1152, 648
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')
running = True
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
background_img = pygame.image.load(join('images', 'background.jpeg')).convert_alpha()

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops= -1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


def game():
    global running
    global current_score

    current_score = 0

    while running:
        dt = clock.tick() / 1000
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                Meteor(meteor_surf, (x,y), (all_sprites, meteor_sprites))
        # update
        all_sprites.update(dt)
        collisions()

        # draw the game
        display_surface.fill('#3a2e3f')
        display_score()
        all_sprites.draw(display_surface)

        pygame.display.update()

def main_menu():
    global running

    while True:
        display_surface.blit(background_img, (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        menu_text = get_font(100).render("Space Shooters", True, "#b68f40")
        menu_rect = menu_text.get_rect(center=(WINDOW_WIDTH/2, 100))

        play_button = Button(image=pygame.image.load(join('images', 'button.png')), pos=(WINDOW_WIDTH/2, 250), 
                            text_input="Play", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        quit_button = Button(image=pygame.image.load(join('images', 'button.png')), pos=(WINDOW_WIDTH/2, 400), 
                            text_input="Quit", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        display_surface.blit(menu_text, menu_rect)

        for button in [play_button, quit_button]:
            button.changeColor(menu_mouse_pos)
            button.update(display_surface)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    running = True
                    game()
                if quit_button.checkForInput(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()

pygame.quit()