import pygame
import sys
from modules.General.controlls import ALL_KEYS
from modules.General.globals import SCREEN_SIZE, changeable_values, ACHIEVEMENTS
from modules.Menu.settings import SettingsMenu
from modules.General.functions import Button, SaveData
from modules.Levels.tutorial import Tutorial
from modules.Levels.endless import ENDLESS


class Modes:
    def __init__(self):
        self.tutorial = Tutorial()
        self.endless = ENDLESS()
        self.all_modes = [self.tutorial, self.endless]

import pygame
import sys

def title_screen(image_path: str,
                 screen: pygame.Surface):
    background = pygame.image.load(image_path).convert()
    background = pygame.transform.scale(background, screen.get_size())

    font = pygame.font.SysFont("Arial", 60, bold=True)
    prompt_text = font.render("Press any key to continue...", True, (255, 255, 255))
    prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))

    waiting = True
    while waiting:
        screen.blit(background, (0, 0))
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False


# CHATGPT PROMPT: create a achievements menu where the input is a dict like this {achievement_name: (description, completed) it should have different colors if completed and not completed lighter if completed and if the achievement isnt unlocked the description is just 3 question marks
def show_achievements_menu(achievements: dict,
                           screen: pygame.Surface):
    font_title = pygame.font.SysFont("Arial", 36, bold=True)
    font_entry = pygame.font.SysFont("Arial", 24)

    bg_color = (30, 30, 30)
    box_color_completed = (80, 160, 80)
    box_color_locked = (60, 60, 60)
    text_color = (255, 255, 255)

    screen_width, screen_height = screen.get_size()
    padding = 20
    box_height = 80
    spacing = 20

    total_height = len(achievements) * (box_height + spacing)
    scroll_y = 0
    scroll_speed = 20

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(bg_color)

        title_text = font_title.render("Achievements", True, text_color)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 20))

        scroll_area_height = max(screen_height, total_height + 100)
        scroll_area = pygame.Surface((screen_width, scroll_area_height), pygame.SRCALPHA)
        scroll_area.fill((0, 0, 0, 0))

        for idx, (name, (desc, completed)) in enumerate(achievements.items()):
            y = 100 + idx * (box_height + spacing)
            box_rect = pygame.Rect(padding, y, screen_width - 2 * padding, box_height)

            color = box_color_completed if completed else box_color_locked
            display_desc = desc if completed else "???"

            pygame.draw.rect(scroll_area, color, box_rect, border_radius=10)

            name_text = font_entry.render(name, True, text_color)
            desc_text = font_entry.render(display_desc, True, text_color)

            scroll_area.blit(name_text, (box_rect.x + 15, box_rect.y + 10))
            scroll_area.blit(desc_text, (box_rect.x + 15, box_rect.y + 40))

        visible_rect = pygame.Rect(0, scroll_y, screen_width, screen_height - 60)
        screen.blit(scroll_area, (0, 80), area=visible_rect)

        esc_text = font_entry.render("Press ESC to return | Scroll with mouse or arrow keys", True, (180, 180, 180))
        screen.blit(esc_text, (padding, screen_height - 30))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(scroll_y + scroll_speed, max(0, scroll_area_height - (screen_height - 60)))
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - scroll_speed)

            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = max(0, min(scroll_y - event.y * scroll_speed, scroll_area_height - (screen_height - 60)))
# CHATGPT END


def show_credits_menu(screen: pygame.Surface,
                      image_path: str):
    image = pygame.transform.scale(pygame.image.load(image_path).convert(), screen.size)
    an = True
    while an:
        screen.blit(image)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                an = False
        pygame.display.flip()


def check_achievements(input_dict: dict):
    if input_dict != {}:
        waves = input_dict["TOTAL WAVES"]
        kills = input_dict["TOTAL KILLS"]
        if 10 <= waves:
            ACHIEVEMENTS.all_achievements["Wrong Number?"] = ("Complete 10 Waves", True)
        if 50 <= waves:
            ACHIEVEMENTS.all_achievements["Hog of War"] = ("Complete 50 Waves", True)
        if 100 <= waves:
            ACHIEVEMENTS.all_achievements["Pigs Fly Now"] = ("Complete 100 Waves", True)
        if 25 <= kills:
            ACHIEVEMENTS.all_achievements["Slice to Meet You"] = ("Kill 25 Tim Cheeses", True)
        if 50 <= kills:
            ACHIEVEMENTS.all_achievements["Grate Expectations"] = ("Kill 50 Tim Cheeses", True)
        if 100 <= kills:
            ACHIEVEMENTS.all_achievements["I am Truly worried about your Mental Health"] = ("Kill 100 Tim Cheeses", True)

class MainMenuApp:
    def __init__(self):
        self.savedata_achievements = SaveData(changeable_values.SAVE_PATH + r"/assets/saved_datas/Achievements.json")
        self.savedate_statistics = SaveData(changeable_values.SAVE_PATH + r"/assets/saved_datas/player_stats.json")
        self.savedata_sound = SaveData(changeable_values.SAVE_PATH + r"/assets/saved_datas/sound.json")
        ACHIEVEMENTS.all_achievements = self.savedata_achievements.load() if self.savedata_achievements.load() != {} else ACHIEVEMENTS.all_achievements

        changeable_values.GENERAL_VOLUME = self.savedata_sound.load()["GENERAL"] if self.savedata_sound.load() != {}  else changeable_values.GENERAL_VOLUME
        changeable_values.MUSIC_VOLUME = self.savedata_sound.load()["MUSIC"] if self.savedata_sound.load() != {}  else changeable_values.MUSIC_VOLUME
        changeable_values.SFX_VOLUME = self.savedata_sound.load()["SFX"] if self.savedata_sound.load() != {}  else changeable_values.SFX_VOLUME

        self.settings_menu = SettingsMenu(ALL_KEYS, changeable_values.SCREEN)
        self.background = pygame.transform.scale(pygame.image.load(changeable_values.DEFAULT_PATH + r"/assets/designs/Titlescreen.png").convert(), changeable_values.SCREEN.size)
        self.button_spritesheet = self.load_button_spritesheet(
            spritesheet_path=changeable_values.DEFAULT_PATH + r"/assets/designs/Buttons.png",
            start_width=100,
            start_height=45,
            final_width=200,
            final_height=90
        )
        self.modes = Modes()

    def load_button_spritesheet(self, spritesheet_path, start_width, start_height, final_width, final_height):
        spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        return {
            str(i): pygame.transform.scale(
                spritesheet.subsurface(pygame.Rect(i * start_width, 0, start_width, start_height)),
                (final_width, final_height)
            )
            for i in range(spritesheet.get_width() // start_width)
        }
    
    def mode_update(self):
        for mode in self.modes.all_modes:
            if mode.completed:
                mode.__init__()

    def choose_mode(self):
        mode_map = {
            "Tutorial": self.modes.tutorial.run,
            "Endless": self.modes.endless.run
        }

        abstand = 50
        width_each = (SCREEN_SIZE[0] - (len(mode_map) + 1) * abstand) // len(mode_map)

        buttons = [
            Button(text=name,
                   center_x=0,
                   center_y=0,
                   width=width_each,
                   height=width_each,
                   callback=callback)
            for name, callback in mode_map.items()
        ]

        for idx, button in enumerate(buttons):
            button.rect.left = (idx + 1) * abstand + idx * width_each
            button.rect.top = SCREEN_SIZE[1] // 2 - width_each // 2

        mode_running = True
        while mode_running:
            self.mode_update()
            changeable_values.SCREEN.fill((100, 100, 100))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for button in buttons:
                    finished = button.handle_event(event)
                    if finished:
                        mode_running = False
                        self.savedata_achievements.set_value(ACHIEVEMENTS.all_achievements)
                        self.savedata_achievements.save()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    mode_running = False

            for button in buttons:
                button.draw(changeable_values.SCREEN)

            escape_info = pygame.font.SysFont("Arial", 20, bold=True).render("ESC TO GET BACK", True, (255, 0, 0))
            changeable_values.SCREEN.blit(escape_info, (5, changeable_values.SCREEN.get_height() - 30))
            pygame.display.flip()

    def run(self):
        def start_game():
            self.choose_mode()

        def open_options():
            self.settings_menu.run()

        def open_credits():
            show_credits_menu(changeable_values.SCREEN,
                              changeable_values.DEFAULT_PATH + r"/assets/designs/credits.png")

        def open_achievements():
            check_achievements(self.savedate_statistics.load())
            show_achievements_menu(ACHIEVEMENTS.all_achievements,
                                     changeable_values.SCREEN)

        def quit_game():
            pygame.quit()
            sys.exit()

        buttons = [
            Button(image=self.button_spritesheet["0"], center_x=SCREEN_SIZE[0]//2, center_y=200, callback=start_game),
            Button(image=self.button_spritesheet["1"], center_x=SCREEN_SIZE[0]//2, center_y=300, callback=open_options),
            Button(image=self.button_spritesheet["2"], center_x=SCREEN_SIZE[0]//2, center_y=400, callback=open_credits),
            Button(image=self.button_spritesheet["3"], center_x=SCREEN_SIZE[0]//2, center_y=600, callback=quit_game),
            Button(image=self.button_spritesheet["4"], center_x=SCREEN_SIZE[0]//2, center_y=500, callback=open_achievements),
        ]
        
        title_screen(changeable_values.DEFAULT_PATH + r"/assets/designs/Titlescreen.png", changeable_values.SCREEN)
        running = True
        while running:
            pygame.display.set_caption("HOTLINE PORK")
            changeable_values.SCREEN.blit(self.background)
            self.mode_update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                for button in buttons:
                    button.handle_event(event)

            for button in buttons:
                button.draw(changeable_values.SCREEN)

            pygame.display.flip()

        pygame.quit()
