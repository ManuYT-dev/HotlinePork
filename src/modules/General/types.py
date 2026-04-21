import pygame

class Entity(pygame.sprite.Sprite):
    """
    A base class representing a generic game entity.

    This class serves as a blueprint for creating game entities with common attributes
    and methods. Subclasses should override the abstract methods to provide specific
    functionality.
    """
    def __init__(self) -> None:
        super().__init__()
        if not hasattr(Entity, "all_entities"):
            Entity.all_entities: Groups[Entity] = Groups()
        Entity.all_entities.add(self)

        cls = type(self)
        self.cls = cls
        if not hasattr(cls, "all"):
            cls.all = Groups()
        cls.all.add(self)
        
        self.x: int
        self.y: int
        self.POSITION: pygame.Vector2
        self.blocking: pygame.FRect | list[pygame.FRect]
        self.health: int
        self.show_hitbox: list[bool, (int, int, int), int]
        self.player_scale: tuple[int, int] | list[int, int]
        self.screen: pygame.surface.Surface
        self.delta_time: float
        self.movement_speed: int
        self.gun: Entity = None

    def initiate_drawing(self) -> None:
        """
        Initializes the drawing of the entity.

        This method should be implemented in subclasses to define how the entity
        is drawn, including setting up the image and rect attributes.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        self.rect: pygame.FRect
        self.mask: pygame.Mask
        self.image: pygame.Surface
        raise NotImplementedError("Subclasses must implement the initiate_drawing method.")
        
    def pickup_weapon(self,
               guns: list,
               new_targets = []) -> None:
        new_targets: Groups[Entity] # Muss man hier machen weil davor hat es keinen bock
        if not isinstance(new_targets, Groups | tuple | list): new_targets = Groups(new_targets)
        if self.holding_weapon():
            return
        
        guns: list = guns if isinstance(guns, list | tuple | Groups) else [guns]
        collided = self.rect.collideobjectsall(guns, key = lambda x: x.pickup_rect)
        if collided:
            for gun in collided:
                if not gun.sticking_to:
                    gun.sticking_to = self
                    self.gun = gun
                    gun.targets = new_targets
                    break

    def drop_weapon(self,
                    position: pygame.Vector2) -> None:
        if self.holding_weapon():
            self.gun.throwing = True
            self.gun.throwing_to = position if isinstance(position, pygame.Vector2) else pygame.Vector2(position)
            self.gun = None

    def holding_weapon(self) -> bool:
        return bool(self.gun)

    def movement(self) -> None:
        """
        Handles the movement logic for the entity.

        This method should be implemented in subclasses to define how the entity
        moves based on input or other factors.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the movement method.")
    
    def damage(self,
               damage: int,
               direction: pygame.Vector2) -> None:
        """
        Applies the given amount of damage to the entity's health.

        If the entity's health is reduced to 0 or below, the entity is killed.

        Args:
            damage: The amount of damage to apply to the entity's health. Must be >= 0.
        Returns:
            None:
        """

        self.health -= damage
        if self.health <= 0:
            if self.gun:
                self.drop_weapon(self.POSITION + direction)
            self.kill()

    def draw(self,
             screen: pygame.surface.Surface) -> None:
        """
        Draws the entity on the given screen surface.

        Args:
            screen: The surface on which the entity is drawn.

        Returns:
            None
        """
        screen.blit(self.image, self.rect.topleft)

    def update(self) -> None:

        self.draw()
        self.movement()

    def All_Entities(self):
        """
        Returns all entities in the game.

        Returns:
            Groups[Entity]: A Group containing all entities in the game.
        """
        return Entity.all_entities
    
    def All(self):
        """
        Returns all entities of the same type as the current entity.

        Returns:
            Groups[Entity]: A Group of all entities of the same type as the current entity.
        """
        return self.cls.all
    
    def clear_cls(self):
        self.cls.all = Groups()
        self.cls.all.add(self)
        return self.cls.all
    
    def hitbox_check(self) -> None:
        """
        Checks if the entity's hitbox collides with any blocking rectangles.

        This method should be implemented in subclasses to define how the entity
        checks for collisions with blocking rectangles.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the hitbox_check method.")
    
    def alive(self):
        """
        Checks if the entity is alive.

        Returns:
            bool: True if the entity is alive, False otherwise.
        """
        return self.health >= 0
    
    def LOS(self) -> None:
        """
        Checks the line of sight between the entity and a target.

        This method should be implemented in subclasses to define how the entity
        checks for line of sight to a target, considering blocking objects.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the LOS method.")
    
    def update_all_delta_times(self,
                               delta_time: float):
        for enemy in self.All():
            enemy.delta_time = delta_time
    
class Groups(pygame.sprite.Group):
    """
    A group of entities.

    Args:
        entitys: A list of entities to add to the group.
    """
    def __init__(self, *entitys: Entity) -> None:
        super().__init__()
        self.spritedict: dict[Entity] = {}
        self.add(*entitys)

    def __len__(self):
        return len(self.spritedict)

    def __getitem__(self, i):
        return self.sprites()[i]
    
    def __iter__(self):
        return iter(self.sprites())
    
    def update(self, *args, **kwargs):
        for entity in self.sprites():
            entity.update(*args, **kwargs)

    def sprites(self) -> list[Entity]:
        return list(self.spritedict)
    
    def movement(self, *args, **kwargs) -> None:
        for entity in self.sprites():
            entity.movement(*args, **kwargs)

    def draw(self, *args, **kwargs) -> None:
        for entity in self.sprites():
            entity.draw(*args, **kwargs)

    def LOS(self, *args, **kwargs) -> dict[Entity, bool]:        
        returning_dict: dict[Entity, bool] = {}
        for entity in self.sprites():
            returning_dict.update(entity.LOS(*args, **kwargs))
        return returning_dict

    def hitbox_check(self, *args, **kwargs) -> dict[Entity, bool]:
        returning_dict: dict[Entity, bool] = {}
        for entity in self.sprites():
            returning_dict[entity] = entity.hitbox_check(*args, **kwargs)
        return returning_dict
    
    def update_delta_time(self,
                          delta_time: float):
        for entity in self.sprites():
            entity.update_all_delta_times(delta_time)

class InputType:
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
