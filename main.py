import pygame
import sys
import math
import random

WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (8, 10, 20)
LINE_COLOR = (60, 120, 160)
TEXT_COLOR = (200, 220, 240)
ACCENT_COLOR = (80, 160, 220)
PORT_COLOR_FREE = (70, 180, 110)
PORT_COLOR_BUSY = (60, 60, 80)
PORT_COLOR_MAINLINE_FREE = (70, 140, 220)
PORT_COLOR_MAINLINE_BUSY = (50, 80, 120)
BUTTON_COLOR = (20, 28, 40)
BUTTON_HOVER_COLOR = (40, 55, 80)
SELECTED_COLOR = (210, 180, 70)

MODULE_SIZE = 70
SOLAR_WIDTH = 70
SOLAR_HEIGHT = 140
DOCKING_DISTANCE = 85
PORT_RADIUS = 8

DIR_VECTORS = [(1, 0), (0, -1), (-1, 0), (0, 1)]
OPPOSITE_DIR = {0: 2, 1: 3, 2: 0, 3: 1}

MODULE_TYPES = {
    "crew": {
        "name": "Жилой отсек",
        "crew": 2, "science": 0, "energy": 0,
        "color": (90, 160, 110), "desc": "+2 экипажа",
        "size": "square", "has_ports": True, "port_type": "normal"
    },
    "science": {
        "name": "Научная лаборатория",
        "crew": 0, "science": 3, "energy": 0,
        "color": (70, 120, 190), "desc": "+3 науки",
        "size": "square", "has_ports": True, "port_type": "normal"
    },
    "solar": {
        "name": "Солнечная панель",
        "crew": 0, "science": 0, "energy": 3,
        "color": (180, 150, 70), "desc": "+3 энергии (нет портов)",
        "size": "tall", "has_ports": False, "port_type": None
    },
    "empty": {
        "name": "Ферменная балка",
        "crew": 0, "science": 0, "energy": 0,
        "color": (110, 110, 130), "desc": "Пустой (магистральные порты)",
        "size": "square", "has_ports": True, "port_type": "normal"
    },
    "reactor": {
        "name": "Ядерный реактор",
        "crew": 0, "science": -1, "energy": 5,
        "color": (200, 80, 60), "desc": "+5 энергии, -1 наука",
        "size": "square", "has_ports": True, "port_type": "normal"
    },
    "hab": {
        "name": "Жилой комплекс",
        "crew": 4, "science": 0, "energy": 0,
        "color": (140, 200, 100), "desc": "+4 экипажа",
        "size": "square", "has_ports": True, "port_type": "normal"
    },
    "lab": {
        "name": "Передовая лаборатория",
        "crew": 0, "science": 5, "energy": -1,
        "color": (100, 150, 220), "desc": "+5 науки, -1 энергия",
        "size": "square", "has_ports": True, "port_type": "normal"
    }
}

CORE_STATS = {"crew": 1, "science": 1, "energy": 2}
CORE_COLOR = (100, 120, 150)

class Module:
    def __init__(self, module_id, module_type, x, y, parent=None, parent_side=None):
        self.id = module_id
        self.type = module_type
        self.x = x
        self.y = y
        self.parent = parent
        self.parent_side = parent_side
        
        if self.type == 'core':
            self.crew = CORE_STATS["crew"]
            self.science = CORE_STATS["science"]
            self.energy = CORE_STATS["energy"]
            self.color = CORE_COLOR
            self.size = "square"
            self.has_ports = True
            self.port_type = "normal"
        else:
            info = MODULE_TYPES[self.type]
            self.crew = info["crew"]
            self.science = info["science"]
            self.energy = info["energy"]
            self.color = info["color"]
            self.size = info.get("size", "square")
            self.has_ports = info.get("has_ports", True)
            self.port_type = info.get("port_type", "normal")
        
        self.free_ports = {d: True for d in range(4)} if self.has_ports else {}
        if parent is not None and parent_side is not None and self.has_ports:
            opposite = OPPOSITE_DIR[parent_side]
            self.free_ports[opposite] = False
    
    def get_port_position(self, direction):
        dx, dy = DIR_VECTORS[direction]
        if self.size == "tall":
            return self.x + dx * (SOLAR_WIDTH//2), self.y + dy * (SOLAR_HEIGHT//2)
        else:
            return self.x + dx * (MODULE_SIZE//2), self.y + dy * (MODULE_SIZE//2)
    
    def draw(self, screen):
        if self.size == "tall":
            rect = pygame.Rect(self.x - SOLAR_WIDTH//2, self.y - SOLAR_HEIGHT//2,
                               SOLAR_WIDTH, SOLAR_HEIGHT)
            pygame.draw.rect(screen, self.color, rect, width=1, border_radius=4)
            for i in range(3):
                y_offset = -SOLAR_HEIGHT//2 + 30 + i*35
                pygame.draw.line(screen, (130,110,60),
                                 (self.x - SOLAR_WIDTH//2 + 10, self.y + y_offset),
                                 (self.x + SOLAR_WIDTH//2 - 10, self.y + y_offset), 1)
            label = "СОЛН"
        else:
            rect = pygame.Rect(self.x - MODULE_SIZE//2, self.y - MODULE_SIZE//2,
                               MODULE_SIZE, MODULE_SIZE)
            pygame.draw.rect(screen, self.color, rect, width=1, border_radius=6)
            if self.type == 'core':
                label = "ЦЕНТР"
            elif self.type == 'crew':
                label = "ЭКИП"
            elif self.type == 'science':
                label = "НАУКА"
            elif self.type == 'empty':
                label = "БАЛКА"
            elif self.type == 'reactor':
                label = "РЕАКТ"
            elif self.type == 'hab':
                label = "ЖИЛОЙ"
            elif self.type == 'lab':
                label = "ЛАБ"
            else:
                label = "МОД"
        font = pygame.font.SysFont("monospace", 12, bold=True)
        text_surf = font.render(label, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, text_rect)
    
    def draw_ports(self, screen):
        if not self.has_ports:
            return
        for direction in range(4):
            if self.free_ports.get(direction, False):
                port_pos = self.get_port_position(direction)
                color = PORT_COLOR_MAINLINE_FREE if self.port_type == "mainline" else PORT_COLOR_FREE
                pygame.draw.circle(screen, color, port_pos, PORT_RADIUS)
                pygame.draw.circle(screen, (200,200,200), port_pos, PORT_RADIUS-3, width=1)
            else:
                if direction in self.free_ports:
                    port_pos = self.get_port_position(direction)
                    color = PORT_COLOR_MAINLINE_BUSY if self.port_type == "mainline" else PORT_COLOR_BUSY
                    pygame.draw.circle(screen, color, port_pos, PORT_RADIUS-2)

class SpaceStation:
    def __init__(self):
        self.modules = []
        self.next_id = 1
        self.total_crew = 0
        self.total_science = 0
        self.total_energy = 0
        self.message = ""
        self.message_timer = 0
        self._init_core()
    
    def _init_core(self):
        core = Module(0, 'core', WIDTH//2, HEIGHT//2)
        self.modules.append(core)
        self._update_stats()
    
    def _update_stats(self):
        self.total_crew = sum(m.crew for m in self.modules)
        self.total_science = sum(m.science for m in self.modules)
        self.total_energy = sum(m.energy for m in self.modules)
        if self.total_energy < 0:
            self.total_science = max(0, self.total_science + self.total_energy)
        if self.total_crew > 5:
            self.total_science = self.total_science + (self.total_crew - 5)
    
    def _is_position_free(self, x, y, module_type):
        for module in self.modules:
            if module.size == "tall":
                w, h = SOLAR_WIDTH, SOLAR_HEIGHT
            else:
                w, h = MODULE_SIZE, MODULE_SIZE
            dx = module.x - x
            dy = module.y - y
            if abs(dx) < (w//2 + MODULE_SIZE//2) and abs(dy) < (h//2 + MODULE_SIZE//2):
                return False
        return True
    
    def _find_module_at_port(self, mouse_pos):
        for module in self.modules:
            if not module.has_ports:
                continue
            for direction in range(4):
                if module.free_ports.get(direction, False):
                    port_pos = module.get_port_position(direction)
                    if math.hypot(mouse_pos[0] - port_pos[0], mouse_pos[1] - port_pos[1]) <= PORT_RADIUS + 5:
                        return module, direction
        return None, None
    
    def attach_module(self, parent_module, direction, module_type):
        if not parent_module.free_ports.get(direction, False):
            self._set_message("Порт занят!", True)
            return False
        
        dx, dy = DIR_VECTORS[direction]
        if parent_module.size == "tall":
            parent_w, parent_h = SOLAR_WIDTH, SOLAR_HEIGHT
        else:
            parent_w, parent_h = MODULE_SIZE, MODULE_SIZE
        offset = (parent_w//2 + MODULE_SIZE//2) if module_type != "solar" else (parent_w//2 + SOLAR_WIDTH//2)
        new_x = parent_module.x + dx * offset
        new_y = parent_module.y + dy * offset
        
        margin = 50
        if new_x < margin or new_x > WIDTH - margin or new_y < margin or new_y > HEIGHT - margin:
            self._set_message("Выход за границы!", True)
            return False
        
        if not self._is_position_free(new_x, new_y, module_type):
            self._set_message("Место занято другим модулем!", True)
            return False
        
        new_module = Module(self.next_id, module_type, new_x, new_y,
                            parent=parent_module, parent_side=direction)
        self.modules.append(new_module)
        self.next_id += 1
        parent_module.free_ports[direction] = False
        self._update_stats()
        self._set_message(f"Пристыкован {MODULE_TYPES[module_type]['name']}", False)
        return True
    
    def reset_station(self):
        self.modules.clear()
        self.next_id = 1
        self._init_core()
        self._set_message("Станция сброшена", False)
    
    def _set_message(self, msg, is_error):
        self.message = msg
        self.message_timer = 180
    
    def update_message(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
    
    def draw_connections(self, screen):
        for module in self.modules:
            if module.parent is not None:
                start = (module.parent.x, module.parent.y)
                end = (module.x, module.y)
                pygame.draw.line(screen, LINE_COLOR, start, end, 1)
    
    def draw(self, screen):
        self.draw_connections(screen)
        for module in self.modules:
            module.draw(screen)
        for module in self.modules:
            module.draw_ports(screen)

class Button:
    def __init__(self, rect, text, color, text_color, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.hovered = False
    
    def draw(self, screen):
        color = BUTTON_HOVER_COLOR if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, width=1, border_radius=8)
        font = pygame.font.SysFont("monospace", 12, bold=True)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ORBIT STATION BUILDER")
clock = pygame.time.Clock()

station = SpaceStation()
selected_module = "crew"

panel_x = WIDTH - 270
panel_y = 60
btn_w = 240
btn_h = 32
gap = 5

def select_crew():
    global selected_module
    selected_module = "crew"
    station._set_message("Выбран: Жилой отсек", False)

def select_science():
    global selected_module
    selected_module = "science"
    station._set_message("Выбрана: Научная лаборатория", False)

def select_solar():
    global selected_module
    selected_module = "solar"
    station._set_message("Выбрана: Солнечная панель (нет портов)", False)

def select_empty():
    global selected_module
    selected_module = "empty"
    station._set_message("Выбрана: Ферменная балка (магистральные порты)", False)

def select_reactor():
    global selected_module
    selected_module = "reactor"
    station._set_message("Выбран: Ядерный реактор (+5 эн, -1 наука)", False)

def select_hab():
    global selected_module
    selected_module = "hab"
    station._set_message("Выбран: Жилой комплекс (+4 экипажа)", False)

def select_lab():
    global selected_module
    selected_module = "lab"
    station._set_message("Выбрана: Передовая лаборатория (+5 науки, -1 эн)", False)

def reset_game():
    station.reset_station()

buttons = []
row1 = ["crew", "science", "solar", "empty"]
row2 = ["reactor", "hab", "lab"]

btn_texts = {
    "crew": "Жилой отсек +2",
    "science": "Лаборатория +3",
    "solar": "Солнечная панель +3 (нет портов)",
    "empty": "Ферменная балка (магистр. порты)",
    "reactor": "Реактор +5 эн, -1 наука",
    "hab": "Жилой комплекс +4 экипажа",
    "lab": "Передовая лаб. +5 науки, -1 эн"
}

actions = {
    "crew": select_crew,
    "science": select_science,
    "solar": select_solar,
    "empty": select_empty,
    "reactor": select_reactor,
    "hab": select_hab,
    "lab": select_lab
}

for i, key in enumerate(row1):
    btn = Button((panel_x, panel_y + i*(btn_h+gap), btn_w, btn_h), btn_texts[key], BUTTON_COLOR, TEXT_COLOR, actions[key])
    buttons.append(btn)

for i, key in enumerate(row2):
    btn = Button((panel_x, panel_y + (len(row1)+i)*(btn_h+gap), btn_w, btn_h), btn_texts[key], BUTTON_COLOR, TEXT_COLOR, actions[key])
    buttons.append(btn)

reset_btn = Button((panel_x, HEIGHT-70, btn_w, 40), "СБРОС СТАНЦИИ", (50,35,45), (200,160,160), reset_game)
buttons.append(reset_btn)

def draw_stats_panel(screen, station, selected_type):
    panel_bg = pygame.Surface((btn_w+10, 120))
    panel_bg.set_alpha(160)
    panel_bg.fill((10,15,25))
    screen.blit(panel_bg, (panel_x-5, panel_y + (len(row1)+len(row2))*(btn_h+gap) + 20))
    
    font_title = pygame.font.SysFont("monospace", 15, bold=True)
    font_value = pygame.font.SysFont("monospace", 22, bold=True)
    title = font_title.render("СТАТУС СТАНЦИИ", True, ACCENT_COLOR)
    y0 = panel_y + (len(row1)+len(row2))*(btn_h+gap) + 25
    screen.blit(title, (panel_x, y0))
    
    screen.blit(font_value.render(f"Ч {station.total_crew}", True, (130,210,130)), (panel_x, y0+25))
    screen.blit(font_value.render(f"Л {station.total_science}", True, (130,180,240)), (panel_x+90, y0+25))
    screen.blit(font_value.render(f"Э {station.total_energy}", True, (230,190,90)), (panel_x+180, y0+25))
    
    if selected_type in MODULE_TYPES:
        info = MODULE_TYPES[selected_type]
        font_sel = pygame.font.SysFont("monospace", 12)
        sel_text = font_sel.render(f"{info['name']}", True, SELECTED_COLOR)
        screen.blit(sel_text, (panel_x, y0 + 70))

def draw_message(screen, msg):
    if msg:
        font = pygame.font.SysFont("monospace", 16, bold=True)
        surf = font.render(msg, True, (240,230,170))
        bg_rect = surf.get_rect(center=(WIDTH//2, HEIGHT-30))
        bg_rect.inflate_ip(20,8)
        pygame.draw.rect(screen, (20,20,45), bg_rect, border_radius=6)
        screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT-30)))

def draw_instructions(screen):
    font = pygame.font.SysFont("monospace", 11)
    lines = ["[1] Выбери тип модуля справа", "[2] Нажми на зелёный/синий порт", "[3] Строй станцию"]
    x, y = 25, HEIGHT - 60
    for line in lines:
        screen.blit(font.render(line, True, (140,160,190)), (x, y))
        y += 18

running = True
while running:
    dt = clock.tick(60)
    station.update_message()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for btn in buttons:
            btn.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            on_button = any(btn.rect.collidepoint(event.pos) for btn in buttons)
            if not on_button:
                parent, direction = station._find_module_at_port(event.pos)
                if parent and selected_module:
                    station.attach_module(parent, direction, selected_module)
    
    screen.fill(BACKGROUND_COLOR)
    station.draw(screen)
    for btn in buttons:
        btn.draw(screen)
    draw_stats_panel(screen, station, selected_module)
    draw_message(screen, station.message)
    draw_instructions(screen)
    
    sel_map = {
        "crew": buttons[0], "science": buttons[1], "solar": buttons[2], "empty": buttons[3],
        "reactor": buttons[4], "hab": buttons[5], "lab": buttons[6]
    }
    for typ, btn in sel_map.items():
        if selected_module == typ:
            pygame.draw.rect(screen, SELECTED_COLOR, btn.rect, width=1, border_radius=8)
    
    pygame.display.flip()

pygame.quit()
sys.exit()