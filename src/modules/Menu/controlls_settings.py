import pygame
import sys
import copy
from modules.General.types import InputType
from modules.General.functions import SaveData
from modules.General.globals import changeable_values
from modules.General.controlls import DEFAULT_KEYS, update_all_keys

class ControllsMenu:
    """
    A class for the controlls menu.
    
    Args:
        keybinds (dict): A dictionary containing the current keybinds for each action.
        surface (pygame.Surface): The surface on which the menu is displayed.
        default_keybinds (dict, optional): A dictionary containing the default keybinds for each action.
        saving_file_path (str, optional): The path to the file where the keybinds are saved.

    Attributes:
        font (pygame.font.Font): The font used for the menu text.
        big_font (pygame.font.Font): The font used for the title text.
        screen_height (int): The height of the screen.
        screen_width (int): The width of the screen.
        screen (pygame.Surface): The surface on which the menu is displayed.
        running (bool): A flag indicating whether the menu is currently running.
        keybinds (dict): A dictionary containing the current keybinds for each action.
        default_keybinds (dict): A dictionary containing the default keybinds for each action.
        actions (list): A list of all the actions in the menu.
        selected_index (int): The index of the currently selected action.
        rebinding (bool): A flag indicating whether a key is currently being rebound.
        rebind_step (int): The step of the key rebinding process.
        new_keys (list): A list containing the new keys for the currently rebinding action.
        scroll_offset (int): The offset used for scrolling the menu.        
        item_height (int): The height of each item in the menu.
        margin (int): The margin between items in the menu.
        visible_area (int): The height of the visible area of the menu.
        scroll_speed (int): The speed at which the menu scrolls.        
        reset_rect (pygame.Rect): The rectangle for the reset button.
        confirm_reset (bool): A flag indicating whether the user is confirming the reset.
    
    Methods:
        update_keybinds(): Updates the keybinds dictionary with the new keybinds.
        draw(): Draws the menu on the screen.
        handle_events(event): Handles user input events.
        handle_rebind(event): Handles the key rebinding process.
        handle_keydown(event): Handles key down events.
        handle_keyup(event): Handles key up events.
        reset_keybinds(): Resets the keybinds dictionary to the default keybinds.
        save_keybinds(): Saves the keybinds dictionary to a file.
        ensure_visible(): Ensures that the currently selected action is visible in the menu.
    """
    def __init__(self,
                 keybinds: dict,
                 surface: pygame.Surface,
                 default_keybinds: dict = DEFAULT_KEYS,
                 saving_file_path=None):
        if saving_file_path is None:
            saving_file_path = changeable_values.SAVE_PATH + r"/assets/saved_datas/controlls.json"
            
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.screen_height = surface.get_height()
        self.screen_width = surface.get_width()
        self.screen = surface
        self.running = True

        self.saving_data = SaveData(saving_file_path)
        self.keybinds = keybinds  # Format: {"Action": [("keyboard", pygame.K_*), ("mouse", 1)]}
        self.default_keybinds = default_keybinds
        self.actions = list(self.keybinds.keys())
        self.selected_index = 0
        self.rebinding = False
        self.rebind_step = 0
        self.new_keys = [None, None]
        self.scroll_offset = 0
        self.action_rects = []

        self.item_height = 50
        self.margin = 10
        self.visible_area = self.screen_height - 100
        self.scroll_speed = 30

        self.reset_rect = pygame.Rect(self.screen_width - 110, self.screen_height - 50, 100, 40)
        self.confirm_reset = False

    def get_key_display(self, input_pair):
        if input_pair is None:
            return "-"
        
        input_type, value = input_pair
        if input_type == InputType.KEYBOARD:
            return pygame.key.name(value).upper()
        
        elif input_type == InputType.MOUSE:
            return f"MOUSE{value}"
        
        return "UNKNOWN"

    def draw(self):
        self.screen.fill((25, 25, 25))
        start_y = 50 - self.scroll_offset
        self.action_rects = []

        for i, action in enumerate(self.actions):
            is_selected = (i == self.selected_index)
            bg_color = (45, 45, 45)
            text_color = (255, 255, 255)
            highlight_color = (200, 200, 50) if is_selected else bg_color

            key1, key2 = self.keybinds[action]
            label = f"{action}: {self.get_key_display(key1)} or {self.get_key_display(key2)}"
            render = self.font.render(label, True, text_color)

            rect_width = 500
            rect_height = self.item_height
            rect_x = (self.screen_width - rect_width) // 2
            rect_y = start_y + i * (rect_height + self.margin)

            rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
            self.action_rects.append(rect)

            pygame.draw.rect(self.screen, highlight_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=8)

            text_rect = render.get_rect(center=rect.center)
            self.screen.blit(render, text_rect)

            pygame.draw.rect(self.screen, (150, 50, 50), self.reset_rect, border_radius=6)
            reset_text = self.font.render("Reset", True, (255, 255, 255))
            self.screen.blit(reset_text, reset_text.get_rect(center=self.reset_rect.center))

        if self.rebinding:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            action = self.actions[self.selected_index]
            msg = f"Press key/mouse #{self.rebind_step + 1}"
            render_action = self.big_font.render(f"Rebinding: {action}", True, (255, 255, 255))
            render_msg = self.big_font.render(msg, True, (100, 255, 100))

            self.screen.blit(render_action, render_action.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 40)))
            self.screen.blit(render_msg, render_msg.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20)))

        if self.confirm_reset:
            popup = pygame.Surface((400, 200))
            popup.fill((30, 30, 30))
            pygame.draw.rect(popup, (255, 255, 255), popup.get_rect(), 2)

            msg = self.font.render("Reset keybinds to default?", True, (255, 255, 255))
            yes_btn = pygame.Rect(100, 130, 80, 40)
            no_btn = pygame.Rect(220, 130, 80, 40)
            pygame.draw.rect(popup, (0, 150, 0), yes_btn)
            pygame.draw.rect(popup, (150, 0, 0), no_btn)

            popup.blit(msg, msg.get_rect(center=(200, 60)))
            popup.blit(self.font.render("Yes", True, (255, 255, 255)), yes_btn.move(20, 10))
            popup.blit(self.font.render("Cancel", True, (255, 255, 255)), no_btn.move(10, 10))

            self.screen.blit(popup, popup.get_rect(center=(self.screen_width // 2, self.screen_height // 2)))
            self.popup_yes = yes_btn.move((self.screen_width - 400) // 2, (self.screen_height - 200) // 2)
            self.popup_no = no_btn.move((self.screen_width - 400) // 2, (self.screen_height - 200) // 2)
        self.screen.blit(pygame.font.SysFont("Arial", 20, bold=True).render("ESC TO GET BACK", True, (255, 0, 0)), (5, self.screen.height - 30))
        pygame.display.flip()

    def handle_keydown(self, event):
        if self.rebinding:
            if event.key == pygame.K_ESCAPE:
                self.rebinding = False
                self.rebind_step = 0
                self.save_rebinding()
                return
            
            self.new_keys[self.rebind_step] = ("keyboard", event.key)
            self.rebind_step += 1
            if self.rebind_step >= 2:
                self.save_rebinding()
            return
        
        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_BACKSPACE:
            self.running = False

        elif event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.actions)
            self.ensure_visible()

        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.actions)
            self.ensure_visible()

        elif event.key == pygame.K_RETURN:
            self.start_rebinding()

    def handle_mouse_click(self, pos, button):
        if self.rebinding:
            self.new_keys[self.rebind_step] = ("mouse", button)
            self.rebind_step += 1

            if self.rebind_step >= 2:
                self.save_rebinding()
            return
        
        if self.confirm_reset:
            if self.popup_yes.collidepoint(pos):
                self.keybinds = copy.deepcopy(self.default_keybinds)
                self.confirm_reset = False
                self.saving_data.set_value(self.keybinds)
                self.saving_data.save()
                
            elif self.popup_no.collidepoint(pos):
                self.confirm_reset = False
            return

        for i, rect in enumerate(self.action_rects):
            if rect.collidepoint(pos):
                self.selected_index = i
                self.start_rebinding()
                break

        if self.reset_rect.collidepoint(pos):
            self.confirm_reset = True
            return

    def handle_mouse_wheel(self, y_scroll):
        max_scroll = max(0, len(self.actions) * (self.item_height + self.margin) - self.visible_area)
        self.scroll_offset = max(0, min(self.scroll_offset - y_scroll * self.scroll_speed, max_scroll))

    def ensure_visible(self):
        target_top = self.selected_index * (self.item_height + self.margin)
        target_bottom = target_top + self.item_height

        if target_top - self.scroll_offset < 0:
            self.scroll_offset = target_top

        elif target_bottom - self.scroll_offset > self.visible_area:
            self.scroll_offset = target_bottom - self.visible_area

    def start_rebinding(self):
        self.rebinding = True
        self.new_keys = [None, None]
        self.rebind_step = 0

    def save_rebinding(self):
        self.keybinds[self.actions[self.selected_index]] = list(self.new_keys)
        self.rebinding = False
        self.rebind_step = 0

    def run(self):
        self.running = True
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [4, 5]:
                        self.handle_mouse_wheel(1 if event.button == 4 else -1)

                    else:
                        self.handle_mouse_click(event.pos, event.button)
        self.saving_data.set_value(self.keybinds)
        self.saving_data.save()
        update_all_keys(self.keybinds)
