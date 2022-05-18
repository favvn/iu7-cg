from tkinter import messagebox, ttk, colorchooser, PhotoImage
from tkinter import *
import colorutils as cu
from time import time, sleep
import matplotlib.path as mplPath
import numpy as np

WIN_WIDTH = 1200
WIN_HEIGHT = 800

SIZE = 900
WIDTH = 100.0

def bresenham_int(p1, p2, color, step_count=False):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]

    if (x2 - x1 == 0) and (y2 - y1 == 0):
        return [[x1, y1, color]]

    x = x1
    y = y1

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    s1 = sign(x2 - x1)
    s2 = sign(y2 - y1)

    swaped = 0
    if dy > dx:
        tmp = dx
        dx = dy
        dy = tmp
        swaped = 1

    e = 2 * dy - dx
    i = 1
    dots = []
    steps = 0

    while i <= dx + 1:
        dot = [x, y, color]
        dots.append(dot)

        x_buf = x
        y_buf = y

        while e > 0:
            if swaped:
                x = x + s1
            else:
                y = y + s2

            e = e - 2 * dx

        if swaped:
            y = y + s2
        else:
            x = x + s1

        e = e + 2 * dy

        if step_count:
            if (x_buf != x) and (y_buf != y):
                steps += 1

        i += 1

    if step_count:
        return steps
    else:
        return dots

def to_coords(dot):
    x = (dot[0] - coord_center[0]) * m_board
    y = (-dot[1] + coord_center[1]) * m_board

    return [x, y]

def to_canva(dot):
    x = coord_center[0] + dot[0] / m_board
    y = coord_center[1] - dot[1] / m_board

    return [x, y]


def sign(diff):
    if diff < 0:
        return -1
    elif diff == 0:
        return 0
    else:
        return 1

def manual_add_dot():
    try:
        x = int(x_entry.get())
        y = int(y_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Неверно введены координаты")
        return

    draw_point(x, y, 0)

def seed_inside_figure(dot_seed):
    for figure in dots_list:
        if len(figure) > 0:
            arr = np.array([[figure[i][0], figure[i][1]] for i in range(len(figure))])
            path = mplPath.Path(arr)

            if path.contains_point(dot_seed):
                return True

    return False


def parse_fill():
    cur_figure = len(dots_list) - 1

    if len(dots_list[cur_figure]) != 0:
        messagebox.showerror("Ошибка", "Фигура не замкнута")
        return

    delay = False
    if option_filling.get() == 1:
        delay = True

    try:
        dot_seed = to_canva(seed)
    except:
        messagebox.showerror("Ошибка", "Не выбран затравочный пиксель")

    if not seed_inside_figure(dot_seed):
        messagebox.showerror("Ошибка", "Затравочный пиксель находится вне какой-либо фигуры")
        return

    fill_with_seed(dot_seed, delay=delay)


def fill_with_seed(dot_seed, delay=False):
    color_fill = cu.Color(filling_color[1])

    start_time = time()

    stack = list()
    stack.append(dot_seed)

    while stack:
        dot_seed = stack.pop()

        x, y = int(dot_seed[0]), int(dot_seed[1])

        image_canvas.put(color_fill, (x, y))
        canvas_win.create_polygon([x, y], [x, y + 1],
                                  [x + 1, y + 1], [x + 1, y],
                                  fill=color_fill, tag='line')

        tmp_x = x
        tmp_y = y

        # Заполнение текущей строки вправо до ребра или уже закрашенного пикселя
        x = x + 1
        while image_canvas.get(x, y) != T_COLOR and image_canvas.get(x, y) != filling_color[0]:
            image_canvas.put(color_fill, (x, y))
            canvas_win.create_polygon([x, y], [x, y + 1],
                                      [x + 1, y + 1], [x + 1, y],
                                      fill=color_fill, tag='line')
            x = x + 1

        x_right = x - 1

        # Заполнение текущей строки влево до ребра или уже закрашенного пикселя
        x = tmp_x - 1

        while image_canvas.get(x, y) != T_COLOR and image_canvas.get(x, y) != filling_color[0]:
            image_canvas.put(color_fill, (x, y))
            canvas_win.create_polygon([x, y], [x, y + 1],
                                      [x + 1, y + 1], [x + 1, y],
                                      fill=color_fill, tag='line')
            x = x - 1

        x_left = x + 1

        # Сканирование верхней строки
        x = x_left
        y = tmp_y + 1

        while x <= x_right:
            flag = False

            # Поиск, есть ли в строке незакрашенный пиксель
            while (image_canvas.get(x, y) != T_COLOR
                   and image_canvas.get(x, y) != filling_color[0]
                   and x <= x_right):
                flag = True

                x = x + 1

            if flag == True:
                if (x == x_right
                        and image_canvas.get(x, y) != T_COLOR
                        and image_canvas.get(x, y) != filling_color[0]):
                    stack.append([x, y])
                else:
                    stack.append([x - 1, y])

                flag = False

            x_begin = x

            while ((image_canvas.get(x, y) == T_COLOR
                    or image_canvas.get(x, y) == filling_color[0])
                   and x < x_right):
                x = x + 1

            if x == x_begin:
                x = x + 1

        # Сканирование нижней строки
        x = x_left

        y = tmp_y - 1

        while x <= x_right:
            flag = False

            # Поиск, есть ли в строке незакрашенный пиксель
            while (image_canvas.get(x, y) != T_COLOR
                   and image_canvas.get(x, y) != filling_color[0]
                   and x <= x_right):
                flag = True

                x = x + 1

            if flag == True:
                if (x == x_right
                        and image_canvas.get(x, y) != T_COLOR
                        and image_canvas.get(x, y) != filling_color[0]):
                    stack.append([x, y])
                else:
                    stack.append([x - 1, y])

                flag = False

            x_begin = x

            while ((image_canvas.get(x, y) == T_COLOR
                    or image_canvas.get(x, y) == filling_color[0])
                   and x < x_right):
                x = x + 1

            if x == x_begin:
                x = x + 1

        if delay:
            sleep(0.0001)
            canvas_win.update()

    end_time = time()

    new_win = time_win(start_time, end_time)
    new_win.mainloop()

def time_win(start_time, end_time):
    win = Tk()
    win.title("Время исполнения")
    win['bg'] = "white"
    win.geometry("265x200+630+100")
    win.resizable(False, False)

    time_label = Label(win, text="Время: %-3.2f с" % (end_time - start_time), bg="white", font="AvantGardeC 14", fg='black')
    time_label.place(x=40, y=30, relheight=0.5, relwidth=0.70)

    return win


def draw_line(dots):
    color_line = cu.Color(line_color[1])
    for dot in dots:
        x, y = dot[0:2]
        canvas_win.create_polygon([x, y], [x, y + 1], [x + 1, y + 1], [x + 1, y], fill=dot[2], tag='line')
        image_canvas.put(TS_COLOR, (x, y))


# замкнуть фигуру
def make_figure():
    cur_figure = len(dots_list)
    cur_dot = len(dots_list[cur_figure - 1])

    if cur_dot < 3:
        messagebox.showerror("Ошибка", "Недостаточно точек, чтобы замкнуть фигуру")
        return
    draw_point(dots_list[cur_figure - 1][0][0], dots_list[cur_figure - 1][0][1], 1)
    canvas_win.delete('dot')

    dots_list.append(list())

    dots_block.insert(END, "-" * 50)


def del_dot():
    try:
        if str(dots_block.get(END))[0] == '-':
            dots_block.delete(END)

        dots_block.delete(END)

    except ValueError:
        messagebox.showerror("Ошибка", "Не выбрана точка")

def draw_point(ev_x, ev_y, click_):
    global dots_block, dots_list, option_coords, seed

    if click_:
        x, y = ev_x, ev_y
    else:
        x, y = to_canva([ev_x, ev_y])

    x_y = to_coords([x, y])

    if option_coords.get() == 0:
        seed = x_y
        dot_str = "  %-3.1f; %-3.1f" % (x_y[0], x_y[1])
        seed_block.delete(0, END)
        seed_block.insert(END, dot_str)

        canvas_win.delete('seed_dot')
        canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                             width=2, tag='seed_dot')
        return

    cur_figure = len(dots_list) - 1
    dots_list[cur_figure].append([int(x), int(y)])

    cur_dot = len(dots_list[cur_figure]) - 1

    dot_str = "%d : (%-3.1f; %-3.1f)" % (cur_dot + 1, x_y[0], x_y[1])
    dots_block.insert(END, dot_str)

    canvas_win.delete('dot')
    canvas_win.create_oval(x - 2, y - 2, x + 2, y + 2,
                           width=2, tag='dot')

    color_line = cu.Color(line_color[1])
    if len(dots_list[cur_figure]) > 1:
        dots = bresenham_int(dots_list[cur_figure][cur_dot - 1], dots_list[cur_figure][cur_dot], color_line)

        draw_line(dots)


def click(event):
    if event.x < 0 or event.x > WIN_WIDTH * win_k or event.y < 0 or event.y > WIN_HEIGHT * win_k:
        return
    draw_point(event.x, event.y, 1)


def draw_lines(click_dots):
    for figure in click_dots:
        for i in range(len(figure) - 1):
            dots = bresenham_int(figure[i], figure[i + 1], cu.Color(line_color[1]))
            draw_line(dots)


def draw_sides(dots):
    for dot in dots:
        x, y = dot[0:2]
        canvas_win.create_polygon([x, y], [x, y + 1],
                                  [x + 1, y + 1], [x + 1, y],
                                  fill=dot[2], tag='line')

def undo():
    global dots_list

    if len(dots_list) == 1 and dots_list[0] == []:
        messagebox.showerror("Внимание", "Достигнуто исходное состояние")
        return

    canvas_win.delete('line', 'coord')

    d = -1
    if not dots_list[-1]:
        if len(dots_list) > 1:
            d = -2
    dots_list[d].pop()
    del_dot()

    if len(dots_list) > 1 and dots_list[-2] == []:
        dots_list = dots_list[:-1]

    draw_lines(dots_list)
    draw_axes()


def choose_fill_color():
    global filling_color
    filling_color = colorchooser.askcolor()


def clean_canvas():
    global canvas_bg

    dots_list.clear()
    dots_list.append([])

    canvas_win.delete('line', 'dot')
    canvas_bg = ((255, 255, 255), "#ffffff")
    canvas_win.configure(bg=cu.Color(canvas_bg[1]))

    image_canvas.put("#ffffff", to=(0, 0, WIN_WIDTH, WIN_HEIGHT))

    dots_block.delete(0, END)


def draw_axes():
    s = int(size)
    canvas_win.create_line(0, s // 2, s - 2, s // 2, fill='black', width=1)
    canvas_win.create_line(s // 2, s, s // 2, 2, fill='black', width=1)

def config(event):
    if event.widget == win:
        global win_x, win_y, win_k, m, size, coord_center

        win_x = win.winfo_width()/WIN_WIDTH
        win_y = (win.winfo_height() + 35)/WIN_HEIGHT
        win_k = min(win_x, win_y)

        size = SIZE * win_k
        m = size / (2 * border + ten_percent)

        canvas_win.place(x=10 * win_x, y=0 * win_y, width=size, height=size)
        canvas_win.create_image((WIN_WIDTH / 2, WIN_HEIGHT / 2), image=image_canvas, state="normal")

        coords_points.place(x=820 * win_x, y=28 * win_y)
        coords_seed.place(x=820 * win_x, y=347 * win_y)

        # координаты
        center_lbl.place(x=820 * win_x, y=28 * win_y, width=220 * win_x, height=24 * win_y)
        dots_block.place(x=820 * win_x, y=60 * win_y, width=300 * win_x, height=270 * win_y)

        # координаты затравки
        seed_lbl.place(x=820 * win_x, y=350 * win_y, width=150 * win_x, height=24 * win_y)
        seed_block.place(x=950 * win_x, y=350 * win_y, width=120 * win_x, height=24 * win_y)

        # добавить, изменить и удалить точку
        x_lbl.place(x=850 * win_x, y=400 * win_y, width=110 * win_x, height=18 * win_y)
        y_lbl.place(x=950 * win_x, y=400 * win_y, width=110 * win_x, height=18 * win_y)
        x_entry.place(x=850 * win_x, y=420 * win_y, width=110 * win_x, height=20 * win_y)
        y_entry.place(x=950 * win_x, y=420 * win_y, width=110 * win_x, height=20 * win_y)

        add.place(x=850 * win_x, y=442 * win_y, width=210 * win_x, height=25 * win_y)

        # закраска
        draw_delay.place(x=850 * win_x, y=520 * win_y)
        draw_without_delay.place(x=990 * win_x, y=520 * win_y)
        fill_figure_btn.place(x=850 * win_x, y=560 * win_y, width=200 * win_x, height=28 * win_y)
        fil.place(x=850 * win_x, y=600 * win_y, width=200 * win_x, height=28 * win_y)

        con.place(x=850 * win_x, y=635 * win_y, width=200 * win_x, height=28 * win_y)

        und.place(x=850 * win_x, y=670 * win_y, width=109 * win_x, height=28 * win_y)

        bgn.place(x=950 * win_x, y=670 * win_y, width=120 * win_x, height=28 * win_y)

        fim.place(x=850 * win_x, y=480 * win_y, width=200 * win_x, height=28 * win_y)

        coord_center = [size / 2, size / 2]

        canvas_win.delete('all')
        draw_axes()

T_COLOR = (255, 0, 255)
TS_COLOR = "#ff00ff"

win = Tk()
win['bg'] = '#e0e0eb'
win.geometry("%dx%d" % (WIN_WIDTH, WIN_HEIGHT))
win.title("Лабораторная работа №6")

filling_color = ((129, 66, 145), "#814291")
line_color = ((0, 0, 0), "#000000")
canvas_bg = ((255, 255, 255), "#ffffff")
canvas_win = Canvas(win, bg=cu.Color(canvas_bg[1]))

image_canvas = PhotoImage(width = WIN_WIDTH, height = WIN_HEIGHT)

center_lbl = Label(text="Координаты точек", bg='#e0e0eb', font="AvantGardeC 14", fg='black')
dots_block = Listbox(bg="#ffffff")
dots_block.configure(font="AvantGardeC 14", fg='black')

seed_lbl = Label(text="Затравка", bg='#e0e0eb', font="AvantGardeC 14", fg='black')
seed_block = Listbox(bg="#ffffff")
seed_block.configure(font="AvantGardeC 14", fg='black')

dots_list = [[]]
seed = []

x_lbl = Label(text="X", bg='white', font="AvantGardeC 14", fg='black')
y_lbl = Label(text="Y", bg='white', font="AvantGardeC 14", fg='black')
x_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')
y_entry = Entry(font="AvantGardeC 14", bg='white', fg='black',
                borderwidth=0, insertbackground='black', justify='center')

color_lbl = Label(text="Цвет", bg='#e0e0eb', font="AvantGardeC 14", fg='black')
answer_lbl = Label(text="Решение задачи", bg='#e0e0eb', font="AvantGardeC 14", fg='black')

xy_current = [-400, -350, -300, -250, -200, -150, -100, -50,
              0, 50, 100, 150, 200, 250, 300, 350, 400]

sct = Button(text="Построить", font="AvantGardeC 14",
             borderwidth=0)
con = Button(text="Условие задачи", font="AvantGardeC 14",
             borderwidth=0, command=lambda: messagebox.showinfo("Задание", TASK + AUTHOR))
bgn = Button(text="Сброс", font="AvantGardeC 14",
             borderwidth=0, command=lambda: clean_canvas())
und = Button(text="Откат", font="AvantGardeC 14",
             borderwidth=0, command=lambda: undo())
fim = Button(text="Замкнуть", font="AvantGardeC 14",
             borderwidth=0, command=lambda: make_figure())
fil = Button(text="Цвет заливки", font="AvantGardeC 14",
             borderwidth=0, command=lambda: choose_fill_color())
add = Button(text="Добавить", font="AvantGardeC 14",
             borderwidth=0, command=lambda: manual_add_dot())

option_filling = IntVar()
option_filling.set(0)

option_color = IntVar()
option_color.set(1)

draw_delay = Radiobutton(text="С задержкой", font="AvantGardeC 14", variable=option_filling, value=1, bg="#e0e0eb",
                         activebackground="#e0e0eb", highlightbackground="#e0e0eb")
draw_without_delay = Radiobutton(text="Без задержки", font="AvantGardeC 14", variable=option_filling,  value=0, bg="#e0e0eb",
                                 activebackground="#e0e0eb", highlightbackground="#e0e0eb")
fill_figure_btn = Button(text="Закрасить", font="AvantGardeC 14",
                         borderwidth=0, command=lambda: parse_fill())

option_coords = IntVar()
option_coords.set(1)

coords_points = Radiobutton(variable=option_coords, value=1, bg="#e0e0eb",
                            activebackground="#e0e0eb", highlightbackground="#e0e0eb")
coords_seed = Radiobutton(variable=option_coords, value=0, bg="#e0e0eb",
                          activebackground="#e0e0eb", highlightbackground="#e0e0eb")

win_x = win_y = 1
win_k = 1
size = SIZE
border = WIDTH
ten_percent = 0
m = size * win_k / border
coord_center = [400, 400]
m_board = 1

win.bind("<Configure>", config)
canvas_win.bind('<1>', click)

menu = Menu(win)
add_menu = Menu(menu)
add_menu.add_command(label='О программе и авторе',
                     command=lambda: messagebox.showinfo('О программе и авторе', "Реализация и исследование " \
       "алгоритма построчного затравочного заполнения. \n\nБалашова Мария ИУ7-44Б"))
add_menu.add_command(label='Выход', command=exit)
menu.add_cascade(label='Info', menu=add_menu)
win.config(menu=menu)

win.mainloop()