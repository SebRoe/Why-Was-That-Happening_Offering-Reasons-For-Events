import pygame, time, json, random 
from pygame.locals import *
from collections import defaultdict
from .utils import spawnRoulette
from .constants import *
from .Player import Player
from .Ground import Ground
from .Enemy import Enemy
from .GoldCoin import GoldCoin
from .PowerUp import PowerUp
from .Goal import Goal
from .Grass import Grass 
from .Sideboard import Sideboard
from .SanityChecker import SanityChecker
from .Agent import Agent, FakeEvent
from pygame_screen_recorder import pygame_screen_recorder as pgr 

class CoinRunner():

    def __init__(self, path, TAG, useAgent=False, max_runs=250, window=True, savescreens=False):

        self.savescreens = savescreens
        print("Savescreens: ", savescreens)
        self.agent = None
        self.window = window


        if useAgent:
            print("Agent is used. Type: ", TAG)

            self.agent = Agent(TAG, max_runs)

        # Paths for current recordings
        self.path_data = path
        self.TAG = TAG

        # Recordings data 
        self.data = None 
        self.current_info = None 
        self.current_run = 0
        self.collected_info = [] 

        # Pygame Setup
        pygame.init()
        pygame.display.set_caption('CoinCollector V1.0')
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        # Pygame Fonts and Background Color 
        self.font_header_max = pygame.font.Font(PATH_FONT, 75)
        self.font_header = pygame.font.Font(PATH_FONT, 50)
        self.font_subheader = pygame.font.Font(PATH_FONT, 35)
        self.font_instructions = pygame.font.Font(PATH_FONT, 25)
        self.font_information = pygame.font.Font(PATH_FONT, 25)
        self.bg_color = (0, 161, 180)

        # Sanity Checker
        self.sanity_checker = SanityChecker()


        # Show Instructions on screen
        self.show_menu(initial_show=True)





    def show_menu(self, initial_show):
        initial_show = initial_show

        while True:

            if not self.current_info is None:
                unique_name = str(int(time.time()))
                new_path = os.path.join(self.path_data, unique_name)
                os.makedirs(new_path, exist_ok=True)
                file_path = os.path.join(new_path, "raw_" + unique_name)

                with open(file_path + ".json", 'w') as f:
                    json.dump(self.current_info, f, indent=4)
                    print(f"\nSaved Informations: {unique_name}.json")

        
            # Texts to be displayed on screen
            texts = []
            infos = [] 

            if initial_show:

                texts.append((self.font_header.render('Welcome to CoinJump V2.0', True, (255, 255, 255)), 25))
                texts.append((self.font_subheader.render('Press Enter to start', True, (255, 255, 255)), 50))

            else:

                result = "Congrats, you won!" if self.current_info["status"]["playerWon"] else "Sorry, you lost!"

                texts.append((self.font_header.render(f'{result}', True, (255, 255, 255)), 25))
                texts.append((self.font_subheader.render('Press Enter to restart.', True, (255, 255, 255)), 20))

                infos.append((self.font_information.render(f'{self.current_run} Round{"s" if self.current_run > 1 else ""} played', True, (255, 255, 255) ), 20))
                infos.append((self.font_information.render(f'Play time: {str(round(self.current_info["status"]["playTime"], 2))}s', True, (255, 255, 255)), 5))
                infos.append((self.font_information.render(f'Killed enemy: {self.current_info["status"]["killedEnemy"]}', True, (255, 255, 255)), 5))
                infos.append((self.font_information.render(f'Collected coin: {self.current_info["status"]["collectedCoin"]}', True, (255, 255, 255)), 5))  
                infos.append((self.font_information.render(f'Collected powerup: {self.current_info["status"]["collectedPowerUp"]}', True, (255, 255, 255)), 5))
                infos.append((self.font_information.render(f'Score: {self.current_info["status"]["finalScore"]}', True, (255, 255, 255)), 5))

            ground = Ground() 
            goal = Goal() 
            enemy = Enemy(moving=True) 
            grass = [Grass() for _ in range(random.randint(15, 25))]

            sideboard = Sideboard() 
            sideboard.set_menu_text()

            menu_sprites = pygame.sprite.Group()
            menu_sprites.add(ground)
            menu_sprites.add(goal)
            menu_sprites.add(enemy)
            menu_sprites.add(sideboard)

            for i in grass:
                menu_sprites.add(i)

            MOVE_ENEMY = pygame.USEREVENT + 1
            pygame.time.set_timer(MOVE_ENEMY, 1000)

            # Gameloop for the menu 
            show_menu, timer_running, start_time, start_game = True, False, None, False  

            if self.agent is not None:
                if not self.agent.isDone():
                    self.agent.next()
                    start_time = time.time()
                    timer_running = True
                else:
                    print("Agent is done")
                    show_menu = False


            while show_menu: 
                
                for entity in menu_sprites:
                    self.screen.blit(entity.surf, entity.rect)

                if not timer_running:
                    ## Showing Text 
                    margin_top = 75 
                    for text, padding in texts:
                        textRect = text.get_rect()
                        margin_top += padding + textRect.height
                        textRect.center = (GAME_WIDTH // 2, margin_top + textRect.height // 2)
                        self.screen.blit(text, textRect)

                    margin_top = 200 
                    for info, padding in infos:
                        textRect = info.get_rect()
                        margin_top += padding + textRect.height
                        textRect.center = (GAME_WIDTH // 2, margin_top + textRect.height // 2 + 75)
                        self.screen.blit(info, textRect)
                else:
                    ## Showing Timer
                    tDiff = int(time.time() - start_time)
                    if tDiff > 1:
                        start_game = True 
                        break  
                    text = self.font_header_max.render(str(1 - tDiff), True, (255, 255, 255))
                    textRect = text.get_rect()
                    textRect.center = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
                    self.screen.blit(text, textRect)


                for event in pygame.event.get():
            
                    if event.type == pygame.QUIT: 
                        show_menu = False 
                        
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN and not timer_running:
                                start_time = time.time()
                                timer_running = True

                        elif event.key == pygame.K_ESCAPE:
                            show_menu = False

                    elif event.type == MOVE_ENEMY:
                        enemy.move()
                    

                

                pygame.display.flip()
                if self.window: self.clock.tick(10)


            if start_game:
                initial_show = self.run() 
            else:
                break 

        pygame.quit()



    def init_sprites(self):

        if pygame.get_init():

            spawn_enemy = spawnRoulette(EXISTENCE_ENEMY)
            spawn_goldcoin = spawnRoulette(EXISTENCE_GOLDCOIN)
            spawn_powerup = spawnRoulette(EXISTENCE_POWERUP)
            
            # Unique Sprites 
            self.goal = Goal(sanity_checker=self.sanity_checker)
            self.player = Player(sanity_checker=self.sanity_checker)
            self.ground = Ground() 

            if spawn_enemy:
                self.enemy = Enemy(moving=ENEMY_MOVING, sanity_checker=self.sanity_checker)
            
            if spawn_goldcoin:
                self.goldcoin = GoldCoin(sanity_checker=self.sanity_checker)
            
            if spawn_powerup:
                self.powerup = PowerUp(sanity_checker=self.sanity_checker)



            self.grass = [Grass() for _ in range(random.randint(15, 25))]
            self.sideboard = Sideboard() 

            # Grouped Sprites
            self.all_sprites = pygame.sprite.Group()
            self.all_sprites.add(self.ground)
            self.all_sprites.add(self.player)
            if spawn_enemy:
                self.all_sprites.add(self.enemy)
            
            if spawn_goldcoin:
                self.all_sprites.add(self.goldcoin)
            
            if spawn_powerup:
                self.all_sprites.add(self.powerup)
            self.all_sprites.add(self.goal)
            self.all_sprites.add(self.sideboard)

            for i in self.grass:
                self.all_sprites.add(i)


            self.recorded_sprites = pygame.sprite.Group()
            self.recorded_sprites.add(self.player)
            if spawn_enemy:
                self.recorded_sprites.add(self.enemy)
            
            if spawn_goldcoin:
                self.recorded_sprites.add(self.goldcoin)
            
            if spawn_powerup:
                self.recorded_sprites.add(self.powerup)
            
            self.recorded_sprites.add(self.goal)
            

            self.goldcoin_sprites = pygame.sprite.Group()
            if spawn_goldcoin:
                self.goldcoin_sprites.add(self.goldcoin)

            self.enemy_sprites = pygame.sprite.Group()
            if spawn_enemy:
                self.enemy_sprites.add(self.enemy)

            self.powerup_sprites = pygame.sprite.Group()
            
            if spawn_powerup:
                self.powerup_sprites.add(self.powerup)

            self.goal_sprites = pygame.sprite.Group()
            self.goal_sprites.add(self.goal)




    def set_initial_informations(self):
        self.current_info["status"]["killedEnemy"] = False
        self.current_info["status"]["collectedCoin"] = False
        self.current_info["status"]["playerWon"] = False
        self.current_info["status"]["killedByEnemy"] = False 

        self.current_info["settings"]["FPS"] = FPS
        self.current_info["settings"]["ENEMY_MOVING"] = ENEMY_MOVING
        self.current_info["settings"]["POSITIONING"] = POSITIONING.value[1]
        self.current_info["settings"]["EXISTENCE_ENEMY"] = EXISTENCE_ENEMY
        self.current_info["settings"]["EXISTENCE_GOLDCOIN"] = EXISTENCE_GOLDCOIN
        self.current_info["settings"]["EXISTENCE_POWERUP"] = EXISTENCE_POWERUP
        self.current_info["settings"]["DISTANCE_METRIC"] = DISTANCE_METRIC.value[1]
        self.current_info["settings"]["TARGETING_METRIC"] = TARGETING_METRIC.value[1]



    def manage_collisions(self, current_frame):

        # Player - Enemy Collision
        col_enemy = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
        if col_enemy:
            if self.player.pu: 
                self.enemy.kill()
                self.current_info["status"]["killedEnemy"] = True
                self.player.killedEnemy = True
                #self.current_info["data"][current_frame]["player"]["killedEnemy"] = True
                self.current_info["data"][current_frame]["player"]["killingEnemy"] = True
                self.current_info["data"][current_frame]["collisions"]["col_playerEnemy"] = True
                del self.current_info["data"][current_frame]["enemy"]
                self.score += 9 
            else:
                self.player.kill() 
                self.current_info["status"]["playerWon"] = False
                self.current_info["status"]["killedByEnemy"] = True
                self.current_info["data"][current_frame]["collisions"]["col_enemyPlayer"] = True 
                self.current_info["data"][current_frame]["collisions"]["col_playerEnemy"] = True
                del self.current_info["data"][current_frame]["enemy"]
                self.score = -20 
                return True 

        # Player - GoldCoin Collision
        col_goldcoin = pygame.sprite.spritecollide(self.player, self.goldcoin_sprites, False)
        if col_goldcoin:
            self.goldcoin.kill()
            self.current_info["status"]["collectedCoin"] = True
            #self.current_info["data"][current_frame]["player"]["collectedCoin"] = True
            self.current_info["data"][current_frame]["player"]["collectingGoldCoin"] = True
            self.current_info["data"][current_frame]["collisions"]["col_playerGoldCoin"] = True
            del self.current_info["data"][current_frame]["goldcoin"]
            self.player.goldCoin = True
            self.score += 5

        # Player - PowerUp Collision
        col_powerup = pygame.sprite.spritecollide(self.player, self.powerup_sprites, False)
        if col_powerup:
            self.player.powerup()
            self.powerup.kill()   
            #self.current_info["data"][current_frame]["player"]["collectedPowerUp"] = True
            self.current_info["data"][current_frame]["player"]["collectingPowerUp"] = True
            self.current_info["data"][current_frame]["collisions"]["col_playerPowerUp"] = True
            self.current_info["status"]["powerup"] = True
            del self.current_info["data"][current_frame]["powerup"]
            

        # Player - Goal Collision 
        col_goal = pygame.sprite.spritecollide(self.player, self.goal_sprites, False)
        if col_goal:
            self.current_info["data"][current_frame]["collisions"]["col_playerGoal"] = True
            self.current_info["status"]["playerWon"] = True
            return True 

        return False 

    def run(self):
        
        # Recorder 
        if self.savescreens:
            recordingSubDir = str(int(time.time()))
            os.makedirs(os.path.join("screenrecordings", recordingSubDir), exist_ok=True)

        self.current_run += 1 
        # Setup new Run
        self.sanity_checker.clean() 
        self.init_sprites()
        self.current_info = defaultdict(dict)
        self.set_initial_informations()
        self.score = 20 

        # Controllers for the game loop
        running = True
        quitted = False 
        current_frame = 0 

        key_mappings = defaultdict(str)
        key_mappings.update({K_w: "W", K_a: "A", K_s: "S", K_d: "D"})
         
        # Custom Events 

        ENEMY_MOVING_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(ENEMY_MOVING, 1000)

        SUBSTRACT_SCORE = pygame.USEREVENT + 2
        self.current_info["status"]["startTime"] = time.time() 
        pygame.time.set_timer(SUBSTRACT_SCORE, 1000)
        while running:
                      
            # Updating data collection 
            current_frame += 1

            lagging_frame = 1 if current_frame == 1 else current_frame - 1

            self.current_info["data"][current_frame] = defaultdict(dict)
            self.current_info["data"][current_frame]["collisions"] = defaultdict(dict)
            self.current_info["data"][current_frame]["collisions"]["col_playerEnemy"] = False
            self.current_info["data"][current_frame]["collisions"]["col_enemyPlayer"] = False 
            self.current_info["data"][current_frame]["collisions"]["col_playerGoldCoin"] = False 
            self.current_info["data"][current_frame]["collisions"]["col_playerPowerUp"] = False
            self.current_info["data"][current_frame]["collisions"]["col_playerGoal"] = False
            self.current_info["data"][current_frame]["pressedKeys"] = []
            self.current_info["data"][current_frame]["eventSubScore"] = False
            self.current_info["data"][current_frame]["frameID"] = current_frame
            self.current_info["data"][current_frame]["terminated"] = False

            # Catching events 
            max_keys_per_frame = 2 
            pressed_keys = []

            if self.agent is not None:
                if current_frame < 3:
                    keys = [ ] 
                else:
                    if current_frame % 2 == 0:
                        directions = self.agent.walk(self.current_info, current_frame)
                        keys = [FakeEvent(type=KEYDOWN, key=direction) for direction in directions]
                        keys.extend(pygame.event.get())
                        if self.savescreens and keys != []:
                            print("Should have saved a screen")
                            pygame.image.save(self.screen, os.path.join("screenrecordings", recordingSubDir, str(current_frame) + ".png"), "PNG")
                    else:
                        keys = [] 
            else:
                keys = pygame.event.get() 
                if self.savescreens and [event for event in keys if event.type == KEYDOWN]:
                    print("Should have saved a screen")
                    pygame.image.save(self.screen, os.path.join("screenrecordings", recordingSubDir, str(current_frame) + ".png"), "PNG")

            for event in keys:

                if event.type == KEYDOWN and max_keys_per_frame > 0:
                    if key_mappings[event.key] != "":
                        self.current_info["data"][lagging_frame]["pressedKeys"].append(key_mappings[event.key])
                        pressed_keys.append(event.key) 
                        max_keys_per_frame -= 1
                    elif event.key == K_ESCAPE:
                        running = False
                        quitted = True
                        break

                elif event.type == pygame.QUIT:
                    running = False 
                    quitted = True
                    break 

                elif event.type == SUBSTRACT_SCORE:
                    if self.score > -20:
                        self.current_info["data"][current_frame]["eventSubScore"] = True
                        self.score -= 1

                elif event.type == ENEMY_MOVING_EVENT and ENEMY_MOVING:
                    self.enemy.move() 
                
            if quitted: break


            # Updating Sprites
            self.player.move(pressed_keys)

            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)


            # Record Updates per Sprite && Create Dictionaries for Collisions
            for entity in self.recorded_sprites:
                entity.record_update(current_frame, lagging_frame,  self.current_info)


            # Collisions
            if self.manage_collisions(current_frame):
                self.current_info["data"][current_frame]["terminated"] = True
                running = False 
                
        
            # Final Steps 
            self.current_info["data"][current_frame]["score"] = self.score
            self.current_info["status"]["collectedPowerUp"] = self.player.pu
            self.current_info["status"]["totalFrames"] = current_frame

            self.current_info = self.sideboard.update(self.current_info, current_frame)
            pygame.display.flip()
            if self.window: self.clock.tick(FPS)



        # Post Game Loop 
        if quitted:
            pygame.quit()
        else:
            self.current_info["status"]["endTime"] = time.time()  
            self.current_info["status"]["playTime"] = self.current_info["status"]["endTime"] - self.current_info["status"]["startTime"]
            self.current_info["status"]["finalScore"] = self.score
            self.current_info["status"]["collectedPowerUp"] = self.player.pu
            self.current_info["status"]["totalFrames"] = current_frame
            return False