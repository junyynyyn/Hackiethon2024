# bot code goes here
from Game.Skills import *
from Game.projectiles import *
from ScriptingHelp.usefulFunctions import *
from Game.playerActions import defense_actions, attack_actions, projectile_actions
from Game.gameSettings import HP, LEFTBORDER, RIGHTBORDER, LEFTSTART, RIGHTSTART, PARRYSTUN


# PRIMARY CAN BE: Teleport, Super Saiyan, Meditate, Dash Attack, Uppercut, One Punch
# SECONDARY CAN BE : Hadoken, Grenade, Boomerang, Bear Trap

# TODO FOR PARTICIPANT: Set primary and secondary skill here
PRIMARY_SKILL = TeleportSkill
SECONDARY_SKILL = Hadoken

#constants, for easier move return
#movements
JUMP = ("move", (0,1))
FORWARD = ("move", (1,0))
BACK = ("move", (-1,0))
JUMP_FORWARD = ("move", (1,1))
JUMP_BACKWARD = ("move", (-1, 1))

# attacks and block
LIGHT = ("light",)
HEAVY = ("heavy",)
BLOCK = ("block",)

PRIMARY = get_skill(PRIMARY_SKILL)
SECONDARY = get_skill(SECONDARY_SKILL)
CANCEL = ("skill_cancel", )

# no move, aka no input
NOMOVE = "NoMove"
# for testing
moves = SECONDARY,
moves_iter = iter(moves)

# TODO FOR PARTICIPANT: WRITE YOUR WINNING BOT
# Ultra Aggro Bot
class Script:
    def __init__(self):
        self.primary = PRIMARY_SKILL
        self.secondary = SECONDARY_SKILL
        # States = [OFFENSIVE, DEFENSIVE, NEUTRAL]
        #Walls are at 0, 15
        self.combocount = 0
        
    # DO NOT TOUCH
    def init_player_skills(self):
        return self.primary, self.secondary
    
    # MAIN FUNCTION that returns a single move to the game manager
    def get_move(self, player, enemy, player_projectiles, enemy_projectiles):
        distance = abs(get_pos(player)[0] - get_pos(enemy)[0])
        position = get_pos(player)
        distance_to_projectile = 100
        if(enemy_projectiles):
            distance_to_projectile = abs(get_pos(player)[0] - get_proj_pos(enemy_projectiles[0])[0])
        
        prev_move = ''
        if (get_last_move(player)):
            prev_move = get_last_move(player)[0]
        if (get_stun_duration(enemy) == 0):
            self.combocount = 0

        if (distance < 1):
            return HEAVY
        if (distance < 5 and not primary_on_cooldown(player)):
            return PRIMARY
        else:
            return FORWARD