import pygame
from modules.General.globals import PLAYER_STATS
import sys

class StatsDisplay:
    def __init__(self,
                 screen: pygame.Surface):
        self.screen = screen
        self.stats = PLAYER_STATS.player_stats
        self.font = pygame.font.SysFont("Courier", 32, True)
        self.title_font = pygame.font.SysFont("Courier", 48, True)
        self.padding = 40

    def draw(self):
        self.screen.fill((30, 30, 30))
        title = self.title_font.render("GAME STATISTICS", True, (255, 255, 0))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 50))

        y_offset = 150
        for key, value in self.stats.items():
            display_value = f"{value:.2f}" if isinstance(value, float) else str(value)
            stat_text = f"{key}: {display_value}"
            text_surf = self.font.render(stat_text, True, (255, 255, 255))
            self.screen.blit(text_surf, (self.padding, y_offset))
            y_offset += self.font.get_height() + 20

        pygame.display.flip()

    def run(self):
        self.__init__(self.screen)
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
