from modules.General.globals import changeable_values
from modules.General.types import Entity
from modules.Entitys.imports import Weapon
import pygame

class WeaponLoader:
    """
    A class for loading and creating weapons."""
    def __init__(self,
                 screen: pygame.Surface = None,
                 blocking: list[pygame.FRect] = [],
                 targets: Entity = None):
        """
        Initializes a weapon loader with the specified parameters.

        Args:
            screen (pygame.Surface): The surface on which the weapons will be drawn.
            blocking (list[pygame.FRect]): The blocking objects to check against.
            targets (Entity): The entities to check for line-of-sight.
        """
        self.screen = screen
        self.blocking = blocking
        self.targets = targets
        self.gun_spritesheet_path: str = changeable_values.DEFAULT_PATH + "/assets/designs/Weapons.png"
        self.gun_spritesheet = self._load_spritesheet(image_width=13,
                                                      image_height=53,
                                                      final_width=39,
                                                      final_height=159,
                                                      path=self.gun_spritesheet_path)
        self.bullet_spritesheet_path: str = changeable_values.DEFAULT_PATH + "/assets/designs/Projectiles.png"
        self.bullet_spritesheet = self._load_spritesheet(image_width=3,
                                                         image_height=6,
                                                         final_width=12,
                                                         final_height=24,
                                                         path=self.bullet_spritesheet_path)
        self.create_guns()

    def _load_spritesheet(self,
                          image_width: int,
                          image_height: int,
                          final_width: int,
                          final_height: int,
                          path: str) -> dict[str, pygame.Surface]:
        """
        Loads and processes a spritesheet to extract individual sprites.

        Args:
            image_width (int): The width of each sprite in the spritesheet.
            image_height (int): The height of each sprite in the spritesheet.
            final_width (int): The width to which each sprite should be scaled.
            final_height (int): The height to which each sprite should be scaled.
            path (str): The file path to the spritesheet image.

        Returns:
            dict[str, pygame.Surface]: A dictionary mapping sprite indices to their corresponding scaled surface.
        """
        spritesheet = pygame.image.load(path).convert_alpha()
        return {str(i): pygame.transform.scale(spritesheet.subsurface(pygame.Rect(i * image_width, 0, image_width, image_height)), (final_width, final_height)) for i in range(spritesheet.width // image_width)}
    
    def load_sounds(self):
        """
        Loads and initializes sound effects for weapons with appropriate volume settings.

        This method loads sound files for various weapons from the specified paths,
        and sets their volumes based on the global and sound effects volume settings.
        
        Attributes:
            shotgun_sound (pygame.mixer.Sound): Sound effect for the shotgun.
            glock_sound (pygame.mixer.Sound): Sound effect for the pistol.
            rocket_sound (pygame.mixer.Sound): Sound effect for the rocket launch.
            rocket_explode (pygame.mixer.Sound): Sound effect for the rocket explosion.
        """
        self.shotgun_sound = pygame.mixer.Sound(changeable_values.DEFAULT_PATH + r"/assets/sounds/Shotgun.wav")
        self.shotgun_sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)
        self.glock_sound = pygame.mixer.Sound(changeable_values.DEFAULT_PATH + r"/assets/sounds/Pistol.wav")
        self.glock_sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)
        self.rocket_sound = pygame.mixer.Sound(changeable_values.DEFAULT_PATH + r"/assets/sounds/Rocket.wav")
        self.rocket_sound.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)
        self.rocket_explode = pygame.mixer.Sound(changeable_values.DEFAULT_PATH + r"/assets/sounds/Explosion.wav")
        self.rocket_explode.set_volume(changeable_values.GENERAL_VOLUME * changeable_values.SFX_VOLUME)

    def create_guns(self):
        """
        Creates instances of the weapons and assigns their properties.

        This method initializes the shotgun, pistol, and rocket launcher with their respective properties such as
        bullet speed, damage, maximum distance, and reload time. It also assigns the sound effects and sprites for
        each weapon.

        Attributes:
            shotgun (Weapon): The shotgun instance.
            glock (Weapon): The pistol instance.
            rocket_launcher (Weapon): The rocket launcher instance.
        """
        self.load_sounds()
        self.shotgun = Weapon(weapon_image=self.gun_spritesheet["0"],
                              bullet_image=self.bullet_spritesheet["2"],
                              screen=self.screen,
                              position=pygame.Vector2(-300, -300),
                              blocking=self.blocking,
                              targets=self.targets,
                              weapon_pickup_multiplier=2,
                              weapon_shoot_sound=self.shotgun_sound,
                              bullets=10,
                              bullet_speed=17,
                              reload_time=1,
                              delta_time=1,
                              spread_degree=40,
                              damage=2,
                              max_distance=400,
                              exploding=False,
                              show_hitbox=[False, (255, 0, 0), 2],
                              weapon_throw_speed=4,
                              weapon_throw_decrease=0.03)
        
        self.glock: Weapon = Weapon(weapon_image=self.gun_spritesheet["1"],
                            bullet_image=self.bullet_spritesheet["0"],
                            screen=self.screen,
                            position=pygame.Vector2(-300, -300),
                            blocking=self.blocking,
                            targets=self.targets,
                            weapon_pickup_multiplier=2,
                            weapon_shoot_sound=self.glock_sound,
                            spread_degree=2,
                            bullets=1,
                            bullet_speed=17,
                            reload_time=0.3,
                            delta_time=1,
                            damage=4,
                            max_distance=1200,
                            exploding=False,
                            show_hitbox=[False, (255, 0, 0), 2],
                            weapon_throw_speed=4,
                            weapon_throw_decrease=0.03)
        
        self.rocket_launcher: Weapon = Weapon(weapon_image=self.gun_spritesheet["2"],
                                     bullet_image=self.bullet_spritesheet["1"],
                                     screen=self.screen,
                                     position=pygame.Vector2(-300, -300),
                                     blocking=self.blocking,
                                     targets=self.targets,
                                     weapon_pickup_multiplier=2,
                                     weapon_shoot_sound=self.rocket_sound,
                                     explode_sound=self.rocket_explode,
                                     spread_degree=0,
                                     bullets=1,
                                     bullet_speed=10,
                                     reload_time=3.5,
                                     delta_time=1,
                                     damage=30,
                                     max_distance=800,
                                     exploding=True,
                                     explosion_radius=50,
                                     exploding_time=1.5,
                                    show_hitbox=[False, (255, 0, 0), 2],
                                    weapon_throw_speed=4,
                                    weapon_throw_decrease=0.03)
        
    def Rocket_Launcher(self):
        return self.rocket_launcher.copy()
    
    def Glock(self):
        return self.glock.copy()
    
    def Shotgun(self):
        return self.shotgun.copy()