import pygame
import sys
from modules.Entitys.imports import Player, Enemy, Weapon
from modules.General.globals import *
from modules.General.functions import check_input, Camera, DialogBox
from modules.General.types import Groups, InputType
from modules.General import controlls
from modules.Map.tiles import TileMap
from modules.General.premade_weapons import WeaponLoader


def dict_to_text(input_pair_list: list[tuple[InputType | None, int | None]]) -> str:
    """
    Converts a list of (InputType, int) pairs to a human-readable string
    suitable for display in a game UI. The input pairs are expected to represent
    possible input combinations for a single action. Examples of the output
    include "W", "MB1", "SPACE or MB2", etc.

    Args:
        input_pair_list: A list of input pairs, where each pair is a tuple of
            an InputType and an int. The int should be a valid argument to
            pygame.key.name() or a valid mouse button number.

    Returns:
        A string representation of the input pair list, or "-" if an error occurs.
    """
    try:
        def format_input(input_type, keycode):
            if input_type is None or keycode is None:
                return None
            if input_type == InputType.MOUSE:
                return f"MB{keycode}"
            return pygame.key.name(keycode).upper()

        formatted = [fmt for fmt in (format_input(it, kc) for it, kc in input_pair_list if it and kc) if fmt]

        if not formatted:
            return ""
        elif len(formatted) == 1:
            return formatted[0]
        else:
            return f"{formatted[0]} or {formatted[1]}"
    except Exception as e:
        return "-"


def player_border_check(player: Player,
                        screen_size: tuple):
    """
    Ensures the player's position is within the screen boundaries by adjusting 
    the player's rectangle if it goes out of bounds.

    Args:
        player (Player): The player object whose position is being checked.
        screen_size (tuple): A tuple representing the width and height of the screen.

    Functionality:
        If the player's rectangle goes beyond the screen boundaries, 
        this function adjusts the rectangle's position to keep it within 
        the screen limits and updates the player's position accordingly.
    """

    temp_rect = player.rect.copy()
    if player.rect.left < 0:
        temp_rect.left = 0
    if screen_size[0] < player.rect.right:
        temp_rect.right = screen_size[0]
    if player.rect.top < 0:
        temp_rect.top = 0
    if screen_size[1] < player.rect.bottom:
        temp_rect.bottom = screen_size[1]
    player.update_all_positions(temp_rect.center)


class Task:
    """
    Base class for tasks in the game.
    """
    def __init__(self):
        self.completed = False
        self.called = False
        self.completed2 = False

    def update(self):
        ...

    def call(self):
        self.called = True
        self.update()

class WASD_Pressed(Task):
    def __init__(self):
        super().__init__()
        self.forward = False
        self.left = False
        self.back = False
        self.right = False

    def update(self):
        if check_input(controlls.ALL_KEYS["UP"]):
            self.forward = True
        if check_input(controlls.ALL_KEYS["LEFT"]):
            self.left = True
        if check_input(controlls.ALL_KEYS["DOWN"]):
            self.back = True
        if check_input(controlls.ALL_KEYS["RIGHT"]):
            self.right = True
        if self.forward and self.left and self.back and self.right:
            self.completed = self.completed2 = True
    

class Kill_All_Enemies(Task):
    def __init__(self,
                 enemys: list[Enemy]):
        super().__init__()
        self.enemys = enemys

    def update(self):
        for enemy in self.enemys:
            self.completed = True if not enemy.alive() else False
            self.completed2 = self.completed
        if len(self.enemys) == 0:
            self.completed = True
            self.completed2 = self.completed


class Search_Enemies(Task):
    def __init__(self,
                 enemys: list[Enemy],
                 camera: Camera):
        super().__init__()
        self.enemys = enemys
        self.camera = camera

    def update(self):
        for enemy in self.enemys:
            if self.camera.rect.contains(enemy.rect):
                self.completed = True
                self.completed2 = self.completed


class Pickup_Weapon(Task):
    def __init__(self,
                 player: Player):
        self.player = player
        super().__init__()

    def update(self):
        if self.player.gun:
            self.completed = True
            self.completed2 = self.completed


class Dialog_Manager:
    """
    Manages the display and interaction with dialog boxes in a game.
    
    Attributes:
        dialog_box (DialogBox): The dialog box object used to display and handle dialog text.
        dialog_data (list): A list of tuples containing dialog text and its associated task.
        current_index (int): The index of the current dialog in the dialog_data list.

    Methods:
        show_next_dialog(): Displays the next dialog in the dialog_data list.
        event(event): Handles events related to the dialog box.
        draw(): Draws the dialog box if it is active.
        update(): Updates the dialog box if it is active.
    """
    def __init__(self,
                 surface: pygame.Surface,
                 font: pygame.font.Font,
                 text: dict[str, tuple[callable, bool]], # dict[text: (task, skipable)]
                 sound: pygame.mixer.Sound = None):
        """
        Initializes the Dialog_Manager object.

        Args:
            surface (pygame.Surface): The surface to draw the dialog box on.
            font (pygame.font.Font): The font to use for the text in the dialog box.
            text (dict[str, tuple[callable, bool]]): A dictionary where each key is a 
                dialog text string, and each value is a tuple with a task callable 
                and a boolean indicating if the dialog is skippable.
            sound (pygame.mixer.Sound, optional): The sound to play when the dialog 
                box is shown. Defaults to None.

        Attributes:
            dialog_box (DialogBox): The dialog box object used to display and handle 
                dialog text.
            dialog_data (list): A list of tuples containing dialog text and its 
                associated task.
            current_index (int): The index of the current dialog in the dialog_data list.
        """
        self.dialog_box = DialogBox(surface=surface,
                                    font=font,
                                    sound=sound)
        self.dialog_data = list(text.items())
        self.current_index = -1
        self.show_next_dialog()

    def show_next_dialog(self):
        self.current_index += 1
        if self.current_index < len(self.dialog_data):
            dialog_text, (task, skipable) = self.dialog_data[self.current_index]
            self.dialog_box.show(dialog_text, skipable=skipable, on_finish=task)

    def event(self,
              event: pygame.event.Event):
        if self.dialog_box.active:
            self.dialog_box.handle_event(event)

    def draw(self):
        if self.dialog_box.active:
            self.dialog_box.draw()

    def update(self):
        if self.dialog_box.active:
            self.dialog_box.update()  


class Tutorial():
    """
    The main game class for the tutorial level.
    
    Attributes:
        screen (pygame.Surface): The main game screen.
        map (TileMap): The tile map object used for rendering the game world.
        surface (pygame.Surface): A surface used for rendering the game world.
        allow_movement (bool): A flag indicating whether player movement is allowed.
        blocking (list): A list of blocking objects in the game.
        camera (Camera): The camera object used for scrolling the game world.
        player (Player): The player object representing the main character.
        enemy1 (Enemy): The first enemy object in the game.
        enemy2 (Enemy): The second enemy object in the game.
    
    Methods:
        __init__(): Initializes the tutorial level.
        event(event): Handles events related to the tutorial level.
        update(): Updates the tutorial level.
        draw(): Draws the tutorial level."""
    def __init__(self,
                 default_path: str = changeable_values.DEFAULT_PATH):
        self.screen = changeable_values.SCREEN
        self.map = TileMap(filename=default_path + r"/assets/maps/tutorial/map_tutorial.csv",
                      spritesheet=default_path + r"/assets/maps/tutorial/Floors.png",
                      final_tile_size=96)
        self.surface = self.map.screen.copy()
        self.allow_movement = False

        self.blocking = self.map.walls

        self.camera: Camera = Camera(main_screen=self.screen,
                    surface=self.surface,
                    width=self.screen.width,
                    height=self.screen.height)

        self.player: Player = Player(image_path=default_path + r"/assets/entities/player.png", 
                                POSITION=pygame.Vector2(200, 200), 
                                blocking=self.blocking, 
                                screen=self.surface,
                                camera=self.camera,
                                speed=10,
                                show_hitbox=[False, (0, 0, 255), 3], 
                                player_scale=(100, 70))
        
        self.enemy1: Enemy = Enemy(image_path=default_path + r"/assets/entities/gegner.png",
                            POSITION=pygame.Vector2(1400, 1000),
                            blocking=self.blocking,
                            screen=self.surface,
                            main_target=self.player,
                            show_hitbox=[False, (0, 0, 255, 128), 3],
                            movement_speed=0,
                            enemy_scale=(100, 60))
        
        self.enemy2: Enemy = Enemy(image_path=default_path + r"/assets/entities/gegner.png",
                            POSITION=pygame.Vector2(800, 1000),
                            blocking=self.blocking,
                            screen=self.surface,
                            main_target=self.player,
                            show_hitbox=[False, (0, 0, 255, 128), 3],
                            movement_speed=0,
                            enemy_scale=(100, 60))
        
        self.enemys = Groups(self.enemy1, self.enemy2)
        
        self.weapon_loader = WeaponLoader(self.surface, self.blocking, self.enemys)
        self.rocket_launcher = self.weapon_loader.Rocket_Launcher()
        self.glock = self.weapon_loader.Glock()
        self.shotgun = self.weapon_loader.Shotgun()
        self.weapons = Groups(self.rocket_launcher, self.glock, self.shotgun)
        self.glock.update_all_positions(pygame.Vector2(700, 550))
        self.shotgun.update_all_positions(pygame.Vector2(800, 575))
        self.rocket_launcher.update_all_positions(pygame.Vector2(900, 575))
        
        self.completed = False
        self.tutorial_an = True
        self.last_active_dialog = pygame.time.get_ticks()
        self.clock = pygame.time.Clock()
        self.wasd = WASD_Pressed()
        self.search_weapon = Pickup_Weapon(player=self.player)
        self.search_enemies = Search_Enemies(enemys=self.enemys, camera=self.camera)
        self.kill_enemies = Kill_All_Enemies(enemys=self.enemys)

        _ = pygame.mixer.Sound(changeable_values.DEFAULT_PATH + r"/assets/sounds/keyboard_press.wav")
        _.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)
        self.text = {"JOHN...": (None, False),
        f"Use {dict_to_text(controlls.ALL_KEYS["UP"])}, {dict_to_text(controlls.ALL_KEYS["LEFT"])}, {dict_to_text(controlls.ALL_KEYS["DOWN"])}, {dict_to_text(controlls.ALL_KEYS["RIGHT"])} to move John...":(self.wasd.call, True),
        f"Great, now pick up the weapon John, press {dict_to_text(controlls.PICK_UP_WEAPON)} and not {dict_to_text(controlls.DROP_WEAPON_KEYS)} or you will drop it": (self.search_weapon.call, True),
        f"Locate the enemies John, use {dict_to_text(controlls.CAMERA_LOOK_AROUND)} to look around...": (self.search_enemies.call, True),
        f"Do you know how to use a trigger? Use {dict_to_text(controlls.SHOOT_KEYS)} to shoot those Tim Cheeses John. Show them no mercy.": (self.kill_enemies.call, True)}
        self.dialog_manager = Dialog_Manager(surface=self.screen,
                                        font=pygame.font.SysFont("Arial", 24),
                                        text=self.text,
                                        sound=_)

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.tutorial_an = False

            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if self.search_weapon.called:
                    if check_input(controlls.PICK_UP_WEAPON, event):
                            self.player.pickup_weapon(self.weapons, self.enemys)

                    if check_input(controlls.DROP_WEAPON_KEYS, event):
                        self.player.drop_weapon(self.camera.get_mouse_pos())

                if check_input(controlls.SHOOT_KEYS, event):
                    if self.player.gun:
                        mouse_pos = self.camera.get_mouse_pos()
                        self.player.gun.shoot(mouse_pos.x, mouse_pos.y)

    def update(self):
        turorial_tasks: list[tuple[Task, bool]] = [(self.wasd, True), (self.search_weapon, True), (self.search_enemies, False), (self.kill_enemies, True)]
        for task, allow_movement in turorial_tasks:
            if task.called:
                if not task.completed:
                    task.update()
                    self.allow_movement = False if (not allow_movement or pygame.time.get_ticks() - self.last_active_dialog < 500) else True

        if self.player.gun:
            self.player.gun.rotate_angle = self.player.angle
        if self.allow_movement:
            self.player.movement()
            player_border_check(self.player, self.surface.get_size())

        if check_input(controlls.CAMERA_LOOK_AROUND):
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            self.camera.look_around(mouse_pos, self.player)

        else:
            self.camera.track(self.player, 0.7, 100)

        if not self.dialog_manager.dialog_box.on_finish and self.dialog_manager.dialog_box.finished:
            self.dialog_manager.show_next_dialog()

        if self.wasd.completed2:
            self.wasd.completed2 = False
            self.dialog_manager.show_next_dialog()

        if self.search_weapon.completed2:
            self.search_weapon.completed2 = False
            self.dialog_manager.show_next_dialog()

        if self.search_enemies.completed2:
            self.search_enemies.completed2 = False
            self.dialog_manager.show_next_dialog()
        
        if self.kill_enemies.completed2:
            self.kill_enemies.completed2 = False
            self.completed = True
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont("Arial", 60, bold=True)
            text = font.render("TUTORIAL COMPLETED!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)
            self.tutorial_an = False

    def draw(self):
        self.player.draw()
        self.weapons.update()
        self.enemys.update()

    def dialog_tasks(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            self.dialog_manager.event(event)
        self.dialog_manager.update()
        self.dialog_manager.draw()

    def run(self):
        self.tutorial_an = True
        pygame.display.set_caption("HOTLINE PORK - TUTORIAL")

        self.text = {"JOHN...": (None, False),
        f"Use {dict_to_text(controlls.ALL_KEYS["UP"])}, {dict_to_text(controlls.ALL_KEYS["LEFT"])}, {dict_to_text(controlls.ALL_KEYS["DOWN"])}, {dict_to_text(controlls.ALL_KEYS["RIGHT"])} to move John...":(self.wasd.call, True),
        f"Great, now pick up the weapon John, press {dict_to_text(controlls.PICK_UP_WEAPON)} and not {dict_to_text(controlls.DROP_WEAPON_KEYS)} or you will drop it": (self.search_weapon.call, True),
        f"Locate the enemies John, use {dict_to_text(controlls.CAMERA_LOOK_AROUND)} to look around...": (self.search_enemies.call, True),
        f"Do you know how to use a trigger? Use {dict_to_text(controlls.SHOOT_KEYS)} to shoot those Tim Cheeses John. Show them no mercy.": (self.kill_enemies.call, True)}
        self.dialog_manager.dialog_data = list(self.text.items())
        if self.dialog_manager.dialog_box.sound:
            self.dialog_manager.dialog_box.sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.DIALOGUE_VOLUME)

        for weapon in self.weapons:
            weapon.update_sound_volume()

        while self.tutorial_an:
            self.surface.blit(self.map.screen)
            self.draw()
            if self.dialog_manager.dialog_box.active:
                self.screen.blit(self.surface, (0, 0), self.camera.rect)
                self.dialog_tasks()
                self.clock.tick(10)
                pygame.display.flip()
                self.last_active_dialog = pygame.time.get_ticks()
                continue

            delta_time = 60 / (self.clock.get_fps() if self.clock.get_fps() > 0 else 60)
            self.player.delta_time = delta_time
            self.weapons.update_delta_time(delta_time)

            self.event()
            self.update()

            self.clock.tick(0)
            self.screen.blit(self.surface, (0, 0), self.camera.rect)
            pygame.display.flip()
        pygame.display.set_caption("HOTLINE PORK")
        if self.completed:
            ACHIEVEMENTS.all_achievements["Tim Cheese Will Remember That"] = ("Finish the Tutorial", True)
