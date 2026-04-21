import pygame

SCREEN_FLAGS = pygame.DOUBLEBUF | pygame.OPENGL
TILE_SIZE: int = 64
SCREEN_STRETCH: tuple[int, int] = (9, 16)
SCREEN_SIZE: tuple[int, int] = (1200, int(1200 * SCREEN_STRETCH[0] / SCREEN_STRETCH[1]))

class changeable_values:
    PLAYER_SPEED: float = 1
    DEFAULT_PATH: str = ""
    SAVE_PATH: str = ""
    SCREEN: pygame.Surface = None
    GENERAL_VOLUME: int = 1
    SFX_VOLUME: int = 1
    MUSIC_VOLUME: int = 1
    DIALOGUE_VOLUME: int = 1

class ACHIEVEMENTS:
    all_achievements = {"Wrong Number?": ("Complete 10 Waves", False),
                        "Hog of War": ("Complete 50 Waves", False),
                        "Pigs Fly Now": ("Complete 100 Waves", False),
                        "Tim Cheese Will Remember That": ("Finish the Tutorial", False),
                        "Slice to Meet You": ("Kill 25 Tim Cheeses", False),
                        "Grate Expectations": ("Kill 50 Tim Cheeses", False),
                        "I am Truly worried about your Mental Health":("Kill 100 Tim Cheeses", False)}
    @staticmethod
    def update_achievements(all_achievements: dict[str, tuple[str, bool]]):
        ACHIEVEMENTS.all_achievements = all_achievements

class PLAYER_STATS:
    player_stats = {"HIGHEST WAVE": 0,
                    "TOTAL WAVES": 0,
                    "LONGEST SURVIVED": 0,
                    "TOTAL PLAYTIME": 0,
                    "MOST KILLS": 0,
                    "TOTAL KILLS": 0}

    @staticmethod
    def update_player_stats(player_stats: dict[str, int]):
        PLAYER_STATS.player_stats = player_stats