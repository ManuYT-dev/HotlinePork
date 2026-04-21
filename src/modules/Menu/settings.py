import pygame
import sys
from modules.General.globals import changeable_values, PLAYER_STATS
from modules.Menu.controlls_settings import ControllsMenu
from modules.Menu.sound_settings import SoundMenu
from modules.Menu.player_stats import StatsDisplay
from modules.General.functions import Button, SaveData

class SettingsMenu:
    def __init__(self,
                 keybinds: dict,
                 screen: pygame.Surface):
        self.screen = screen
        self.keybinds = keybinds
        self.load_stats = SaveData(changeable_values.SAVE_PATH + r"/assets/saved_datas/player_stats.json")
        PLAYER_STATS.player_stats = self.load_stats.load() if self.load_stats.load() != {} else PLAYER_STATS.player_stats
        self.keybind_menu = ControllsMenu(self.keybinds, self.screen)
        self.keybind_button = Button(text="Keybinds", center_x=self.screen.get_width() // 2, center_y=150, width=400, height=120, callback=self.keybind_menu.run)
        self.sound_menu = SoundMenu(self.screen)
        self.sound_button = Button(text="Sound", center_x=self.screen.get_width() // 2, center_y=350, width=400, height=120, callback=self.sound_menu.run)
        self.stats_display = StatsDisplay(self.screen)
        self.stats_button = Button(text="Statistics", center_x=self.screen.get_width() // 2, center_y=550, width=400, height=120, callback=self.stats_display.run)


    def run(self):
        running = True
        PLAYER_STATS.player_stats = self.load_stats.load() if self.load_stats.load() != {} else PLAYER_STATS.player_stats
        while running:
            self.screen.fill((100, 100, 100))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                self.keybind_button.handle_event(event)
                self.sound_button.handle_event(event)
                self.stats_button.handle_event(event)
            self.keybind_button.draw(self.screen)
            self.sound_button.draw(self.screen)
            self.stats_button.draw(self.screen)
            self.screen.blit(pygame.font.SysFont("Arial", 20, bold=True).render("ESC TO GET BACK", True, (255, 0, 0)), (5, self.screen.height - 30))
            pygame.display.flip()