import pygame
import sys
from modules.General.functions import SaveData
from modules.General.globals import changeable_values

class Slider:
    def __init__(self,
                 label: str,
                 value: int,
                 center_pos: tuple[int, int],
                 multiplier: float = 2,
                 font: pygame.font.Font = None):
        self.label = label
        self.value = value
        self.width = 200
        self.height = 10
        self.multiplier = multiplier
        self.rect = pygame.Rect(center_pos[0] - (self.width // 2) * multiplier,
                                center_pos[1] - (self.height // 2) * multiplier,
                                self.width * multiplier,
                                self.height * multiplier)
        self.knob_radius = 8 * multiplier
        self.knob_x = self.rect.left + (self.value / 100) * self.rect.width
        self.dragging = False
        self.input_box = pygame.Rect(self.rect.right + 20, self.rect.top - 10 * multiplier, 50 * multiplier, 30 * multiplier)
        self.text = str(value)
        self.active = False
        self.original_value = str(value)
        self.font = font if font else pygame.font.SysFont("Arial", 20, bold=True)

    def handle_event(self,
                     event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                if not self.active:
                    self.text = ""
                self.active = True
            else:
                self.try_commit_text()
                self.active = False

            knob_rect = pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius,
                                    self.knob_radius * 2, self.knob_radius * 2)

            if self.rect.collidepoint(event.pos):
                self.knob_x = max(self.rect.left, min(event.pos[0], self.rect.right))
                self.value = int(((self.knob_x - self.rect.left) / self.rect.width) * 100)
                self.text = str(self.value)

            if knob_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.knob_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.value = int(((self.knob_x - self.rect.left) / self.rect.width) * 100)
            self.text = str(self.value)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode
            self.try_commit_text()

    def try_commit_text(self):
        try:
            val = int(self.text) if self.text else 0
            self.value = max(0, min(100, val))
            self.text = str(self.value)
            self.knob_x = self.rect.left + (self.value / 100) * self.rect.width
        except ValueError:
            self.text = str(self.value)
            

    def draw(self,
             surface: pygame.Surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect)
        pygame.draw.circle(surface, (20, 220, 220) if self.dragging else (21, 72, 137), (int(self.knob_x), self.rect.centery), self.knob_radius)

        label_surface = self.font.render(f"{self.label}", True, (255, 255, 255))
        surface.blit(label_surface, (self.rect.left - 120, self.rect.top))

        pygame.draw.rect(surface, (160, 160, 255) if self.active else (200, 200, 200), self.input_box, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), self.input_box, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surface, (self.input_box.x + 15 * self.multiplier, self.input_box.y + 18))

    def get_value(self):
        self.try_commit_text()
        return self.value
    

class SoundMenu:
    def __init__(self,
                 screen: pygame.Surface,
                 audio_settings: dict[str, int] = {"GENERAL": 1, "SFX": 1, "MUSIC": 1, "DIALOG": 1}):
        self.saver = SaveData(changeable_values.DEFAULT_PATH + r"/assets/saved_datas/sound.json")
        self.settings = self.saver.data if self.saver.data != {} else audio_settings
        for key, value in self.settings.items():
            self.settings[key] = int(value * 100)
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 20)
        self.sliders: list[Slider] = []

        multiplier = 2
        slider_height = 50 * multiplier
        total_height = len(self.settings) * slider_height
        for i, (key, val) in enumerate(self.settings.items()):
            y = (self.screen.height - total_height) // 2 + i * slider_height
            self.sliders.append(Slider(key, val, (self.screen.width // 2, y), multiplier=multiplier))

    def cleanup(self):
        for slider in self.sliders:
            slider.try_commit_text()
            self.settings[slider.label] = slider.get_value() / 100 if slider.get_value() != 0 else 0
        self.saver.set_value(self.settings)
        self.saver.save()
        changeable_values.GENERAL_VOLUME = self.settings["GENERAL"]
        changeable_values.SFX_VOLUME = self.settings["SFX"]
        changeable_values.MUSIC_VOLUME = self.settings["MUSIC"]
        changeable_values.DIALOGUE_VOLUME = self.settings["DIALOG"]

    def run(self):
        running = True
        while running:
            self.screen.fill((25, 25, 25))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cleanup()
                        running = False

                for slider in self.sliders:
                    slider.handle_event(event)

            for slider in self.sliders:
                slider.draw(self.screen)

            self.screen.blit(pygame.font.SysFont("Arial", 20, bold=True).render("ESC TO GET BACK", True, (255, 0, 0)), (5, self.screen.height - 30))
            pygame.display.flip()
