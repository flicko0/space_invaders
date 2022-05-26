import random
import time

projectile_launchers = {
    "cod": {"dmg": 0, "collision_dmg": 5, "firerate": 0, "speed": 1, "pen": 0},
    "gun": {
        "dmg": 1,
        "collision_dmg": 5,
        "firerate": 0.5,
        "speed": 1,
        "pen": 0,
    },
}
alien_models = {
    "cod": {
        "launcher": projectile_launchers["cod"],
        "hp": 1,
    }
}


class Alien:
    def __init__(
        self, level, x: int, y: int, model=alien_models["cod"], dmg_multi=1
    ) -> None:
        self.level = level
        self.pos = (x, y)
        self.model = model
        self.dmg_multi = dmg_multi

    def update(self):
        x, y = self.pos
        print("alien: ", self.pos)
        if (
            x == 0
            and self.pos[1] % 2
            or x == self.level.x - 1
            and not self.pos[1] % 2
        ):
            self.pos = (self.pos[0], self.pos[1] + 1)
            print("alien1: ", self.pos)
        elif self.pos[1] % 2:
            self.pos = (self.pos[0] - 1, self.pos[1])
            print("alien2: ", self.pos)
        else:
            self.pos = (self.pos[0] + 1, self.pos[1])
            print("alien3: ", self.pos)
        self.contacted_ship()

    def hit(self, dmg):
        self.model["hp"] -= dmg
        if self.model["hp"] <= 0:
            self.level.aliens.remove(self)

    def contacted_ship(self):
        if self.pos == self.level.ship:
            self.level.hp -= 1
        elif self.pos == (self.level.x - 1, self.level.ship[1]):
            self.level.hp -= 1


class Projectile:
    def __init__(
        self,
        level,
        x: int,
        y: int,
        launcher=projectile_launchers["gun"],
        dmg_multi=1,
    ) -> None:
        self.level = level
        self.pos = (x, y - 1)
        self.launcher = launcher
        self.dmg_multi = dmg_multi

    def update(self):
        if self.pos[1] == 0:
            print("removing proj1")
            self.level.projectiles.remove(self)
        print("moving proj: ", self.pos)
        self.pos = (self.pos[0], self.pos[1] - self.launcher["speed"])
        print("projectile:", self.pos)
        alien = self.contacted()
        for alien in self.contacted():
            alien.hit(self.launcher["dmg"] * self.dmg_multi)
            if self.launcher["pen"] != 0:
                self.launcher["pen"] -= 1
            else:
                print("removing proj2")
                self.level.projectiles.remove(self)

    def contacted(self):
        for alien in self.level.aliens:
            if alien.pos == self.pos:
                yield alien


class Level:
    def __init__(self, lvl: int, x: int = 10, y: int = 5):
        self.lvl = lvl
        self.aliens = []
        self.projectiles = []
        self.x = x
        self.launcher = projectile_launchers["gun"]
        self.firerate = self.launcher["firerate"]
        self.waves = 1
        self.hp = 1
        self.y = y
        self.ship = (0, 0)
        for _ in range(self.x // 2):
            self.spawn_alien()
        self.spawn_ship()

    def get_board(self):
        board = []
        for x in range(self.x):
            board.append([])
            for y in range(self.y):
                board[x].append({})
        for alien in self.aliens:
            x, y = alien.pos
            board[x][y] = {"alien": True}
        for bullet in self.projectiles:
            x, y = bullet.pos
            print("bullet: ", x, ",", y)
            board[x][y].update({"bullet": True})
        x, y = self.ship
        board[x][y] = {"ship": True}
        return {"board": board}

    def spawn_alien(self):
        self.aliens.append(Alien(self, 0, 0))

    def spawn_projectile(self):
        self.projectiles.append(
            Projectile(
                self,
                self.ship[0],
                self.ship[1] + 1,
                self.launcher,
            )
        )

    def update(self):
        if self.waves == self.lvl and self.aliens == []:
            return {"win": True}
        elif self.hp <= 0:
            return {"lose": True}
        if self.firerate == 1:
            print("spawning proj")
            self.firerate = self.launcher["firerate"]
            self.spawn_projectile()
        else:
            self.firerate += self.launcher["firerate"]
        for projectile in self.projectiles:
            projectile.update()
        for alien in self.aliens:
            alien.update()
        if self.waves < self.lvl:
            if random.choice([True, False, True, True]):
                self.spawn_alien()
                self.waves += 1
        return self.get_board()

    def spawn_ship(self):
        ship_x = self.x // 2
        self.ship = (ship_x, self.y - 1)
        print("ship_pos ", self.ship)

    def control_ship(self, way: str):
        if way == "left":
            if self.ship[0] == 0:
                self.ship = (self.x - 1, self.y - 1)
            else:
                self.ship = (self.ship[0] - 1, self.y - 1)
        elif way == "right":
            if self.ship[0] == self.x - 1:
                self.ship = (0, self.y - 1)
            else:
                self.ship = (self.ship[0] + 1, self.y - 1)
        print("ship_pos ", self.ship)
        return self.update()


def new(lvl: int, rows: int, cols: int):
    return Level(lvl, rows, cols)
