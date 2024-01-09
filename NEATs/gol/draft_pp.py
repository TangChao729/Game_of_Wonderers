import pygame

pygame.init()

screen_size = 500

screen = pygame.display.set_mode([screen_size, screen_size])

running = True

line_start = (430,470)
line_end = (630,670)

def get_lines(line_start, line_end, screen_size=500):

    lines = []
    lines.append((line_start, line_end))

    x1, y1 = line_start
    x2, y2 = line_end

    if x2 >= 0:
        new_line_start = (x1 - screen_size, y1)
        new_line_end = (x2 - screen_size, y2)
        lines.append((new_line_start, new_line_end))

    if x2 <= screen_size:
        new_line_start = (x1 + screen_size, y1)
        new_line_end = (x2 + screen_size, y2)
        lines.append((new_line_start, new_line_end))

    if y2 >= 0:
        new_line_start = (x1, y1 - screen_size)
        new_line_end = (x2, y2 - screen_size)
        lines.append((new_line_start, new_line_end))

    if y2 <= screen_size:
        new_line_start = (x1, y1 + screen_size)
        new_line_end = (x2, y2 + screen_size)
        lines.append((new_line_start, new_line_end))

    return lines

while running:

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        lines = get_lines(line_start, line_end)
        for line_start, line_end in lines:
            pygame.draw.line(screen, (255, 255, 255), line_start, line_end, 1)
        # pygame.draw.line(screen, (255, 255, 255), line_start, line_end, 1)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
