import pygame
import os
import tkinter.filedialog
import json
import creating_levels

# const
barriers_cords = []
buttons_cords = []
barriers = []
buttons = []
# музыка
sound_flag = None
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.music.load("sounds/music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)
jump = pygame.mixer.Sound("sounds/jump.ogg")
jump.set_volume(0.5)
death = pygame.mixer.Sound("sounds/death.wav")
death.set_volume(0.5)
win_end = pygame.mixer.Sound("sounds/win.wav")
win_end.set_volume(0.5)

# работа с окном
pygame.init()
size = 1000, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption("@godofnatural")
screen.fill("black")
clock = pygame.time.Clock()
fps = 60

# группы спрайтов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
heroes = pygame.sprite.Group()
boxes = pygame.sprite.Group()
btns = pygame.sprite.Group()
bars = pygame.sprite.Group()
red_portal = pygame.sprite.Group()
blue_portal = pygame.sprite.Group()
water = pygame.sprite.Group()
lava = pygame.sprite.Group()
poison = pygame.sprite.Group()
fake_bars = pygame.sprite.Group()
fake_platforms = pygame.sprite.Group()
water_jumping_start = pygame.USEREVENT + 1
fire_jumping_start = pygame.USEREVENT + 2


# загрузка фото
def load_image(s, key=None):
    name = os.path.join("data", s)
    try:
        image = pygame.image.load(name).convert()
    except pygame.error as message:
        print("error with " + s)
        raise SystemExit(message)
    if key is not None:
        if key == -1:
            key = image.get_at((0, 0))
            image.set_colorkey(key)
        elif key == -2:
            key = image.get_at((0, 0))
            image.set_colorkey(key)
            key = image.get_at((949, 0))
            image.set_colorkey(key)
    else:
        image = image.convert_alpha()
    return image


PL = load_image("stone.png")
lava_block = load_image('lava-block.png')
water_block = load_image('water-block.png')
poison_block = load_image('poison-block.png')


# меню выбора файла из проводника
def prompt_file():
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=(("text files", "*.txt"),),
                                                   title="Выберите уровень",
                                                   initialdir="levels/", multiple=False)
    top.destroy()
    return file_name


# персонажы
class Heroes(pygame.sprite.Sprite):
    def __init__(self, x, y, hero):
        super().__init__(all_sprites)
        self.x = x
        self.y = y
        self.add(heroes)
        self.hero = hero
        self.frames = []
        if self.hero == "fire":
            self.cut_sheet(load_image("fire-sheet1.png", -1), 5, 2)
        else:
            self.cut_sheet(load_image("water-sheet1.png", -1), 5, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (48, 80))
        self.rect.x = x
        self.rect.y = y
        self.jump_flag = False
        self.in_portal = False
        self.on_button = False
        self.lose = False
        # self.is_win = False
        self.under_bar = False
        self.music_flag = True
        self.index = (-100, -100)

    # нарезка анимации
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # анимация
    def animation(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (50, 80))
        x = self.rect.x
        y = self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    # гравитация
    def update(self):
        if self.rect.y >= 824:
            self.lose = True
        if not pygame.sprite.spritecollideany(self, platforms) \
                and not pygame.sprite.spritecollideany(self, boxes) and not \
                pygame.sprite.spritecollideany(self, bars) and not pygame.sprite.spritecollideany(self, btns) \
                and not self.under_bar:
            self.rect = self.rect.move(0, 200 / fps)
        for block in barriers:
            for bar in block:
                if pygame.sprite.collide_mask(self, bar) and not bar.bar_max and \
                        (pl1.on_button or pl2.on_button or box1.on_button) and not \
                        self.under_bar and not bar.bar_min:
                    self.rect = self.rect.move(0, - 120 / fps)
                    break
        if (self.hero == "fire" and pygame.sprite.spritecollideany(self, red_portal)) or \
                (self.hero == "water" and pygame.sprite.spritecollideany(self, blue_portal)):
            self.in_portal = True
        else:
            self.in_portal = False
        if self.hero == "fire" and pygame.sprite.spritecollideany(self, water) or \
                self.hero == "water" and pygame.sprite.spritecollideany(self, lava) or \
                pygame.sprite.spritecollideany(self, poison):
            self.lose = True

        for block in buttons_cords:
            for i, j in block:
                if (i - 1) * 24 <= self.rect.x - 20 <= (i + 1) * 24 and \
                        j * 24 <= self.rect.y <= (j + 1) * 24:
                    self.on_button = True
                    ind_bl = buttons_cords.index(block)
                    self.index = (ind_bl, buttons_cords[ind_bl].index((i, j)))
                    return
                else:
                    self.on_button = False
                    self.index = (-100, -100)

    # движение вправо
    def right(self):
        self.rect = self.rect.move(4, -5)
        box1.rect = box1.rect.move(0, -5)
        if not pygame.sprite.spritecollideany(self, platforms) \
                and not pygame.sprite.spritecollideany(self, bars) \
                and not (pygame.sprite.spritecollideany(self, boxes)
                         and abs(self.rect.y - box1.rect.y + 45) <= 5
                         and pygame.sprite.spritecollideany(box1, platforms)):
            self.rect = self.rect.move(200 / fps, 0)
        box1.rect = box1.rect.move(0, 5)
        self.rect = self.rect.move(-4, 5)

    # движение влево
    def left(self):
        self.rect = self.rect.move(-4, -5)
        box1.rect = box1.rect.move(-4, -5)
        if not pygame.sprite.spritecollideany(self, platforms) \
                and not pygame.sprite.spritecollideany(self, bars) \
                and not (pygame.sprite.spritecollideany(self, boxes)
                         and abs(self.rect.y - box1.rect.y + 45) <= 5
                         and pygame.sprite.spritecollideany(box1, platforms)):
            self.rect = self.rect.move(-(200 / fps), 0)
        box1.rect = box1.rect.move(4, 5)
        self.rect = self.rect.move(4, 5)

    # прыжок
    def jump(self):
        self.rect = self.rect.move(0, -5)
        if not pygame.sprite.spritecollideany(self, platforms):
            self.rect = self.rect.move(0, -300 / fps)
        else:
            self.jump_flag = False
        self.rect = self.rect.move(0, 5)


# платформа(составляет стены, пол уровня, остальные препятствия)
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, flag=False):
        super().__init__(all_sprites)
        self.add(platforms)
        self.image = PL
        if flag:
            self.image = pygame.transform.scale(self.image, (24, 12))
        else:
            self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


# плотный блок
class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(boxes)
        self.image = load_image("box.png")
        self.image = pygame.transform.scale(self.image, (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)
        self.on_button = False
        self.index = (-100, -100)

    # гравитация и коллизия
    def update(self):
        for block in barriers:
            for bar in block:
                if pygame.sprite.collide_mask(self, bar) and not bar.bar_max and \
                        (pl1.on_button or pl2.on_button or box1.on_button) and not bar.bar_min:
                    self.rect = self.rect.move(0, - 120 / fps)
                    break
        if not pygame.sprite.spritecollideany(self, platforms) and \
                not pygame.sprite.spritecollideany(self, bars) and \
                not pygame.sprite.spritecollideany(self, btns):
            self.rect = self.rect.move(0, 200 / fps)
        for block in buttons_cords:
            for x, y in block:
                if (x - 0.5) * 24 <= self.rect.x - 20 <= (x + 1) * 24 and \
                        y * 24 <= self.rect.y - 33 <= (y + 1) * 24:
                    self.on_button = True
                    ind_bl = buttons_cords.index(block)
                    self.index = (ind_bl, buttons_cords[ind_bl].index((x, y)))
                    return
                else:
                    self.on_button = False
                    self.index = (-100, -100)

    # движение вправо
    def right(self):
        self.rect = self.rect.move(1, -5)
        if not pygame.sprite.spritecollideany(self, platforms):
            if (pygame.sprite.collide_mask(self, pl1) and
                self.rect.y < pl1.rect.y + 45 < self.rect.y + 35) \
                    or (pygame.sprite.collide_mask(self, pl2)
                        and self.rect.y < pl2.rect.y + 45 < self.rect.y + 35):
                self.rect = self.rect.move(200 / fps, 0)
        self.rect = self.rect.move(-1, 5)

    # движение влево
    def left(self):
        self.rect = self.rect.move(-1, -5)
        if not pygame.sprite.spritecollideany(self, platforms):
            if (pygame.sprite.collide_mask(self, pl1) and
                self.rect.y < pl1.rect.y + 45 < self.rect.y + 35) \
                    or (pygame.sprite.collide_mask(self, pl2)
                        and self.rect.y < pl2.rect.y + 45 < self.rect.y + 35):
                self.rect = self.rect.move(-(200 / fps), 0)
        self.rect = self.rect.move(1, 5)


# создаёт барьер
class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(bars)
        self.image = load_image("barrier.png")
        self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect()
        self.start_rect = y
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)
        self.bar_max = False
        self.down_motion = False
        self.bar_min = False

    # подъем вверх
    def up(self):
        self.down_motion = False
        self.bar_min = False
        if self.rect.y > self.start_rect - 120:
            self.rect.y -= 120 / fps
            self.bar_max = False
        else:
            self.bar_max = True

    # подъем вниз
    def down(self):
        if not (pl1.under_bar and pl2.under_bar):
            self.down_motion = True
            self.bar_max = False
            if self.rect.y < self.start_rect:
                self.rect.y += 120 / fps
                self.bar_min = False
            else:
                self.bar_min = True


class FakeBarrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(fake_bars)
        self.image = load_image("barrier.png")
        self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect()
        self.start_rect = y
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)


class FakePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(fake_platforms)
        self.image = PL
        self.image = pygame.transform.scale(self.image, (24, 24))
        self.rect = self.image.get_rect()
        self.start_rect = y
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)


# Создание кнопки, активирующей движения барера
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.add(btns)
        self.image = load_image("activate_button.png", -1)
        self.image = pygame.transform.scale(self.image, (48, 12))
        self.rect = self.image.get_rect()
        self.start_rect = y
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)

    def down(self):
        if self.rect.y < self.start_rect + 4:
            self.rect.y += 60 / fps

    def up(self):
        if self.rect.y > self.start_rect:
            self.rect.y -= 60 / fps


# Конечный выход с уровня
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, type_of):
        super().__init__()
        if type_of == "red":
            self.add(red_portal)
        elif type_of == "blue":
            self.add(blue_portal)
        self.image = load_image(f"portal_{type_of}.png", -1)
        self.image = pygame.transform.scale(self.image, (48, 72))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        all_sprites.add(self)
        self.mask = pygame.mask.from_surface(self.image)


class Final(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = load_image('final.png', -1)
        self.image = pygame.transform.scale(self.image, (96, 96))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(blue_portal), self.add(red_portal)
        self.mask = pygame.mask.from_surface(self.image)


# жидкости
class Liquids(pygame.sprite.Sprite):
    def __init__(self, x, y, type_of):
        super().__init__(all_sprites)
        if type_of == "lava":
            self.image = lava_block
            self.add(lava)
            self.add(lava)
            self.image = lava_block
        elif type_of == "water":
            self.image = water_block
            self.add(water)
            self.add(water)
        else:
            self.image = poison_block
            self.add(poison)
            self.add(poison)
        self.image = pygame.transform.scale(self.image, (24, 12))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.Mask(size=(self.rect.x, 12))


# загрузка уровня
class Game:
    def __init__(self, name):
        self.fon = ''
        self.name = name
        self.running = True
        self.cnt_flag = 0
        self.flag_sound = False
        self.final_screen_win = False
        self.final_screen_lose = False
        self.col_retry = False
        self.col_set_lvl = False
        self.col_next = False
        self.col_exit = False
        self.new_lvl = True
        self.win = False
        self.death = False
        self.final_win = False
        self.barriers_cords = []
        self.buttons_cords = []
        self.barriers = []
        self.buttons = []
        self.load_pictures()
        self.default()

    # загрузка картинок
    def load_pictures(self):
        self.fon = pygame.transform.scale(load_image('fon_for_game.png'), (926, 720))
        self.PL = load_image("stone.png")
        self.exit_mouse = pygame.transform.scale(load_image('exit_mouse.png', -1), (150, 150))
        self.exit = pygame.transform.scale(load_image('exit.png', -1), (150, 150))
        self.play_mouse = load_image('play_mouse.png', -1)
        self.play = load_image('play.png', -1)
        self.retry_mouse = pygame.transform.scale(load_image('retry_mouse.png', -1), (150, 150))
        self.retry = pygame.transform.scale(load_image('retry.png', -1), (150, 150))
        self.what_mouse = load_image('how_to_play_mouse.png', -1)
        self.what = load_image('how_to_play.png', -1)
        self.sound_on_mouse = load_image('music_on_mouse.png', -1)
        self.sound_on = load_image('music_on.png', -1)
        self.sound_off_mouse = load_image('music_off_mouse.png', -1)
        self.sound_off = load_image('music_off.png', -1)
        self.bar = load_image('barrier.png', -1)
        self.btn = load_image('activate_button.png', -1)
        self.r_portal = load_image('portal_red.png', -1)
        self.b_portal = load_image('portal_blue.png', -1)
        self.w_b = load_image('water-block.png', -1)
        self.f_b = load_image('lava-block.png', -1)
        self.p_b = load_image('poison-block.png', -1)
        self.box = load_image('box.png', -1)
        self.fire = load_image('fire-bg.png', -1)
        self.water = load_image('water-bg.png', -1)
        self.set_lvl = pygame.transform.scale(load_image('set_lvl.png', -1), (150, 150))
        self.set_lvl_mouse = pygame.transform.scale(load_image('set_lvl_mouse.png', -1), (150, 150))
        self.next_lvl = pygame.transform.scale(load_image('next_lvl.png', -1), (150, 150))
        self.next_lvl_mouse = pygame.transform.scale(load_image('next_lvl_mouse.png', -1), (150, 150))
        self.close = pygame.transform.scale(load_image('close.png', -1), (75, 75))
        self.close_mouse = pygame.transform.scale(load_image('close_mouse.png', -1), (75, 75))
        self.pause = load_image('pause.png', -1)
        self.pause_mouse = load_image('pause_mouse.png', -1)

    # обнуление групп и констант
    def default(self):
        all_sprites.empty()
        platforms.empty()
        heroes.empty()
        boxes.empty()
        btns.empty()
        bars.empty()
        red_portal.empty()
        blue_portal.empty()
        water.empty()
        lava.empty()
        poison.empty()
        buttons_cords.clear()
        barriers_cords.clear()
        barriers.clear()
        buttons.clear()
        fake_platforms.empty()
        fake_platforms.empty()
        self.final_screen_win = False
        self.final_screen_lose = False

    # пауза в игре
    def stop_game(self):
        new_screen = pygame.display.set_mode((1000, 840))
        new_screen.fill("black")
        run = True
        s_c_retry, s_c_play, s_c_exit, s_c_music, s_c_what = False, False, False, False, False
        font = pygame.font.SysFont('Segoe Print', 75)
        text = font.render('Игра приостановлена', True, (255, 255, 255))
        new_screen.blit(text, ((1000 - text.get_width()) // 2, 50))
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    if 100 <= x <= 300 and 290 <= y <= 490:
                        s_c_exit = True
                    else:
                        s_c_exit = False
                    if 400 <= x <= 600 and 290 <= y <= 490:
                        s_c_play = True
                    else:
                        s_c_play = False
                    if 700 <= x <= 900 and 290 <= y <= 490:
                        s_c_retry = True
                    else:
                        s_c_retry = False
                    if 250 <= x <= 450 and 540 <= y <= 740:
                        s_c_what = True
                    else:
                        s_c_what = False
                    if 550 <= x <= 750 and 540 <= y <= 740:
                        s_c_music = True
                    else:
                        s_c_music = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if 100 <= x <= 300 and 290 <= y <= 490:
                        self.running = False
                        run = False
                    elif 400 <= x <= 600 and 290 <= y <= 490:
                        run = False
                    elif 700 <= x <= 900 and 290 <= y <= 490:
                        self.new_lvl = True
                        return
                    elif 550 <= x <= 750 and 540 <= y <= 740:
                        self.cnt_flag = (self.cnt_flag + 1) % 2
                        self.set_music()
                        new_screen.fill((0, 0, 0))
                        new_screen.blit(text, ((1000 - text.get_width()) // 2, 50))
                    elif 250 <= x <= 450 and 540 <= y <= 740:
                        self.do_info()
                        new_screen.fill((0, 0, 0))
                        new_screen.blit(text, ((1000 - text.get_width()) // 2, 50))
                        s_c_what = False
                        break
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            btn_exit = self.exit_mouse if s_c_exit else self.exit
            btn_exit = pygame.transform.scale(btn_exit, (200, 200))
            screen.blit(btn_exit, (100, 290))
            btn_play = self.play_mouse if s_c_play else self.play
            btn_play = pygame.transform.scale(btn_play, (200, 200))
            screen.blit(btn_play, (400, 290))
            btn_retry = self.retry_mouse if s_c_retry else self.retry
            btn_retry = pygame.transform.scale(btn_retry, (200, 200))
            screen.blit(btn_retry, (700, 290))
            if not self.flag_sound:
                btn_music = self.sound_on_mouse if s_c_music else self.sound_on
            else:
                btn_music = self.sound_off_mouse if s_c_music else self.sound_off
            btn_music = pygame.transform.scale(btn_music, (200, 200))
            screen.blit(btn_music, (550, 540))
            btn_info = self.what_mouse if s_c_what else self.what
            btn_info = pygame.transform.scale(btn_info, (200, 200))
            screen.blit(btn_info, (250, 540))
            pygame.display.flip()

    # работа с музыкой
    def set_music(self):
        global sound_flag
        if self.cnt_flag:
            self.flag_sound = True
            pygame.mixer.music.pause()
            sound_flag = True
            creating_levels.sound_flag = True
        else:
            self.flag_sound = False
            pygame.mixer.music.unpause()
            sound_flag = False
            creating_levels.sound_flag = False

    # текст + картинки
    def set_text_image(self, screen, photo, font_size, x_size, y_size, txt1,
                       blit_txt_x1, blit_txt_y1, blit_photo_x, blit_photo_y):
        photo = pygame.transform.scale(photo, (x_size, y_size))
        font = pygame.font.SysFont('Segoe print', font_size)
        text1 = font.render(txt1, True, (255, 255, 255))
        screen.blit(text1, (blit_txt_x1, blit_txt_y1))
        screen.blit(photo, (blit_photo_x, blit_photo_y))

    # текст
    def set_text(self, screen, font_size, text, text_x, text_y, color=(255, 255, 255)):
        font = pygame.font.SysFont('Segoe print', font_size)
        text = font.render(text, True, color)
        screen.blit(text, (text_x, text_y))

    # инструкция в паузе
    def do_info(self):
        screen.fill("black")
        pygame.display.flip()

        font = pygame.font.SysFont('Segoe print', 30)
        text = font.render('Информация об объектах', True, (153, 255, 153))
        screen.blit(text, (500 - text.get_width() // 2, 10))

        self.set_text_image(screen, self.PL, 20, 30, 30, "платформа, на которой можно стоять", 75, 60, 20, 60)
        self.set_text_image(screen, self.bar, 20, 30, 30, 'движущийся барьер, который можно активировать кнопкой', 75,
                            100, 20, 100)
        self.set_text_image(screen, self.btn, 20, 30, 15, "активирующая барьер кнопка, \
при нажатии на неё немного опускается", 75, 140, 20, 150)
        self.set_text_image(screen, self.r_portal, 20, 30, 30, 'портал завершения уровня для огня', 75, 180, 20, 180)
        self.set_text_image(screen, self.b_portal, 20, 30, 30, 'портал завершения уровня для воды', 75, 220, 20, 220)
        self.set_text_image(screen, self.w_b, 20, 30, 30, "блок воды, при попадании в который персонаж огоня умирает",
                            75, 260, 20, 260)
        self.set_text_image(screen, self.f_b, 20, 30, 30, 'блок лавы, при попадании в который персонаж воды умирает',
                            75, 300, 20, 300)
        self.set_text_image(screen, self.p_b, 20, 30, 30, 'блок яда, при попадании \
в который любой из персонажей умирает', 75, 340, 20, 340)
        self.set_text_image(screen, self.box, 20, 30, 30, 'объект, котрый можно толкать при взаимодействии \
в сторону движения персонажа', 75, 380, 20, 380)
        self.set_text_image(screen, self.fire, 20, 30, 50, 'главные герои', 75,
                            460, 20, 420)
        screen.blit(pygame.transform.scale(self.water, (30, 50)), (20, 480))

        self.set_text(screen, 30, 'Управление', 410, 530, (153, 255, 153))
        self.set_text(screen, 30, 'Вода', 153, 560, (0, 100, 255))
        self.set_text(screen, 30, 'Огонь', 753, 560, (255, 100, 0))
        self.set_text(screen, 30, '-->  движение вправо', 20, 620)
        self.set_text(screen, 30, '<--  движение влево', 20, 670)
        self.set_text(screen, 40, '|    прыжок', 40, 720)
        self.set_text(screen, 40, '^', 36, 705)
        self.set_text(screen, 30, 'D  движение вправо', 650, 620)
        self.set_text(screen, 30, 'A  движение влево', 650, 670)
        self.set_text(screen, 40, 'W  прыжок', 650, 720)
        self.set_text(screen, 30, 'ESC пауза', 420, 770, (255, 0, 0))

        screen.blit(self.close, (900, 25))
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    if 900 <= x <= 975 and 25 <= y <= 100:
                        screen.blit(self.close_mouse, (900, 25))
                    else:
                        screen.blit(self.close, (900, 25))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 900 <= x <= 975 and 25 <= y <= 100 and event.button == 1:
                        return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            pygame.display.flip()

    def draw_levels(self):
        # pl1.in_portal = False
        # pl2.in_portal = False
        size = 1000, 440
        screen = pygame.display.set_mode(size)
        screen.fill('black')
        font = pygame.font.SysFont('Segoe print', 100)
        top = 50
        left = 50
        n = 1
        with open("levels_info.json", "r") as f:
            data = json.load(f)
            for i in range(2):
                for k in range(5):
                    if data[f"level_{n}"] == "opened":
                        text = font.render(str(n), True, (255, 255, 254))
                        pygame.draw.rect(screen, color=(15, 82, 186), rect=(left + 190 * k, top + 200 * i, 140, 140),
                                         border_radius=40)
                    else:
                        text = font.render(str(n), True, (255, 255, 255))
                        pygame.draw.rect(screen, color=(128, 128, 128), rect=(left + 190 * k, top + 200 * i, 140, 140),
                                         border_radius=40)
                    if n == 10:
                        screen.blit(text, (left + 190 * k - 5, top + 200 * i - 20))
                    else:
                        screen.blit(text, (left + 190 * k + 40, top + 200 * i - 20))
                    n += 1
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if screen.get_at((x, y))[:3] in ((255, 255, 254), (15, 82, 186)):
                        x = (x - 50 * (x // 190 + 1)) // 140 + 1
                        y = (y - 50 * (y // 190 + 1)) // 140
                        if not sound_flag:
                            pygame.mixer.music.unpause()
                        with open("levels_info.json") as f:
                            data = json.load(f)
                            data["current_level"] = f"main_levels/{x + y * 5}.txt"
                            with open("levels_info.json", "w") as f2:
                                json.dump(data, f2)
                            run = False
                            self.new_lvl = True
                            size = 1000, 840
                            pygame.display.set_mode(size)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    size = 1000, 840
                    pygame.display.set_mode(size)
                    self.running = False
                    return
            pygame.display.flip()

    # загрузка уровня из файла
    def load_level(self):
        screen.fill('black')
        font = pygame.font.SysFont('Segoe Print', 30)
        with open("levels_info.json") as f2:
            name = json.load(f2)["current_level"]
            if 'user' not in name:
                num = name.split('/')[1][:name.split('/')[1].index('.')]
            else:
                num = name[name.index('_') + 1:name.index('.')]
            if num == '10':
                self.final_win = True
            self.fon = pygame.transform.scale(pygame.image.load(f'caves/{num}.jpg'), (926, 720))
            level_text = font.render(f"Уровень {num}", True, (255, 255, 255))
            screen.blit(level_text, (20, 10))
            with open(name) as f:
                rows = f.readlines()
                for row in rows[rows.index('\n') + 1:]:
                    if len(row) > 3:
                        block_bar = [tuple(map(int, k.split(', ')))
                                     for k in row.split('; ')[0].replace('\n', '')[2:-2].split('), (')]
                        block_btn = [tuple(map(int, k.split(', ')))
                                     for k in row.split('; ')[1].replace('\n', '')[2:-2].split('), (')]
                        barriers_cords.append(block_bar)
                        buttons_cords.append(block_btn)
                for block_cords in barriers_cords:
                    block_bar = []
                    for x, y in block_cords:
                        bar = Barrier(20 + x * 24, 80 + y * 24)
                        block_bar.append(bar)
                    barriers.append(block_bar)
                for block_cords in buttons_cords:
                    block_btn = []
                    for x, y in block_cords:
                        btn = Button(20 + x * 24, 80 + y * 24)
                        block_btn.append(btn)
                    buttons.append(block_btn)
                for i in range(len(rows[:rows.index('\n')])):
                    for j in range(len(rows[i])):
                        if rows[i][j] == "a":
                            Platform(20 + j * 24, 80 + i * 24)
                        elif rows[i][j] in ["c", "f", "g", "h"]:
                            Platform(20 + j * 24, 92 + i * 24, True)
                            if rows[i][j] == 'c':
                                Platform(20 + (j + 1) * 24, 92 + i * 24, True)
                            else:
                                if rows[i][j] == "h":
                                    name = "poison"
                                elif rows[i][j] == 'f':
                                    name = "water"
                                else:
                                    name = "lava"
                                Liquids(20 + j * 24, 80 + i * 24, name)
                        elif rows[i][j] == "d":
                            Portal(20 + j * 24, 80 + i * 24, "red")
                        elif rows[i][j] == "e":
                            Portal(20 + j * 24, 80 + i * 24, "blue")
                        elif rows[i][j] == 'b' and all([True if (j, i) not in block else False
                                                        for block in barriers_cords]):
                            FakeBarrier(20 + j * 24, 80 + i * 24)
                        elif rows[i][j] == 'z':
                            FakePlatform(20 + j * 24, 80 + i * 24)
                        elif rows[i][j] == 'm':
                            Final(20 + j * 24, 80 + i * 24)
                for i in range(len(rows[:rows.index('\n')])):
                    for j in range(len(rows[i])):
                        if rows[i][j] == "i":
                            global box1
                            box1 = Box(20 + j * 24, 80 + i * 24)
                        elif rows[i][j] == "j":
                            global pl1
                            pl1 = Heroes(20 + j * 24, 80 + i * 24, "fire")
                        elif rows[i][j] == "k":
                            global pl2
                            pl2 = Heroes(20 + j * 24, 80 + i * 24, "water")

    # основной цикл
    def mainloop(self):
        self.running = True
        set_pause = False
        font = pygame.font.SysFont('Segoe Print', 30)
        level_text = font.render('Уровень 1', True, (255, 255, 255))
        screen.blit(level_text, (20, 10))
        anim = pygame.USEREVENT + 3
        pygame.time.set_timer(anim, 100)
        if "main" not in self.name:
            with open("levels_info.json") as f:
                data = json.load(f)
                data["current_level"] = self.name
                with open("levels_info.json", "w") as f2:
                    json.dump(data, f2)
        else:
            self.draw_levels()
        while self.running:
            if self.new_lvl:
                if not self.cnt_flag:
                    death.stop()
                    win_end.stop()
                    pygame.mixer.music.unpause()
                self.default()
                self.default_color_w_l()
                self.load_level()
                self.new_lvl = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    if not (self.final_screen_win or self.final_screen_lose):
                        if 930 <= x <= 990 and 10 <= y <= 70:
                            set_pause = True
                        else:
                            set_pause = False
                    if self.final_screen_win:
                        self.set_col_win(x, y)
                    elif self.final_screen_lose:
                        self.set_col_lose(x, y)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    if not (self.final_screen_win or self.final_screen_lose):
                        if 930 <= x <= 990 and 10 <= y <= 70:
                            self.stop_game()
                            set_pause = False
                            if self.running:
                                screen.fill((0, 0, 0))
                                screen.blit(level_text, (20, 10))
                            else:
                                return
                    if self.final_screen_win:
                        if 80 <= x <= 230 and 490 <= y <= 640:
                            win_end.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            return
                        elif 310 <= x <= 460 and 490 <= y <= 640:
                            win_end.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            self.final_screen_win = False
                            self.new_lvl = True
                        elif 540 <= x <= 690 and 490 <= y <= 640:
                            win_end.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            self.draw_levels()
                        elif 770 <= x <= 920 and 490 <= y <= 640:
                            self.new_lvl = True
                            with open("levels_info.json") as f:
                                data = json.load(f)
                                text = data["current_level"]
                                num = int(text[text.index('/') + 1:text.index('.')])
                                data["current_level"] = f'main_levels/{num + 1}.txt'
                                with open("levels_info.json", "w") as f2:
                                    json.dump(data, f2)
                                pl1.in_portal = False
                                pl2.in_portal = False
                    elif self.final_screen_lose:
                        if 137 <= x <= 287 and 490 <= y <= 640:
                            death.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            return
                        elif 425 <= x <= 575 and 490 <= y <= 640:
                            death.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            self.final_screen_lose = False
                            self.new_lvl = True
                        elif 712 <= x <= 862 and 490 <= y <= 640:
                            death.stop()
                            if not sound_flag:
                                pygame.mixer.music.unpause()
                            self.draw_levels()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.jump_test(pl2):
                        pygame.time.set_timer(water_jumping_start, 650)
                        if not self.cnt_flag:
                            jump.play()
                        pl2.jump_flag = True
                    if event.key in [pygame.K_w, pygame.K_SPACE] and self.jump_test(pl1):
                        pygame.time.set_timer(fire_jumping_start, 650)
                        if not self.cnt_flag:
                            jump.play()
                        pl1.jump_flag = True
                    if not (pl1.lose or pl1.lose) or not (pl1.in_portal and pl2.in_portal):
                        if event.key == pygame.K_ESCAPE:
                            self.stop_game()
                            if self.running:
                                screen.fill((0, 0, 0))
                                screen.blit(level_text, (20, 10))
                            else:
                                return
                if event.type == fire_jumping_start:
                    if not pl1.jump_flag:
                        pygame.time.set_timer(fire_jumping_start, 0)
                    else:
                        pl1.jump_flag = False
                if event.type == water_jumping_start:
                    if not pl2.jump_flag:
                        pygame.time.set_timer(water_jumping_start, 0)
                    else:
                        pl2.jump_flag = False
                if event.type == anim:
                    pl1.animation()
                    pygame.time.set_timer(anim, 100)
                    pl2.animation()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_d]:
                pl1.right()
                box1.right()
            if keys[pygame.K_a]:
                pl1.left()
                box1.left()
            if keys[pygame.K_RIGHT]:
                pl2.right()
                box1.right()
            if keys[pygame.K_LEFT]:
                pl2.left()
                box1.left()
            if pl1.jump_flag and not pl1.under_bar:
                pl1.jump()
            if pl2.jump_flag and not pl2.under_bar:
                pl2.jump()
            if pl1.on_button or pl2.on_button or box1.on_button:
                pl1.under_bar, pl2.under_bar = False, False
                ind = []
                for i in [pl1, pl2, box1]:
                    if i.index[0] != -100 and i.index not in ind:
                        ind.append(i.index)
                if buttons:
                    for x, y in ind:
                        buttons[x][y].down()
                        block = barriers[x]
                        for bar in block:
                            bar.up()
                    for x in range(len(buttons)):
                        for y in range(len(buttons[x])):
                            if (x, y) not in ind:
                                buttons[x][y].up()
                    for x in range(len(barriers)):
                        if x not in [j[0] for j in ind]:
                            for bar in barriers[x]:
                                bar.down()
            else:
                self.bar_move()
            pl1.music_flag = self.cnt_flag
            pl2.music_flag = self.cnt_flag
            if self.final_win and pl1.in_portal and pl2.in_portal:
                if not self.cnt_flag:
                    win_end.play()
                    pygame.mixer.music.pause()
                self.create_btns_lose(['Ты потрясающий'])
                pygame.display.flip()
                self.final_screen_lose = True
            elif pl1.lose or pl2.lose:
                if not self.cnt_flag:
                    death.play()
                    pygame.mixer.music.pause()
                self.create_btns_lose(['Попробуй снова'])
                pygame.display.flip()
                self.final_screen_lose = True
            elif pl1.in_portal and pl2.in_portal:
                if not self.cnt_flag:
                    win_end.play()
                    pygame.mixer.music.pause()
                self.create_btns_win(["Mission completed", "respect+"])
                with open("levels_info.json") as f1:
                    data = json.load(f1)
                    data[f"level_{int(data['current_level'].split('/')[1][0]) + 1}"] = "opened"
                    with open("levels_info.json", "w") as f2:
                        json.dump(data, f2)
                pygame.display.flip()
                self.final_screen_win = True
            else:
                screen.blit(self.fon, (44, 104))
                all_sprites.update()
                all_sprites.draw(screen)
                setting_image = pygame.transform.scale(self.pause
                                                       if not set_pause else self.pause_mouse, (60, 60))
                screen.blit(setting_image, (920, 10))
                pygame.display.flip()
                clock.tick(fps)

    def jump_test(self, hero):
        if pygame.sprite.spritecollideany(hero, platforms) or \
                pygame.sprite.spritecollideany(hero, bars) or \
                pygame.sprite.spritecollideany(hero, btns) or \
                pygame.sprite.spritecollideany(hero, boxes) or \
                pygame.sprite.spritecollideany(hero, lava) or \
                pygame.sprite.spritecollideany(hero, water) or \
                pygame.sprite.spritecollideany(hero, poison):
            return True
        else:
            return False

    def bar_move(self):
        for block in buttons:
            for btn in block:
                btn.up()
        for block in barriers:
            s = []
            for bar in block:
                s.append(bar.rect.y)
            for bar in block:
                if pygame.sprite.collide_mask(bar, pl1) and \
                        pl1.rect.y + 40 >= max(s) + 24 >= pl1.rect.y and bar.down_motion:
                    pl1.under_bar = True
                    return
                elif pygame.sprite.collide_mask(bar, pl2) and \
                        pl2.rect.y + 40 >= max(s) + 24 >= pl2.rect.y and bar.down_motion:
                    pl2.under_bar = True
                    return
                else:
                    pl1.under_bar, pl2.under_bar = False, False
        if not (pl1.under_bar or pl2.under_bar):
            for block in barriers:
                for bar in block:
                    bar.down()

    # создание кнопок в паузе при победе
    def create_btns_win(self, printings):
        screen.fill("black")
        font = pygame.font.SysFont('Segoe print', 75)
        for i in range(len(printings)):
            text = font.render(printings[i], True, (254, 150, 0))
            screen.blit(text, (500 - text.get_width() // 2, 50 + i * 100))
        screen.blit(self.exit_mouse if self.col_exit else self.exit, (80, 490))
        screen.blit(self.retry_mouse if self.col_retry else self.retry, (310, 490))
        screen.blit(self.set_lvl_mouse if self.col_set_lvl else self.set_lvl, (540, 490))
        screen.blit(self.next_lvl_mouse if self.col_next else self.next_lvl, (770, 490))

    # создание кнопок в паузе при смерти
    def create_btns_lose(self, printings):
        screen.fill("black")
        font = pygame.font.SysFont('Segoe print', 75)
        for i in range(len(printings)):
            text = font.render(printings[i], True, (254, 150, 0))
            screen.blit(text, (500 - text.get_width() // 2, 50 + i * 100))
        screen.blit(self.exit_mouse if self.col_exit else self.exit, (137, 490))
        screen.blit(self.retry_mouse if self.col_retry else self.retry, (425, 490))
        screen.blit(self.set_lvl_mouse if self.col_set_lvl else self.set_lvl, (712, 490))

    # нейтральный цвет для кнопок в меню побед/поражений
    def default_color_w_l(self):
        self.col_exit = False
        self.col_set_lvl = False
        self.col_retry = False
        self.col_next = False

    # подсветка кнопок в меню победы
    def set_col_win(self, x, y):
        if 80 <= x <= 230 and 490 <= y <= 640:
            self.col_exit = True
        elif 310 <= x <= 460 and 490 <= y <= 640:
            self.col_retry = True
        elif 540 <= x <= 690 and 490 <= y <= 640:
            self.col_set_lvl = True
        elif 770 <= x <= 920 and 490 <= y <= 640:
            self.col_next = True
        else:
            self.default_color_w_l()

    # подсветка кнопок в меню поражения
    def set_col_lose(self, x, y):
        if 137 <= x <= 287 and 490 <= y <= 640:
            self.col_exit = True
        elif 425 <= x <= 575 and 490 <= y <= 640:
            self.col_retry = True
        elif 712 <= x <= 812 and 490 <= y <= 640:
            self.col_set_lvl = True
        else:
            self.default_color_w_l()
