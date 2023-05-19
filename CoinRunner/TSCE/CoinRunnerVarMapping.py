import enum 

class VarTypes(enum.Enum):
    BOOLEAN = 0 
    NUMERIC = 1 

class VarProperties(enum.Enum):
    STATE = "time step" 
    ACTION = "action" 

playerName = "Mario"

varMapping = {

    "enemyExists": (lambda y, x: f"{y} the enemy did {x}exist", VarTypes.BOOLEAN, lambda x: f"The enemy does {x} exist", "The existence of the enemy", "the existence of the enemy", VarProperties.STATE),
    "goldcoinExists": (lambda y, x: f"{y} the goldcoin did {x}exist", VarTypes.BOOLEAN, lambda x: f"The goldcoin does {x} exist", "The existence of the goldcoin", "the existence of the goldcoin", VarProperties.STATE),
    "powerupExists": (lambda y, x: f"{y} the powerup did {x}exist", VarTypes.BOOLEAN, lambda x: f"The powerup does {x} exist", "The existence of the powerup", "the existence of the powerup", VarProperties.STATE),

    "targEnemy": (lambda y, x: f"{y} the enemy was {x} targeted",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} targeting the enemy", "Targeting the enemy", "targeting the enemy", VarProperties.ACTION),
    "targGoldcoin": (lambda y, x: f"{y} the goldcoin was {x} targeted",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} targeting the goldcoin", "Targeting the goldcoin", "targeting the goldcoin" , VarProperties.ACTION),
    "targPowerup": (lambda y, x: f"{y} the powerup was {x} targeted",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} targeting the powerup", "Targeting the powerup", "targeting the powerup", VarProperties.ACTION),
    "targGoal": (lambda y, x: f"{y} the goal was {x} targeted",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} targeting the goal", "Targeting the goal", "targeting the goal", VarProperties.ACTION),

    "collPlayerEnemy": (lambda y, x: f"{y} the player did {x}collide with the enemy",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} colliding with the enemy", "Colliding with the enemy", "colliding with the enemy", VarProperties.ACTION),
    "collPlayerGoldcoin": (lambda y, x: f"{y} the player did {x}collide with the goldcoin",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} colliding with the goldcoin", "Colliding with the goldcoin", "colliding with the goldcoin", VarProperties.ACTION),
    "collPlayerPowerup": (lambda y, x: f"{y} the player did {x}collide with the powerup",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} colliding with the powerup", "Colliding with the powerup", "colliding with the powerup", VarProperties.ACTION),
    "collPlayerGoal": (lambda y, x: f"{y} the player did {x}collide with the goal",VarTypes.BOOLEAN, lambda x: f"{playerName} is {x} colliding with the goal", "Colliding with the goal", "colliding with the goal", VarProperties.ACTION),

    "collectedPowerUp": (lambda y, x: f"{y} the player had {x}already collected the powerup ",VarTypes.BOOLEAN, lambda x: f"The powerup was {x} collected", "Collecting the powerup", "collecting the powerup", VarProperties.STATE),
    "collectedGoldCoin": (lambda y, x: f"{y} the player had {x}already collected the goldcoin ",VarTypes.BOOLEAN, lambda x: f"The goldcoin was {x} collected", "Collecting the goldcoin", "collecting the goldcoin", VarProperties.STATE),
    "killedEnemy": (lambda y, x: f"{y} the player had {x}killed enemy",VarTypes.BOOLEAN, lambda x: f"The enemy was {x} killed", "Killing the enemy", "killing the enemy", VarProperties.STATE),
    "terminated": (lambda y, x: f"{y} the game is {x}terminated",VarTypes.BOOLEAN, lambda x: f"The game is {x} terminated", "Termination of the game", "termination of the game", VarProperties.STATE),

    "reward": (lambda y, x: f"{y} he did {x} receive a reward",VarTypes.BOOLEAN, lambda x: f"{playerName} did {x} receive a reward", "Receiving a reward", "receiving a reward", VarProperties.STATE),

    "frameID": (lambda y, x: f" because the frame ID had a {y} influence on it",VarTypes.NUMERIC, lambda x: f"The frame ID has a {x} influence", "The frame ID", "the frame ID", VarProperties.STATE),
    "score": (lambda y, x: f" because the score had a {y} influence on it",VarTypes.NUMERIC, lambda x: f"The score has a {x} influence", "The score", "the score", VarProperties.STATE),

}