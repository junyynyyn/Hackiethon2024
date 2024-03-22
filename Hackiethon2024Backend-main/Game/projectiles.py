import itertools
from Game.Skills import AttackSkill
from Game.gameSettings import LEFTBORDER, RIGHTBORDER

class Projectile:
    # auto increment projectile id whenever a new projectile is summoned
    id = itertools.count()
    
    def __init__(self, player, path, size, type, trait, collision, timer, 
                 collisionHp):
        # size = (x, y) hitbox size of projectile
        # type =  type of projectile eg hadoken
        self._direction = player._direction
        self._distance = 0
        self._size = list(size)
        self._type = type
        self._timer = timer
        self._entity_type = "projectile"
        self._collisionHp = collisionHp
        self._playerInitPos = player.get_pos()
        
        # True if projectile damages on hit during travel eg hadoken, lasso
        # False if prpojectile damages after travel eg ice wall, landmine
        self._collision = collision
        
        # trait = effect after projectile has travelled its path
        # pop = remove projectile, explode = AOE dmg after timer, timer = pop after timer, no dmg
        self._trait = trait
        self._id = next(self.id)
        # reference to caster
        self._player = player
        
        # this is an array of projectile positions relative to cast position over time
        self._path = list(path)
        self._pathIndex = 0
        
        # orientate path in player direction
        for i in range(len(self._path)):
            self._path[i][0] = self._direction * self._path[i][0]
        
        # initialize first position
        self._xCoord = player._xCoord + path[0][0]
        self._yCoord = player._yCoord + path[0][1]
        
            
    def get_type(self):
        return self._type
    
    # move one step along path
    def _travel(self):
        if 0 < self._pathIndex < len(self._path) and LEFTBORDER < self._xCoord < RIGHTBORDER:
            pos = self._path[self._pathIndex]
            self._xCoord += pos[0] - self._path[self._pathIndex - 1][0]
            self._yCoord += pos[1] - self._path[self._pathIndex - 1][1]
            # bear trap should fall if midair
            if self._trait == "timer" and self._yCoord > 0:
                self._yCoord -= 1
                
        elif self._pathIndex >= len(self._path) or ((self._xCoord <= LEFTBORDER) 
                            or (self._xCoord >= RIGHTBORDER)):
            # has reached end of path, so do effects based on trait
            self._do_trait()
        self._pathIndex += 1

    # unique effects that occur once projectile reaches end of path
    def _do_trait(self):
        if not self._trait:
            # pop
            self._size = (0, 0)
        
        if self._trait == "return":
            # check if hit border
            hit_border = False
            if self._xCoord <= LEFTBORDER:
                self._xCoord = LEFTBORDER
                hit_border = True
            elif self._xCoord >= RIGHTBORDER:
                self._xCoord = RIGHTBORDER
                hit_border = True
            
            rev_path = []
            # if hit border, recalculate return path based on player's position on cast
            if hit_border:
                if self._pathIndex == 0:
                    # hits border on the first tick of travel
                    self._path = [self._path[0]]
                else:
                    self._path = self._path[:self._pathIndex]
                x_dist = abs(self._playerInitPos[0] - self._xCoord)
                height = self._playerInitPos[1]
                
                start_x = abs(self._path[-1][0])
                proj_direction = self._direction
                for i in range(1, x_dist):
                    rev_path.append([(start_x - i)*proj_direction, height])
            else:
            # if doesn't hit border, get the reverse of the current path - 1
                rev_path = self._path[::-1][1:]
            # after calculating return path, append it to path
            self._path += rev_path
            # then move to the next step along the path
            pos = self._path[self._pathIndex]
            self._xCoord += pos[0] - self._path[self._pathIndex - 1][0]
            self._yCoord += pos[1] - self._path[self._pathIndex - 1][1]
            self._trait = None
            self._direction *= -1
                
        elif self._trait == "timer":
            # stay at current position for given time to live
            # does damage if hits opponent before given time
            if (self._xCoord < LEFTBORDER):
                self._xCoord = LEFTBORDER
            elif (self._xCoord > RIGHTBORDER):
                self._xCoord = RIGHTBORDER
            self._collision = True
            if self._timer:
                self._timer -= 1
            else:
                self._size = (0,0)
            
            
        elif self._trait == "timer_explode":
            # similar to timer, but does aoe damage after timer
            explode = False
            if (self._xCoord < LEFTBORDER):
                self._xCoord = LEFTBORDER
                explode = True
            elif (self._xCoord > RIGHTBORDER):
                self._xCoord = RIGHTBORDER
                explode = True
                
            if self._timer and not explode:
                self._timer -= 1
            else:
                # explode
                self._size = (self._size[0] + 1, self._size[1] + 1)
                self._collision = True
                self._trait = "explode"
                # allow to destroy proj and players
                self._collisionHp = 10
                
              
    def get_pos(self):
        return (self._xCoord, self._yCoord)
    
    # destroys itself if takes enough damage from another projectile
    def take_col_dmg(self, colDmg):
        self._collisionHp -= colDmg
        if self._collisionHp <= 0:
            # destroy this projectile
            self._collisionHp = 0
            self._size = (0,0)
            
    # check for collision with player
    def _checkCollision(self, target):
        # checks if projectile has a size
        if self._size[0] and self._size[1] and self._collision:
            # checks if projectile hits target
            if ((abs(target._xCoord-self._xCoord) < self._size[0]) and
                (abs(target._yCoord-self._yCoord) < self._size[1])):
                return target != self._player
        return False
            
    # check for collision with projectile      
    def _checkProjCollision(self, target):
        if self._size[0] and self._size[1]:
            # this projectiles range = x to x + target size * direction
            # therefore, get max x and max y sizes, check if they hit
            # hits if both positions within the max x and y sizes
            max_x = max(target._size[0], self._size[0])
            max_y = max(target._size[1], self._size[1])
            if ((abs(target._xCoord-self._xCoord) < max_x) and 
                (abs(target._yCoord-self._yCoord) < max_y)):
                return True
        return False
    
class ProjectileSkill(AttackSkill):
    def __init__(self, player, startup, cooldown, damage, blockable, knockback,
                 stun, skillName):
        AttackSkill.__init__(self, startup=startup, cooldown=cooldown, 
                            damage=damage, xRange=0, vertical=0, 
                            blockable=blockable, knockback=knockback, 
                            stun=stun)
        self._player = player
        self._skillType = skillName
        self._path = []
        # default recovery for all projectile skills
        self._recovery = 1
        
    def summonProjectile(self, path, size, trait, collision, timer, colHp):
        projectile = Projectile(self._player, path, size, self._skillType, trait, 
                                collision, timer, collisionHp=colHp)
        return projectile

    
class Hadoken(ProjectileSkill):
    def __init__(self, player):
        ProjectileSkill.__init__(self, player, startup=0, cooldown=10, damage=10,
                                 blockable=True, knockback=2, stun=2, 
                                 skillName="hadoken")
        self._stunself = False
        self.init_path()
        
    def init_path(self):
        self._path = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6,0], [7,0]]
        
    def _activateSkill(self):
        self.init_path()
        travelPath = self._path
        atk_info = super()._activateSkill()
        if isinstance(atk_info, int):
            return atk_info
        
        projectile = self.summonProjectile(path = travelPath, size=(1,1), 
                                           trait=None, collision=True, timer=0,
                                           colHp= 3)
        return [self._skillType,  {"damage":self._skillValue, "blockable": self._blockable, 
                "knockback":self._knockback, "stun":self._stun,  "self_stun":self._stunself,
                "projectile": projectile}]
        
    def path_range(self):
        return self._path[-1][0] - self._path[0][0]
    
    
class Boomerang(ProjectileSkill):
    def __init__(self, player):
        ProjectileSkill.__init__(self, player, startup=0, cooldown=14, damage=8,
                                 blockable=True, knockback=2, stun=2, 
                                 skillName="boomerang")
        self._stunself = False
        self.init_path()
    
    def init_path(self):
        self._path = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
        
    def _activateSkill(self, travelPath=None):
        self.init_path()
        travelPath = self._path
        atk_info = super()._activateSkill()
        if isinstance(atk_info, int):
            return atk_info
        
        projectile = self.summonProjectile(path = travelPath, size=(1,1), 
                                           trait="return", collision=True, timer=0,
                                           colHp=3)
        return [self._skillType,  {"damage":self._skillValue, "blockable": self._blockable, 
                "knockback":self._knockback, "stun":self._stun,  "self_stun":self._stunself,
                "projectile": projectile}]
            
    def path_range(self):
        return self._path[-1][0] - self._path[0][0]
    
        
class Grenade(ProjectileSkill):
    def __init__(self, player):
        ProjectileSkill.__init__(self, player, startup=0, cooldown=12, damage=20,
                                 blockable=False, knockback=3, stun=3, 
                                 skillName="grenade")
        
        self._stunself = False
        self._recovery = 0
        self.init_path()
    
    def init_path(self):
         self._path = [[1,1], [2,1], [3,1]]   
         
    def _activateSkill(self, travelPath=None):
        self.init_path()
        travelPath = self._path
        atk_info = super()._activateSkill()
        if isinstance(atk_info, int):
            return atk_info
        
        projectile = self.summonProjectile(path = travelPath, size=(1,1), 
                                           trait="timer_explode", 
                                           collision=False, timer=0, colHp=1)
        return [self._skillType,  {"damage":self._skillValue, "blockable": self._blockable, 
                "knockback":self._knockback, "stun":self._stun,  "self_stun":self._stunself,
                "projectile": projectile}]
        
    def path_range(self):
        return self._path[-1][0] - self._path[0][0]
    
class BearTrap(ProjectileSkill):
    def __init__(self, player):
        ProjectileSkill.__init__(self, player, startup=0, cooldown=15, damage=10,
                                 blockable=False, knockback=0, stun=3, 
                                 skillName="beartrap")
        
        self._stunself = False
        self.init_path()
        
    def init_path(self):
        self._path = [[1,0]]
        
    def _activateSkill(self, travelPath=None):
        self.init_path()
        travelPath = self._path
        atk_info = super()._activateSkill()
        if isinstance(atk_info, int):
            return atk_info
        
        projectile = self.summonProjectile(path = travelPath, size=(1,1), 
                                           trait="timer", 
                                           collision=False, timer=10, colHp=2)
        return [self._skillType,  {"damage":self._skillValue, "blockable": self._blockable, 
                "knockback":self._knockback, "stun":self._stun,  "self_stun":self._stunself,
                "projectile": projectile}]
        
    def path_range(self):
        return self._path[-1][0] - self._path[0][0]

