import pygame
import sys
import random
from concurrent.futures import ProcessPoolExecutor
from modules.General import controlls
from modules.General.functions import Button, SaveData
from modules.General.globals import *
from modules.Entitys.imports import Player, Enemy
from modules.General.premade_weapons import WeaponLoader
from modules.General.types import Groups
from modules.Map.tiles import TileMap
from modules.General.functions import Camera, check_input, a_star

def draw_text(text: str,
              font: pygame.font.Font,
              screen: pygame.Surface,
              pos_left: tuple[int, int] = None,
              pos_right: tuple[int, int] = None):
    """
    Draws a given text string onto a given screen at the specified position.

    Args:
        text (str): The text to be drawn.
        font (pygame.font.Font): The font to use for the text.
        screen (pygame.Surface): The screen to draw the text onto.
        pos_left (tuple[int, int], optional): The top left coordinate of the text. Defaults to None.
        pos_right (tuple[int, int], optional): The top right coordinate of the text. Defaults to None.
    """
    text_surface = font.render(text, True, (255, 255, 255))
    rect = text_surface.get_rect()
    if pos_left:
        rect.topleft = pos_left
    else:
        rect.topright = pos_right
    screen.blit(text_surface, rect)

def compute_path(args):
    """
    Computes the shortest path from the given start position to the target rectangle
    avoiding the given walls using A* pathfinding.

    Args:
        args (tuple): A tuple containing the start position, target rectangle, walls, grid size, buffer
            and maximum distance.

    Returns:
        list[pygame.Vector2]: A list of positions representing the shortest path from the start position
            to the target rectangle.
    """
    start_pos, target_rect, walls, grid_size, buffer, max_distance = args
    return a_star(start=start_pos,
                  target=target_rect,
                  blocking=walls,
                  grid_size=grid_size,
                  buffer=buffer,
                  max_distance=max_distance)


def show_survival_stats(survived_waves, time_alive):
    """
    Displays the survival statistics on the screen and waits for user input to continue.

    This function fills the screen with a black background and renders the survival
    statistics including the number of survived waves and the time alive. It waits
    for the user to press any key or mouse button to continue.

    Args:
        survived_waves (int): The number of waves the player survived.
        time_alive (float): The amount of time the player stayed alive in seconds.
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    font_large = pygame.font.SysFont('Arial', 50)
    font_small = pygame.font.SysFont('Arial', 36)
    screen_width = changeable_values.SCREEN.width
    
    waiting = True
    while waiting:
        changeable_values.SCREEN.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        title = font_large.render("Survival Statistics", True, WHITE)
        waves_text = font_small.render(f"Survived Waves: {survived_waves}", True, WHITE)
        time_text = font_small.render(f"Time Alive: {time_alive:.2f} seconds", True, WHITE)
        prompt = font_small.render("Press any key to continue...", True, WHITE)
        
        changeable_values.SCREEN.blit(title, (screen_width//2 - title.get_width()//2, 150))
        changeable_values.SCREEN.blit(waves_text, (screen_width//2 - waves_text.get_width()//2, 250))
        changeable_values.SCREEN.blit(time_text, (screen_width//2 - time_text.get_width()//2, 300))
        changeable_values.SCREEN.blit(prompt, (screen_width//2 - prompt.get_width()//2, 450))
        
        pygame.display.flip()


class Difficulty_Chooser:
    """
    Class for the difficulty chooser menu.

    This class handles the logic for the difficulty chooser menu, including the display of the
    difficulty buttons and the handling of user input to select a difficulty.

    Attributes:
        screen (pygame.Surface): The screen to display the menu on.
        font (pygame.font.Font): The font to use for the text.
        easy_button (Button): The button for the easy difficulty.
        medium_button (Button): The button for the medium difficulty.
        hard_button (Button): The button for the hard difficulty.
        buttons (list[Button]): A list of all the difficulty buttons.

    Methods:
        run(): Runs the difficulty chooser menu."""
    def __init__(self, screen: pygame.Surface):
        """
        Initializes the Difficulty_Chooser class.

        Args:
            screen (pygame.Surface): The screen to display the menu on.

        Attributes:
            screen (pygame.Surface): The screen to display the menu on.
            font (pygame.font.Font): The font to use for the text.
            easy_button (Button): The button for the easy difficulty.
            medium_button (Button): The button for the medium difficulty.
            hard_button (Button): The button for the hard difficulty.
            buttons (list[Button]): A list of all the difficulty buttons.
        """

        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.easy_button = Button(text="EASY", center_x=screen.get_width() // 2, center_y=150, width=400, height=120, callback=lambda: "EASY")
        self.medium_button = Button(text="MEDIUM", center_x=screen.get_width() // 2, center_y=350, width=400, height=120, callback=lambda: "MEDIUM")
        self.hard_button = Button(text="HARD", center_x=screen.get_width() // 2, center_y=550, width=400, height=120, callback=lambda: "HARD")
        self.buttons = [self.easy_button, self.medium_button, self.hard_button]

    def run(self):
        """
        Runs the difficulty chooser menu.

        This method runs the difficulty chooser menu and returns the chosen difficulty
        as a string. The menu displays three buttons for the easy, medium and hard
        difficulties and waits for the user to select one. If the user presses the
        escape key, the method returns None.

        Returns:
            str: The chosen difficulty as a string, or None if the user pressed the
                escape key.
        """
        running = True
        chosen_difficulty = None

        while running:
            self.screen.fill((100, 100, 100))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                for button in self.buttons:
                    result = button.handle_event(event)
                    if result:
                        chosen_difficulty = button.text
                        running = False

            for button in self.buttons:
                button.draw(self.screen)

            text = self.font.render("ESC TO GET BACK", True, (255, 0, 0))
            self.screen.blit(text, (5, self.screen.get_height() - 30))
            pygame.display.flip()

        return chosen_difficulty


class ENDLESS:
    """
    Class representing the endless mode of the game.

    Attributes:
        stat_saver (SaveData): A SaveData object for saving and loading the player stats.
        screen (pygame.Surface): The main screen surface.
        map (TileMap): The TileMap object representing the map.
        entity_surface (pygame.Surface): The surface for drawing entities.
        completed (bool): Whether the game is completed.
        kills (int): The number of kills the player has.
        clock (pygame.time.Clock): The clock object for tracking time.
        wave (int): The current wave number.
        kills (int): The number of kills the player has.
        alive_enemies (int): The number of alive enemies.
        difficulty (dict): A dictionary with the difficulty settings.
        wave_difficulty (dict): A dictionary containing the wave difficulty settings.
        wave_number (int): The current wave number.
        wave_kills (int): The number of kills in the current wave.
        wave_alive_enemies (int): The number of alive enemies in the current wave.
        """
    def __init__(self):
        """
        Initializes the ENDLESS class.

        This method initializes the ENDLESS class. It creates a TileMap object
        from the map_endless.csv and Floors.png files, creates a surface for
        drawing entities, and sets up the difficulty settings. It also sets up
        the wave and kill counters, the clock, and the ProcessPoolExecutor for
        running the waves in parallel.

        Attributes:
            stat_saver (SaveData): A SaveData object for saving and loading the
                player stats.
            screen (pygame.Surface): The main screen surface.
            map (TileMap): The TileMap object representing the map.
            entity_surface (pygame.Surface): The surface for drawing entities.
            completed (bool): Whether the game is completed.
            kills (int): The number of kills the player has.
            clock (pygame.time.Clock): The clock object for tracking time.
            wave (int): The current wave number.
            kills (int): The number of kills the player has.
            alive_enemies (int): The number of alive enemies.
            difficulty (dict): A dictionary with the difficulty settings.
            executor (ProcessPoolExecutor): The ProcessPoolExecutor for running
                the waves in parallel.
            wave_futures (list): A list of futures for the waves.
            walls (list): A list of walls.
            font (pygame.font.Font): The font for drawing text.
            entity_init (function): A function to initialize the entities.
        """
        self.stat_saver = SaveData(changeable_values.DEFAULT_PATH + r"/assets/saved_datas/player_stats.json")
        self.screen = changeable_values.SCREEN
        self.map = TileMap(changeable_values.DEFAULT_PATH + r"/assets/maps/endless/map_endless.csv",
                  changeable_values.DEFAULT_PATH + r"/assets/maps/endless/Floors.png",
                  final_tile_size=64)
        self.entity_surface = pygame.Surface(self.map.screen.size, pygame.SRCALPHA)
        self.completed = False
        self.kills = 0

        self.clock = pygame.time.Clock()
        self.wave: int = 1
        self.kills: int = 0
        self.alive_enemies: int = 1
        self.difficulty = {"EASY": (0.5, 200, 10, 100), 
                           "MEDIUM": (0.75, 150, 20, 50),
                           "HARD": (1, 100, 30, 25)} # speed, playerhp, enemyhp, hp_gain_pw

        self.executor = ProcessPoolExecutor()
        self.wave_futures = []

        self.walls = self.map.walls
        self.font = pygame.font.SysFont("Courier", 32, True)
        self.entity_init()

    def entity_init(self):
        """
        Initializes the entities for the ENDLESS game mode.

        This method initializes the entities for the ENDLESS game mode. It sets
        up the player, the enemy spawns, the camera, and the weapon loader.

        Attributes:
            enemy_spawns (list[pygame.Vector2]): A list of positions for the
                enemy spawns.
            camera (Camera): The camera for the game.
            player (Player): The player entity.
            enemy1 (Enemy): The first enemy entity.
            enemys (Groups[Enemy]): A group containing the enemy entities.
            weapon_loader (WeaponLoader): The weapon loader for the game.
            player_start_weapon (Weapon): The starting weapon for the player.
        """
        self.enemy_spawns: list[pygame.Vector2] = [pygame.Vector2(100, 100), pygame.Vector2(1550, 100), pygame.Vector2(3100, 100),
                                                   pygame.Vector2(100, 1550), pygame.Vector2(3100, 1550),
                                                   pygame.Vector2(100, 3100), pygame.Vector2(1550, 3150), pygame.Vector2(3150, 3150)] # 3100x3100
                
        self.camera: Camera = Camera(main_screen=self.screen,
                        surface=self.entity_surface,
                        width=self.screen.width,
                        height=self.screen.height)
        
        self.player: Player = Player(image_path=changeable_values.DEFAULT_PATH + r"/assets/entities/player.png", 
                        POSITION=pygame.Vector2(100, 100), 
                        blocking=self.walls, 
                        screen=self.entity_surface,
                        camera=self.camera,
                        show_hitbox=[False, (0, 0, 255, 128), 3], 
                        player_scale=(100, 70),
                        health=1)
        
        self.player.drop_weapon(self.player.POSITION)
        
        self.enemy1: Enemy = Enemy(image_path=changeable_values.DEFAULT_PATH + r"/assets/entities/gegner.png",
                        POSITION=pygame.Vector2(600, 600),
                        blocking=self.walls,
                        screen=self.entity_surface,
                        main_target=self.player,
                        show_hitbox=[False, (0, 0, 255, 128), 3],
                        movement_speed=0.5,
                        enemy_scale=(100, 60))
        
        self.enemys: Groups[Enemy] = self.enemy1.clear_cls()

        self.weapon_loader = WeaponLoader(self.entity_surface, self.walls, [self.player])
        self.player_start_weapon = self.weapon_loader.Glock()
        self.player_start_weapon.clear_cls()
        self.player_start_weapon.targets = self.enemys
        self.player_start_weapon.sticking_to = self.player
        self.weapons = self.player_start_weapon.All()

    @staticmethod
    def draw_health_bar(screen: pygame.Surface,
                        health: int,
                        max_health: int = 100,
                        width: int = 200,
                        height: int = 25,
                        padding: int = 10):
        """
        Draws a health bar on the given screen.

        This method draws a health bar that visually represents the current health
        relative to the maximum health. The bar consists of a red background with
        a green overlay indicating the proportion of health remaining. It also
        includes a text display of the current health over the maximum health.

        Args:
            screen (pygame.Surface): The surface on which to draw the health bar.
            health (int): The current health value.
            max_health (int, optional): The maximum health value. Defaults to 100.
            width (int, optional): The width of the health bar. Defaults to 200.
            height (int, optional): The height of the health bar. Defaults to 25.
            padding (int, optional): The padding from the bottom and left edges of
                the screen. Defaults to 10.
        """
        health = max(0, min(health, max_health))
        screen_height = screen.height
        x = padding
        y = screen_height - height - padding
        pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
        green_width = int(width * (health / max_health))
        pygame.draw.rect(screen, (0, 255, 0), (x, y, green_width, height))
        font = pygame.font.SysFont(None, 36, bold=True)
        text = font.render(f"{health} / {max_health}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text, text_rect)
        
    def update(self):
        """
        Updates the state of the entities in the level.

        This method updates the player, all enemies, and all bullets in the level. It
        also checks if the current wave of enemies has been cleared and if so, spawns a
        new wave of enemies. Finally, it increments the player's score if the number of
        alive enemies has decreased.

        Returns:
            None
        """
        self.update_delta_times()
        self.player.update()
        self.enemys.update()
        self.player_start_weapon.All().update()
        self.check_path_ready()
        if not self.enemys:
            self.next_wave()

        if self.alive_enemies > len(self.enemys):
            self.alive_enemies -= 1
            self.kills += 1

    def update_delta_times(self):
        """
        Updates the delta time for all entities in the level.

        This method gets the current frame rate from the clock object and calculates
        the delta time from it. It then iterates over all entities in the level and
        updates their delta time.

        Returns:
            None
        """
        self.clock.tick(0)
        self.delta_time = 600 / self.clock.get_fps() if self.clock.get_fps() > 0 else 1
        for entity in self.player.All_Entities():
            entity.update_all_delta_times(self.delta_time)

    def event(self):
        """
        Handles game events for the endless mode.

        This method processes and handles various pygame events such as quitting 
        the game, key presses, and mouse button presses. It allows the player to 
        pick up, drop, and shoot weapons based on the input controls. It also 
        handles camera movement, either tracking the player or looking around 
        based on mouse position.

        Attributes:
            endless_an (bool): A flag to indicate whether the endless mode is active.
        
        Controls:
            PICK_UP_WEAPON: Allows the player to pick up a weapon.
            DROP_WEAPON_KEYS: Allows the player to drop a weapon.
            SHOOT_KEYS: Allows the player to shoot.
            CAMERA_LOOK_AROUND: Allows the camera to look around.
        
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or pygame.MOUSEBUTTONDOWN:
                if check_input(controlls.PICK_UP_WEAPON, event):
                    self.player.pickup_weapon(self.player_start_weapon.All(), self.enemys)
                if check_input(controlls.DROP_WEAPON_KEYS, event):
                    self.player.drop_weapon(self.camera.get_mouse_pos())
                if check_input(controlls.SHOOT_KEYS, event):
                    if self.player.gun:
                        mouse_pos = self.camera.get_mouse_pos()
                        self.player.gun.shoot(mouse_pos.x, mouse_pos.y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.endless_an = False
        if check_input(controlls.CAMERA_LOOK_AROUND):
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            self.camera.look_around(mouse_pos, self.player)
        else:
            self.camera.track(self.player, 0.7, 100)

    def draw(self):
        """
        Renders the game screen, displaying the map, entities, and various game stats.

        This method blits the map and entity surfaces onto the main screen using the current camera view.
        It also displays the player's time alive, current wave, difficulty level, and kill count.
        Additionally, it draws the player's health bar at the top of the screen.

        Args:
            None

        Returns:
            None
        """
        self.map.screen.set_clip(self.camera.rect)
        self.screen.blit(self.map.screen, (0, 0), self.camera.rect)
        self.screen.blit(self.entity_surface, (0, 0), self.camera.rect)
        alive_time_seconds = (pygame.time.get_ticks() - self.start_time) // 1000
        alive_time_minutes = alive_time_seconds // 60
        alive_time_seconds %= 60
        draw_text(f"Time Alive: {alive_time_minutes if alive_time_minutes > 9 else '0' + str(alive_time_minutes)}:{alive_time_seconds if alive_time_seconds > 9 else '0' + str(alive_time_seconds)}", self.font, self.screen, pos_right=(self.screen.width - 20, 20))
        draw_text(f"Wave: {self.wave}", self.font, self.screen, (20, 20))
        draw_text(f"Difficulty: {self.current_difficulty}", self.font, self.screen, (20, 60))
        draw_text(f"Kills: {self.kills}", self.font, self.screen, (20, 100))
        self.draw_health_bar(screen=self.screen,
                              health=self.player.health,
                              max_health=self.difficulty[self.current_difficulty][1],
                              width=300,
                              height=40)
        pygame.display.flip()

    def next_wave(self):
        """
        Starts the next wave of enemies.

        This method increments the current wave number and increases the player's health by a certain amount.
        It then spawns a certain number of enemies at random locations on the map, with a random weapon. The
        enemies are added to the `enemys` list and their `gun` attribute is set. The `alive_enemies` attribute is
        updated to reflect the number of alive enemies.

        Finally, the method calculates the path for each enemy to the player and updates the `wave_futures`
        list with the future objects returned by the executor. The `new_path` method is called to start the
        pathfinding process.

        Args:
            None

        Returns:
            None
        """
        self.wave += 1
        self.kills += 1
        self.player.health += self.difficulty[self.current_difficulty][3] if self.player.health + self.difficulty[self.current_difficulty][3] < self.difficulty[self.current_difficulty][1] else 0
        spawnable_locations = [location for location in self.enemy_spawns if not self.camera.rect.collidepoint(location)]
        weapons = [self.weapon_loader.Glock, self.weapon_loader.Shotgun, self.weapon_loader.Rocket_Launcher]

        for _ in range(self.wave):
            if spawnable_locations:
                current_location = random.choice(spawnable_locations)
                current_enemy = Enemy(image_path=changeable_values.DEFAULT_PATH + r"/assets/entities/gegner.png",
                        POSITION=current_location,
                        blocking=self.walls,
                        screen=self.entity_surface,
                        main_target=self.player,
                        show_hitbox=[False, (0, 0, 255, 128), 3],
                        movement_speed=self.difficulty[self.current_difficulty][0],
                        health=self.difficulty[self.current_difficulty][2],
                        enemy_scale=(100, 60))
                
                self.enemys.add(current_enemy)

                weapon = random.choice(weapons)()
                weapon.update_all_positions(current_enemy.POSITION)
                current_enemy.pickup_weapon([weapon], [self.player])

        self.alive_enemies = len(self.enemys)

        self.wave_futures = []
        for enemy in self.enemys:
            args = (enemy.POSITION, self.player.rect.copy(), self.walls, 32, (51, 31), 4000)
            future = self.executor.submit(compute_path, args)
            self.wave_futures.append((future, enemy))
        self.new_path()
    
    def new_path(self):
        """
        Starts a new path calculation for all enemies.

        This method submits a path calculation for each enemy in the `enemys` list to the executor.
        The arguments for the path calculation are the enemy's position, the player's position, the
        blocking tiles, the tile size, the algorithm parameters and the maximum allowed time for
        the path calculation. The futures are stored in the `wave_futures` list.
        """
        for enemy in self.enemys:
            args = (enemy.POSITION, self.player.rect.copy(), self.walls, 32, (51, 31), 4000)
            future = self.executor.submit(compute_path, args)
            self.wave_futures.append((future, enemy))
    
    def check_path_ready(self):
        """
        Checks if the pathfinding computations for enemies are complete.

        This method iterates over the list of wave futures to check if any futures have completed.
        If a future is done, it retrieves the computed path and updates the enemy's path and
        last seen position. Completed futures are removed from the wave futures list. If an
        exception occurs during the path retrieval, an error message is printed.

        Args:
            None

        Returns:
            None
        """
        for future, enemy in self.wave_futures[:]:
            if future.done():
                try:
                    enemy.path = future.result()
                    enemy.last_seen = self.player.rect.copy()
                    self.wave_futures.remove((future, enemy))
                except Exception as e:
                    print(f"Pathfinding failed: {e}")

    def cleanup(self):
        self.entity_surface.fill((0, 0, 0, 0))

    def run(self):
        """
        Starts the endless mode game loop.

        This method is the main loop for the endless mode. It first checks if the user has selected a difficulty
        level. If not, it shows the difficulty chooser menu. If the user has chosen a difficulty, it sets the
        player's health to the maximum for that difficulty and resets the enemies to the starting positions.
        It then starts the main game loop, where it handles events, updates the game state, draws the screen,
        and limits the frame rate to 60 FPS. If the player's health reaches 0, the game loop ends and the
        `completed` attribute is set to True.

        Args:
            None

        Returns:
            None
        """
        if not hasattr(self, "current_difficulty"):
            self.current_difficulty = Difficulty_Chooser(self.screen).run()
        if self.current_difficulty:
            self.player.health = self.difficulty[self.current_difficulty][1]
            self.enemys = self.enemy1.clear_cls()
            self.player_start_weapon.targets = self.enemys
            pygame.display.set_caption("Hotline Pork - Endless Mode")

            if not hasattr(self, "first_call_start_time"):
                self.start_time: int = pygame.time.get_ticks()
                self.first_call_start_time = None

        for weapon in self.weapons:
            weapon.update_sound_volume()
            
        self.endless_an = True
        while self.endless_an:
            if not self.current_difficulty:
                break
            if self.player.health <= 0:
                self.endless_an = False
                self.completed = True
            self.event()
            self.update()
            self.draw()
            self.cleanup()
            self.clock.tick(60)
        if self.completed:
            show_survival_stats(self.wave, (pygame.time.get_ticks() - self.start_time) / 1000)
            if self.stat_saver.load() == {}:
                self.stat_saver.set_value({"HIGHEST WAVE": self.wave,
                                           "TOTAL WAVES": self.wave,
                                          "LONGEST SURVIVED": (pygame.time.get_ticks() - self.start_time) / 1000,
                                          "TOTAL PLAYTIME": (pygame.time.get_ticks() - self.start_time) / 1000,
                                          "MOST KILLS": self.kills,
                                          "TOTAL KILLS": self.kills})
                self.stat_saver.save()
            else:
                self.stat_saver.load()
                self.stat_saver.set_value({"HIGHEST WAVE": max(self.wave, self.stat_saver.data["HIGHEST WAVE"]),
                                          "TOTAL WAVES": self.wave + self.stat_saver.data["TOTAL WAVES"],
                                          "LONGEST SURVIVED": max((pygame.time.get_ticks() - self.start_time) / 1000, self.stat_saver.data["LONGEST SURVIVED"]),
                                          "TOTAL PLAYTIME": (pygame.time.get_ticks() - self.start_time) / 1000 + self.stat_saver.data["TOTAL PLAYTIME"],
                                          "MOST KILLS": max(self.kills, self.stat_saver.data["MOST KILLS"]),
                                          "TOTAL KILLS": self.kills + self.stat_saver.data["TOTAL KILLS"]})
                self.stat_saver.save()
            