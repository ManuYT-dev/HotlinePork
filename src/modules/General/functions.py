import pygame
import json
import os
from modules.General.types import Entity, InputType
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

def circle_collision_check(blocking: pygame.FRect | list[pygame.FRect],
                       radius: int,
                       position: pygame.Vector2 = None) -> bool:
    """
    Checks for collisions using a circular hitbox.
    
    Args:
        blocking: Rectangle(s) to check collision against
        radius: Radius of the circular hitbox
        position: Optional position to check from (defaults to self.POSITION)
    
    Returns:
        bool: True if collision detected, False otherwise
    """
    blocks = blocking if isinstance(blocking, list) else [blocking]
    position = position if isinstance(position, pygame.Vector2) else pygame.Vector2(position)
    
    for block in blocks:
        closest_x = max(block.left, min(position.x, block.right))
        closest_y = max(block.top, min(position.y, block.bottom))
        closest_point = pygame.Vector2(closest_x, closest_y)

        if (position - closest_point).length_squared() <= radius * radius:
            return True

    return False

class Camera:
    """
    A camera class that tracks a target and renders the main screen and smaller surface to render to.
    """
    def __init__(self,
                 main_screen: pygame.Surface,
                 surface: pygame.Surface,
                 width: int,
                 height: int,
                 main_target: Entity | pygame.Vector2 = None):
        """
        Initializes a camera object that tracks a target, with a main screen and a smaller surface to render to.
        
        Args:
            main_screen (pygame.Surface): The main screen to render to
            surface (pygame.Surface): The smaller surface to render to
            width (int): The width of the smaller surface
            height (int): The height of the smaller surface
            main_target (Entity | pygame.Vector2): The target to track (defaults to None)
        
        Attributes:
            main_screen (pygame.Surface): The main screen to render to
            surface (pygame.Surface): The smaller surface to render to
            width (int): The width of the smaller surface
            height (int): The height of the smaller surface
            main_target (Entity | pygame.Vector2): The target to track
            rect (pygame.FRect): The rectangle representing the camera's position and size
            POSITION (pygame.Vector2): The camera's position
            x (int): The x-coordinate of the camera's position
            y (int): The y-coordinate of the camera's position
        """

        self.main_screen = main_screen
        self.surface = surface
        self.width = width
        self.height = height
        self.main_target = main_target
        self.rect = pygame.FRect(0, 0, width, height)
        self.POSITION = pygame.Vector2(self.rect.center)
        self.x, self.y = self.POSITION

    def track(self,
              target: Entity | pygame.Vector2 | tuple[int, int] | list[int, int] = None,
              speed: float = 0.1,
              max_away: float = 200):
        """
        Tracks a target and updates the camera's position to follow it.
        
        Args:
            target (Entity | pygame.Vector2 | tuple[int, int] | list[int, int], optional): The target to track (defaults to None)
            speed (float, optional): The speed at which the camera moves (defaults to 0.1)
            max_away (float, optional): The maximum distance the camera can be from the target (defaults to 200)
        """
        target = target if isinstance(target, (Entity | pygame.Vector2 | tuple | list)) else self.main_target
        target_position = target.POSITION if isinstance(target, Entity) else pygame.Vector2(target)

        normalized_vector = ((target_position - self.POSITION).normalize() if ((target_position - self.POSITION) != pygame.Vector2(0, 0))
        else pygame.Vector2(0, 0))

        if speed != 0:
            new_pos = self.POSITION + normalized_vector * speed
        else:
            new_pos = target_position

        self.update_all_position(new_pos)

        if self.POSITION.distance_squared_to(target_position) > max_away ** 2:
            self.update_all_position(target_position - normalized_vector * max_away)

        new_x, new_y = self.rect.center

        if self.rect.left < 0:
            new_x = self.rect.width // 2
        if self.surface.width < self.rect.right:
            new_x = self.surface.width - self.rect.width // 2
        if self.rect.top < 0:
            new_y = self.rect.height // 2
        if self.surface.height < self.rect.bottom:
            new_y = self.surface.height - self.rect.height // 2

        self.update_all_position((new_x, new_y))

    def look_around(self,
                    position: pygame.Vector2 | tuple[int, int] | list[int, int],
                    target: Entity = None,
                    buffer: float = 50,
                    follow_speed: float = 1,
                    max_away: float = 100):
        """
        Adjusts the camera's position to be within a certain distance (buffer) of the target's position.

        Args:
            position (pygame.Vector2 | tuple[int, int] | list[int, int]): The position to look around
            target (Entity, optional): The target to look around. Defaults to None.
            buffer (float, optional): The buffer distance to stay away from the target. Defaults to 50.
            follow_speed (float, optional): The speed at which the camera moves. Defaults to 1.
            max_away (float, optional): The maximum distance the camera can be from the target. Defaults to 100.
        """
        target = target if isinstance(target, Entity | pygame.Vector2) else self.main_target
        position = (target.POSITION + pygame.Vector2(position)) - pygame.Vector2(self.rect.size) / 2
        
        self.track(position, speed = follow_speed, max_away = max_away)
        new_x, new_y = self.rect.center

        if self.rect.right < target.rect.right + buffer and self.rect.right < self.surface.width : 
            new_x = target.rect.right - self.rect.width // 2 + buffer
        if target.rect.left < self.rect.left + buffer and 0 < self.rect.left:
            new_x = target.rect.left + self.rect.width // 2 - buffer
        if self.rect.bottom < target.rect.bottom + buffer and self.rect.bottom < self.surface.height :
            new_y = target.rect.bottom - self.rect.height // 2 + buffer
        if target.rect.top < self.rect.top + buffer and 0 < self.rect.top:
            new_y = target.rect.top + self.rect.height // 2 - buffer

        self.update_all_position((new_x, new_y))

    def draw_debug(self):
        """
        Draws a red rectangle around the camera's view and a black circle at the camera's position, for debugging purposes.

        Args:
            None

        Returns:
            None
        """
        pygame.draw.rect(self.surface, (255, 0, 0), self.rect, 10)
        pygame.draw.circle(self.surface, (0, 0, 0), self.POSITION, 20)

    def update_all_position(self,
                            position: pygame.Vector2 | tuple[int, int] | list[int, int]):
        """
        Updates the camera's position and rect attributes to the given position.

        Args:
            position (pygame.Vector2 | tuple[int, int] | list[int, int]): The new position to set the camera to.

        Returns:
            None
        """

        self.x, self.y = self.rect.center = self.POSITION = pygame.Vector2(position)

    def get_mouse_pos(self):
        """
        Returns the current mouse position relative to the camera's position.

        This method calculates the mouse position by adding the current position
        of the mouse within the window to the top-left corner position of the
        camera's view rectangle.

        Returns:
            pygame.Vector2: The mouse position as a vector relative to the camera.
        """
        return pygame.Vector2(self.rect.topleft) + pygame.Vector2(pygame.mouse.get_pos())

def check_input(input_keys: list[tuple[str, int]], 
                event: pygame.event.Event = None) -> bool:
    """
    Check if any of the specified inputs are pressed
    Args:
        input_keys: List of tuples containing ((input_type, key_code), (input_type, key_code))
        event: Optional pygame event to check for KEYDOWN/MOUSEBUTTONDOWN
    Returns:
        bool: True if any input is pressed
    """
    if event:
        for combo in input_keys:

            if not isinstance(combo, tuple | list) or len(combo) != 2:
                continue
            
            input_type, key_code = combo
            if not input_type or not key_code:
                continue

            if input_type == InputType.KEYBOARD and event.type == pygame.KEYDOWN:
                if event.key == key_code:
                    return True
                
            elif input_type == InputType.MOUSE and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == key_code:
                    return True
    else:
        pressed_keys = pygame.key.get_pressed()
        pressed_mouse = pygame.mouse.get_pressed()

        for key_combo in input_keys:
            if not isinstance(key_combo, tuple | list) or len(key_combo) != 2:
                continue

            input_type, key_code = key_combo

            if not input_type or not key_code:
                continue

            if input_type == InputType.KEYBOARD and pressed_keys[key_code]:
                return True
            
            elif input_type == InputType.MOUSE and pressed_mouse[key_code - 1]:
                return True
    return False

class InputFieldText:
    """
    A class representing a text input field with keyboard and mouse input support.
    """
    def __init__(self,
                 position: tuple[int, int],
                 size: tuple[int, int],
                 font: pygame.font.Font,
                 start_text: str = "",
                 max_length: int = 20,
                 inactive_image: pygame.Surface = None,
                 active_image: pygame.Surface = None):
        """
        Initializes an InputFieldText object.

        Args:
            position (tuple[int, int]): The top-left corner of the input field.
            size (tuple[int, int]): The size of the input field.
            font (pygame.font.Font): The font of the input text.
            start_text (str, optional): The initial text in the input field. Defaults to "".
            max_length (int, optional): The maximum length of the text in the input field. Defaults to 20.
            inactive_image (pygame.Surface, optional): The image to display when the input field is inactive. Defaults to None.
            active_image (pygame.Surface, optional): The image to display when the input field is active. Defaults to None.
        """

        self.rect = pygame.Rect(position, size)
        self.font = font
        self.start_text = start_text
        self.text = ""
        self.max_length = max_length
        self.active = False
        self.inactive_image = inactive_image
        self.active_image = active_image

        self.color_inactive = (200, 200, 200)
        self.color_active = (100, 100, 255)
        self.color = self.color_inactive

    def handle_event(self,
                     event: pygame.event.Event) -> str | None:
        """
        Handles events related to the input field.

        If the event is a MOUSEBUTTONDOWN and the mouse is within the input field's rectangle,
        the input field is toggled as active or inactive. If the event is a KEYDOWN and the
        input field is active, the input field processes the key event by appending the key's
        corresponding character to the input field's text, or by removing the last character
        if the key was the backspace key.

        Args:
            event (pygame.event.Event): The event to be processed.

        Returns:
            str | None: The current text in the input field if the return key was pressed, otherwise None.
        """

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.color = self.color_active if self.active else self.color_inactive
            else:
                self.active = False
                self.color = self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.text = ""
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1] if len(self.text) > 0 else ""
            elif len(self.text) < self.max_length:
                self.text += event.unicode

    def draw(self,
             surface: pygame.Surface):
        """
        Draws the input field on the given surface.

        If the input field does not have inactive or active images, it draws a rectangle
        with the current color. Otherwise, it blits the appropriate image depending on the
        active state. Additionally, the text within the input field is rendered and blitted
        onto the surface.

        Args:
            surface (pygame.Surface): The surface on which to draw the input field.
        """
        if not self.inactive_image and not self.active_image:
            pygame.draw.rect(surface, self.color, self.rect, 2)
        else:
            image = self.active_image if self.active else self.inactive_image
            surface.blit(image, self.rect.topleft)
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

class SaveData:
    """
    A class representing save data for a game.
    """
    def __init__(self,
                 filename: str = "save_data.json") -> None:
        """
        Initializes a new SaveData object with the given filename.

        Args:
            filename: The name of the file to store the save data in.
        """
        self.filename = filename
        self.data = self.load()

    def load(self) -> dict:
        """
        Loads the data from the save file.

        If the file exists, it reads the file and returns the data as a dict.
        If the file does not exist, it returns an empty dict.

        Returns:
            dict: The data from the save file.
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        return {}
    
    def save(self) -> None:
        """
        Saves the data to the save file.

        This method writes the current data dictionary to the save file in
        JSON format, with indentation of 4 spaces.

        Returns:
            None
        """
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        data = self.data
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def set_value(self,
                  dict: dict) -> None:
        """
        Sets the current data dictionary to the given dictionary.

        This method is used to set the data of the SaveData object to a new dictionary.
        The given dictionary is not copied, so any changes to the dictionary after
        calling this method will affect the data of the SaveData object.

        Args:
            dict (dict): The dictionary to use as the new data.
            """
        self.data = dict

    def reload(self) -> None:
        """
        Reloads the data from the save file.

        This method is used to reload the data from the save file after the
        save file has been modified. The data of the SaveData object is
        replaced with the data loaded from the file.

        Returns:
            None
        """
        self.data = self.load()

class DialogBox:
    """
    A class representing a dialog box.
    """
    def __init__(self,
                 surface: pygame.Surface,
                 font: pygame.font.Font,
                 width: int = None,
                 height: int = 150,
                 sound: pygame.mixer.Sound = None):
        """
        Initializes a DialogBox object.

        Args:
            surface (pygame.Surface): The surface to draw the dialog box on.
            font (pygame.font.Font): The font to use for the text in the dialog box.
            width (int, optional): The width of the dialog box. Defaults to None.
            height (int, optional): The height of the dialog box. Defaults to 150.
            sound (pygame.mixer.Sound, optional): The sound to play when the dialog box is shown. Defaults to None.

        Attributes:
            surface (pygame.Surface): The surface to draw the dialog box on.
            font (pygame.font.Font): The font to use for the text in the dialog box.
            screen_width (int): The width of the screen.
            screen_height (int): The height of the screen.
            box_width (int): The width of the dialog box.
            box_height (int): The height of the dialog box.
            box_rect (pygame.Rect): The rectangle of the dialog box.
            active (bool): Whether the dialog box is currently active.
            full_text (str): The full text of the dialog box.
            visible_text (str): The currently visible text of the dialog box.
            char_index (int): The index of the current character in the text.
            text_speed (int): The speed of the text in chars per frame.
            sound (pygame.mixer.Sound): The sound to play when the dialog box is shown.
            skipable (bool): Whether the dialog box can be skipped.
            on_finish (callable): The function to call when the dialog box is finished.
            frame_counter (int): The number of frames the dialog box has been active.
            finished (bool): Whether the dialog box has finished showing the text.
        """
        self.surface = surface
        self.font = font
        self.screen_width = surface.get_width()
        self.screen_height = surface.get_height()
        self.box_width = width if width else self.screen_width - 40
        self.box_height = height
        self.box_rect = pygame.Rect(
            (self.screen_width - self.box_width) // 2,
            self.screen_height - self.box_height - 20,
            self.box_width,
            self.box_height
        )

        self.active = False
        self.full_text = ""
        self.visible_text = ""
        self.char_index = 0
        self.text_speed = 1  # chars per frame
        self.sound = sound
        self.skipable = True
        self.on_finish = None

        self.frame_counter = 0
        self.finished = False

    def show(self,
             message: str,
             skipable: bool = True,
             on_finish: callable = None):
        """
        Shows the dialog box with the given message.

        Args:
            message (str): The text to display in the dialog box.
            skipable (bool, optional): Whether the dialog box can be skipped. Defaults to True.
            on_finish (callable, optional): A function to call after the dialog box has finished showing the text. Defaults to None.
        """
        self.full_text = message
        self.visible_text = ""
        self.char_index = 0
        self.frame_counter = 0
        self.skipable = skipable
        self.active = True
        self.on_finish = on_finish
        self.finished = False

    def handle_event(self, event):
        """
        Handles user input events related to the dialog box.

        If the dialog box is active, this method will check for key or mouse button
        events. If the dialog box is skippable or finished, it will either fast-forward
        the text display or close the dialog box.

        Args:
            event (pygame.event.Event): The event to handle.
        """
        if not self.active:
            return

        if self.skipable or self.finished:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if not self.finished:
                    self.char_index = len(self.full_text)
                    self.visible_text = self.full_text
                else:
                    self.close()

    def update(self):
        """
        Updates the state of the dialog box.

        If the dialog box is active and not finished, this method will increment a
        frame counter and check if it has reached the text speed. If it has, it will
        increment the character index and update the visible text. If the character
        index has reached the length of the full text, it will set the finished flag
        to True.

        Args:
            None

        Returns:
            None
        """
        if not self.active or self.finished:
            return

        self.frame_counter += 1
        if self.frame_counter >= self.text_speed:
            self.frame_counter = 0
            if self.char_index < len(self.full_text):
                self.char_index += 1
                self.visible_text = self.full_text[:self.char_index]
                if self.sound:
                    self.sound.play()
            else:
                self.finished = True

    def draw(self):
        """
        Draws the dialog box on the given surface.

        If the dialog box is active, this method will draw a black rectangle with a
        white border and render the visible text on it. If the dialog box is
        finished or has a skipable flag, it will also render a hint text on the
        bottom right of the box.

        Args:
            None

        Returns:
            None
        """
        if not self.active:
            return

        pygame.draw.rect(self.surface, (30, 30, 30), self.box_rect, border_radius=10)
        pygame.draw.rect(self.surface, (200, 200, 200), self.box_rect, 2, border_radius=10)

        words = self.visible_text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.font.size(test_line)[0] < self.box_width - 40:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        for i, text in enumerate(lines[:5]):
            render = self.font.render(text, True, (255, 255, 255))
            self.surface.blit(render, (self.box_rect.x + 20, self.box_rect.y + 20 + i * 30))

        if self.skipable or self.finished:
            hint = self.font.render("Press any key to continue...", True, (200, 200, 200))
            self.surface.blit(hint, (self.box_rect.right - 240, self.box_rect.bottom - 30))

    def close(self):
        """
        Closes the dialog box and runs its on_finish callback if it exists.

        The active flag is set to False, and if the on_finish callback exists, it is
        called. This method is called when the dialog box is finished, or when the
        user presses any key to skip the dialog box if it is skipable.
        """
        self.active = False
        if self.on_finish:
            self.on_finish()

class Button:
    """
    A class representing a button."""
    def __init__(self,
                 image: pygame.Surface = None,
                 text: str = "",
                 center_x: int = 0,
                 center_y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 border_radius: int = 10,
                 callback: callable = None,
                 font: pygame.font.Font = None):
        """
        Initializes a Button instance with the specified attributes.

        Args:
            image (pygame.Surface, optional): The image to display on the button. Defaults to None.
            text (str, optional): The text to display on the button. Defaults to an empty string.
            center_x (int, optional): The x-coordinate of the button's center. Defaults to 0.
            center_y (int, optional): The y-coordinate of the button's center. Defaults to 0.
            width (int, optional): The width of the button. Defaults to 0.
            height (int, optional): The height of the button. Defaults to 0.
            border_radius (int, optional): The radius of the button's border corners. Defaults to 10.
            callback (callable, optional): The function to call when the button is pressed. Defaults to None.
            font (pygame.font.Font, optional): The font to use for rendering text. Defaults to None, which uses a default font.

        Attributes:
            image (pygame.Surface): The image displayed on the button.
            text (str): The text displayed on the button.
            rect (pygame.Rect): The rectangle defining the button's position and size.
            border_radius (int): The radius of the button's border corners.
            callback (callable): The function to call when the button is pressed.
            color (tuple[int, int, int]): The color of the button.
            font (pygame.font.Font): The font used for rendering text on the button.
        """

        self.image = image
        self.text = text
        self.rect = self.image.get_rect() if image else pygame.Rect(center_x, center_y, width, height)
        self.border_radius = border_radius
        self.rect.center = (center_x, center_y) 
        self.callback = callback
        self.color = (50, 50, 50)
        self.font = font if font else pygame.font.SysFont(None, 48)

    def draw(self, screen: pygame.Surface):
        """
        Draws the button on the given screen surface.

        If an image is provided for the button, it will be blitted onto the screen
        at the button's top-left corner. Otherwise, a rectangle with the button's
        color and border radius will be drawn. The button's text is rendered and
        centered within the rectangle.

        Args:
            screen (pygame.Surface): The surface on which to draw the button.
        """
        if self.image:
            screen.blit(self.image, self.rect.topleft)
            return
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=self.border_radius)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event) -> bool:
        """
        Handles events related to the button.

        This method updates the button's color when the mouse moves over it and
        triggers the button's callback function if the button is clicked.

        Args:
            event (pygame.event.Event): The event to be processed.

        Returns:
            bool: True if the button was clicked and a callback was executed,
                otherwise False.
        """
        if event.type == pygame.MOUSEMOTION:
            self.color = (150, 150, 150) if self.rect.collidepoint(event.pos) else (50, 50, 50)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                    return True
        return False
    
def  a_star(
    start: pygame.Vector2,
    target: pygame.Rect,
    blocking: list[pygame.FRect],
    max_distance: int = 1000,
    grid_size: int = 32,
    buffer: tuple[int, int] = (30, 20)
) -> list[pygame.Vector2]:
    """
    Performs A* pathfinding centered around the enemy's position.
    """
    try:
        width = (max_distance * 2) // grid_size
        height = (max_distance * 2) // grid_size

        offset_x = start.x - max_distance
        offset_y = start.y - max_distance
        
        matrix = np.ones((height, width), dtype=int)

        for block in blocking:
            block_x1 = max(0, int((block.left - offset_x - buffer[0]) / grid_size))
            block_y1 = max(0, int((block.top - offset_y - buffer[1]) / grid_size))
            block_x2 = min(width - 1, int((block.right - offset_x + buffer[0]) / grid_size))
            block_y2 = min(height - 1, int((block.bottom - offset_y + buffer[1]) / grid_size))

            if block_x1 <= block_x2 and block_y1 <= block_y2:
                matrix[block_y1:block_y2 + 1, block_x1:block_x2 + 1] = 0

        grid = Grid(matrix=matrix)

        start_x = int((start.x - offset_x) / grid_size)
        start_y = int((start.y - offset_y) / grid_size)
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