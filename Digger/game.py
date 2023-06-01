import numpy as np
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from PIL import ImageTk, Image

class GameMenu:
    def __init__(self, canvas):
        self.canvas = canvas
        self.canvas_width = canvas.winfo_width()
        self.canvas_height = canvas.winfo_height()

        self.new_game_button = Button(
            self.canvas, text="Новая игра", command=self.start_game,
            bg="#35682D", fg="white"
        )
        self.rules = Button(self.canvas, text="Правила", command=self.rules_game,
            bg="#35682D", fg="white")
        self.exit_button = Button(
            self.canvas, text="Выход", command=self.exit_game,
            bg="#35682D", fg="white"
        )

    def show(self):      
        self.new_game_button.config(width=25, height=3)
        self.rules.config(width=25, height=3)
        self.exit_button.config(width=25, height=3)
        self.new_game_button.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.rules.place(relx=0.5, rely=0.6, anchor=CENTER)
        self.exit_button.place(relx=0.5, rely=0.7 , anchor=CENTER)

    def start_game(self):
        self.canvas.delete("all")  
        self.canvas.unbind('<KeyPress>')
        self.canvas.unbind('<Button-1>')       
        game = Game(self.canvas)
        game.start()


    def exit_game(self):
        if messagebox.askyesno(title="Выход", message="Вы действительно хотите выйти из игры?"):
            self.canvas.quit()
    def rules_game(self):
        messagebox.showinfo(title="Правила",message="                      Правила игры Digger     \nВаша задача управлять машиной и сбоирать арлмазы\nВы не должны столкнуться с врагами\nЧтобы управлять машиной нажимайте на стрелочки на клаивиатуре"
                            )
class Mapa:
    def __init__(self, map_matrix, canvas_width, canvas_height):
        self.map_matrix = map_matrix
        self.dirt_image = PhotoImage(file="Assets/Texture/SpriteBlock.png")
        self.dirt_image = self.dirt_image.zoom(2)
        self.tile_size = self.dirt_image.width()
        self.width = canvas_width
        self.height = canvas_height
        self.tonnel_image = PhotoImage(file="Assets/Texture/BlackTonnel.png")
        self.tonnel_image = self.tonnel_image.zoom(2)
        self.diamond_image = PhotoImage(file="Assets/Texture/SpriteDiamonds.png")
        self.diamond_image = self.diamond_image.zoom(2)
        self.stone_image = PhotoImage(file="Assets/Texture/stone.png")
        self.stone_image = self.stone_image.zoom(2)
        self.dirty_rects = [] 
        

    def draw(self, canvas):
        canvas.config(width=self.width, height=self.height + 50, bg='black')
        self.dirty_rects = []  # Очищаем лист
        for y, row in enumerate(self.map_matrix):
            for x, cell in enumerate(row):
                self.draw_cell(canvas, x, y, cell)

    def draw_cell(self, canvas, x, y, cell):
        if cell == 0:
            rect= canvas.create_image(x * self.tile_size, self.height - (y + 1) * self.tile_size + self.tile_size / 2,
                                anchor=NW, image=self.dirt_image)
        elif cell == 1:
            rect =canvas.create_image(x * self.tile_size, self.height - (y + 1) * self.tile_size + self.tile_size / 2,
                                anchor=NW, image=self.tonnel_image)
        elif cell == 2:
            rect= canvas.create_image(x * self.tile_size, self.height - (y + 1) * self.tile_size + self.tile_size / 2,
                                anchor=NW, image=self.diamond_image)
        elif cell == 3:
            rect = canvas.create_image(x * self.tile_size, self.height - (y + 1) * self.tile_size + self.tile_size / 2,
                            anchor=NW, image=self.stone_image)
        
        self.dirty_rects.append(rect)
        return rect



class Player:
    def __init__(self, x, y, mapa, canvas, enemy1, enemy2, enemy3, score_label, map_matrix):
        self.x = x
        self.y = y
        self.mapa = mapa
        self.map_matrix = map_matrix
        self.player_image = PhotoImage(file="Assets/Texture/Carych.png")
        self.player_image = self.player_image.zoom(2)
        self.player_size = self.player_image.width()
        self.map_matrix = mapa.map_matrix
        self.canvas = canvas
        self.score_label = score_label
        self.score = 0
        self.enemy1 = enemy1
        self.enemy2 = enemy2
        self.enemy3 = enemy3
        self.canvas.bind('<KeyPress>', self.on_key_press)
        self.dirty_rects = []
        self.draw()
        self.root = root

    def draw(self):
        self.canvas_object = self.canvas.create_image(self.x, self.y, anchor=NW, image=self.player_image)
        self.canvas.create_window(10, self.canvas.winfo_height() - 598, anchor=NW, window=self.score_label)
        self.enemy1.draw()
        self.enemy2.draw()
        self.enemy3.draw()
    def check_collision(self):
        player_rect = self.canvas.bbox(self.canvas_object)
        for enemy in [self.enemy1, self.enemy2, self.enemy3]:
            enemy_rect = self.canvas.bbox(enemy.canvas_object)
            if self.is_collision(player_rect, enemy_rect):
                self.display_game_over_image()  # функция картинки
                self.canvas.bind('<Return>', self.return_to_menu)  # Биндим клавишу Enter 
                return True
        return False

    def is_collision(self, rect1, rect2):
        player_left, player_top, player_right, player_bottom = rect1
        enemy_left, enemy_top, enemy_right, enemy_bottom = rect2
        # Нижная сторона игрока над верхней стороной противника
        if player_bottom <= enemy_top:
            return False
        # Верхняя сторона игрока над нижней сторорой противника
        if player_top >= enemy_bottom:
            return False
        # Правая сторона игрока с левой стороной противника
        if player_right <= enemy_left:
            return False
        # ЛЕвая сторона игрока с правой стороной противника
        if player_left >= enemy_right:
            return False
        return True

    def move(self, dx, dy):
        # Вычисляем новые координаты игрока
        new_x = self.x + dx
        new_y = self.y + dy
        # Находяться ли координаты на границе холста
        if (
            new_x >= 0 and new_x <= self.canvas.winfo_width() - self.player_size
            and new_y >= 0 and new_y <= self.canvas.winfo_height() - self.player_size
        ):
            # Проверяем ячейку в которую перемещается игрок 
            row = int((self.mapa.height - new_y) / self.mapa.tile_size)
            col = int(new_x / self.mapa.tile_size)
            cell = self.map_matrix[row][col]


            # Игрок перемещается если ячейка не 3 
            if cell != 3:
                # Обновляем координаты игрока 
                self.x = new_x
                self.y = new_y
                if self.check_collision():
                    return 

                # Перемещяем игрока на холсте
                self.canvas.coords(self.canvas_object, self.x, self.y)

                # Проверяем что в ячейке содердится блок земли
                if cell == 0:
                    self.map_matrix[row][col] = 1
                    self.mapa.map_matrix = self.map_matrix
                    self.mapa.draw(self.canvas)
                    self.draw()

                # Проверяем что в ячейке содержится блок алмаза 
                elif cell == 2:
                    self.map_matrix[row][col] = 1
                    self.mapa.map_matrix = self.map_matrix
                    self.mapa.draw(self.canvas)
                    self.draw()
                    self.score += 1
                    self.score_label.config(text=f"Счет: {self.score}")

                    # Проверяем, что все алмазы собраны
                    remaining_diamonds = np.count_nonzero(self.map_matrix == 2)
                    if remaining_diamonds == 0:
                        self.canvas.delete("all")
                        self.display_victory_image()
    def return_to_menu(self, event=None):
        self.canvas.config(bg='#FFC018')
        self.canvas.delete("all") 
        self.canvas.unbind('<Return>')
        menu = GameMenu(self.canvas)  
        menu.show()
    
           
    def display_victory_image(self):
        victory_image = Image.open("Assets/Texture/Winn.png")
        self.canvas.bind('<Return>', self.return_to_menu)
        # меняем размер картинки под холст
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        resized_image = victory_image.resize((canvas_width, canvas_height))
        image_tk = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk
    def display_game_over_image(self):
        game_over_image = Image.open("Assets/Texture/gameover.png")
        self.canvas.bind('<Return>', self.return_to_menu)  
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        resized_image = game_over_image.resize((canvas_width, canvas_height))
        image_tk = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

    def on_key_press(self, event):
        if event.keysym == 'Up':
            self.move(0, -7)
        elif event.keysym == 'Down':
            self.move(0, 7)
        elif event.keysym == 'Left':
            self.move(-7, 0)
        elif event.keysym == 'Right':
            self.move(7, 0)
class Game:
    def __init__(self, root):
        self.сanvas = Canvas
        self.canvas = Canvas(root)
        self.canvas.pack()
        self.canvas.focus_set()
        self.score_label = Label(root, text="Счет: 0", font=("Arial", 20), fg="white", bg="black")

        self.map_matrix = np.array([
            [3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3],
            [3, 0, 2, 0, 3, 0, 0, 1, 0, 2, 2, 3],
            [1, 1, 1, 1, 1, 0, 0, 1, 0, 2, 0, 3],
            [3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3],
            [3, 3, 3, 3, 0, 0, 0, 1, 1, 1, 1, 1],
            [3, 2, 2, 3, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 0, 0, 3, 1, 0, 0, 0, 3, 3, 3, 3],
            [3, 0, 1, 1, 1, 1, 1, 0, 0, 0, 2, 3],
            [3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 3],
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
        ])

        self.mapa = Mapa(self.map_matrix, 770, 600)
        self.enemy1 = Enemy(740, 350, self.mapa, self.canvas, [(470, 280)])
        self.enemy2 = Enemy(30, 465, self.mapa, self.canvas, [(280, 407)])
        self.enemy3 = Enemy(480, 570, self.mapa, self.canvas, [(450, 360)])
        self.player = None

    def start(self):
        self.mapa.draw(self.canvas)
        self.player = Player(260, 160, self.mapa, self.canvas, self.enemy1, self.enemy2, self.enemy3, self.score_label, self.map_matrix)
        self.enemy1.move_x()
        self.enemy2.move_x()
        self.enemy3.move_y()
        self.canvas.bind('<KeyPress>', self.player.on_key_press) 
        self.canvas.pack()

    def return_to_menu(self, event=None):
        self.canvas.config(bg='#FFC018')
        self.canvas.delete("all") 
        self.canvas.unbind('<Return>')
        menu = GameMenu(self.canvas) 
        menu.show()


class Enemy:
    def __init__(self, x, y, mapa, canvas, target_coordinates):
        self.x = x
        self.y = y
        self.initial_coordinates = (x, y)  # Сохраняем начальные координаты
        self.direction = 1
        self.mapa = mapa
        self.image = PhotoImage(file="Assets/Texture/Spriteenemy15.png")
        self.canvas_object = canvas.create_image(self.x, self.y, image=self.image)
        self.image = self.image.zoom(2)
        self.enemy_size = self.image.width()
        self.map_matrix = mapa.map_matrix
        self.canvas = canvas
        self.target_coordinates = target_coordinates
        self.target_index = 0
        self.direction = 1

    def draw(self):
        self.canvas_object = self.canvas.create_image(self.x, self.y, image=self.image)

    def move_x(self):
        target_x = self.target_coordinates[self.target_index][0]
        if self.direction == 1:  # Движенеи вперед
            if self.x < target_x:
                self.x += 1
            elif self.x > target_x:
                self.x -= 1
            else:
                self.direction = -1  # Меняем направление
                self.target_index += 1  # Переходим к следующей цели
                if self.target_index == len(self.target_coordinates):
                    self.target_index = 0  # По кругу теперь 
        else:  # Движение назад
            if self.x > self.initial_coordinates[0]:
                self.x -= 1
            elif self.x < self.initial_coordinates[0]:
                self.x += 1
            else:
                self.direction = 1  
                self.target_index += 1  
                if self.target_index == len(self.target_coordinates):
                    self.target_index = 0 

        self.canvas.coords(self.canvas_object, self.x, self.y)
        self.canvas.after(15, self.move_x) #Скорость 15 

    def move_y(self):
        target_y = self.target_coordinates[self.target_index][1]
        if self.direction == 1:  # ДВижение вперед
            if self.y < target_y:
                self.y += 1
            elif self.y > target_y:
                self.y -= 1
            else:
                self.direction = -1  
                self.target_index += 1 
                if self.target_index == len(self.target_coordinates):
                    self.target_index = 0  
        else:  # ДВиженеи назад
            if self.y > self.initial_coordinates[1]:
                self.y -= 1
            elif self.y < self.initial_coordinates[1]:
                self.y += 1
            else:
                self.direction = 1  
                self.target_index += 1  
                if self.target_index == len(self.target_coordinates):
                    self.target_index = 0  

        self.canvas.coords(self.canvas_object, self.x, self.y)
        self.canvas.after(15, self.move_y)
# Создаем главное окно приложения
root = Tk()
root.geometry("770x600")  
root.resizable(False, False)
root.title("DIGGER")
canvas = Canvas(root, background='#FFC018', width=770, height=600)
canvas.pack()
menu = GameMenu(canvas)
menu.show()
root.iconphoto(True, tk.PhotoImage(file='Assets/Texture/icon.png'))
root.mainloop()
