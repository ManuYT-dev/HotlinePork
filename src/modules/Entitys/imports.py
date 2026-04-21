import pygame
import numpy as np
from pygame.typing import Point
import time
from modules.General.globals import changeable_values, SCREEN_SIZE
from modules.General.functions import circle_collision_check, check_input, Camera
from modules.General import controlls
from modules.General.types import Entity, Groups
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import random

class Player(Entity):
    def __init__(self,
                  image_path: str,
                  POSITION: Point,
                  blocking: pygame.FRect | list[pygame.FRect],
                  screen: pygame.surface.Surface,
                  camera: Camera,
                  health: float = 10,
                  delta_time = 1,
                  speed: int = changeable_values.PLAYER_SPEED,
                  show_hitbox: list[bool, (int, int, int), int] = [False, (0, 0, 0), 2],
                  player_scale: tuple[int, int] | list[int, int] = (100, 100),
                  auto_inits: bool = True) -> None:
        """
        Initializes a player entity with the specified parameters.

        Args:
            image_path (str): The file path to the image to be loaded.
            POSITION (pygame.Vector2): The position where the image will be drawn.
            health (float): The initial health of the player.
            show_hitbox (bool, optional): Whether to display the hitbox of the image. Defaults to False.
            player_scale (tuple[int, int] | list[int, int], optional): The size of the image. Defaults to (100, 100).

        Raises:
            TypeError: If `image_path` is not a string.
            TypeError: If `POSITION` is not a `pygame.Vector2` instance.
            TypeError: If `show_hitbox` is not a boolean.
            TypeError: If `player_scale` is not a tuple or list of two integers.

        Attributes:
            show_hitbox (bool): Indicates whether the hitbox is displayed.
            image (pygame.surface.Surface): The loaded and scaled image surface.
            rect (pygame.FRect): The rectangle representing the image's dimensions and position.
        """
        super().__init__()
        self.gun: Weapon
        self.camera = camera
        self.x: int = POSITION.x if isinstance(POSITION, pygame.Vector2) else POSITION[0]
        self.y: int = POSITION.y if isinstance(POSITION, pygame.Vector2) else POSITION[1]
        self.POSITION: pygame.Vector2 = POSITION if isinstance(POSITION, pygame.Vector2) else pygame.Vector2(POSITION)
        self.angle: float = 0
        self.blocking: pygame.FRect | list[pygame.FRect] = blocking
        self.health: int = health
        self.show_hitbox: list[bool, (int, int, int), int] = show_hitbox
        self.player_scale: tuple[int, int] | list[int, int] = player_scale
        self.screen: pygame.Surface = screen
        self.movement_speed: int = speed
        self.delta_time: float = delta_time
        if auto_inits:
            self.initiate_drawing(image_path)

    def initiate_drawing(self,
                        image: str,
                        show_error_messages: bool = True) -> None:
        """
        Initializes the drawing of the player with specified parameters.
        Args:
            image_path (str): The file path to the image to be loaded.
            POSITION (pygame.Vector2): The position where the image will be drawn.
            show_hitbox (bool, optional): Whether to display the hitbox of the image. Defaults to False.
        Raises:
            TypeError: If `image_path` is not a string.
            TypeError: If `POSITION` is not a `pygame.Vector2` instance.
            TypeError: If `show_hitbox` is not a boolean.
        Attributes:
            show_hitbox (bool): Indicates whether the hitbox is displayed.
            image (pygame.surface.Surface): The loaded and scaled image surface.
            rect (pygame.FRect): The rectangle representing the image's dimensions and position.
        """
        if show_error_messages:
            if not isinstance(self.screen, pygame.Surface): raise TypeError("screen must be a pygame.Surface")
            if not isinstance(image, str): raise TypeError("image_path must be a str or pygame.Surface")
            if not isinstance(self.POSITION, pygame.Vector2): raise TypeError("POSITION must be a pygame.Vector2")
            if not isinstance(self.show_hitbox, list): raise TypeError("show_hitbox must be a tuple[bool, (int, int, int), int]")
            if not isinstance(self.show_hitbox[0], bool): raise TypeError("show_hitbox[0] must be a bool")
            if not isinstance(self.show_hitbox[1], tuple): raise TypeError("show_hitbox[1] must be a tuple of (int, int, int)")
            if not isinstance(self.show_hitbox[2], int): raise TypeError("show_hitbox[2] must be an int")
        

        self.image: pygame.surface.Surface = pygame.image.load(image).convert_alpha()
        self.image: pygame.surface.Surface  = pygame.transform.scale(self.image, self.player_scale) 
        self.rect: pygame.FRect = pygame.FRect(self.image.get_rect())
        self.default_rect = self.rect.copy()
        self.default_rect.topleft = (0, 0)
        self.mask_player: pygame.Mask = pygame.mask.from_surface(self.image)
        self.rect.center = self.POSITION
    
    def update_all_positions(self,
                             POSITION: Point,
                             show_error_messages: bool = True) -> None:
        if show_error_messages:
            if not isinstance(POSITION, (pygame.Vector2 | tuple | list)): raise TypeError("POSITION must be a pygame.Vector2 or tuple[int, int] or list[int, int]")
        
        self.x, self.y = self.rect.center = self.POSITION = pygame.Vector2(POSITION)

    def movement(self) -> None:
        """
        Handles the movement of an object based on keyboard input.
        This method checks for specific key presses to determine the direction of movement
        (up, down, left, right) and adjusts the object's position accordingly. Diagonal movement
        is normalized using a multiplier to ensure consistent speed.
        Attributes:
            KEYS (pygame.key.ScancodeWrapper): A mapping of all keyboard keys and their states.
            check_keys (function): A lambda function to check if any of the specified keys are pressed.
            possible_keys (dict): A dictionary mapping movement directions to tuples of possible key bindings.
            diagonal_multiplier (float): A multiplier to normalize diagonal movement speed.
            x (float): The horizontal movement offset.
            y (float): The vertical movement offset.
        Movement Logic:
            - If a key corresponding to "UP" is pressed, the object moves upward.
            - If a key corresponding to "DOWN" is pressed, the object moves downward.
            - If a key corresponding to "LEFT" is pressed, the object moves leftward.
            - If a key corresponding to "RIGHT" is pressed, the object moves rightward.
            - If both horizontal and vertical keys are pressed simultaneously, the movement
              is adjusted using the diagonal multiplier.
        Updates:
            - The object's `rect` position is updated based on the calculated offsets.
            - The object's `POSITION` and `x`, `y` attributes are updated to reflect the new center position.
        """        
        diagonal_multiplier: float = 0.70710678118 # Formel = wurzel((speed ** 2) / 2)
        x = y = 0

        coordinates_before_movement: pygame.Vector2 = self.POSITION.copy()
        if check_input(controlls.ALL_KEYS["UP"]): y -= self.movement_speed * self.delta_time
        if check_input(controlls.ALL_KEYS["DOWN"]): y += self.movement_speed * self.delta_time
        if check_input(controlls.ALL_KEYS["LEFT"]): x -= self.movement_speed * self.delta_time
        if check_input(controlls.ALL_KEYS["RIGHT"]): x += self.movement_speed * self.delta_time

        if x != 0 and y != 0:
            x *= diagonal_multiplier
            y *= diagonal_multiplier
        
        self.rect.x += x
        self.x = self.POSITION.x = self.rect.centerx
       
        if self.hitbox_check(self.blocking):
            self.update_all_positions((coordinates_before_movement[0], self.y))

        self.rect.y += y
        self.POSITION.y = self.y = self.rect.centery

        if self.hitbox_check(self.blocking):
            self.update_all_positions((self.x, coordinates_before_movement[1]))


    def draw(self,
             show_error_message: bool = True) -> None:
        """
        Draws the player's image on the given screen surface.

        This method blits the player's image onto the provided screen surface
        at the player's current position. If the player's hitbox is set to be
        shown, a red rectangle will be drawn around the image to indicate the
        hitbox.

        Args:
            screen (pygame.surface.Surface): The surface on which the player's
            image will be drawn.

        Raises:
            TypeError: If `screen` is not a `pygame.surface.Surface` instance.
        """
        if show_error_message:
            if not isinstance(self.image, pygame.Surface): raise TypeError("self.image must be a pygame.surface.Surface")
            if not isinstance(self.rect, (pygame.FRect)): raise TypeError("self.rect must be a pygame.FRect")
        mouse_pos = self.camera.get_mouse_pos()
        new_angle = (mouse_pos - self.POSITION).angle_to(pygame.Vector2(1, 0)) - 90

        if self.angle != new_angle:
            self.angle = new_angle
            image = pygame.transform.rotate(self.image, self.angle)
            old_mask = self.mask_player.copy()
            old_rect = self.rect.copy()
            
            self.mask_player = pygame.mask.from_surface(image)
            rect = pygame.FRect(image.get_rect(center=self.rect.center))

            collision = False
            for wall in self.blocking:
                offset = (int(wall.x - rect.x), int(wall.y - rect.y))
                if self.mask_player.overlap(pygame.mask.Mask((int(wall.width), int(wall.height)), fill=True), offset):
                    collision = True
                    break

            if collision:
                self.mask_player = old_mask
                self.rect = old_rect
            else:
                self.last_image = image
                self.rect = rect
        self.screen.blit(self.last_image, self.rect)
        
        if self.show_hitbox[0]:
            has_transparency: bool = True if isinstance(self.show_hitbox[1], tuple) and len(self.show_hitbox[1]) == 4 else False
            if has_transparency:
                temp_surface: pygame.Surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(temp_surface, self.show_hitbox[1], self.rect, self.show_hitbox[2])
                self.screen.blit(temp_surface, self.rect.topleft)
            else:
                pygame.draw.rect(self.screen, self.show_hitbox[1], self.rect, self.show_hitbox[2])

    def update(self) -> None:
        """
        Updates the state of the object by performing necessary operations.
        
        This method is responsible for invoking the movement logic or any 
        other updates required for the object's state.
        """
        self.draw()
        self.movement()
        if self.gun:
            self.gun.rotate_angle = self.angle

    def LOS(self,
            target: pygame.sprite.Group | pygame.sprite.Sprite | list[pygame.sprite.Sprite],
            blocking: pygame.FRect | list[pygame.FRect],
            max_distance: int = 1000,
            steps: int = 5, 
            visuals_toggled: bool = False,
            show_error_messages: bool = True) -> dict[pygame.sprite.Sprite, bool]:
        """
        Performs a line-of-sight check between the player and the given target(s)
        within the specified maximum distance and with the given number of steps.

        Args:
            target (pygame.sprite.Group | pygame.sprite.Sprite | list[pygame.sprite.Sprite]):
                The target(s) to check for line-of-sight.
            blocking (pygame.FRect | list[pygame.FRect]):
                The blocking objects to check against.
            max_distance (int, optional): The maximum distance to check. Defaults to 1000.
            steps (int, optional): The number of steps to take when checking. Defaults to 5.
            screen (pygame.surface.Surface, optional): The screen to draw debugging circles on. Defaults to None.

        Returns:
            dict[pygame.sprite.Sprite, bool]: A dictionary containing the target(s) as keys and
            a boolean indicating whether the target is in line-of-sight as values.

        Raises:
            ValueError: If `max_distance` or `steps` are not positive integers.
        """
        if show_error_messages:
            if not isinstance(max_distance, int) or max_distance < 1:
                raise ValueError("max_distance must be a positive integer")
            if not isinstance(steps, int) or steps < 1:
                raise ValueError("steps must be a positive integer")
            if not isinstance(blocking, (pygame.FRect, list)):
                raise TypeError("blocking must be a pygame.FRect or a list of pygame.FRect")
            if not isinstance(target, (Groups, Entity, list)):
                raise TypeError("target must be a pygame.sprite.Group, a pygame.sprite.Sprite, or a list of pygame.sprite.Sprite")

        blocking_list: list[pygame.FRect] | pygame.sprite.Group = blocking if isinstance(blocking, (list, pygame.sprite.Group)) else [blocking]
        max_distance_sq: int = max_distance ** 2
        returning_dict: dict = {}

        def check_blocking(_pos: pygame.Vector2,
                           _blocking_list: list[pygame.FRect] = blocking_list) -> bool:
            """
            Checks if a given position is blocked by any of the blocking rectangles.

            Args:
                _pos (pygame.Vector2): The position to check.
                _blocking_list (list[pygame.FRect], optional): The list of blocking rectangles. Defaults to blocking_list.

            Returns:
                bool: True if the position is blocked, False otherwise.
            """
            x, y = int(_pos.x), int(_pos.y)
            for block in _blocking_list:
                if block.collidepoint(x, y):
                    return True
            return False

        def process_sprite(_sprite: Entity,
                           _starting_pos: pygame.Vector2,
                           _max_distance_sq: int = max_distance_sq,
                           _visuals_toggled: bool = visuals_toggled) -> bool:
            """
            Processes a single sprite to check if it is in line-of-sight of the player.

            Args:
                _sprite (Entity): The sprite to check.
                _starting_pos (pygame.Vector2): The starting position to check from.
                _max_distance_sq (int, optional): The maximum distance to check. Defaults to max_distance_sq.
                _visuals_toggled (bool, optional): Whether to draw debugging circles. Defaults to visuals_toggled.

            Returns:
                bool: True if the sprite is in line-of-sight, False otherwise.
            """
            sprite_pos: pygame.Vector2 = _sprite.POSITION
            if (sprite_pos - _starting_pos).length_squared() > _max_distance_sq:
                return False

            if self.rect.colliderect(_sprite.rect):
                return True

            direction = (sprite_pos - _starting_pos).normalize()
            steps_needed = int(_starting_pos.distance_to(sprite_pos) / steps) + 1

            for i in range(steps_needed):
                current_pos = _starting_pos + direction * (steps * i)
                
                if _visuals_toggled and i % 5 == 0:
                    pygame.draw.circle(self.screen, (255, 0, 0), (int(current_pos.x), int(current_pos.y)), 2)
                
                if check_blocking(current_pos):
                    return False
            return True

        if isinstance(target, pygame.sprite.Group):
            returning_dict.update({sprite: process_sprite(sprite, self.POSITION, max_distance_sq, visuals_toggled) for sprite in target})
        elif isinstance(target, pygame.sprite.Sprite):
            returning_dict[target] = process_sprite(target, self.POSITION, max_distance_sq, visuals_toggled)
        elif isinstance(target, list):
            returning_dict.update({sprite: process_sprite(sprite, self.POSITION, max_distance_sq, visuals_toggled) for sprite in target})

        return returning_dict
    
    def hitbox_check(self,
                     blocking: pygame.FRect | list[pygame.FRect]) -> bool: # TODO: Falls es lagt mask fixen da es viele Punkte checkt
        """
        Checks if the player's hitbox collides with any blocking rectangles.

        Args:
            blocking (pygame.FRect | list[pygame.FRect]):
                The blocking objects to check against.

        Returns:
            bool: True if the player's hitbox collides with any of the blocking rectangles, False otherwise.

        Raises:
            TypeError: If `blocking` is not a `pygame.FRect` or a list of `pygame.FRect` instances.
        """
        if not isinstance(blocking, (pygame.FRect, list)):
            raise TypeError("blocking must be a pygame.FRect or a list of pygame.FRect")
        
        def check_blocking(_blocking: pygame.FRect) -> bool:
            mask_blocking: pygame.Mask = pygame.mask.from_surface(pygame.Surface(_blocking.size))
            return bool(self.mask_player.overlap(mask_blocking, (_blocking.x - self.rect.x, _blocking.y - self.rect.y)))
        

        if isinstance(blocking, pygame.FRect):
            return check_blocking(blocking)
        
        else:
            for block in blocking:
                collision: bool = check_blocking(block)
                if collision:
                    return collision
            return False


class Enemy(Entity):
    def __init__(self,
                 image_path: str,
                 POSITION: pygame.Vector2,
                 blocking: pygame.FRect | list[pygame.FRect],
                 screen: pygame.surface.Surface,
                 main_target: Entity = None,
                 health: float = 10,
                 show_hitbox: list[bool, (int, int, int), int] = [False, (0, 0, 0), 2],
                 enemy_scale: tuple[int, int] | list[int, int] = (100, 100),
                 delta_time: float = 1,
                 movement_speed: float = 1,
                 auto_inits: bool = True) -> Entity:
        """
        Initializes an enemy entity with the specified parameters.

        Args:
            image_path (str): The file path to the image to be loaded.
            POSITION (pygame.Vector2): The position where the enemy will be drawn.
            blocking (pygame.FRect | list[pygame.FRect]): The blocking objects for collision detection.
            screen (pygame.surface.Surface): The surface on which the enemy will be drawn.
            main_target (Entity, optional): The main target for the enemy. Defaults to None.
            health (float, optional): The initial health of the enemy. Defaults to 100.
            show_hitbox (list[bool, (int, int, int), int], optional): Settings for displaying the hitbox. Defaults to [False, (0, 0, 0), 2].
            enemy_scale (tuple[int, int] | list[int, int], optional): The size of the enemy image. Defaults to (100, 100).
            movement_speed (float, optional): The movement speed of the enemy. Defaults to 1.
            auto_inits (bool, optional): Whether to automatically initialize drawing. Defaults to True.

        Raises:
            TypeError: If `image_path` is not a string.
            TypeError: If `POSITION` is not a `pygame.Vector2` instance.
            TypeError: If `blocking` is not a `pygame.FRect` or a list of `pygame.FRect`.
            TypeError: If `screen` is not a `pygame.Surface`.
            TypeError: If `show_hitbox` is not a list with the correct format.
            TypeError: If `enemy_scale` is not a tuple or list of two integers.
        """
        super().__init__()

        self.x: int = POSITION.x
        self.y: int = POSITION.y
        self.POSITION: pygame.Vector2 = POSITION

        self.gun: Weapon
        self.blocking: pygame.FRect | list[pygame.FRect] = blocking
        self.main_target: Entity = main_target
        
        self.screen: pygame.surface.Surface = screen
        self.show_hitbox: list[bool, (int, int, int), int] = show_hitbox
        self.enemy_scale: tuple[int, int] | list[int, int] = enemy_scale

        self.health: int = health
        self.delta_time: float = delta_time
        self.movement_speed: float = movement_speed
        self.a_star_grid_size: int = 32
        self.a_star_update_time: int = 2
        self.a_star_update_distance: float = 300
        if auto_inits:
            self.initiate_drawing(image_path)

    def initiate_drawing(self,
                         image_path: str,
                         show_error_messages: bool = True) -> None:
        """
        Initializes the drawing of the enemy with specified parameters.

        Args:
            image_path (str): The file path to the image to be loaded.
            show_error_messages (bool, optional): Whether to display error messages. Defaults to True.

        Raises:
            TypeError: If `image_path` is not a string.
            TypeError: If `show_error_messages` is not a boolean.
            TypeError: If `show_hitbox` is not a tuple of [bool, (int, int, int), int].
            TypeError: If `show_hitbox[0]` is not a boolean.
            TypeError: If `show_hitbox[1]` is not a tuple of (int, int, int).
            TypeError: If `show_hitbox[2]` is not an integer.

        Attributes:
            show_hitbox (bool): Indicates whether the hitbox is displayed.
            image (pygame.surface.Surface): The loaded and scaled image surface.
            rect (pygame.FRect): The rectangle representing the image's dimensions and position.
        """
        if show_error_messages:
            if not isinstance(self.screen, pygame.Surface): raise TypeError("screen must be a pygame.Surface")
            if not isinstance(image_path, str): raise TypeError("image_path must be a str")
            if not isinstance(self.POSITION, pygame.Vector2): raise TypeError("POSITION must be a pygame.Vector2")
            if not isinstance(self.show_hitbox, list): raise TypeError("show_hitbox must be a tuple[bool, (int, int, int), int]")
            if not isinstance(self.show_hitbox[0], bool): raise TypeError("show_hitbox[0] must be a bool")
            if not isinstance(self.show_hitbox[1], tuple): raise TypeError("show_hitbox[1] must be a tuple of (int, int, int)")
            if not isinstance(self.show_hitbox[2], int): raise TypeError("show_hitbox[2] must be an int")

        image = pygame.image.load(image_path).convert_alpha()
        self.image: pygame.surface.Surface = pygame.transform.scale(image, self.enemy_scale)
        self.rect: pygame.FRect = pygame.FRect(self.image.get_rect())
        self.default_rect = self.rect.copy()
        self.default_rect.topleft = (0, 0)
        self.mask_enemy: pygame.Mask = pygame.mask.from_surface(self.image)
        self.rect.center = self.POSITION
    
    def movement(self,
                 current_target: Entity = None,
                 current_blocking: pygame.FRect | list[pygame.FRect] = None,
                 LOS_STEPS: int = 3,
                 max_distance: int = 1000,
                 visuals: bool = None,
                 visible_corners_needed = 2,
                 wait_time: int = 10,
                 show_error_messages: bool = True) -> None: #TODO: Idk irgendwas will hier nicht es laggt immer
        """
        Handles the movement logic for the enemy.

        This method should be called every frame to update the enemy's position.

        Args:
            current_target (Entity, optional): The current target of the enemy. Defaults to None.
            current_blocking (pygame.FRect | list[pygame.FRect], optional): The current blocking objects. Defaults to None.
            LOS_STEPS (int, optional): The number of steps to check for line of sight. Defaults to 3.
            max_distance (int, optional): The maximum distance to check for line of sight. Defaults to 1000.
            visuals (bool, optional): Whether to display the pathfinding visuals. Defaults to None.
            visible_corners_needed (int, optional): The number of corners that need to be in line of sight. Defaults to 2.
            wait_time (int, optional): The time to wait before recalculating the path. Defaults to 10.
            show_error_messages (bool, optional): Whether to display error messages. Defaults to True.

        Raises:
            TypeError: If `current_target` is not an instance of Entity or None.
            TypeError: If `current_blocking` is not a pygame.FRect or a list of pygame.FRect or None.
            ValueError: If `LOS_STEPS` is not a positive integer.
            ValueError: If `max_distance` is not a positive integer.
            ValueError: If `wait_time` is not a positive integer.
            TypeError: If `visuals` is not a boolean or None.
            TypeError: If `visible_corners_needed` is not an integer.
        """
        if show_error_messages:
            if not isinstance(self.main_target, Entity) or (current_target is not None and not isinstance(current_target, Entity)):
                raise TypeError("main_target or current_target must be instances of Entity")
            if not isinstance(self.blocking, (pygame.FRect, list)) or (current_blocking is not None and not isinstance(current_blocking, (pygame.FRect, list))):
                raise TypeError("blocking or current_blocking must be a pygame.FRect or a list of pygame.FRect")
            if not isinstance(LOS_STEPS, int) or LOS_STEPS < 1:
                raise ValueError("LOS_STEPS must be a positive integer")
            if not isinstance(visuals, bool | None) or (visuals is not None and not isinstance(self.show_hitbox[0], bool)):
                raise TypeError("visuals must be a boolean or none")
            if not isinstance(wait_time, int) or wait_time < 1:
                raise ValueError("wait_time must be a positive integer")

        self.first_call: bool
        self.starting_pos: pygame.Rect
        self.started_counter: bool
        self.had_los: bool
        self.last_calculation: float
        self.path: list[pygame.Vector2]

        def init() -> None:
            self.first_call = True
            self.starting_pos = self.rect.copy()
            self.started_counter = False
            self.going_back = False
            self.had_los = False
            self.last_calculation = time.time()
            self.path = [self.POSITION.copy()] if not hasattr(self, "path") else self.path
        
        def cleanup() -> None:
            del self.path
            del self.last_calculation
            del self.first_call
            del self.starting_pos
            del self.started_counter
            del self.last_seen
            del self.counter_time
            del self.had_los
            del self.going_back
            del self.back_path

        if current_target is None:
            current_target = self.main_target

        if current_blocking is None:
            current_blocking = self.blocking
                
        if visuals is None:
            visuals = self.show_hitbox[0]

        if not hasattr(self, "first_call"):
            init()

        Line_of_sight: bool = self.LOS(current_target, current_blocking, max_distance=max_distance, steps=LOS_STEPS, visuals_toggled=visuals, show_error_messages=show_error_messages)
        corner_los: list[bool] = self.player_corners_los(current_target, current_blocking, max_distance=max_distance, steps=LOS_STEPS, visuals_toggled=visuals)

        if Line_of_sight or corner_los.count(True) >= visible_corners_needed:
            self.last_seen: pygame.FRect = current_target.rect.copy()
            self.started_counter = False
            self.going_back = False
            self.had_los: bool = True
            if hasattr(self, "back_path"):
                del self.back_path

        if hasattr(self, "last_seen"):
            if not self.going_back:
                if False in corner_los:
                    distance_bigger_than_last_seen: bool = self.path[-1].distance_to(self.last_seen.center) > self.a_star_update_distance if len(self.path) >= 1 else False

                    if time.time() - self.last_calculation > wait_time or distance_bigger_than_last_seen:
                        self.path = self.a_star(self.last_seen,
                                                current_blocking,
                                                grid_size=self.a_star_grid_size,
                                                buffer=(51, 31),
                                                max_distance=max_distance)
                        self.last_calculation = time.time()

                    if self.path and len(self.path) >= 1:
                        movement = self.move_to(self.path[0], 0.1)
                        if movement is False:
                                self.path.pop(0)

                    if visuals and len(self.path) > 1:
                        pygame.draw.lines(self.screen, (0, 0, 0), False, self.path, 2)

                elif all(corner_los):
                    self.move_to(self.last_seen.center)
                    if visuals:
                        pygame.draw.line(self.screen, (0, 0, 0), self.POSITION, self.last_seen.center, 2)
        
            if len(self.path) == 1 and not self.started_counter and self.had_los:
                self.started_counter = True
                self.counter_time = time.time()

        if hasattr(self, "counter_time"):
            if time.time() - self.counter_time > wait_time and self.started_counter:
                self.started_counter = False
                self.going_back = True

        if hasattr(self, "going_back"):
            if self.going_back:
                if not hasattr(self, "back_path"):
                    distance = int(pygame.Vector2(self.rect.center).distance_to(self.starting_pos.center))
                    self.back_path = self.a_star(self.starting_pos,
                                                 current_blocking,
                                                 grid_size=self.a_star_grid_size,
                                                 buffer=(51, 31),
                                                 max_distance=distance)
                if len(self.back_path) >= 1:
                    movement = self.move_to(self.back_path[0], 0.1)
                    if movement is False:
                        self.back_path.pop(0)

                    if visuals and len(self.back_path) > 1:
                        pygame.draw.lines(self.screen, (0, 0, 0), False, self.back_path, 2)
                else:
                    cleanup()

    def update_all_positions(self,
                             POSITION: pygame.Vector2 | tuple[int, int] | list[int, int],
                             show_error_messages: bool = True) -> None:
        """
        Updates the position of the Entity's rect and POSITION attribute.

        Args:
            POSITION (pygame.Vector2 | tuple[int, int] | list[int, int]): The new position to be set.
            show_error_messages (bool, optional): Whether to show error messages. Defaults to True.

        Raises:
            TypeError: If `POSITION` is not a pygame.Vector2 or tuple[int, int] or list[int, int].
        """
        if show_error_messages:
            if not isinstance(POSITION, (pygame.Vector2, tuple, list)): raise TypeError("POSITION must be a pygame.Vector2 or tuple[int, int] or list[int, int]")
        
        self.x, self.y = self.rect.center = self.POSITION = pygame.Vector2(POSITION)

    def a_star(
        self,
        target: pygame.Rect,
        blocking: list[pygame.FRect],
        max_distance: int = 1000,
        grid_size: int = 32,
        buffer: tuple[int, int] = (30, 20)
    ) -> list[pygame.Vector2]:
        """
        Performs an A* pathfinding algorithm to find the shortest path from the
        Entity's current position to the given target position.

        Args:
            target (pygame.Rect): The target position to find the path to.
            blocking (list[pygame.FRect]): A list of blocking rectangles to avoid.
            max_distance (int, optional): The maximum distance to search. Defaults to 1000.
            grid_size (int, optional): The size of the grid to use for pathfinding. Defaults to 32.
            buffer (tuple[int, int], optional): A buffer to apply to the blocking rectangles.
                Defaults to (30, 20).

        Returns:
            list[pygame.Vector2]: A list of positions representing the shortest path from
                the Entity's current position to the target position. If no path is found,
                an empty list is returned.
        """
        try:
            width = (max_distance * 2) // grid_size
            height = (max_distance * 2) // grid_size

            offset_x = self.POSITION.x - max_distance
            offset_y = self.POSITION.y - max_distance
            
            if not hasattr(self, "matrix"):
                self.matrix = np.ones((height, width), dtype=int)
            else:
                self.matrix.fill(1)

            for block in blocking:
                block_x1 = max(0, int((block.left - offset_x - buffer[0]) / grid_size))
                block_y1 = max(0, int((block.top - offset_y - buffer[1]) / grid_size))
                block_x2 = min(width - 1, int((block.right - offset_x + buffer[0]) / grid_size))
                block_y2 = min(height - 1, int((block.bottom - offset_y + buffer[1]) / grid_size))

                if block_x1 <= block_x2 and block_y1 <= block_y2:
                    self.matrix[block_y1:block_y2 + 1, block_x1:block_x2 + 1] = 0

            grid = Grid(matrix=self.matrix)

            start_x = int((self.POSITION.x - offset_x) / grid_size)
            start_y = int((self.POSITION.y - offset_y) / grid_size)
            start = grid.node(start_x, start_y)

            candidate_positions = [
                pygame.Vector2(target.center),
                pygame.Vector2(target.topleft),
                pygame.Vector2(target.topright),
                pygame.Vector2(target.bottomleft),
                pygame.Vector2(target.bottomright),
            ]

            finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
            for pos in candidate_positions:
                end_x = int((pos.x - offset_x) / grid_size)
                end_y = int((pos.y - offset_y) / grid_size)
                
                if 0 <= end_x < width and 0 <= end_y < height:
                    end = grid.node(end_x, end_y)
                    path, _ = finder.find_path(start, end, grid)
                    
                    if path:
                        return [
                            pygame.Vector2(
                                x * grid_size + offset_x + grid_size / 2,
                                y * grid_size + offset_y + grid_size / 2
                            )
                            for x, y in path
                        ]

            return []

        except Exception as e:
            print(f"[A* ERROR] {e}")
            return []
        
    def move_to(self,
                POSITION: pygame.Vector2 | tuple[int, int] | list[int, int],
                show_error_messages: bool = True) -> bool:
        """
        Moves the Entity to the specified position.

        Args:
            POSITION (pygame.Vector2 | tuple[int, int] | list[int, int]): The position to move to.
            show_error_messages (bool, optional): Whether to show error messages. Defaults to True.

        Raises:
            TypeError: If `POSITION` is not a pygame.Vector2 or tuple[int, int] or list[int, int].

        Returns:
            bool: False if the Entity is already at the target position, True otherwise.
        """
        if show_error_messages:
            if not isinstance(POSITION, (pygame.Vector2, tuple, list)): raise TypeError("POSITION must be a pygame.Vector2 or tuple[int, int] or list[int, int]")
        
        planned_position = POSITION if isinstance(POSITION, pygame.Vector2) else pygame.Vector2(POSITION)
        pre_move_pos = self.POSITION.copy()

        distance_vector = (planned_position - self.POSITION)
        if distance_vector == pygame.Vector2(0, 0) or planned_position == self.POSITION:
            return False
        
        winkel = distance_vector.normalize()
        
        movement_vector = winkel * self.movement_speed * self.delta_time
        new_position_enemy = self.POSITION + movement_vector
        
        if (planned_position - self.POSITION).length_squared() < movement_vector.length_squared():
            new_position_enemy = planned_position

        self.update_all_positions((new_position_enemy.x, pre_move_pos.y))
        x = pre_move_pos.x if self.hitbox_check(self.blocking) else new_position_enemy.x

        self.update_all_positions((pre_move_pos.x, new_position_enemy.y))
        y = pre_move_pos.y if self.hitbox_check(self.blocking) else new_position_enemy.y

        self.update_all_positions((x, y))
        return True
    
    def shoot(self):
        if self.holding_weapon():
            los: bool = self.LOS(self.main_target, self.blocking, max_distance=self.gun.max_distance + 100)
            if los:
                self.gun.shoot(self.main_target.POSITION.x, self.main_target.POSITION.y)
            self.gun.update()

    def update(self, *args, **kwargs):
        """
        Updates the entity's position and redraws it on the screen.

        Args:
            *args: Additional positional arguments to be passed to the `movement` method.
            **kwargs: Additional keyword arguments to be passed to the `movement` method.

        Calls the `movement` method and then calls the `draw` method to redraw the entity at its new position.

        Note: This method should be called once per frame to update the entity's state and redraw it on the screen.
        """
        self.movement(*args, **kwargs)
        self.draw()
        self.shoot()

    def draw(self,
             show_error_messages: bool = True) -> None:
        """
        Draws the entity on the given screen.

        Args:
            show_error_messages (bool, optional): Whether to display error messages. Defaults to True.

        Raises:
            TypeError: If `self.image` is not a `pygame.Surface` instance.
            TypeError: If `self.rect` is not a `pygame.FRect` instance.

        Attributes:
            show_hitbox (bool): Indicates whether the hitbox is displayed.
        """
        if show_error_messages:
            if not isinstance(self.image, pygame.Surface): raise TypeError("self.image must be a pygame.surface.Surface")
            if not isinstance(self.rect, (pygame.FRect)): raise TypeError("self.rect must be a pygame.FRect")
            
        self.screen.blit(self.image, self.rect.topleft)

        if self.show_hitbox[0]:
            outline = self.mask_enemy.outline()
            
            has_transparency: bool = True if isinstance(self.show_hitbox[1], tuple) and len(self.show_hitbox[1]) == 4 else False
            
            if has_transparency:
                temp_surface: pygame.surface.Surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                pygame.draw.lines(temp_surface, self.show_hitbox[1], True, [(point[0], point[1]) for point in outline], self.show_hitbox[2])
                pygame.draw.rect(temp_surface, self.show_hitbox[1], self.image.get_rect(), self.show_hitbox[2])
                self.screen.blit(temp_surface, self.rect.topleft)
            
            else:
                pygame.draw.lines(self.screen, self.show_hitbox[1], True, [(point[0] + self.rect.x, point[1] + self.rect.y) for point in outline], self.show_hitbox[2])


    def LOS(self,
            target: pygame.sprite.Group[Entity] | Entity | list[Entity] | pygame.Vector2,
            blocking: pygame.FRect | list[pygame.FRect],
            starting_pos: pygame.Vector2 = None,
            max_distance: int = 1000,
            steps: int = 5, 
            visuals_toggled: bool = False,
            show_error_messages: bool = True) -> bool:
        """
        Performs a line-of-sight check between the player and the given target(s)
        within the specified maximum distance and with the given number of steps.

        Args:
            target (pygame.sprite.Group | pygame.sprite.Sprite | list[pygame.sprite.Sprite]):
                The target(s) to check for line-of-sight.
            blocking (pygame.FRect | list[pygame.FRect]):
                The blocking objects to check against.
            max_distance (int, optional): The maximum distance to check. Defaults to 1000.
            steps (int, optional): The number of steps to take when checking. Defaults to 5.
            screen (pygame.surface.Surface, optional): The screen to draw debugging circles on. Defaults to None.

        Returns:
            dict[pygame.sprite.Sprite, bool]: A dictionary containing the target(s) as keys and
            a boolean indicating whether the target is in line-of-sight as values.

        Raises:
            ValueError: If `max_distance` or `steps` are not positive integers.
        """
        if show_error_messages:
            if not isinstance(max_distance, int) or max_distance < 1:
                raise ValueError("max_distance must be a positive integer")
            if not isinstance(steps, int) or steps < 1:
                raise ValueError("steps must be a positive integer")
            if not isinstance(blocking, (pygame.FRect, list)):
                raise TypeError("blocking must be a pygame.FRect or a list of pygame.FRect")
            if not isinstance(target, (pygame.sprite.Group, pygame.sprite.Sprite, list, pygame.Vector2)):
                raise TypeError("target must be a pygame.sprite.Group, a pygame.sprite.Sprite, or a list of pygame.sprite.Sprite")
            if not isinstance(starting_pos, pygame.Vector2) and starting_pos is not None:
                raise TypeError("starting_pos must be a pygame.Vector2 or None")
        if starting_pos is None: starting_pos = self.POSITION
        blocking_list: list[pygame.FRect] | pygame.sprite.Group = blocking if isinstance(blocking, (list, pygame.sprite.Group)) else [blocking]
        max_distance_square: int = max_distance ** 2

        def check_blocking(_pos: pygame.Vector2,
                           _blocking_list: list[pygame.FRect] = blocking_list) -> bool:
            x, y = int(_pos.x), int(_pos.y)
            for block in _blocking_list:
                if block.collidepoint(x, y):
                    return True
            return False

        def process_sprite(_sprite: Entity | pygame.Vector2,
                           _starting_pos: pygame.Vector2,
                           _max_distance_sq: int = max_distance_square,
                           _visuals_toggled: bool = visuals_toggled) -> bool:
            sprite_pos = _sprite.POSITION if isinstance(_sprite, Entity) else _sprite

            if isinstance(_sprite, pygame.Vector2):
                temp_rect = pygame.FRect(_sprite.x, _sprite.y, 1, 1)
            
            else: temp_rect = _sprite.rect

            if (sprite_pos - _starting_pos).length_squared() > _max_distance_sq:
                return False

            if self.rect.colliderect(temp_rect):
                return True

            direction = (sprite_pos - _starting_pos).normalize() if sprite_pos - _starting_pos != (0, 0) else pygame.Vector2(0, 0)
            steps_needed = int(_starting_pos.distance_to(sprite_pos) / steps) + 1

            for i in range(steps_needed):
                current_pos = _starting_pos + direction * (steps * i)
                
                if _visuals_toggled and i % 5 == 0:
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(current_pos.x), int(current_pos.y)), 2)
                
                if check_blocking(current_pos):
                    return False
            return True

        if isinstance(target, pygame.sprite.Group):
            return (process_sprite(sprite, starting_pos, max_distance_square, visuals_toggled) for sprite in target)
        elif isinstance(target, pygame.sprite.Sprite):
            return process_sprite(target, starting_pos, max_distance_square, visuals_toggled)
        elif isinstance(target, list):
            return (process_sprite(sprite, starting_pos, max_distance_square, visuals_toggled) for sprite in target)
        elif isinstance(target, pygame.Vector2):
            return process_sprite(target, starting_pos, max_distance_square, visuals_toggled)
    
    def player_corners_los(self,
                           target: Entity,
                           blocking: pygame.FRect | list[pygame.FRect] = None,
                           max_distance: int = 1000,
                           steps: int = 5,
                           visuals_toggled: bool = True,
                           show_error_messages: bool = True) -> list[bool]:
        """
        Performs a line-of-sight check between each of the player's corners and the corresponding corner of the target entity.

        Args:
            target (Entity): The target entity to check against.
            blocking (pygame.FRect | list[pygame.FRect], optional): The objects to check for blocking. Defaults to None.
            max_distance (int, optional): The maximum distance to check. Defaults to 1000.
            steps (int, optional): The number of steps to take when checking. Defaults to 5.
            visuals_toggled (bool, optional): Whether to draw debugging circles. Defaults to True.
            show_error_messages (bool, optional): Whether to show error messages. Defaults to True.

        Returns:
            list[bool]: A list of booleans indicating whether each corner is in line-of-sight.
        """
        each_corner: list[(pygame.Vector2, pygame.Vector2)] = [(pygame.Vector2(self.rect.topleft), pygame.Vector2(target.rect.topleft)),
                                             (pygame.Vector2(self.rect.topright), pygame.Vector2(target.rect.topright)),
                                             (pygame.Vector2(self.rect.bottomleft),pygame.Vector2(target.rect.bottomleft)),
                                             (pygame.Vector2(self.rect.bottomright), pygame.Vector2(target.rect.bottomright))]
        if blocking is None:
            blocking = self.blocking
        return [self.LOS(player_corner, blocking, enemy_corner, max_distance, steps, visuals_toggled, show_error_messages) for enemy_corner, player_corner in each_corner]

    def hitbox_check(self,
                     blocking: pygame.FRect | list[pygame.FRect] = None,
                     position: pygame.Vector2 = None,
                     show_error_messages: bool = True):  # TODO: Falls es lagt mask fixen da es viele Punkte checkt
        """
        Checks if the entity's hitbox collides with any blocking rectangles at a given position.

        Args:
            blocking (pygame.FRect | list[pygame.FRect]):
                The blocking objects to check against.
            position (pygame.Vector2, optional):
                The position to use for collision detection. Defaults to the entity's current position.

        Returns:
            bool: True if the entity's hitbox collides with any of the blocking rectangles, False otherwise.

        Raises:
            TypeError: If `blocking` is not a `pygame.FRect` or a list of `pygame.FRect` instances.
        """
        if show_error_messages:
            if not isinstance(blocking, (pygame.FRect, list)) and blocking is not None: raise TypeError("blocking must be a pygame.FRect or a list of pygame.FRect")
            if not isinstance(position, pygame.Vector2) and position is not None: raise TypeError("position must be a pygame.Vector2 or None")
            position = self.POSITION if position is None else position
            blocking = self.blocking if blocking is None else blocking

        def check_blocking(_blocking: pygame.FRect) -> bool:
            mask_blocking: pygame.Mask = pygame.mask.from_surface(pygame.Surface(_blocking.size))
            return bool(self.mask_enemy.overlap(mask_blocking, (_blocking.x - (position.x - self.rect.width // 2), _blocking.y - (position.y- self.rect.height // 2)))) # Checkt ob Enemy mit Blocking kollidiert wenn nicht return

        if isinstance(blocking, pygame.FRect):
            return check_blocking(blocking)
        
        else:
            for block in blocking:
                collision: bool = check_blocking(block)
                if collision:
                    return collision
            return False
        

class Weapon(Entity):
    def __init__(self,
                 weapon_image: pygame.Surface,
                 bullet_image: pygame.Surface,
                 screen: pygame.surface.Surface,
                 position: pygame.Vector2,
                 blocking: list[pygame.FRect],
                 targets: Groups[Entity],
                 weapon_shoot_sound: pygame.mixer.Sound,
                 explode_sound: pygame.mixer.Sound = None,
                 sticking_to: Entity = None,
                 weapon_pickup_multiplier: float = 2,
                 rotate_angle = 0,
                 spread_degree = 30,
                 bullets = 1,
                 bullet_speed = 10,
                 reload_time = 0,
                 delta_time: float = 1,
                 damage: float = 10,
                 max_distance: int = 1000,
                 exploding: bool = True,
                 exploding_time: float = 1.5,
                 explosion_radius: int = 20,
                 bullet_size = (10, 10),
                 weapon_throw_speed: float = 2,
                 weapon_throw_decrease: float = 0.01,
                 show_hitbox: list[bool, (int, int, int), int] = [False, (0, 0, 0), 2])-> None:
        """
        Initializes a weapon entity with the specified parameters.

        Args:
            weapon_image_path (str): The file path to the image to be loaded.
            bullet_image_path (str): The file path to the image to be loaded.
            screen (pygame.surface.Surface): The surface on which to draw the weapon.
            position (pygame.Vector2): The position where the image will be drawn.
            blocking (list[pygame.FRect]): The blocking objects to check against.
            targets (Groups[Entity]): The entities to check for line-of-sight.
            sticking_to (Entity, optional): The entity to which the weapon is attached. Defaults to None.
            spread_degree (int, optional): The degree of spread for the weapon. Defaults to 30.
            bullets (int, optional): The number of bullets to fire. Defaults to 1.
            bullet_speed (int, optional): The speed of the bullets. Defaults to 10.
            damage (float, optional): The damage the bullets will do. Defaults to 10.
            max_distance (int, optional): The maximum distance the bullets will travel. Defaults to 1000.
            exploding (bool, optional): Whether the bullets will explode upon hitting a target. Defaults to True.
            exploding_time (float, optional): The time the bullets will take to explode. Defaults to 1.5.
            explosion_radius (int, optional): The radius of the explosion. Defaults to 20.
            bullet_size (tuple[int, int], optional): The size of the bullets. Defaults to (10, 10).
            weapon_size (tuple[int, int], optional): The size of the weapon. Defaults to (100, 100).
            weapon_throw_speed (float, optional): The speed at which the weapon is thrown. Defaults to 2.
            weapon_throw_decrease (float, optional): The rate at which the weapon throw speed decreases. Defaults to 0.01.
            show_hitbox (list[bool, (int, int, int), int], optional): Whether to display the hitbox of the weapon. Defaults to [False, (0, 0, 0), 2].
        """
        super().__init__()

        self.x: int = position.x
        self.y: int = position.y
        self.POSITION: pygame.Vector2 = position
        self.throwing: bool = False
        if hasattr(self, "sticking_to") and self.sticking_to:
            self.offset = pygame.Vector2(self.sticking_to.rect.topright) - self.sticking_to.POSITION
            self.offset.x += 5
        self.rotate_angle = rotate_angle

        self.weapon_shoot_sound: pygame.mixer.Sound = weapon_shoot_sound
        self.bullet_image = bullet_image
        self.weapon_pickup_multiplier: float = weapon_pickup_multiplier
        self.weapon_image = weapon_image
        self.initiate_drawing()
        self.screen: pygame.surface.Surface = screen

        self.blocking: pygame.FRect | list[pygame.FRect] = blocking
        self.targets: Groups[Entity] = targets
        self.sticking_to: Entity = sticking_to

        self.explode_sound: pygame.mixer.Sound = explode_sound
        self.exploding: bool = exploding
        self.explosion_radius: tuple[int, int] = explosion_radius
        self.exploding_time: float = exploding_time

        self.spread_degree: int = spread_degree
        self.bullets: int = bullets
        self.bullet_speed: int = bullet_speed
        self.delta_time: float = delta_time
        self.damage: float = damage
        self.bullet_size: tuple[int, int] = bullet_size
        self.max_distance: int = max_distance

        self.throw_speed: float = weapon_throw_speed
        self.throw_decrease: float = weapon_throw_decrease

        self.reload_time: float = reload_time
        self.last_shot: int = pygame.time.get_ticks()
        self.shot_bullets: Groups = Groups()
        self.show_hitbox = show_hitbox
        self.update_all_positions(self.rect.center)

    def initiate_drawing(self):
        """
        Initializes the drawing of the player with specified parameters.

        Args:
            image_path (str): The file path to the image to be loaded.
            image_size (tuple[int, int]): The size of the image.

        Raises:
            TypeError: If `image_path` is not a string.
            TypeError: If `image_size` is not a tuple of two integers.

        Attributes:
            image (pygame.surface.Surface): The loaded and scaled image surface.
            rect (pygame.FRect): The rectangle representing the image's dimensions and position.
        """
        self.rect = pygame.FRect(self.weapon_image.get_bounding_rect())
        self.weapon_image = self.weapon_image.subsurface(self.rect)
        self.pickup_rect: pygame.FRect = self.rect.copy()
        self.pickup_rect.width *= self.weapon_pickup_multiplier
        self.pickup_rect.height *= self.weapon_pickup_multiplier
        self.update_all_positions(self.rect.center)

    def shoot(self,
              x: int,
              y: int,
              show_debug: bool = False) -> None:
        """
        Fires bullets towards a specified target position with a spread.

        Args:
            x (int): The x-coordinate of the target position.
            y (int): The y-coordinate of the target position.
            show_debug (bool, optional): Whether to show debugging visuals for the bullet spread. Defaults to False.

        This function calculates a spread area around the target position and fires multiple bullets
        with random trajectories within this spread. The bullets are added to the shot_bullets group
        and will interact with the blocking objects and targets specified.

        The spread is visualized with red lines when `show_debug` is True.
        Returns:
            None:
        """
        try:
            if pygame.time.get_ticks() - self.last_shot < self.reload_time * 1000:
                return
            
            vec = pygame.Vector2(x, y) - self.POSITION
            top_spread = vec.rotate(self.spread_degree/2) + self.POSITION
            bottom_spread= vec.rotate(-self.spread_degree/2) + self.POSITION

            smaller_x = round(min(top_spread.x, bottom_spread.x))
            bigger_x = round(max(top_spread.x, bottom_spread.x))

            smaller_y = round(min(top_spread.y, bottom_spread.y))
            bigger_y = round(max(top_spread.y, bottom_spread.y))

            if show_debug:
                pygame.draw.lines(self.screen, (255, 0, 0), False, [self.POSITION, top_spread, bottom_spread, self.POSITION], 2)

            self.weapon_shoot_sound.play()

            for i in range(self.bullets):
                random_x = random.randint(smaller_x, bigger_x) if smaller_x != bigger_x else smaller_x
                random_y = random.randint(smaller_y, bigger_y) if smaller_y != bigger_y else smaller_y
                self.shot_bullets.add(Bullet(image=self.bullet_image,
                                            POSITION=self.POSITION,
                                            target_position=pygame.Vector2(random_x, random_y),
                                            blocking=self.blocking,
                                            targets=self.targets,
                                            screen=self.screen,
                                            damage=self.damage,
                                            speed=self.bullet_speed,
                                            max_distance=self.max_distance,
                                            bullet_size=self.bullet_size,
                                            sound=self.explode_sound,
                                            explosion_radius=[self.exploding, self.explosion_radius, self.exploding_time],
                                            show_hitbox=self.show_hitbox))
                self.last_shot = pygame.time.get_ticks()
        except Exception as e:
            print("[!]Fehler beim Schiessen", e)

    def draw(self,
             surface = None) -> None:
        """
        Draws the player's image on the given surface.

        This method blits the player's image onto the provided surface
        at the player's current position. If the player's hitbox is set to be
        shown, a red rectangle will be drawn around the image to indicate the
        hitbox.

        Args:
            surface (pygame.surface.Surface, optional): The surface on which the player's
            image will be drawn. Defaults to None.

        Raises:
            TypeError: If `surface` is not a `pygame.surface.Surface` instance.

        Returns:
            None:
        """
        try:
            surface: pygame.surface.Surface = self.screen if surface is None else surface
            if self.show_hitbox[0]:
                temp_surface: pygame.Surface = pygame.Surface(self.pickup_rect.size, pygame.SRCALPHA)
                temp_pickup_rect: pygame.FRect = temp_surface.get_rect()

                temp_rect: pygame.FRect = self.rect.copy()
                temp_rect.center = temp_pickup_rect.center

                pygame.draw.rect(temp_surface, self.show_hitbox[1], temp_pickup_rect, self.show_hitbox[2])
                pygame.draw.rect(temp_surface, self.show_hitbox[1], temp_rect, self.show_hitbox[2])

                if self.throwing:
                    pygame.draw.line(surface, self.show_hitbox[1], self.POSITION, self.throwing_to, self.show_hitbox[2])

                surface.blit(temp_surface, self.pickup_rect)
            
            image = self.weapon_image
            rect = self.rect.copy()

            if self.sticking_to:
                if not hasattr(self, "offset"):
                    self.offset = pygame.Vector2(self.sticking_to.default_rect.topright) - pygame.Vector2(self.sticking_to.default_rect.center)
                    self.offset.x += 5

                image = pygame.transform.rotate(image, self.rotate_angle)
                rotated_offset = self.offset.rotate(-self.rotate_angle)
                self.update_all_positions(self.sticking_to.POSITION + rotated_offset)
                rect = pygame.FRect(image.get_rect(center=self.rect.center))

            surface.blit(image, rect)
        except Exception as e:
            print("[!]Fehler beim Waffen Zeichnen", e)

    def movement(self) -> None:
        """
        Handles the movement of the player.

        If the player is sticking to another entity, this method will
        adjust the player's position to be at the midright of that entity's
        rect.

        If the player is throwing a pickup, this method will call the
        `throw` method to handle the throwing logic.

        Returns:
            None:
        """
        try:
            if self.sticking_to:
                x, y = self.sticking_to.rect.topright
                self.update_all_positions((x, y+5))

            if self.throwing:
                self.throw()

        except Exception as e:
            print("[!]Fehler beim Waffen Bewegen", e)

    def throw(self) -> None:
        """
        Handles the logic for throwing an object to a target position.

        This method calculates and updates the position of the object being
        thrown based on its speed and direction. It also handles collisions
        with blocking objects and reflects the direction accordingly. If the
        object's speed decreases to zero or below, it performs cleanup operations.

        Attributes:
            throwing (bool): Indicates if the object is currently being thrown.
            throwing_to (pygame.Vector2): The target position for the throw.
            first_call (bool): Flag for initializing the throw logic.
            current_speed (float): The current speed of the thrown object.
            normalized_throw (pygame.Vector2): The normalized direction vector
                for the throw.

        Raises:
            AttributeError: If there are issues accessing object attributes.
        """
        try:
            self.throwing: bool
            self.throwing_to: pygame.Vector2
            self.first_call: bool
            self.current_speed: float
            self.normalized_throw: pygame.Vector2
            def init():
                if self.rect.collidelist(self.blocking) != -1:
                    self.update_all_positions(self.sticking_to.POSITION)
                self.first_call = False
                self.throwing = True
                self.normalized_throw = (self.throwing_to - self.sticking_to.POSITION).normalize()
                self.sticking_to = None
                self.targets = None
                self.current_speed = self.throw_speed * self.delta_time

            def cleanup():
                del self.first_call
                del self.throwing_to
                del self.normalized_throw
                self.current_speed = 0
                self.throwing = False

            if not hasattr(self, "first_call"):
                init()

            starting_position = self.POSITION.copy()
            self.update_all_positions(self.POSITION + self.normalized_throw * self.current_speed)
            
            if self.rect.collidelist(self.blocking) != -1:
                x_movement = self.normalized_throw.x * self.current_speed
                y_movement = self.normalized_throw.y * self.current_speed

                self.update_all_positions((starting_position.x + x_movement, starting_position.y))
                if self.rect.collidelist(self.blocking) != -1:
                    self.normalized_throw.x *= -1

                self.update_all_positions((starting_position.x, starting_position.y + y_movement))
                if self.rect.collidelist(self.blocking) != -1:
                    self.normalized_throw.y *= -1

                self.update_all_positions((starting_position + self.normalized_throw * self.current_speed))

            self.current_speed -= self.throw_decrease * (self.delta_time ** 2)

            if self.current_speed <= 0:
                cleanup()

        except AttributeError as e:
            print("[!]Fehler beim Waffen Wurf", e)
    
    def update_sound_volume(self):
        if self.weapon_shoot_sound:
            self.weapon_shoot_sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)
        if self.explode_sound:
            self.explode_sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)

    def update(self) -> None:
        """
        Updates the state of the entity.

        This method should be called once per frame to update the entity's state and redraw it on the screen.

        Calls the `movement` method to update the entity's position, then calls the `draw` method to redraw the entity at its new position.

        If the entity has shot bullets, this method will call the `update` method on the `shot_bullets` group to update the state of the bullets.

        Returns:
            None:
        """
        try:
            self.movement()
            self.draw()
            if self.shot_bullets:
                self.shot_bullets.update(self.delta_time)
            
            if self.sticking_to and not self.sticking_to.gun:
                self.sticking_to.gun = self
                
        except Exception as e:
            print("[!]Fehler beim Waffen Update", e)

    def update_all_positions(self, position: pygame.Vector2 | tuple[int, int] | list[int, int]) -> None:
        """
        Updates the position of the Entity's rect and POSITION attribute.

        Args:
            position (pygame.Vector2 | tuple[int, int] | list[int, int]): The new position to be set.

        Returns:
            None:
        """
        try:
            self.x, self.y = self.pickup_rect.center = self.rect.center = self.POSITION = pygame.Vector2(position)
        except Exception as e:
            print("[!]Fehler beim Update der Waffen Position", e)

    def copy(self) -> "Weapon":
        """
        Creates a deep copy of the Weapon instance, excluding transient runtime state like shot bullets.
        
        Returns:
            Weapon: A new instance with the same configuration and position.
        """
        new_weapon = Weapon(
            weapon_image=self.weapon_image,
            bullet_image=self.bullet_image,
            screen=self.screen,
            position=pygame.Vector2(self.POSITION),
            blocking=self.blocking.copy() if isinstance(self.blocking, list) else self.blocking,  # shallow copy if list
            targets=self.targets.copy(),
            weapon_shoot_sound=self.weapon_shoot_sound,
            explode_sound=self.explode_sound,
            sticking_to=self.sticking_to,
            weapon_pickup_multiplier=self.weapon_pickup_multiplier,
            spread_degree=self.spread_degree,
            bullets=self.bullets,
            bullet_speed=self.bullet_speed,
            reload_time=self.reload_time,
            delta_time=self.delta_time,
            damage=self.damage,
            max_distance=self.max_distance,
            exploding=self.exploding,
            exploding_time=self.exploding_time,
            explosion_radius=self.explosion_radius,
            weapon_throw_speed=self.throw_speed,
            weapon_throw_decrease=self.throw_decrease,
            show_hitbox=self.show_hitbox.copy()
        )

        if self.throwing:
            new_weapon.throwing = True
            new_weapon.throwing_to = pygame.Vector2(self.throwing_to)
            new_weapon.first_call = self.first_call
            new_weapon.normalized_throw = pygame.Vector2(self.normalized_throw)
            new_weapon.current_speed = self.current_speed

        return new_weapon
        
class Bullet(Entity):
    """
    The Bullet class represents a bullet entity in a game.

    Attributes:
        image (pygame.Surface): The image representing the bullet.
        POSITION (pygame.Vector2): The position of the bullet on the screen.
        target_position (pygame.Vector2): The target position of the bullet.
        blocking (pygame.FRect | list[pygame.FRect]): The blocking area for the bullet.
        targets (pygame.sprite.Group[Entity] | list[Entity]): The targets that the bullet can hit.
        screen (pygame.surface.Surface): The screen on which the bullet is drawn.
        sound (pygame.mixer.Sound): The sound to play when the bullet hits a target.
        damage (float): The amount of damage the bullet inflicts on targets.
        speed (float): The speed at which the bullet moves.
        max_distance (int): The maximum distance the bullet can travel before it is removed.
        bullet_size (tuple[int, int]): The size of the bullet.
        explosion_radius (tuple[bool, int]): A tuple indicating whether the bullet should explode and the radius of the explosion.
        show_hitbox (list[bool, (int, int, int), int]): A list indicating whether to show the hitbox, the color of the hitbox, and the width of the hitbox.
        auto_inits (bool): A boolean indicating whether to automatically initialize the bullet.

    Methods:
        __init__(): Initializes the Bullet object.
        update(): Updates the position and state of the bullet.
        draw(): Draws the bullet on the screen.
    """
    def __init__(self,
                 image: pygame.Surface,
                 POSITION: pygame.Vector2,
                 target_position: pygame.Vector2,
                 blocking: pygame.FRect | list[pygame.FRect],
                 targets: pygame.sprite.Group[Entity] | list[Entity],
                 screen: pygame.surface.Surface,
                 sound: pygame.mixer.Sound = None,
                 damage: float = 10,
                 speed: float = 10,
                 max_distance: int = 1000,
                 bullet_size: tuple[int, int] = (10, 10),
                 explosion_radius: tuple[bool, int] = [False, 5, 3],
                 show_hitbox: list[bool, (int, int, int), int] = [False, (0, 0, 0), 2],
                 auto_inits: bool = True) -> Entity:
        super().__init__()
        self.x: int = POSITION.x
        self.y: int = POSITION.y
        self.starting_pos: pygame.Vector2 = POSITION.copy()
        self.POSITION: pygame.Vector2 = POSITION
        self.target_position = target_position.copy()

        self.direction: pygame.Vector2 = (target_position - POSITION).normalize()
        self.movement_vector: pygame.Vector2 = self.direction * speed
        self.max_distance: int = max_distance

        self.blocking: pygame.FRect | list[pygame.FRect] = blocking
        self.targets: Groups[Entity] | list[Entity] = targets

        self.damage: float = damage
        self.speed: float = speed
        self.bullet_size: tuple[int, int] = bullet_size
        self.explosion_radius: tuple[bool, int] = explosion_radius[:2]
        self.explosion_time: float = explosion_radius[2]
        self.exploding_sound: pygame.mixer.Sound = sound

        self.image = image
        self.screen: pygame.surface.Surface = screen
        self.show_hitbox: list[bool, (int, int, int), int] = show_hitbox
        self.exploding: bool = False
        self.rotate_bullet()

        if auto_inits:
            self.initiate_drawing()

    def rotate_bullet(self) -> None:
        """
        Rotates the bullet's image by 90 degrees.

        Returns:
            None:
        """
        angle = (self.target_position - self.POSITION).angle_to(pygame.Vector2(1, 0)) - 90
        self.turned_bullet = pygame.transform.rotate(self.image, angle)

    def initiate_drawing(self) -> None:
        """
        Initializes the drawing of the bullet with the specified parameters.

        Args:
            image_path (str): The file path to the image to be loaded.
            image_size (tuple[int, int]): The size of the image to be scaled to.

        Attributes:
            image (pygame.surface.Surface): The loaded and scaled image surface.
            rect (pygame.FRect): The rectangle representing the image's dimensions and position.
            explosion_rect (pygame.FRect): The rectangle representing the explosion's dimensions and position.

        Returns:
            None:
        """
        self.rect: pygame.FRect = pygame.FRect(self.image.get_rect())
        self.explosion_rect: pygame.FRect = pygame.FRect(self.rect.topleft, (self.explosion_radius[1] * 2, self.explosion_radius[1] * 2))
        self.update_all_positions(self.POSITION)

    def movement(self) -> None:
        """
        Handles the movement of the bullet and checks for collisions with the blocking objects or targets.

        The bullet will move in the direction of the movement vector, and its position will be updated accordingly.
        If the bullet has moved more than the maximum allowed distance, it will be killed.

        If the bullet collides with any of the blocking objects, it will explode.

        If the bullet collides with any of the targets, it will deal damage to them. If the bullet has an explosion radius, it will explode after dealing damage.

        Attributes:
            any_hits (list[Entity] | None): A list of entities that the bullet has collided with.
            target (Entity): An individual target that the bullet has collided with.
        
        Returns:
            None
        """
        movement = self.movement_vector.copy() * self.delta_time if self.delta_time else self.movement_vector

        self.update_all_positions(self.POSITION + movement)
        if abs(self.POSITION.x - self.starting_pos.x) > self.max_distance or abs(self.POSITION.y - self.starting_pos.y) > self.max_distance:
            self.kill()
        
        if self.rect.collidelist(self.blocking) != -1: # -1 Wenn keine Kollision
            if self.explosion_radius[0]:
                self.exploding_sound.play()
            self.explode()

        any_hits: list[Entity] | None = self.rect.collideobjectsall(self.targets, key = lambda x: x.rect)
        if any_hits:
            if not self.explosion_radius[0]: # Keine Explosion
                for target in any_hits:
                    if target.rect.colliderect(self.rect):
                        target.damage(self.damage, self.direction)
                        self.kill()
            else:
                self.exploding_sound.play()
                self.explode()

    def update(self,
               delta_time: float) -> None:
        """
        Updates the state of the bullet.

        If the bullet is in an exploding state, it calls the `explode` method.
        Otherwise, it performs movement and drawing operations to update the
        bullet's position and render it on the screen.

        Returns:
            None
        """
        if self.exploding:
            self.explode()
        else:
            self.delta_time: float = delta_time
            self.movement()
            self.draw()

        
    def explode(self) -> None:
        """
        Handles the explosion logic for the bullet.

        This method manages the initialization and processing of the bullet's
        explosion when triggered. It determines the entities within the explosion
        radius and applies damage to them. The explosion is visually represented
        on the screen and lasts for a specified duration before the bullet is removed.

        Attributes:
            started_exploding (float): The timestamp when the explosion started.
            first_call (bool): Indicates whether the explosion logic has been initialized.

        The explosion logic is as follows:
        1. If an explosion is desired (self.explosion_radius[0] is True), the method
        initializes the explosion if it hasn't been started already.
        2. During the explosion, it checks for entities within the explosion radius
        and applies damage to them.
        3. The explosion is rendered as a fading red circle on the screen.
        4. If the explosion duration has elapsed, the bullet is removed.
        5. If no explosion is desired, the bullet is immediately removed.

        Returns:
            None:
        """
        self.started_exploding: float
        self.first_call: bool
        def init():
            self.first_call = False
            self.exploding = True
            self.started_exploding = time.time()

            x: list[Entity] | list[None] = self.explosion_rect.collideobjectsall(self.targets, key = lambda x: x.rect)
            if x:
                for entity in x:
                    explosion_hitbox = circle_collision_check(entity.rect,
                                              self.explosion_radius[1],
                                              self.explosion_rect.center)
                    if explosion_hitbox:
                        entity.damage(self.damage, self.direction) # TODO: Schaden vielleicht ändern zu Explosionsschaden

        if self.explosion_radius[0]:
            if not hasattr(self, "first_call"): # die init
                init()

            if self.exploding: # Explosion
                if time.time() - self.started_exploding > self.explosion_time:
                    self.kill()
                else:
                    temp_surface = pygame.Surface(self.explosion_rect.size, pygame.SRCALPHA)
                    visibility = 255 - ((time.time() - self.started_exploding) / self.explosion_time) * 255
                    pygame.draw.circle(temp_surface, (255, 0, 0, visibility), pygame.Vector2(temp_surface.size) / 2, self.explosion_radius[1])
                    self.screen.blit(temp_surface, self.explosion_rect.topleft)

        else: # Wenn keine Explosion gewünscht ist einfach killen
            self.kill()

    def draw(self):
        """
        Draws the bullet on the screen.

        If the show_hitbox is enabled, it first creates a temporary surface and draws
        the hitbox of the bullet on it. This is then blitted onto the screen. After that,
        the actual image of the bullet is blitted onto the screen.

        Args:
            None:

        Returns:
            None:
        """
        if self.show_hitbox[0]:
            temp_surface: pygame.Surface = pygame.Surface(self.explosion_rect.size, pygame.SRCALPHA)
            temp_explosion_rect: pygame.FRect = temp_surface.get_rect()
            temp_rect: pygame.FRect = self.rect.copy()
            temp_rect.center = temp_explosion_rect.center
            pygame.draw.circle(temp_surface, self.show_hitbox[1], temp_explosion_rect.center, self.explosion_radius[1], self.show_hitbox[2])
            pygame.draw.rect(temp_surface, self.show_hitbox[1], temp_rect, self.show_hitbox[2])
            pygame.draw.rect(temp_surface, self.show_hitbox[1], temp_explosion_rect, self.show_hitbox[2])
            self.screen.blit(temp_surface, self.explosion_rect.topleft)
        self.screen.blit(self.turned_bullet, self.rect.topleft)

    def update_all_positions(self,
                             position: pygame.Vector2 | tuple[int, int] | list[int, int]) -> None:
        """
        Updates the position of the Bullet's rect and POSITION attribute.

        Args:
            position (pygame.Vector2 | tuple[int, int] | list[int, int]): The new position to be set.

        Returns:
            None:
        """
        self.x, self.y = self.explosion_rect.center = self.rect.center = self.POSITION = pygame.Vector2(position)
