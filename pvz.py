import random
import pygame
from cursor import Cursor
from plant import Peashooter, Sunflower, Bullet
from enemy import Enemy
from terrain import *
from boxes import *
from button import ButtonStart, ButtonConfig, ButtonExit, ButtonRestart

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GAME_NAME = 'Plantas vs Zumbis'

size = [SCREEN_WIDTH, SCREEN_HEIGHT]

class SunLight(pygame.sprite.Sprite):
    def __init__(self, isRandom=True, pos=(0, 0)):
        super().__init__()

        self.image = pygame.transform.smoothscale(pygame.image.load("graphics/sol/sol.png").convert_alpha(), (22, 22))
        self.rect = self.image.get_rect(bottomleft=pos)

        self.isRandom = isRandom
        self.initial_x = pos[0]
        self.initial_y = pos[1]

        if isRandom:
            self.initial_x = random.randint(150, 1000)
            self.rect.x = self.initial_x
            self.rect.y = -20
            self.final_y = random.randint(200, 600)
        else:
            self.yvertice = 120
            self.b = random.randint(9, 18)
            self.a = ((self.b ** 2) * -1) / (4 * self.yvertice)
            self.flag = True
            self.direcao = random.randint(0, 1)
            self.x = 0.8

    def check_click(self, mouse):
        if self.rect.colliderect(mouse):
            return True

    def update(self):
        if self.isRandom:
            if not self.rect.bottom > self.final_y:
                self.rect.y += 2
        else:
            if self.rect.y < self.initial_y:
                self.y = ((self.a * (self.x ** 2)) + (self.b * self.x)) * -1
                self.rect.y = self.initial_y + self.y

                if self.direcao == 0:
                    self.rect.x = self.initial_x + self.x
                else:
                    self.rect.x = self.initial_x + (self.x * -1)

                self.x += 0.8


class Game:
    def add_plant(self, grass: Grass, plantType):
        grass.has_plant = True
        plant = plantType(grass.rect.center)

        if plant.shooter:
            self.shooter_plant_group.add(plant)
        
        if plant.__class__ == Sunflower().__class__:
            self.sunflower_group.add(plant)
        
        self.plant_group.add(plant)
        
        plant.terrain = grass

    def display_money(self, screen):
        
        self.game_font = pygame.font.Font('font/font.ttf', 72)
        self.money_surf = self.game_font.render(f'{self.money}$', False, (255, 255, 255))
        
        self.game_font = pygame.font.Font('font/font.ttf', 30)
        self.cost_peashooter = self.game_font.render('100$', False, (255, 255, 255))
        self.cost_sunflower = self.game_font.render('50$', False, (255, 255, 255))
        self.cost_wallnut = self.game_font.render('50$', False, (255, 255, 255))

        self.money_rect = self.money_surf.get_rect(topleft=(28, 44))
        self.peashooter_rect = self.cost_peashooter.get_rect(topleft=(155, 20))
        self.sunflower_rect = self.cost_sunflower.get_rect(topleft=(300, 20))
        self.wallnut_rect = self.cost_wallnut.get_rect(topleft=(430, 20))
        
        screen.blit(self.money_surf, self.money_rect)
        screen.blit(self.cost_peashooter, self.peashooter_rect)
        screen.blit(self.cost_sunflower, self.sunflower_rect)
        screen.blit(self.cost_wallnut, self.wallnut_rect)

    def __init__(self):
        self.game_over = False
        self.score = 0

        self.shoot = pygame.mixer.Sound('sfx/shoot.mp3')
        self.damage = pygame.mixer.Sound('sfx/damage.mp3')

        self.zombie_sound1 = pygame.mixer.Sound('sfx/zombie_sound1.mp3')
        self.zombie_sound2 = pygame.mixer.Sound('sfx/zombie_sound2.mp3')
        self.zombie_sound3 = pygame.mixer.Sound('sfx/zombie_sound3.mp3')

        self.shoot.set_volume(0.3)
        self.damage.set_volume(0.3)

        self.background = pygame.image.load("graphics/background.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (1200,680))
        self.background_rect = self.background.get_rect(topleft = (0,120))
        self.menu = pygame.image.load("graphics/menuBar.png").convert_alpha()
        self.menu = pygame.transform.scale(self.menu,(1200, 120))
        self.menu_rect = self.menu.get_rect(topleft = (0,0))
        self.game_font = pygame.font.Font('font/font.ttf', 66)
        #Variáveis de hordas
        self.spawning = False
        self.zombie_timer = pygame.USEREVENT + 2
        self.break_time = pygame.USEREVENT + 3
        self.second_break_time = pygame.USEREVENT + 4
        self.super_horde = pygame.USEREVENT + 5
        self.zombie_sound = pygame.USEREVENT + 6

        self.quantity = 1
        self.quantity_hordes = 1
        self.difficulty = 1
        self.spawns = 0
        self.horde_active = False
        self.n_hordes = 0


        self.sprite_group = pygame.sprite.Group()
        self.plant_group = pygame.sprite.Group()
        self.shooter_plant_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.grass_group = pygame.sprite.Group()
        self.bullets_groups = pygame.sprite.Group()
        self.draggable_group = pygame.sprite.Group()
        self.boxes_group = pygame.sprite.Group()
        self.sunflower_group = pygame.sprite.Group()

        self.peashooter_box = PeashooterBox((178, 38))

        self.sprite_group.add(self.peashooter_box)
        self.draggable_group.add(self.peashooter_box)
        self.boxes_group.add(self.peashooter_box)

        self.sunflower_box = SunflowerBox((312, 38))
        self.sprite_group.add(self.sunflower_box)
        self.draggable_group.add(self.sunflower_box)
        self.boxes_group.add(self.sunflower_box)
        
        self.wallnut_box = WallnutBox((448, 38))
        self.sprite_group.add(self.wallnut_box)
        self.draggable_group.add(self.wallnut_box)
        self.boxes_group.add(self.wallnut_box)

        self.money = 250

        self.dragging_plant = None
        self.dragging_plant_group = pygame.sprite.GroupSingle()

        self.grass_x = 345
        self.grass_y = 250
        self.grass_gap_x = 94
        self.grass_gap_y = 112

        for i in range(5):
            for j in range(9):
                grass = Grass((self.grass_x + (j * self.grass_gap_x), self.grass_y + (i * self.grass_gap_y)))
                self.grass_group.add(grass)
                self.sprite_group.add(grass)

        self.shovel = Shovel()
        self.shovel_sprite = pygame.sprite.GroupSingle()
        self.shovel_sprite.add(self.shovel)
        self.draggable_group.add(self.shovel)

        self.cursor = Cursor()
        self.cursor_sprite = pygame.sprite.GroupSingle()
        self.cursor_sprite.add(self.cursor)

        self.sun_group = pygame.sprite.Group()
        self.obstacle_timer = pygame.USEREVENT + 1

        pygame.time.set_timer(self.obstacle_timer, 12000)
        pygame.time.set_timer(self.zombie_timer, 7000)
        pygame.time.set_timer(self.break_time, 2300)
        pygame.time.set_timer(self.second_break_time, 1000)
        pygame.time.set_timer(self.super_horde, 50000)
        pygame.time.set_timer(self.zombie_sound, 15000)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return True
            
            self.cursor.mouse_events(event, self.draggable_group)

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_DOWN:
            #         for i in range(5):
            #             enemy = Enemy((400, self.grass_y + (i * self.grass_gap_y) - 25))
            #             self.enemy_group.add(enemy)
            #             # self.sprite_group.add(enemy)

            if event.type == self.obstacle_timer:
                    self.sun_group.add(SunLight())

            if not self.spawning:
                if event.type == self.zombie_timer:
                    self.spawning = True

            if self.spawning:
                self.spawns += 1
                num = random.randint(0, 4)
                
                x = random.randint(1300, 1600)
                enemy = Enemy((x, self.grass_y + (num * self.grass_gap_y) - 25))

                self.enemy_group.add(enemy)
                # self.sprite_group.add(enemy)

                if self.spawns >= int(self.quantity):
                    self.spawns = 0
                    self.spawning = False
                    self.difficulty += 1
                    self.quantity = 1/2 * (self.difficulty ** 1/2) + 1

            if not self.horde_active:
                if event.type == self.super_horde:
                    self.horde_active = True

            if self.zombie_sound:
                num = random.randint(1, 220)

                if num == 1:
                    self.zombie_sound1.play()
                elif num == 2:
                    self.zombie_sound2.play()
                elif num == 3:
                    self.zombie_sound3.play()

                num = 4

            if self.horde_active:
                if event.type == self.second_break_time:
                    if self.n_hordes <= int(self.quantity_hordes):
                        self.n_hordes += 1
                        for i in range(5):
                            enemy = Enemy((1200, self.grass_y + (i * self.grass_gap_y) - 25))

                            self.enemy_group.add(enemy)
                            # self.sprite_group.add(enemy)

                if self.n_hordes >= int(self.quantity_hordes):
                    self.horde_active = False
                    self.quantity_hordes = 1 + self.quantity_hordes * self.quantity_hordes

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Shovel Click Logic

                for sun in self.sun_group:
                    if sun.check_click(self.cursor.rect):
                        self.money += 50
                        sun.kill()


                if self.shovel.rect.colliderect(self.cursor.rect):
                    self.shovel.isDragging = True

                for box in self.boxes_group:
                    if box.rect.colliderect(self.cursor.rect) and self.money >= box.price:
                        # self.dragging_plant = Plant(pygame.mouse.get_pos())
                        self.dragging_plant = box.getPlant(pygame.mouse.get_pos()) 
                        
                        self.dragging_plant_group.add(self.dragging_plant)
                        self.draggable_group.add(self.dragging_plant)
                        break
                    else:
                        if self.dragging_plant:
                            self.dragging_plant.kill()
                            self.dragging_plant = None
                        
            
            # Shovel Logic
            if event.type == pygame.MOUSEBUTTONUP:    
                if self.shovel.isDragging:
                    if self.shovel.selected_plant is not None:
                        grass = pygame.sprite.spritecollide(self.shovel.selected_plant, self.grass_group, False)
                        grass[0].has_plant = False

                        self.shovel.selected_plant.kill()
                    self.shovel.isDragging = False
            
                if self.dragging_plant is not None:
                    grass = pygame.sprite.spritecollide(self.dragging_plant, self.grass_group, False)
                    if grass:
                        if not grass[0].has_plant:

                            self.money -= self.dragging_plant.price
                            self.add_plant(grass[0], self.dragging_plant.__class__)
                    self.dragging_plant.kill()
                    self.dragging_plant = None


    def run_logic(self):
        if not self.game_over:
            for enemy in self.enemy_group:
                collide_plant = pygame.sprite.spritecollide(enemy, self.plant_group, False)

                if enemy.rect[0] < 230:
                    self.game_over = True

                if collide_plant:
                    enemy.speed = 0
                    enemy.give_damage(collide_plant[0])
                    
                else:
                    enemy.speed = 0.5

            for plant in self.shooter_plant_group:
                bullets = None
                if pygame.sprite.spritecollide(plant.plant_range, self.enemy_group, False):
                    bullets = plant.shoot()
                if bullets is not None:
                    self.bullets_groups.add(bullets)
                    self.sprite_group.add(bullets)

                    count = 0
                    for plant in self.plant_group:
                        count+=1

                    num = 0

                    if num > 0:
                        num = random.randint(1, count)

                    if num == 1:
                        self.shoot.play()

            for bullet in self.bullets_groups:
                collide_enemy = pygame.sprite.spritecollide(bullet, self.enemy_group, False)
                if collide_enemy:
                    if bullet.give_damage(collide_enemy[0]) == -1:
                        self.score+=5
                    self.damage.play()
            
            for sunflower in self.sunflower_group:
                if sunflower.drop_sun():
                    self.sun_group.add(SunLight(False, sunflower.rect.midbottom))



            collide_shovel = pygame.sprite.spritecollide(self.shovel, self.plant_group, False)

            if collide_shovel:
                self.shovel.collide_logic(collide_shovel[0])
            else:
                self.shovel.collide_detach()

            
    def display_frame(self, screen):
        screen.fill('Black')
        if not self.game_over:
            screen.blit(self.menu, self.menu_rect)
            screen.blit(self.background ,self.background_rect)
            self.sprite_group.draw(screen)
            self.sprite_group.update()
            self.plant_group.draw(screen)
            self.plant_group.update()
            self.enemy_group.draw(screen)
            self.enemy_group.update()
            self.shovel_sprite.update()
            self.shovel_sprite.draw(screen)

            self.display_money(screen)

            self.game_font = pygame.font.Font('font/font.ttf', 72)
            self.score_surf = self.game_font.render(f'Score: {self.score}', False, (255, 255, 255))
            self.score_rect = self.score_surf.get_rect(topleft=(820, 14))

            screen.blit(self.score_surf, self.score_rect)


            if self.dragging_plant is not None:
                grass = pygame.sprite.spritecollide(self.dragging_plant, self.grass_group, False)
                if grass:
                    if not grass[0].has_plant:
                        temp_image = self.dragging_plant.image
                        # temp_image.fill(self.dragging_plant.__class__.color)
                        temp_rect = temp_image.get_rect(center=(grass[0].rect.center))
                        screen.blit(temp_image, temp_rect)


            if self.dragging_plant is not None:
                self.dragging_plant_group.draw(screen)
                self.dragging_plant.rect.center = pygame.mouse.get_pos()

            self.sun_group.draw(screen)
            self.sun_group.update()

            self.cursor_sprite.update()
            self.cursor_sprite.draw(screen)


class Menu():
    def __init__(self):
        self.game_font = pygame.font.Font('font/Zombie Slayer.ttf', 72)
        self.sprite_group = pygame.sprite.Group()
        self.button_group = pygame.sprite.Group()
        self.started = False
        button_start = ButtonStart((450, 250))
        button_config = ButtonConfig((400, 400))
        button_exit = ButtonExit((470, 550))
        
        self.title = self.game_font.render(GAME_NAME, False, (255, 255, 255))
        self.title.get_rect(topleft=(400, 240))

        self.button_group.add(button_start)
        self.button_group.add(button_config)
        self.button_group.add(button_exit)

        self.sprite_group.add(button_start)
        self.sprite_group.add(button_config)
        self.sprite_group.add(button_exit)

        self.cursor = Cursor()
        self.cursor_sprite = pygame.sprite.GroupSingle()
        self.cursor_sprite.add(self.cursor)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            self.cursor.mouse_events(event, self.button_group)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.button_group:
                    if button.check_click(self.cursor.rect.topleft):
                        if button.do_action() == "exit":
                            return True
                        elif button.do_action() == "start":
                            return "start"

    def run_logic(self):
        if not self.started:
            for button in self.button_group:
                if button.check_click(self.cursor.rect.topleft):
                    button.do_action()

    def display_frame(self, screen):
        screen.fill('Black')
        
        screen.blit(self.title, (290, 120))

        if not self.started:
            self.sprite_group.draw(screen)
            self.sprite_group.update()

            self.cursor_sprite.update()
            self.cursor_sprite.draw(screen)


class GameOver():
    def __init__(self):
        self.game_font = pygame.font.Font('font/Zombie Slayer.ttf', 72)
        self.sprite_group = pygame.sprite.Group()
        self.button_group = pygame.sprite.Group()

        button_restart = ButtonRestart((535, 550))

        self.image = pygame.image.load('graphics/brain.jpg').convert_alpha()
        self.title = self.game_font.render('GAME OVER', False, (255, 255, 255))
        self.title.get_rect(topleft=(500, 240))

        self.button_group.add(button_restart)
        self.sprite_group.add(button_restart)

        self.cursor = Cursor()
        self.cursor_sprite = pygame.sprite.GroupSingle()
        self.cursor_sprite.add(self.cursor)
        self.score = 0
        self.text = ""

    def set_score(self, score, new_high = False):
        if new_high:
            self.text = "New High Score! "
        else:
            self.text = "Score Final: "

        self.score = score

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

            self.cursor.mouse_events(event, self.button_group)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.button_group:
                    if button.check_click(self.cursor.rect.topleft):
                        if button.do_action() == "restart":
                            return True

    def run_logic(self):
        for button in self.button_group:
            if button.check_click(self.cursor.rect.topleft):
                button.do_action()

    def display_frame(self, screen, max_score):
        screen.fill('Black')


        self.game_font = pygame.font.Font('font/font.ttf', 72)
        self.score_surf = self.game_font.render(f"{self.text}: {self.score} / High Score: {max_score}", False, (255, 255, 255))
        self.score_surf.get_rect(topleft=(350, 550))

        screen.blit(self.title, (430, 120))
        screen.blit(self.score_surf, (430, 240))
        screen.blit(self.image, (350, 350))

        self.sprite_group.draw(screen)
        self.sprite_group.update()
        self.cursor_sprite.update()
        self.cursor_sprite.draw(screen)


def main():
    pygame.init()

    pygame.mixer.init()

    screen = pygame.display.set_mode(size)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(GAME_NAME)

    done = False
    clock = pygame.time.Clock()
    game = Game()
    menu = Menu()
    gameOver = GameOver()

    states = ["MENU", "GAME", "GAMEOVER"]
    actual_state = states[0]
    max_score = 0

    flag = True

    while not done:
        if actual_state == states[0]:
            done = menu.process_events()
            menu.run_logic()
            menu.display_frame(screen)

            if flag:
                pygame.mixer.music.load('sfx/menu_there.mp3')
                pygame.mixer.music.play(loops=-1)
                flag = False

            if done == "start":
                pygame.time.set_timer(game.super_horde, 50000)
                actual_state = states[1]
                done = None
                flag = True
        elif actual_state == states[1]:
            done = game.process_events()
            game.run_logic()
            game.display_frame(screen)
            
            if flag:
                pygame.mixer.music.load('sfx/main_theme.mp3')
                pygame.mixer.music.play(loops=-1)
                flag = False

            if game.game_over:
                flag = True
                game.enemy_group.empty()
                game.plant_group.empty()
                game.difficulty = 1
                game.spawns = 0
                game.quantity = 1
                game.n_hordes = 0
                game.quantity_hordes = 1
                game.sun_group.empty()
                game.sunflower_group.empty()
                game.shooter_plant_group.empty()
                pygame.time.set_timer(game.super_horde, 0)

                if game.score > max_score:
                    max_score = game.score
                    gameOver.set_score(game.score, True)
                else:
                    gameOver.set_score(game.score)

                game.score = 0


                for grass in game.grass_group:
                    if grass.has_plant:
                        grass.has_plant = False


                game.money = 250
                game.game_over = False
                actual_state = states[2]

        elif actual_state == states[2]:
            restart = gameOver.process_events()
            gameOver.run_logic()
            gameOver.display_frame(screen, max_score)
            
            if flag:
                pygame.mixer.music.load('sfx/menu_there.mp3')
                pygame.mixer.music.play(loops=-1)
                flag = False

            if restart:
                actual_state = states[0]
            
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':

    main()
