# background_image_filename = '1.png'
#
# import pygame
# from pygame.locals import *
# from sys import exit
#
# pygame.init()
# screen = pygame.display.set_mode((640, 480), 0, 32)
# background = pygame.image.load(background_image_filename).convert()
#
# Fullscreen = False
#
# while True:
#
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             exit()
#     if event.type == KEYDOWN:
#         if event.key == K_f:
#             Fullscreen = not Fullscreen
#             if Fullscreen:
#                 screen = pygame.display.set_mode((640, 480), FULLSCREEN, 32)
#             else:
#                 screen = pygame.display.set_mode((640, 480), 0, 32)
#
#     screen.blit(background, (0, 0))
#     pygame.display.update()

import pygame
from pygame.locals import *
import math

class Brush:
    def __init__(self, screen):
        self.screen = screen
        self.color = (0, 0, 0)
        self.size = 1
        self.drawing = False
        self.last_pos = None
        self.space = 1
        # if style is True, normal solid brush
        # if style is False, png brush
        self.style = False
        # load brush style png
        # self.brush = pygame.image.load("brush.png").convert_alpha()
        # set the current brush depends on size
        # self.brush_now = self.brush.subsurface((0, 0), (1, 1))

    def start_draw(self, pos):
        self.drawing = True
        self.last_pos = pos

    def end_draw(self):
        self.drawing = False

    def set_brush_style(self, style):
        print("* set brush style to", style)
        self.style = style

    def get_brush_style(self):
        return self.style

    def set_size(self, size):
        if size < 0.5:
            size = 0.5
        elif size > 50:
            size = 50
        print("* set brush size to", size)
        self.size = size
        self.brush_now = self.brush.subsurface((0, 0), (size * 2, size * 2))

    def get_size(self):
        return self.size

    def draw(self, pos):
        if self.drawing:
            for p in self._get_points(pos):
                # draw eveypoint between them
                if not self.style:
                    pygame.draw.circle(self.screen,
                                       self.color, p, self.size)
                else:
                    raise NotImplemented('brush not implemented!')
                    # self.screen.blit(self.brush_now, p)

            self.last_pos = pos

    def _get_points(self, pos):
        """ Get all points between last_point ~ now_point. """
        points = [(self.last_pos[0], self.last_pos[1])]
        len_x = pos[0] - self.last_pos[0]
        len_y = pos[1] - self.last_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        step_x = len_x / length
        step_y = len_y / length
        for i in range(int(length)):
            points.append(
                (points[-1][0] + step_x, points[-1][1] + step_y))
        points = map(lambda x: (int(0.5 + x[0]), int(0.5 + x[1])), points)
        # return light-weight, uniq list
        return list(set(points))

class Painter:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), 0, 32)
        pygame.display.set_caption("Painter")
        self.clock = pygame.time.Clock()
        self.brush = Brush(self.screen)

    def run(self):
        self.screen.fill((255, 255, 255))
        while True:
            # max fps limit
            self.clock.tick(120)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    # press esc to clear screen
                    if event.key == K_ESCAPE:
                        self.screen.fill((255, 255, 255))
                elif event.type == MOUSEBUTTONDOWN:
                    self.brush.start_draw(event.pos)
                elif event.type == MOUSEMOTION:
                    self.brush.draw(event.pos)
                elif event.type == MOUSEBUTTONUP:
                    self.brush.end_draw()
            pygame.display.update()


if __name__ == '__main__':
    app = Painter()
    app.run()