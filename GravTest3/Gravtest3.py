<<<<<<< HEAD
import pygame
import math
import random

pygame.init()
clock = pygame.time.Clock()

WIDTH = 1000
HEIGHT = 1000
BODY_COUNT = 100
ENERGY_LOSS = 0.95

win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
colours = [[0, 0, 0], [0, 255, 0], [0, 0, 128], [255, 128, 0], [0, 153, 0]]
# white, red, green, cyan, magenta, orange, dark green
WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
RED = [255, 0, 0]

win.fill(WHITE)

MaxFps = 90

G = 6.7 * (10 ** -2)


class COMCircle(object):
    def __init__(self, x, y, radius, colour):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour

    def move(self, centre):
        self.x += centre["x_move"]
        self.y += centre["y_move"]

    def draw(self, win, centre):
        self.move(centre)
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), round(self.radius), 1)


class Body(object):
    def __init__(self, x, y, radius, colour, mass, x_vel, y_vel):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.mass = mass
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.reversed = False
        self.current_zoom = 1

    def move(self, screen_move):
        self.current_zoom = self.current_zoom * screen_move["zoom"]
        self.x += self.x_vel * self.current_zoom + screen_move["x_move"]
        self.y += self.y_vel * self.current_zoom + screen_move["y_move"]
        x_from_centre, y_from_centre = screen_move["x"] - self.x, screen_move["y"] - self.y
        self.x += abs(x_from_centre * screen_move["zoom"] - x_from_centre)
        self.y += abs(y_from_centre * screen_move["zoom"] - y_from_centre)
        self.radius = self.radius * screen_move["zoom"]

    def draw(self, win, screen_move):
        self.move(screen_move)
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), round(self.radius))


def single_press_inc(key):
    if key > 0:
        if key > 90:
            key = 0
        else:
            key += 1
    return key


def spawn_body(x, y, mass, colour, bodies, x_vel, y_vel):
    radius = math.sqrt(mass)
    bodies.append(Body(x, y, radius, colour, mass, x_vel, y_vel))
    return bodies


def impact(body1, body2, bodies):
    new_mass = body1.mass + body2.mass
    if body1.mass > body2.mass:
        new_x, new_y = body1.x, body1.y
    else:
        new_x, new_y = body2.x, body2.y
    new_x_vel = ((body1.x_vel * body1.mass + body2.x_vel * body2.mass) / new_mass)
    new_y_vel = ((body1.y_vel * body1.mass + body2.y_vel * body2.mass) / new_mass)
    bodies = (spawn_body(new_x, new_y, new_mass, (169, 169, 169), bodies, new_x_vel, new_y_vel))
    body1.dead = True
    body2.dead = True
    return bodies


def impact_calc(body1, body2):
    if not body1.reversed:
        tmp_x_vel = body1.x_vel
        tmp_y_vel = body1.y_vel
        body1.x_vel = body2.x_vel
        body1.y_vel = body2.y_vel
        body2.x_vel = tmp_x_vel
        body2.y_vel = tmp_y_vel
        rel_x_vel = abs(body1.x_vel - body2.x_vel) - (ENERGY_LOSS * abs(body1.x_vel - body2.x_vel))
        rel_y_vel = abs(body1.y_vel - body2.y_vel) - (ENERGY_LOSS * abs(body1.y_vel - body2.y_vel))
        energy_calc(body1, rel_x_vel, rel_y_vel)
        energy_calc(body2, rel_x_vel, rel_y_vel)
        body1.reversed = True
    else:
        if math.hypot(abs(body1.x - body2.x), abs(body1.y - body2.y)) > body1.radius:
            body1.reversed = False


def energy_calc(body, rel_x, rel_y):
    if body.x_vel > 0:
        sign_offset = -1
    else:
        sign_offset = 1
    body.x_vel += sign_offset * rel_x
    if body.y_vel > 0:
        sign_offset = -1
    else:
        sign_offset = 1
    body.y_vel += sign_offset * rel_y
    
    
def gravity_calc(major_body, minor_body):
    hypotenuse = math.hypot(abs(major_body.x - minor_body.x), abs(major_body.y - minor_body.y))
    if hypotenuse == 0:
        g = 0
        ratio_total = 1
    else:
        g = (G * major_body.mass * minor_body.mass) / hypotenuse ** 2
        ratio_total = (abs(major_body.x - minor_body.x)) + (abs(major_body.y - minor_body.y))
    if hypotenuse > major_body.radius * 2:
        minor_body.x_vel += g * ((major_body.x - minor_body.x) / ratio_total)
        minor_body.y_vel += g * ((major_body.y - minor_body.y) / ratio_total)


def calc_com_circle(bodies, com_circle):
    total_pos = [0, 0]
    total_hypot = 0
    for body in bodies:
        total_pos[0] += body.x
        total_pos[1] += body.y
    com_circle.x = total_pos[0] / BODY_COUNT
    com_circle.y = total_pos[1] / BODY_COUNT
    for body in bodies:
        total_hypot += math.hypot(com_circle.x - body.x, com_circle.y - body.y)
    com_circle.radius = total_hypot / BODY_COUNT


def redraw(com_circle, bodies, screen_move):
    win.fill(WHITE)
    for i in bodies:
        Body.draw(i, win, screen_move)
    COMCircle.draw(com_circle, win, screen_move)
    pygame.display.update()


def mainloop():
    screen_move = {"x": 0, "y": 0, "x_move": 0, "y_move": 0, "zoom": 0}
    run = True
    single_press = [0, 0, 0]
    bodies = []
    horizontal_move = 0
    vertical_move = 0
    zoom = 1
    com_circle = COMCircle(WIDTH / 2, HEIGHT / 2, 5, [255, 0, 0])
    for i in range(0, BODY_COUNT - 1):
        bodies = spawn_body(random.randint(200, WIDTH), random.randint(100, HEIGHT),
                            15, (169, 169, 169), bodies, random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
    while run:
        clock.tick(MaxFps)
        keys = pygame.key.get_pressed()

        for i in range(0, len(single_press) - 1):
            single_press[i] = single_press_inc(single_press[i])

        clock.tick(MaxFps)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for i in single_press:
            single_press[single_press.index(i)] = single_press_inc(i)

        if keys[pygame.K_SPACE] and single_press[0] == 0:
            pause = True
            single_press[0] = 1

        if keys[pygame.K_a]:
            horizontal_move += 15

        if keys[pygame.K_d]:
            horizontal_move -= 15

        if keys[pygame.K_w]:
            vertical_move += 15

        if keys[pygame.K_s]:
            vertical_move -= 15

        if keys[pygame.K_q] and single_press[1] == 0:
            single_press[1] += 1
            zoom = 0.5

        if keys[pygame.K_e] and single_press[2] == 0:
            single_press[2] += 1
            zoom = 2

        for body1 in bodies:
            for body2 in bodies:
                gravity_calc(body1, body2)

        for i, body1 in enumerate(bodies):
            for j in range(i + 1, len(bodies)):
                body2 = bodies[j]
                if body1 != body2:
                    if math.hypot(abs(body1.x - body2.x), abs(body1.y - body2.y)) < body1.radius + body2.radius:
                        impact_calc(body1, body2)

        screen_move["x"] = (WIDTH + horizontal_move) / 2
        screen_move["y"] = (HEIGHT + vertical_move) / 2
        screen_move["x_move"] = horizontal_move
        screen_move["y_move"] = vertical_move
        screen_move["zoom"] = zoom
        calc_com_circle(bodies, com_circle)
        redraw(com_circle, bodies, screen_move)
        horizontal_move, vertical_move = 0, 0
        zoom = 1


mainloop()
=======
import pygame
import math
import random

pygame.init()
clock = pygame.time.Clock()

WIDTH = 1000
HEIGHT = 1000
BODY_COUNT = 100
ENERGY_LOSS = 0.95

win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
colours = [[0, 0, 0], [0, 255, 0], [0, 0, 128], [255, 128, 0], [0, 153, 0]]
# white, red, green, cyan, magenta, orange, dark green
WHITE = [255, 255, 255]
BLUE = [0, 0, 255]
RED = [255, 0, 0]

win.fill(WHITE)

MaxFps = 90

G = 6.7 * (10 ** -2)


class COMCircle(object):
    def __init__(self, x, y, radius, colour):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour

    def move(self, centre):
        self.x += centre["x_move"]
        self.y += centre["y_move"]

    def draw(self, win, centre):
        self.move(centre)
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), round(self.radius), 1)


class Body(object):
    def __init__(self, x, y, radius, colour, mass, x_vel, y_vel):
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.mass = mass
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.reversed = False
        self.current_zoom = 1

    def move(self, screen_move):
        self.current_zoom = self.current_zoom * screen_move["zoom"]
        self.x += self.x_vel * self.current_zoom + screen_move["x_move"]
        self.y += self.y_vel * self.current_zoom + screen_move["y_move"]
        x_from_centre, y_from_centre = screen_move["x"] - self.x, screen_move["y"] - self.y
        self.x += abs(x_from_centre * screen_move["zoom"] - x_from_centre)
        self.y += abs(y_from_centre * screen_move["zoom"] - y_from_centre)
        self.radius = self.radius * screen_move["zoom"]

    def draw(self, win, screen_move):
        self.move(screen_move)
        pygame.draw.circle(win, self.colour, (round(self.x), round(self.y)), round(self.radius))


def single_press_inc(key):
    if key > 0:
        if key > 90:
            key = 0
        else:
            key += 1
    return key


def spawn_body(x, y, mass, colour, bodies, x_vel, y_vel):
    radius = math.sqrt(mass)
    bodies.append(Body(x, y, radius, colour, mass, x_vel, y_vel))
    return bodies


def impact(body1, body2, bodies):
    new_mass = body1.mass + body2.mass
    if body1.mass > body2.mass:
        new_x, new_y = body1.x, body1.y
    else:
        new_x, new_y = body2.x, body2.y
    new_x_vel = ((body1.x_vel * body1.mass + body2.x_vel * body2.mass) / new_mass)
    new_y_vel = ((body1.y_vel * body1.mass + body2.y_vel * body2.mass) / new_mass)
    bodies = (spawn_body(new_x, new_y, new_mass, (169, 169, 169), bodies, new_x_vel, new_y_vel))
    body1.dead = True
    body2.dead = True
    return bodies


def impact_calc(body1, body2):
    if not body1.reversed:
        tmp_x_vel = body1.x_vel
        tmp_y_vel = body1.y_vel
        body1.x_vel = body2.x_vel
        body1.y_vel = body2.y_vel
        body2.x_vel = tmp_x_vel
        body2.y_vel = tmp_y_vel
        rel_x_vel = abs(body1.x_vel - body2.x_vel) - (ENERGY_LOSS * abs(body1.x_vel - body2.x_vel))
        rel_y_vel = abs(body1.y_vel - body2.y_vel) - (ENERGY_LOSS * abs(body1.y_vel - body2.y_vel))
        energy_calc(body1, rel_x_vel, rel_y_vel)
        energy_calc(body2, rel_x_vel, rel_y_vel)
        body1.reversed = True
    else:
        if math.hypot(abs(body1.x - body2.x), abs(body1.y - body2.y)) > body1.radius:
            body1.reversed = False


def energy_calc(body, rel_x, rel_y):
    if body.x_vel > 0:
        sign_offset = -1
    else:
        sign_offset = 1
    body.x_vel += sign_offset * rel_x
    if body.y_vel > 0:
        sign_offset = -1
    else:
        sign_offset = 1
    body.y_vel += sign_offset * rel_y
    
    
def gravity_calc(major_body, minor_body):
    hypotenuse = math.hypot(abs(major_body.x - minor_body.x), abs(major_body.y - minor_body.y))
    if hypotenuse == 0:
        g = 0
        ratio_total = 1
    else:
        g = (G * major_body.mass * minor_body.mass) / hypotenuse ** 2
        ratio_total = (abs(major_body.x - minor_body.x)) + (abs(major_body.y - minor_body.y))
    if hypotenuse > major_body.radius * 2:
        minor_body.x_vel += g * ((major_body.x - minor_body.x) / ratio_total)
        minor_body.y_vel += g * ((major_body.y - minor_body.y) / ratio_total)


def calc_com_circle(bodies, com_circle):
    total_pos = [0, 0]
    total_hypot = 0
    for body in bodies:
        total_pos[0] += body.x
        total_pos[1] += body.y
    com_circle.x = total_pos[0] / BODY_COUNT
    com_circle.y = total_pos[1] / BODY_COUNT
    for body in bodies:
        total_hypot += math.hypot(com_circle.x - body.x, com_circle.y - body.y)
    com_circle.radius = total_hypot / BODY_COUNT


def redraw(com_circle, bodies, screen_move):
    win.fill(WHITE)
    for i in bodies:
        Body.draw(i, win, screen_move)
    COMCircle.draw(com_circle, win, screen_move)
    pygame.display.update()


def mainloop():
    screen_move = {"x": 0, "y": 0, "x_move": 0, "y_move": 0, "zoom": 0}
    run = True
    single_press = [0, 0, 0]
    bodies = []
    horizontal_move = 0
    vertical_move = 0
    zoom = 1
    com_circle = COMCircle(WIDTH / 2, HEIGHT / 2, 5, [255, 0, 0])
    for i in range(0, BODY_COUNT - 1):
        bodies = spawn_body(random.randint(200, WIDTH), random.randint(100, HEIGHT),
                            15, (169, 169, 169), bodies, random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
    while run:
        clock.tick(MaxFps)
        keys = pygame.key.get_pressed()

        for i in range(0, len(single_press) - 1):
            single_press[i] = single_press_inc(single_press[i])

        clock.tick(MaxFps)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for i in single_press:
            single_press[single_press.index(i)] = single_press_inc(i)

        if keys[pygame.K_SPACE] and single_press[0] == 0:
            pause = True
            single_press[0] = 1

        if keys[pygame.K_a]:
            horizontal_move += 15

        if keys[pygame.K_d]:
            horizontal_move -= 15

        if keys[pygame.K_w]:
            vertical_move += 15

        if keys[pygame.K_s]:
            vertical_move -= 15

        if keys[pygame.K_q] and single_press[1] == 0:
            single_press[1] += 1
            zoom = 0.5

        if keys[pygame.K_e] and single_press[2] == 0:
            single_press[2] += 1
            zoom = 2

        for body1 in bodies:
            for body2 in bodies:
                gravity_calc(body1, body2)

        for i, body1 in enumerate(bodies):
            for j in range(i + 1, len(bodies)):
                body2 = bodies[j]
                if body1 != body2:
                    if math.hypot(abs(body1.x - body2.x), abs(body1.y - body2.y)) < body1.radius + body2.radius:
                        impact_calc(body1, body2)

        screen_move["x"] = (WIDTH + horizontal_move) / 2
        screen_move["y"] = (HEIGHT + vertical_move) / 2
        screen_move["x_move"] = horizontal_move
        screen_move["y_move"] = vertical_move
        screen_move["zoom"] = zoom
        calc_com_circle(bodies, com_circle)
        redraw(com_circle, bodies, screen_move)
        horizontal_move, vertical_move = 0, 0
        zoom = 1


mainloop()
>>>>>>> c7a0373bdb057c4134c1181a9f016fc771ee6792
pygame.QUIT