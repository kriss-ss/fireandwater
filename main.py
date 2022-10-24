import json

import pygame
import os

import creating_levels
import game
from creating_levels import Level
from game import Game


# загрузка изображения
def load_image(s, key=None):
    name = os.path.join("data", s)
    try:
        image = pygame.image.load(name).convert()
    except pygame.error as message:
        print("error with " + s, message)
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


# меню игры
class MainMenu:
    def __init__(self, width, height):
        self.cnt, self.flag_sound = 0, False
        self.run = False
        self.save_pos_flag_settings = False
        self.save_pos_flag_del = False
        self.make_inscriptions(width, height)

    # отображение текста с подсветкой
    def make_inscriptions(self, width, height, col_redactor=(255, 255, 255),
                          col_single=(255, 255, 255), col_online=(255, 255, 255),
                          col_reset=(255, 255, 255), flag_settings=False,
                          main_lvls_col=(255, 255, 255), user_lvls_col=(255, 255, 255)):
        self.start_screen(width, height)
        self.main_font = pygame.font.SysFont('Segoe Print', round(height // 5 * 0.3))
        if not self.flag_sound:
            file = sound_on_mouse \
                if flag_settings else sound_on
        else:
            file = sound_off_mouse \
                if flag_settings else sound_off
        self.setting_image = pygame.transform.scale(file, (100, 100))
        screen.blit(self.setting_image, (width * 0.89, height // 75))

        self.txt_online_btn = self.main_font.render('Игра по сети', True, col_online)
        screen.blit(self.txt_online_btn, (width // 75, height * 0.83))

        self.txt_redactor = self.main_font.render('Создать карту', True, col_redactor)
        screen.blit(self.txt_redactor, (width // 75, height * 0.9))

        self.txt_one_pc_btn = self.main_font.render('Один компьютер', True, col_single)
        screen.blit(self.txt_one_pc_btn, (width // 75, height * 0.76))

        reset_font = pygame.font.SysFont('Segoe Print', 20)
        self.txt_reset_stat = reset_font.render('Сбросить статистику', True, col_reset)
        screen.blit(self.txt_reset_stat, (width // 1.34, height * 0.962))
        if self.run:
            self.font = pygame.font.SysFont('Segoe Print', 40)
            self.plot = self.font.render('Сюжетные уровни', True, main_lvls_col)
            self.user_levels = self.font.render('Пользовательские', True, user_lvls_col)
            screen.blit(self.plot, (550, 675))
            screen.blit(self.user_levels, (550, 750))

        # all_title = fire + and + water
        font_for_title = pygame.font.SysFont('Comic Sans MS', round(height // 5 * 0.6))
        fire = font_for_title.render('Огонь', True, (255, 100, 0))
        screen.blit(fire, ((width - fire.get_width() * 2.15) // 2, round(height // 2.7)))
        _and_ = font_for_title.render('и', True, (255, 255, 255))
        screen.blit(_and_, (width // 2, round(height // 2.7)))
        water = font_for_title.render('Вода', True, (0, 100, 255))
        screen.blit(water, ((width + water.get_width() * 0.7) // 2, round(height // 2.7)))

    # обработка нажатий на текст
    def go_next(self, x, y, width, height):
        if width // 75 <= x <= width // 75 + self.txt_redactor.get_width() \
                and height * 0.92 <= y <= height:
            self.run = False
            self.creating_levels()
        elif width // 75 <= x <= width // 75 + self.txt_one_pc_btn.get_width() \
                and height * 0.78 <= y <= height * 0.84:
            self.run = False
            self.start_game()
        elif width // 75 <= x <= width // 75 + self.txt_online_btn.get_width() \
                and height * 0.85 <= y <= height * 0.91:
            self.run = False
            print("""Coming soon""")
        elif width // 1.34 <= x <= width // 1.34 + self.txt_reset_stat.get_width() \
                and height * 0.962 <= y <= height * 0.962 + self.txt_reset_stat.get_height():
            self.reset_stat()
            self.save_pos_flag_del = True
        elif width * 0.89 <= x <= width * 0.89 + width // 10 \
                and height // 75 <= y <= height // 75 + height // 8:
            self.run = False
            self.cnt = (self.cnt + 1) % 2
            self.set_music()

    # работа с музыкой
    def set_music(self):
        if self.cnt:
            self.flag_sound = True
            game.sound_flag = True
            creating_levels.sound_flag = True
            pygame.mixer.music.pause()
        else:
            self.flag_sound = False
            game.sound_flag = False
            creating_levels.sound_flag = False
            pygame.mixer.music.unpause()
        self.save_pos_flag_settings = True

    # подсветка текста
    def set_color(self, x, y, width, height):
        if width // 75 <= x <= width // 75 + self.txt_redactor.get_width() \
                and height * 0.92 <= y <= height * 0.99:
            self.make_inscriptions(width, height, col_redactor='yellow')
        elif width // 75 <= x <= width // 75 + self.txt_one_pc_btn.get_width() \
                and height * 0.78 <= y <= height * 0.83:
            self.make_inscriptions(width, height, col_single='yellow')
        elif width // 75 <= x <= width // 75 + self.txt_online_btn.get_width() \
                and height * 0.85 <= y <= height * 0.9:
            self.make_inscriptions(width, height, col_online='yellow')
        elif width // 1.34 <= x <= width // 1.34 + self.txt_reset_stat.get_width() \
                and height * 0.962 <= y <= height * 0.962 + self.txt_reset_stat.get_height():
            self.make_inscriptions(width, height, col_reset='yellow')
        elif width * 0.89 <= x <= width * 0.89 + width // 10 \
                and height // 75 <= y <= height // 75 + height // 8:
            self.make_inscriptions(width, height, flag_settings=True)
        else:
            self.save_pos_flag_settings = False
            self.save_pos_flag_del = False
            self.make_inscriptions(width, height)
        if self.run:
            if 550 <= x <= 550 + self.user_levels.get_width() \
                    and 750 <= y <= 750 + self.user_levels.get_height():
                self.make_inscriptions(width, height, user_lvls_col='yellow')
            elif 550 <= x <= 550 + self.plot.get_width() \
                    and 675 <= y <= 675 + self.plot.get_height():
                self.make_inscriptions(width, height, main_lvls_col='yellow')

    # сброс статистики
    def reset_stat(self):
        with open("levels_info.json") as f1:
            data = json.load(f1)
            data["current_level"] = "main_levels/1.txt"
            for i in range(2, 11):
                data[f"level_{i}"] = "locked"
            with open("levels_info.json", 'w') as f2:
                json.dump(data, f2)

    # начальный экран
    def start_screen(self, width, height):
        fon = pygame.transform.scale(background, (width, height))
        screen.blit(fon, (0, 0))

    # старт игры
    def start_game(self):
        name = self.first_select()
        if name:
            g = Game(name)
            g.flag_sound = self.flag_sound
            g.cnt_flag = self.cnt
            g.mainloop()
            if game.sound_flag is not None or creating_levels.sound_flag is not None:
                if game.sound_flag and creating_levels.sound_flag:
                    self.cnt = 1
                    self.flag_sound = True
                    game.sound_flag = True
                    creating_levels.sound_flag = True
                else:
                    self.cnt = 0
                    self.flag_sound = False
                    game.sound_flag = False
                    creating_levels.sound_flag = False
            self.make_inscriptions(1000, 840)

    # нажатие на один комьютер
    def first_select(self):
        self.run = True
        self.make_inscriptions(1000, 840, col_single='yellow')
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if event.button == 1 and 550 <= x <= 550 + self.plot.get_width() and \
                            675 <= y <= 675 + self.plot.get_height():
                        self.run = False
                        return os.path.join("main_levels", "1.txt")
                    elif event.button == 1 and 550 <= x <= 550 + self.user_levels.get_width() and \
                            750 <= y <= 750 + self.user_levels.get_height():
                        self.run = False
                        return game.prompt_file()[-17:]
                    else:
                        self.go_next(*event.pos, 1000, 840)
                if event.type == pygame.MOUSEMOTION:
                    self.set_color(*event.pos, 1000, 840)
                    break
            pygame.display.flip()

    # открытие меню с создание карт
    def creating_levels(self):
        level = Level(40, 31)
        level.flag_sound = self.flag_sound
        level.cnt_flag = self.cnt
        level.mainloop(level)
        if game.sound_flag is not None or creating_levels.sound_flag is not None:
            if game.sound_flag and creating_levels.sound_flag:
                self.cnt = 1
                self.flag_sound = True
            else:
                self.cnt = 0
                self.flag_sound = False


# основной запуск программы
if __name__ == '__main__':
    save_pos_flag = False
    sound_on_mouse = load_image("music_on_mouse.png", -1)
    sound_on = load_image("music_on.png", -1)
    sound_off_mouse = load_image("music_off_mouse.png", -1)
    sound_off = load_image("music_off.png", -1)
    background = load_image('main_menu_picture.jpg')
    pygame.init()
    size = 1000, 840
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('God_of_natural')
    main = MainMenu(*size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                main.go_next(*event.pos, *size)
                if main.save_pos_flag_settings:
                    main.make_inscriptions(*size, flag_settings=True)
                elif main.save_pos_flag_del:
                    main.make_inscriptions(*size, col_reset='yellow')
                else:
                    main.make_inscriptions(*size)
            if event.type == pygame.MOUSEMOTION:
                main.set_color(*event.pos, *size)
        pygame.display.flip()
    pygame.quit()
