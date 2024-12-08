from shiny.express import ui, render, ui, input
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Функция для расчета потенциала
def calculate_potential(E0, charges, positions, Lx, Ly, dLx, dLy):
    x, y = np.meshgrid(
        np.arange(-Lx, Lx + dLx, dLx),
        np.arange(-Ly, Ly + dLy, dLy)
    )
    Fi = np.zeros_like(x, dtype=np.float64)  # Указываем тип данных явно
    for charge, (px, py) in zip(charges, positions):
        K = charge / (4 * np.pi * E0)
        Fi += K / np.sqrt((x - px) ** 2 + (y - py) ** 2)
    return x, y, Fi

MAX_VALUE = 10**5
# Интерфейс приложения
ui.h2("Эквипотенциальные линии электрического поля"),
Q = [(50, 0.5, -0.5), (-100, 0, 0), (100, 0, -0.5)]
ui.input_text("charge_input", "Введите заряды:", value=str(Q), width="100%"),
ui.help_text("Заряды вводятся в формате списка кортежей (x, y, заряд), например [(0, 1, -2), (-2, 1, 1)].")
ui.input_numeric("Lx", "Размер области по x (м)", 1),
ui.input_numeric("Ly", "Размер области по y (м)", 1),
ui.input_numeric("dLx", "Шаг сетки по x (м)", 0.1),
ui.input_numeric("dLy", "Шаг сетки по y (м)", 0.1)

# Серверная часть приложения
with ui.card(full_screen=True):
    @render.plot
    def potential_plot():
        try:
            # Обработка пользовательского ввода
            user_input = input.charge_input()
            Q = eval(user_input)
            if not all(isinstance(q, tuple) and len(q) == 3 for q in Q):
                raise ValueError("Неверный формат заряда. Ожидается список кортежей в формате [(заряд, x, y), ...]")
            if any(abs(val) > MAX_VALUE for q in Q for val in q):
                raise ValueError(f"Значение зарядов или координат превышает допустимый предел {MAX_VALUE}.")
        except Exception as e:
            raise ValueError(f"Ошибка ввода: {e}")

        # Получение параметров из интерфейса
        Lx = input.Lx()
        Ly = input.Ly()
        dLx = input.dLx()
        dLy = input.dLy()
        
        # Физические параметры
        E0 = 8.854e-12
        charges = [q[0] * E0 for q in Q]
        positions = [(q[1], q[2]) for q in Q]
        
        # Вычисление потенциала
        x, y, Fi = calculate_potential(E0, charges, positions, Lx, Ly, dLx, dLy)
        
        # Визуализация
        fig, ax = plt.subplots(figsize=(8, 6))
        LevelCon = [10, 20, 40, 60]
        LevelCon_neg = [-60, -40, -20, -10]
        
        # Положительные контуры
        contour_pos = ax.contour(x, y, Fi, levels=LevelCon, colors='red', linewidths=2)
        ax.clabel(contour_pos, inline=True, fontsize=10, fmt='%1.1f', colors='red')
        
        # Отрицательные контуры
        contour_neg = ax.contour(x, y, Fi, levels=LevelCon_neg, colors='green', linewidths=2)
        ax.clabel(contour_neg, inline=True, fontsize=10, fmt='%1.1f', colors='green')
        
        # Общий вид графика
        ax.set_title("Эквипотенциальные линии электрического поля")
        ax.set_xlabel('x, м')
        ax.set_ylabel('y, м')
        ax.scatter(*zip(*positions), color='blue', s=100, label='Заряды')
        ax.legend()
        ax.grid()
        
        return fig
