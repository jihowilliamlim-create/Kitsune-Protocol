import pygame
import sys
import math
import random

# ==========================================
# 1. 초기화 및 기본 설정
# ==========================================
pygame.init()
font = pygame.font.SysFont("arial", 20, bold=True)
small_font = pygame.font.SysFont("arial", 14, bold=True)

# 한글/일어 폰트 안전 로드
kor_font_name = "malgungothic"
if "malgungothic" not in pygame.font.get_fonts():
    kor_font_name = "applegothic" if "applegothic" in pygame.font.get_fonts() else "arial"
intro_font = pygame.font.SysFont(kor_font_name, 32, bold=True)
title_font = pygame.font.SysFont(kor_font_name, 80, bold=True)
boss_font = pygame.font.SysFont(kor_font_name, 24, bold=True)

screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("キツネ protocol")

# 최적화를 위한 전역 알파 서피스와 배경 찢기용 스크린샷 캡처 변수
alpha_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
snapshot_surf = None

try:
    char_raw = pygame.image.load("아카이1.png").convert_alpha()
    scale = 4
    player_img_right = pygame.transform.scale(char_raw, (char_raw.get_width() * scale, char_raw.get_height() * scale))
    player_img_left = pygame.transform.flip(player_img_right, True, False)
except Exception:
    player_img_right = pygame.Surface((40, 64), pygame.SRCALPHA);
    player_img_right.fill((0, 255, 0))
    player_img_left = pygame.Surface((40, 64), pygame.SRCALPHA);
    player_img_left.fill((0, 200, 0))

yomi_face_size = 60
yomi_face_img = pygame.Surface((yomi_face_size, yomi_face_size), pygame.SRCALPHA)
try:
    head_crop = player_img_right.subsurface((player_img_right.get_width() // 2 - 15, 0, 30, 30))
    head_crop = pygame.transform.scale(head_crop, (50, 50))
    yomi_face_img.blit(head_crop, (5, 5))
except:
    pygame.draw.circle(yomi_face_img, (150, 150, 150), (30, 30), 20)


def hit_player(dmg, d_texts, px, py, stun_time=0):
    global p_hp, p_dodge_stacks, p_stun_timer
    if p_dodge_stacks > 0:
        p_dodge_stacks -= 1
        d_texts.append(DamageText(px, py - 50, "EVADE!", (0, 255, 255)))
    else:
        p_hp -= dmg
        d_texts.append(DamageText(px, py - 50, str(dmg), (255, 0, 0)))
        if stun_time > 0:
            p_stun_timer = stun_time


# ==========================================
# 2. 인트로 및 타이틀
# ==========================================
def run_intro(screen):
    story_texts = [
        "2077년의 일본.",
        "일본을 움직이는건 밝은 네온사인과 어두운 조직뿐.",
        "그중 가장 큰 조직이자 회사 [히카리].",
        "그 기업의 사장은 부모님의 원수이자 당신의 형이다.",
        "당신이 가진건 부모님의 유품과 형이 버린 이능.",
        "어둠속에서 다시 복수의 매듭을 풀길..."
    ]

    def draw_scene_0(surf, tick):
        for i in range(15):
            h = 150 + (i * 53 % 300)
            pygame.draw.rect(surf, (15, 20, 35), (i * 80, 500 - h, 70, h))
            if i % 2 == 0:
                for y in range(500 - h + 20, 500, 30):
                    if (tick + i + y) % 40 < 20: pygame.draw.rect(surf, (0, 255, 255), (i * 80 + 10, y, 15, 15))
                    if (tick + i * 2 + y) % 50 < 25: pygame.draw.rect(surf, (255, 0, 255), (i * 80 + 40, y, 15, 15))

    def draw_scene_1(surf, tick):
        alpha = abs(math.sin(tick * 0.05)) * 255
        pygame.draw.rect(surf, (255, 50, 100), (300, 200, 600, 100), 8)
        pygame.draw.rect(surf, (0, 200, 255), (400, 350, 400, 80), 8)
        s = pygame.Surface((1200, 800), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 50, 100, int(alpha * 0.15)), (290, 190, 620, 120))
        pygame.draw.rect(s, (0, 200, 255, int((255 - alpha) * 0.15)), (390, 340, 420, 100))
        surf.blit(s, (0, 0))

    def draw_scene_2(surf, tick):
        pygame.draw.rect(surf, (10, 15, 20), (400, 100, 400, 400))
        pygame.draw.circle(surf, (0, 150, 255), (600, 300), 120, 15)
        pygame.draw.line(surf, (0, 150, 255), (600, 150), (600, 450), 15)
        pygame.draw.line(surf, (0, 150, 255), (450, 300), (750, 300), 15)
        glow = max(5, int(20 * abs(math.sin(tick * 0.05))))
        pygame.draw.circle(surf, (255, 255, 255), (600, 300), glow)

    def draw_scene_3(surf, tick):
        pygame.draw.rect(surf, (5, 5, 10), (0, 0, 1200, 800))
        for i in range(0, 1200, 80):
            h = 100 + (i * 73 % 200)
            pygame.draw.rect(surf, (12, 15, 25), (i, 800 - h, 60, h))
            if (tick + i) % 60 < 30: pygame.draw.rect(surf, (0, 255, 255), (i + 20, 800 - h + 50, 10, 10))
        pygame.draw.rect(surf, (8, 8, 12), (0, 0, 1200, 800), 20)
        pygame.draw.line(surf, (8, 8, 12), (0, 500), (1200, 500), 15)
        for x in range(300, 1200, 300): pygame.draw.line(surf, (8, 8, 12), (x, 0), (x, 800), 15)
        pygame.draw.polygon(surf, (0, 0, 0), [(450, 800), (520, 400), (680, 400), (750, 800)])
        pygame.draw.circle(surf, (0, 0, 0), (600, 350), 50)
        for i in range(min(40, int(tick / 3))):
            start_pos = (0, (i * 60) % 800);
            end_pos = (1200, (i * 85 + tick * 8) % 800)
            ctrl_y = 400 + math.sin(tick * 0.1 + i) * 350
            pts = []
            for t in range(11):
                ratio = t / 10.0
                px = start_pos[0] * (1 - ratio) + end_pos[0] * ratio
                py = start_pos[1] * (1 - ratio) + end_pos[1] * ratio + math.sin(ratio * math.pi) * ctrl_y * 0.5
                pts.append((px, py))
            if len(pts) > 1:
                pygame.draw.lines(surf, (0, 150, 255), False, pts, 4)
                pygame.draw.lines(surf, (200, 240, 255), False, pts, 1)

    def draw_scene_4(surf, tick):
        pygame.draw.polygon(surf, (200, 200, 200), [(590, 200), (610, 200), (600, 600)])
        pygame.draw.polygon(surf, (80, 80, 80), [(590, 200), (600, 200), (600, 600)])
        pygame.draw.rect(surf, (150, 100, 50), (560, 180, 80, 20))
        pygame.draw.rect(surf, (30, 30, 30), (585, 60, 30, 120))
        for i in range(10):
            y_center = 120 + i * 45
            radius_x = 70 + math.sin(tick * 0.05 + i * 0.5) * 50
            radius_y = 15 + math.cos(tick * 0.05 + i * 0.5) * 5
            rect = pygame.Rect(0, 0, int(abs(radius_x) * 2), int(abs(radius_y) * 2))
            rect.center = (600, y_center)
            color_intensity = 150 + int(100 * abs(math.sin(tick * 0.1 + i)))
            pygame.draw.ellipse(surf, (color_intensity, 20, 30), rect, 4)
            pygame.draw.ellipse(surf, (255, 100, 100), rect, 1)

    def draw_scene_5(surf, tick):
        shadow = player_img_right.copy()
        shadow.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.circle(shadow, (255, 0, 0), (shadow.get_width() // 2 + 5, 20), 4)
        scaled_shadow = pygame.transform.scale(shadow, (shadow.get_width() * 3, shadow.get_height() * 3))
        surf.blit(scaled_shadow, (600 - scaled_shadow.get_width() // 2, 200 - scaled_shadow.get_height() // 2))
        y = 350
        pygame.draw.line(surf, (255, 0, 0), (0, y), (1200, y), 4)
        rad = int(25 + math.sin(tick * 0.1) * 5)
        pygame.draw.circle(surf, (255, 30, 30), (600, y), rad, 5)

    scenes = [draw_scene_0, draw_scene_1, draw_scene_2, draw_scene_3, draw_scene_4, draw_scene_5]
    clock = pygame.time.Clock();
    page, char_idx, tick = 0, 0, 0
    in_intro = True
    while in_intro:
        screen.fill((0, 0, 0));
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_z, pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    if char_idx < len(story_texts[page]):
                        char_idx = len(story_texts[page])
                    else:
                        page += 1;
                        char_idx = 0
                        if page >= len(story_texts): in_intro = False
        if not in_intro: break
        scenes[page](screen, tick)
        box_rect = pygame.Rect(100, 550, 1000, 200)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 4)
        pygame.draw.rect(screen, (10, 10, 15), (104, 554, 992, 192))
        if tick % 3 == 0 and char_idx < len(story_texts[page]): char_idx += 1
        text_surf = intro_font.render(story_texts[page][:char_idx], True, (255, 255, 255))
        screen.blit(text_surf, (140, 600))
        if char_idx >= len(story_texts[page]) and (tick // 30) % 2 == 0:
            screen.blit(intro_font.render("▼", True, (255, 255, 255)), (1050, 700))
        pygame.display.flip()
        clock.tick(60)


def run_title_screen(screen):
    clock = pygame.time.Clock()
    city_size = 1800
    city_surf = pygame.Surface((city_size, city_size), pygame.SRCALPHA)
    center = city_size // 2
    for r in range(100, 900, 80):
        pygame.draw.circle(city_surf, (15, 30, 50), (center, center), r, 3)
        pygame.draw.circle(city_surf, (0, 100, 255, 100), (center, center), r + 2, 1)
    for i in range(0, 360, 30):
        rad = math.radians(i)
        pygame.draw.line(city_surf, (15, 30, 50), (center, center),
                         (center + math.cos(rad) * 900, center + math.sin(rad) * 900), 3)
    lights = []
    for _ in range(600):
        angle, radius = random.uniform(0, 2 * math.pi), random.uniform(90, 850)
        color = random.choice([(0, 255, 255), (255, 0, 255), (0, 150, 255), (255, 50, 100)])
        lights.append((angle, radius, color, random.randint(2, 6)))
    for a, r, c, s in lights: pygame.draw.rect(city_surf, c, (center + math.cos(a) * r, center + math.sin(a) * r, s, s))

    angle_offset, tick, waiting = 0, 0, True
    while waiting:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: waiting = False
        screen.fill((5, 10, 20))
        angle_offset += 0.15
        rotated_city = pygame.transform.rotate(city_surf, angle_offset)
        rect = rotated_city.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
        screen.blit(rotated_city, rect.topleft)
        bx, by, levels = screen_width // 2, screen_height // 2 + 150, 22
        for i in range(levels):
            w, h, y_pos = max(10, 180 - (i * 8)), 40, by - (i * 28)
            c_val = min(255, 80 + i * 8)
            pts = [(bx, y_pos + h // 2), (bx - w // 2, y_pos), (bx, y_pos - h // 2), (bx + w // 2, y_pos)]
            pygame.draw.polygon(screen, (c_val, c_val, min(255, c_val + 40)), pts)
            pygame.draw.polygon(screen, (255, 255, 255), pts, 2)
            if i % 3 == 0: pygame.draw.circle(screen, (0, 255, 255), (bx, y_pos), 3)
        top_y = by - (levels * 28)
        pygame.draw.line(screen, (255, 255, 255), (bx, top_y), (bx, top_y - 180), 3)
        if tick % 60 < 30: pygame.draw.circle(screen, (255, 0, 50), (bx, top_y - 180), 6)

        title_surf = title_font.render("キツネ protocol", True, (255, 50, 100))
        screen.blit(title_surf, (screen_width // 2 - title_surf.get_width() // 2, 80))
        subtitle_surf = intro_font.render("HIKARI REVENGE", True, (0, 255, 255))
        screen.blit(subtitle_surf, (screen_width // 2 - subtitle_surf.get_width() // 2, 170))
        if tick % 80 < 40:
            prompt_surf = intro_font.render("PRESS ANY BUTTON TO BEGIN", True, (255, 255, 255))
            screen.blit(prompt_surf, (screen_width // 2 - prompt_surf.get_width() // 2, screen_height - 100))
        pygame.display.flip()
        clock.tick(60)


# ==========================================
# 3. 스테이지 및 배경
# ==========================================
STAGES = {
    "alley": {
        "width": 2200, "height": 800, "ground_y": 700,
        "lighting": (10, 10, 22, 160), "platforms": [(600, 550, 150, 20), (1200, 450, 150, 20)],
        "enemies": [(800, 700, "thug"), (1200, 700, "thug"), (1600, 700, "thug"), (2000, 700, "thug")],
        "next": "early_boss"
    },
    "early_boss": {
        "width": 1600, "height": 800, "ground_y": 700,
        "lighting": (15, 10, 20, 140), "platforms": [],
        "enemies": [(1200, 700, "boss")], "next": "company_front"
    },
    "company_front": {
        "width": 2200, "height": 800, "ground_y": 700,
        "lighting": (180, 220, 255, 50), "platforms": [],
        "enemies": [(800, 700, "shield_guard"), (1200, 700, "shield_guard"), (1600, 700, "shield_guard"),
                    (2000, 700, "shield_guard")], "next": "mid_boss"
    },
    "mid_boss": {
        "width": 2400, "height": 900, "ground_y": 800,
        "lighting": (20, 35, 30, 160), "platforms": [(600, 600, 200, 20), (1600, 600, 200, 20)],
        "enemies": [(1200, 800, "komainu")], "next": "company_hall"
    },
    "company_hall": {
        "width": 2400, "height": 800, "ground_y": 700,
        "lighting": (80, 100, 140, 120), "platforms": [],
        "enemies": [],
        "next": "turret_room"
    },
    "turret_room": {
        "width": 2600, "height": 800, "ground_y": 700,
        "lighting": (10, 20, 15, 150),
        "platforms": [(400, 550, 150, 150), (900, 600, 100, 100), (1400, 500, 120, 200), (1900, 580, 100, 120)],
        "enemies": [
            (300, 100, "turret"), (800, 100, "turret"), (1300, 100, "turret"), (1800, 100, "turret"),
            (2300, 100, "turret"),
            (500, 650, "turret"), (1000, 450, "turret"), (1500, 350, "turret"), (2000, 500, "turret"),
            (2400, 650, "turret")
        ],
        "next": "corridor"
    },
    "corridor": {
        "width": 2800, "height": 700, "ground_y": 600,
        "lighting": (20, 20, 25, 180), "platforms": [],
        "enemies": [(800, 600, "shield_guard"), (1400, 600, "guard"), (2000, 600, "shield_guard"),
                    (2600, 600, "guard")], "next": "final_boss"
    },
    "final_boss": {
        "width": 3200, "height": 800, "ground_y": 700,
        "lighting": (40, 70, 150, 90), "platforms": [],
        "enemies": [(1600, 700, "brother")], "next": None
    },
    "hidden_abyss": {
        "width": 3200, "height": 800, "ground_y": 700,
        "lighting": (20, 10, 30, 100), "platforms": [],
        "enemies": [(1600, 700, "true_boss")], "next": None
    }
}


def generate_bg(stage_id, w, h, gy):
    surf = pygame.Surface((w, h))

    def draw_stars(surface, count, max_y):
        for _ in range(count):
            sx, sy = random.randint(0, w), random.randint(0, max_y)
            color = random.choice([(255, 255, 255), (200, 200, 255), (255, 255, 200)])
            pygame.draw.circle(surface, color, (sx, sy), random.randint(1, 2))

    if stage_id in ["alley", "early_boss"]:
        surf.fill((15, 15, 20));
        draw_stars(surf, int(w / 4), gy)
        for i in range(0, w, 200):
            bh = random.randint(300, 600);
            by = gy - bh
            pygame.draw.rect(surf, (25, 25, 35), (i, by, 180, bh))
            if random.random() > 0.5: pygame.draw.rect(surf, (255, 50, 50), (i + 20, by + 20, 40, 10))
        pygame.draw.rect(surf, (30, 30, 35), (0, gy, w, h - gy))
    elif "company" in stage_id:
        surf.fill((200, 220, 240) if stage_id == "company_front" else (50, 60, 80))
        for i in range(0, w, 300): pygame.draw.rect(surf, (150, 180, 200), (i + 50, 100, 200, gy - 100), 5)
        pygame.draw.rect(surf, (100, 110, 120), (0, gy, w, h - gy))
    elif stage_id == "mid_boss":
        surf.fill((15, 20, 15))
        pygame.draw.rect(surf, (80, 20, 20), (w // 2 - 150, gy - 400, 300, 400), 20)
        pygame.draw.rect(surf, (80, 20, 20), (w // 2 - 200, gy - 400, 400, 30))
        pygame.draw.rect(surf, (40, 40, 45), (0, gy, w, h - gy))
    elif stage_id == "corridor":
        surf.fill((10, 10, 10))
        for i in range(0, w, 150): pygame.draw.rect(surf, (30, 30, 30), (i, 0, 50, gy))
        pygame.draw.rect(surf, (20, 20, 20), (0, gy, w, h - gy))

    elif stage_id == "turret_room":
        surf.fill((10, 15, 15))
        for _ in range(50):
            lx = random.randint(0, w)
            pygame.draw.line(surf, (0, 100, 100), (lx, 0), (lx, h), random.randint(1, 3))
            if random.random() > 0.7:
                pygame.draw.rect(surf, (200, 100, 0), (lx - 2, random.randint(100, gy), 6, random.randint(10, 30)))
        pygame.draw.rect(surf, (20, 25, 25), (0, gy, w, h - gy))

    elif stage_id == "final_boss":
        surf.fill((5, 10, 20))
        draw_stars(surf, int(w / 1.5), gy)
        frame_color = (25, 25, 30)
        glass_overlay = pygame.Surface((w, gy), pygame.SRCALPHA)
        glass_overlay.fill((100, 150, 255, 15))
        surf.blit(glass_overlay, (0, 0))
        pygame.draw.rect(surf, frame_color, (0, 0, w, 100))
        for i in range(0, w, 400):
            pygame.draw.rect(surf, frame_color, (i, 100, 40, gy - 100))
        for j in range(300, gy, 300):
            pygame.draw.rect(surf, frame_color, (0, j, w, 20))
        pygame.draw.rect(surf, frame_color, (0, gy - 20, w, 20))
        pygame.draw.rect(surf, (30, 30, 35), (0, gy, w, h - gy))
        pygame.draw.rect(surf, (150, 20, 30), (0, gy, w, 40))
        pygame.draw.rect(surf, (200, 40, 50), (0, gy, w, 5))

    elif stage_id == "hidden_abyss":
        surf.fill((10, 15, 25))
        draw_stars(surf, int(w / 1.5), gy)
        moon_glow = pygame.Surface((400, 400), pygame.SRCALPHA)
        pygame.draw.circle(moon_glow, (255, 255, 200, 15), (200, 200), 200)
        pygame.draw.circle(moon_glow, (255, 255, 220, 30), (200, 200), 120)
        pygame.draw.circle(moon_glow, (255, 255, 255, 255), (200, 200), 70)
        surf.blit(moon_glow, (w // 2 - 200, 250 - 200))

        frame_color = (25, 25, 30)
        for i in range(0, w, 300):
            broken_height = random.randint(150, 400)
            pygame.draw.rect(surf, frame_color, (i, gy - broken_height, 60, broken_height))
            pygame.draw.polygon(surf, (40, 40, 45),
                                [(i, gy - broken_height), (i + 30, gy - broken_height - random.randint(20, 50)),
                                 (i + 60, gy - broken_height)])
            pygame.draw.rect(surf, (15, 15, 20), (i + 40, gy - broken_height, 20, broken_height))

        for j in range(400, gy, 150):
            for i in range(0, w, 300):
                if random.random() > 0.4:
                    length = random.randint(100, 250)
                    pygame.draw.rect(surf, frame_color, (i + random.randint(0, 50), j, length, 25))

        pygame.draw.rect(surf, frame_color, (0, gy - 30, w, 30))
        pygame.draw.rect(surf, (20, 20, 25), (0, gy, w, h - gy))
        pygame.draw.rect(surf, (150, 20, 30), (0, gy, w, 15))

    return surf


current_stage_id = "alley"
current_stage = STAGES[current_stage_id]
bg_surf = None
cam_x, cam_y = 0, 0

security_disabled = False
laser_lines = []
hidden_button_rect = None
puzzle_password = ""
input_password = ""
terminal_rect = None
cheat_terminal_rect = None
active_terminal = ""
is_typing = False
turret_timer = -1


def load_stage(stage_id):
    global current_stage_id, current_stage, bg_surf, platforms, ground_y, dummies, p_x, p_y
    global ghosts, combo_effects, black_flames, slashes, wire_spawn, explosions, d_texts, steam, sparkles, dash_effects, enemy_projectiles, boss_effects
    global security_disabled, laser_lines, hidden_button_rect, puzzle_password, input_password, terminal_rect, cheat_terminal_rect, active_terminal, is_typing
    global turret_timer

    current_stage_id = stage_id
    current_stage = STAGES[stage_id]
    ground_y = current_stage["ground_y"]
    bg_surf = generate_bg(stage_id, current_stage["width"], current_stage["height"], ground_y)

    platforms = [pygame.Rect(*p) for p in current_stage["platforms"]]
    dummies = []

    security_disabled = False
    laser_lines = []
    hidden_button_rect = None
    puzzle_password = ""
    input_password = ""
    terminal_rect = None
    cheat_terminal_rect = None
    active_terminal = ""
    is_typing = False

    if stage_id == "alley":
        cheat_terminal_rect = pygame.Rect(40, ground_y - 80, 60, 80)

    if stage_id == "company_hall":
        puzzle_password = str(random.randint(1000, 9999))
        terminal_rect = pygame.Rect(2100, ground_y - 80, 60, 80)
        platforms.append(pygame.Rect(800, 500, 100, 20))
        platforms.append(pygame.Rect(950, 350, 100, 20))
        for _ in range(30):
            pt1 = (random.randint(1200, 1600), random.randint(0, ground_y))
            pt2 = (random.randint(1200, 1600), random.randint(0, ground_y))
            laser_lines.append((pt1, pt2))
        hidden_button_rect = pygame.Rect(970, 120, 60, 60)

    if stage_id == "turret_room":
        turret_timer = 3600
    else:
        turret_timer = -1

    for ex, ey, etype in current_stage["enemies"]:
        dummies.append(DummyBot(ex, ey, is_special=(etype in ["boss", "komainu", "brother", "true_boss"]), etype=etype))

    if stage_id != "hidden_abyss":
        p_x, p_y = 100, ground_y
    ghosts, combo_effects, black_flames, slashes, wire_spawn, explosions, d_texts, steam, sparkles, dash_effects, enemy_projectiles, boss_effects = [], [], [], [], [], [], [], [], [], [], [], []


def update_camera():
    global cam_x, cam_y
    target_x = p_x - screen_width // 2
    target_y = p_y - screen_height // 2 + 100
    cam_x += (target_x - cam_x) * 0.1
    cam_y += (target_y - cam_y) * 0.1
    if ground_y < 90000:
        cam_x = max(0, min(cam_x, current_stage["width"] - screen_width))
        cam_y = max(0, min(cam_y, current_stage["height"] - screen_height))


# ==========================================
# 4. 이펙트 및 파티클
# ==========================================
class BossSlashEffect:
    def __init__(self, x, y, angle, scale=1.0, color=(255, 50, 50)):
        self.x, self.y, self.angle, self.life = x, y, angle, 15
        self.scale = scale
        self.color = color

    def update(self): self.life -= 1

    def draw(self, target_surf, cx, cy):
        if self.life > 0:
            alpha = int((self.life / 15) * 255)
            px1 = self.x - cx + math.cos(self.angle - 0.5) * (40 * self.scale)
            py1 = self.y - cy + math.sin(self.angle - 0.5) * (40 * self.scale)
            px2 = self.x - cx + math.cos(self.angle + 0.5) * (40 * self.scale)
            py2 = self.y - cy + math.sin(self.angle + 0.5) * (40 * self.scale)
            px3 = self.x - cx + math.cos(self.angle) * (160 * self.scale)
            py3 = self.y - cy + math.sin(self.angle) * (160 * self.scale)
            pygame.draw.polygon(target_surf, self.color[:3] + (alpha,),
                                [(self.x - cx, self.y - cy), (px1, py1), (px3, py3), (px2, py2)])


class EnemyProjectile:
    def __init__(self, x, y, tx, ty, speed=6, dmg=10, stun=0, color=(255, 50, 0), radius=6, is_missile=False,
                 parryable=False, is_crescent=False):
        self.x, self.y = x, y
        self.speed = speed
        self.angle = math.atan2(ty - y, tx - x)
        self.dx, self.dy = math.cos(self.angle) * speed, math.sin(self.angle) * speed
        self.active = True
        self.dmg = dmg
        self.stun = stun
        self.color = color
        self.radius = radius
        self.is_missile = is_missile
        self.parryable = parryable
        self.is_reflected = False
        self.is_crescent = is_crescent

    def update(self, px=0, py=0, bx=0, by=0):
        if self.is_missile:
            target_x = bx if self.is_reflected else px
            target_y = by if self.is_reflected else py
            target_angle = math.atan2(target_y - self.y, target_x - self.x)
            ang_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += max(-0.015, min(0.015, ang_diff))
            self.dx, self.dy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed
        self.x += self.dx;
        self.y += self.dy

    def draw(self, screen, cx, cy):
        if getattr(self, 'is_thrust', False):
            p1 = (self.x - cx, self.y - cy)
            p2 = (self.x - math.cos(self.angle) * 150 - cx, self.y - math.sin(self.angle) * 150 - cy)
            pygame.draw.line(screen, (255, 0, 0), p1, p2, 40)
            pygame.draw.line(screen, (255, 255, 255), p1, p2, 10)
        elif getattr(self, 'is_cannon', False):
            pygame.draw.circle(screen, (255, 50, 0), (int(self.x - cx), int(self.y - cy)), self.radius)
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x - cx), int(self.y - cy)), self.radius - 10)
        elif self.is_crescent:
            pygame.draw.circle(screen, self.color, (int(self.x - cx), int(self.y - cy)), self.radius, 3)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x - cx), int(self.y - cy)), self.radius)
            if self.is_missile:
                pygame.draw.circle(screen, (255, 200, 0), (int(self.x - cx), int(self.y - cy)), self.radius // 2)


class ComboEffect:
    def __init__(self, combo_type, pos, target_pos, facing_dir):
        self.type, self.pos, self.lifetime, self.max_life, self.lines = combo_type, list(pos), 15, 15, []
        self.angle = math.atan2(target_pos[1] - pos[1], target_pos[0] - pos[0])

        if combo_type == 1:
            arc = [(pos[0] + math.cos(self.angle + math.radians(i)) * 140,
                    pos[1] + math.sin(self.angle + math.radians(i)) * 140) for i in range(-45, 46, 10)]
            self.lines.append({'pts': arc, 'color': (255, 50, 50), 'w1': 10, 'w2': 4})
        elif combo_type == 2:
            circle1, circle2 = [], []
            cx, cy = pos[0] + math.cos(self.angle) * 20, pos[1] + math.sin(self.angle) * 20
            for i in range(0, 361, 20):
                rad = math.radians(i)
                circle1.append((cx + math.cos(rad) * 140, cy + math.sin(rad) * 140))
                circle2.append((cx + math.cos(rad) * 110, cy + math.sin(rad) * 110))
            self.lines.append({'pts': circle1, 'color': (220, 20, 50), 'w1': 12, 'w2': 4})
            self.lines.append({'pts': circle2, 'color': (255, 50, 50), 'w1': 6, 'w2': 2})
        elif combo_type == 3:
            l = 350
            self.lines.append(
                {'pts': [(pos[0], pos[1]), (pos[0] + math.cos(self.angle) * l, pos[1] + math.sin(self.angle) * l)],
                 'color': (255, 0, 0), 'w1': 12, 'w2': 5})
            for _ in range(6):
                off = self.angle + random.uniform(-0.15, 0.15);
                sl = random.uniform(150, 320)
                self.lines.append(
                    {'pts': [(pos[0], pos[1]), (pos[0] + math.cos(off) * sl, pos[1] + math.sin(off) * sl)],
                     'color': (255, 50, 50), 'w1': 4, 'w2': 2})

    def update(self):
        self.lifetime -= 1

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_life))))
        if alpha <= 0: return
        for line in self.lines:
            pts = [(p[0] - cx, p[1] - cy) for p in line['pts']]
            c = line['color']
            if len(pts) == 2:
                pygame.draw.line(target_surf, c + (alpha,), pts[0], pts[1], line['w1'])
                pygame.draw.line(target_surf, (255, 255, 255, alpha), pts[0], pts[1], line['w2'])
            elif len(pts) > 2:
                pygame.draw.lines(target_surf, c + (alpha,), False, pts, line['w1'])
                pygame.draw.lines(target_surf, (255, 255, 255, alpha), False, pts, line['w2'])


class CrescentSlash:
    def __init__(self, p_pos, mouse_pos, sparkles, black_flames, p_size_h, dummies, d_texts):
        self.sparkles = sparkles;
        self.black_flames = black_flames;
        self.dummies = dummies;
        self.d_texts = d_texts;
        self.hit_targets = []
        p_x, p_y = p_pos;
        m_x, m_y = mouse_pos
        self.max_frames, self.current_frame, self.trail_life = 18, 0, 6
        self.lifetime = self.max_frames + self.trail_life
        self.history = []
        self.apex = (p_x, p_y - 20)
        self.target_angle = math.atan2(m_y - self.apex[1], m_x - self.apex[0])
        self.L = max(180, int(1.8 * p_size_h));
        self.width_angle = 0.8
        self.start_angle = self.target_angle - self.width_angle;
        self.end_angle = self.target_angle + self.width_angle

    def update(self):
        global akai_stack, p_stun_timer
        self.lifetime -= 1
        for h in self.history: h['life'] -= 1
        self.history = [h for h in self.history if h['life'] > 0]

        if self.current_frame <= self.max_frames:
            progress = self.current_frame / self.max_frames
            curr_angle = self.start_angle + (self.end_angle - self.start_angle) * progress
            self.history.append({'angle': curr_angle, 'life': self.trail_life})

            for d in self.dummies:
                if d.state == "ALIVE" and d not in self.hit_targets:
                    dist = math.hypot(d.x - self.apex[0], d.y - self.apex[1])
                    ang_to_d = math.atan2(d.y - self.apex[1], d.x - self.apex[0])
                    ang_diff = (ang_to_d - curr_angle + math.pi) % (2 * math.pi) - math.pi
                    if dist <= self.L + 40 and abs(ang_diff) < 0.35:

                        if getattr(d, 'has_shield', False):
                            ang_to_hit = math.atan2(self.apex[1] - d.y, self.apex[0] - d.x)
                            shield_diff = (ang_to_hit - d.shield_ang + math.pi) % (2 * math.pi) - math.pi
                            if abs(shield_diff) < 0.8:
                                self.hit_targets.append(d)
                                self.d_texts.append(
                                    DamageText(d.rect.centerx, d.rect.top - 30, "BLOCKED", (0, 255, 255)))
                                for _ in range(5): self.sparkles.append(
                                    AmaterasuWhiteCoreParticle(d.x + math.cos(d.shield_ang) * d.shield_dist,
                                                               d.y + math.sin(d.shield_ang) * d.shield_dist, True))
                                continue

                        self.hit_targets.append(d)
                        if d.etype == "true_boss":
                            self.d_texts.append(DamageText(d.rect.centerx, d.rect.top - 20, "IMMUNE", (100, 100, 100)))
                        elif d.etype == "boss" and d.boss_state == "PARRY":
                            p_stun_timer = 120
                            self.d_texts.append(DamageText(self.apex[0], self.apex[1] - 50, "PARRIED!", (255, 255, 0)))
                        else:
                            d.hp -= 25;
                            d.burn_timer = 240
                            self.d_texts.append(DamageText(d.rect.centerx, d.rect.top - 30, "25"))
                            akai_stack = min(9, akai_stack + 1)
                            if d.hp <= 0 and not (d.etype == "brother" and getattr(d, 'phase', 1) == 2):
                                d.hp, d.state, d.timer, d.death_type = 0, "DYING", 60, "NORMAL"

            for _ in range(40):
                r = math.sqrt(random.random()) * self.L
                px, py = self.apex[0] + math.cos(curr_angle) * r, self.apex[1] + math.sin(curr_angle) * r
                if random.random() < 0.5: self.sparkles.append(AmaterasuWhiteCoreParticle(px, py, is_static=True))
                if random.random() < 0.8: self.black_flames.append(BlackFlameParticle(px, py, is_static=True))
                if random.random() < 0.4: self.sparkles.append(AmaterasuSilverShell(px, py, curr_angle, is_static=True))

            tip_x, tip_y = self.apex[0] + math.cos(curr_angle) * self.L, self.apex[1] + math.sin(curr_angle) * self.L
            for _ in range(4):
                if random.random() < 0.7: self.sparkles.append(
                    AmaterasuSilverShell(tip_x, tip_y, curr_angle, is_static=False))
                if random.random() < 0.5: self.sparkles.append(
                    AmaterasuWhiteCoreParticle(tip_x, tip_y, is_static=False))
            self.current_frame += 1

    def draw(self, target_surf, cx, cy):
        if not self.history: return
        for h in self.history:
            a, alpha = h['angle'], int(200 * (h['life'] / self.trail_life))
            apex_c, tip_c = (self.apex[0] - cx, self.apex[1] - cy), (self.apex[0] + math.cos(a) * self.L - cx,
                                                                     self.apex[1] + math.sin(a) * self.L - cy)
            pygame.draw.line(target_surf, (0, 0, 0, alpha), apex_c, tip_c, 35)
        for h in self.history:
            a, alpha = h['angle'], int(255 * (h['life'] / self.trail_life))
            apex_c, tip_c = (self.apex[0] - cx, self.apex[1] - cy), (self.apex[0] + math.cos(a) * self.L - cx,
                                                                     self.apex[1] + math.sin(a) * self.L - cy)
            pygame.draw.line(target_surf, (150, 150, 150, alpha), apex_c, tip_c, 15)
            pygame.draw.line(target_surf, (255, 255, 255, alpha), apex_c, tip_c, 5)


class DashThrustEffect:
    def __init__(self, x, y, angle):
        self.x, self.y, self.angle, self.lifetime, self.max_life, self.size = x, y, angle, 15, 15, 65

    def update(self): self.lifetime -= 1

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_life))))
        if alpha <= 0: return
        apex_x, apex_y = self.x + math.cos(self.angle) * self.size - cx, self.y + math.sin(self.angle) * self.size - cy
        ta, ba = self.angle + math.radians(155), self.angle - math.radians(155)
        top_x, top_y = apex_x + math.cos(ta) * self.size * 1.4, apex_y + math.sin(ta) * self.size * 1.4
        bot_x, bot_y = apex_x + math.cos(ba) * self.size * 1.4, apex_y + math.sin(ba) * self.size * 1.4
        pts = [(top_x, top_y), (apex_x, apex_y), (bot_x, bot_y)]
        pygame.draw.lines(target_surf, (0, 0, 0, alpha), False, pts, 20)
        pygame.draw.lines(target_surf, (0, 255, 255, alpha), False, pts, 8)
        pygame.draw.lines(target_surf, (255, 255, 255, alpha), False, pts, 3)


class SteamParticle:
    def __init__(self, x, y, color=(255, 255, 255)):
        self.x, self.y = x + random.randint(-20, 20), y + random.randint(-10, 30)
        self.vel_x, self.vel_y = random.uniform(-0.8, 0.8), random.uniform(-0.5, -2.5)
        self.radius, self.alpha, self.color, self.fade_speed = random.randint(5, 12), 220, color, random.randint(8, 15)

    def update(self):
        self.x += self.vel_x;
        self.y += self.vel_y;
        self.alpha -= self.fade_speed
        if self.radius > 0.8: self.radius -= 0.15

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, self.color + (alpha,), (int(self.x - cx), int(self.y - cy)),
                               int(self.radius))

    def is_vanished(self):
        return self.alpha <= 0


class BlackFlameParticle:
    def __init__(self, x, y, is_static=False):
        self.x, self.y = x + random.randint(-15, 15), y + random.randint(-15, 15)
        self.vel_x, self.vel_y = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) if is_static else (0,
                                                                                                           random.uniform(
                                                                                                               -1, -3))
        self.fade_speed = 45 if is_static else 15
        self.radius, self.alpha = random.uniform(3, 7), 255

    def update(self):
        self.x += self.vel_x;
        self.y += self.vel_y;
        self.alpha -= self.fade_speed
        if self.radius > 0: self.radius -= 0.2

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, (0, 0, 0, alpha), (int(self.x - cx), int(self.y - cy)), int(self.radius))

    def is_vanished(self):
        return self.alpha <= 0


class AmaterasuSparkle:
    def __init__(self, x, y, is_static=False):
        self.x, self.y = x + random.randint(-15, 15), y + random.randint(-10, 10)
        self.vel_x, self.vel_y = (random.uniform(-1, 1), random.uniform(-1, 1)) if is_static else (
            random.uniform(-2, 2), random.uniform(-2, 2))
        self.fade_speed = 45 if is_static else random.randint(15, 25)
        self.radius, self.alpha = random.uniform(1, 3), 255
        self.color = random.choice([(150, 255, 255), (255, 255, 255)])

    def update(self): self.x += self.vel_x; self.y += self.vel_y; self.alpha -= self.fade_speed

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, self.color + (alpha,), (int(self.x - cx), int(self.y - cy)),
                               int(self.radius))

    def is_vanished(self): return self.alpha <= 0


class AmaterasuSilverShell:
    def __init__(self, x, y, angle, is_static=False):
        dist = random.uniform(5, 20);
        shell_angle = angle + random.choice([-1.5, 1.5])
        self.x, self.y = x + math.cos(shell_angle) * dist, y + math.sin(shell_angle) * dist
        if is_static:
            self.vel_x, self.vel_y = random.uniform(-1, 1), random.uniform(-1, 1);
            self.fade_speed = 45
        else:
            spd = random.uniform(3, 8);
            self.vel_x, self.vel_y = math.cos(angle) * spd, math.sin(angle) * spd;
            self.fade_speed = random.randint(20, 35)
        self.radius, self.alpha = random.uniform(2, 5), 255
        self.color = random.choice([(200, 200, 200), (220, 220, 220), (255, 255, 255)])

    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.alpha -= self.fade_speed

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, self.color + (alpha,), (int(self.x - cx), int(self.y - cy)),
                               int(self.radius))

    def is_vanished(self):
        return self.alpha <= 0


class AmaterasuWhiteCoreParticle:
    def __init__(self, x, y, is_static=False):
        self.x, self.y = x + random.randint(-8, 8), y + random.randint(-8, 8)
        self.vel_x, self.vel_y = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) if is_static else (0, 0)
        self.fade_speed = 45 if is_static else random.randint(30, 45)
        self.radius, self.alpha = random.uniform(4, 9), 255
        self.color = (255, 255, 255)

    def update(self):
        self.x += self.vel_x;
        self.y += self.vel_y
        self.alpha -= self.fade_speed
        if self.radius > 0: self.radius -= 0.3

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, (255, 255, 255, alpha), (int(self.x - cx), int(self.y - cy)),
                               int(self.radius))

    def is_vanished(self):
        return self.alpha <= 0


class DamageText:
    def __init__(self, x, y, damage, color=None):
        self.x, self.y, self.damage, self.alpha, self.life = x, y, str(damage), 255, 30
        if color:
            self.color = color
        else:
            self.color = (255, 100, 0) if damage in ["15", "4", "20", "10", "25", "30", "40", "50", "80"] else (255, 50,
                                                                                                                50)

    def update(self):
        self.y -= 1; self.alpha -= 8; self.life -= 1

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0:
            s = font.render(self.damage, True, self.color);
            s.set_alpha(alpha);
            target_surf.blit(s, (self.x - cx, self.y - cy))


class Ghost:
    def __init__(self, x, y, image, alpha, tint=None):
        self.x, self.y, self.image, self.alpha, self.tint = x, y, image.copy(), alpha, tint

    def update(self):
        self.alpha -= 25

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0:
            self.image.set_alpha(alpha)
            if self.tint:
                t = pygame.Surface(self.image.get_size(), pygame.SRCALPHA);
                t.fill(self.tint);
                self.image.blit(t, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            target_surf.blit(self.image, self.image.get_rect(center=(self.x - cx, self.y - cy)))

    def is_vanished(self):
        return self.alpha <= 0


class WireSpawnParticle:
    def __init__(self, x, y):
        self.cx, self.cy = x, y
        self.color, self.angle, self.orbit = random.choice([(100, 20, 20), (255, 60, 0)]), random.uniform(0,
                                                                                                          6.28), random.randint(
            10, 35)
        self.radius, self.alpha, self.fade_speed = random.uniform(3, 8), 255, random.randint(10, 20)

    def update(self):
        self.alpha -= self.fade_speed;
        self.angle += 0.2
        self.x = self.cx + math.cos(self.angle) * self.orbit;
        self.y = self.cy + math.sin(self.angle) * self.orbit
        if self.radius > 0.5: self.radius -= 0.1

    def draw(self, target_surf, cx, cy):
        alpha = max(0, min(255, int(self.alpha)))
        if alpha > 0 and self.radius >= 1:
            pygame.draw.circle(target_surf, self.color + (alpha,), (int(self.x - cx), int(self.y - cy)),
                               int(self.radius))

    def is_vanished(self):
        return self.alpha <= 0


class AkaiIto:
    def __init__(self, sx, sy, tx, ty):
        angle = math.atan2(ty - sy, tx - sx)
        self.dx, self.dy = math.cos(angle) * 25, math.sin(angle) * 25
        self.curr_x, self.curr_y = sx, sy
        self.pulling = False
        self.is_dead = False

    def update(self, platforms):
        if not self.pulling and not self.is_dead:
            self.curr_x += self.dx;
            self.curr_y += self.dy
            if self.curr_y <= 0:
                self.curr_y, self.pulling = 0, True
            elif self.curr_x <= 0 or self.curr_x >= current_stage["width"] or self.curr_y >= current_stage["ground_y"]:
                self.is_dead = True
            for p in platforms:
                if p.collidepoint(self.curr_x, self.curr_y): self.pulling = True


# ==========================================
# 5. 봇 (보스 및 적) 클래스
# ==========================================
class DummyBot:
    def __init__(self, x, y, is_special=False, etype="guard"):
        self.etype = etype
        if etype == "komainu":
            self.max_hp = 500
        elif etype == "brother":
            self.max_hp = 1000
        elif etype == "true_boss":
            self.max_hp = 1000
        elif etype == "turret":
            self.max_hp = 40
        elif etype == "shield_guard":
            self.max_hp = 150
        elif is_special:
            self.max_hp = 350
        else:
            self.max_hp = 100

        self.x, self.y, self.hp, self.v_y, self.state, self.is_special = x, y, self.max_hp, 0, "ALIVE", is_special

        self.scale = 2.0 if etype == "komainu" else 0.8 if etype == "brother" else 2.5 if etype == "true_boss" else 1.0
        orig_w, orig_h = player_img_left.get_size()
        self.img = pygame.transform.smoothscale(player_img_left, (int(orig_w * self.scale), int(orig_h * self.scale)))

        self.rect = self.img.get_rect(center=(x, y))
        self.timer, self.burn_timer, self.is_airborne = 0, 0, False
        self.split_timer, self.death_type = 0, "NORMAL"
        self.attack_timer = random.randint(60, 180)

        self.boss_state = "IDLE" if etype not in ["brother", "true_boss"] else "HOVER" if etype == "brother" else "IDLE"
        self.combo_step = 0
        self.dash_dir = 0
        self.phase = 1
        self.phase2 = False
        self.jump_count = 0
        self.charge_count = 0
        self.target_x = 0

        self.hover_angle = 0
        self.lasers = []
        self.bullet_timer = random.randint(60, 300) if etype == "turret" else 300
        self.aura_lifetime = 0
        self.aura_timer = 0
        self.grid_target = (0, 0)
        self.prep_hp = 0
        self.parry_count = 0

        self.has_shield = (etype == "shield_guard")
        self.shield_ang = 0
        self.shield_dist = 65

    def update(self, explosions, d_texts, px=0, py=0, projs=None, boss_effs=None, ghost_list=None, draw_surf=None, cx=0,
               cy=0):
        global ground_y, p_bind_timer, p_x, p_y, game_state, screen_cracks, screen_crack_timer, v_y

        if self.state == "DYING":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "DEAD";
                self.timer = 180
                if self.death_type == "THREAD":
                    for _ in range(15): explosions.append(
                        [self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), 25])
                else:
                    for _ in range(20): explosions.append(
                        [self.x, self.y, random.uniform(-6, 6), random.uniform(-6, 6), 25])
        elif self.state == "DEAD":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "ALIVE";
                self.hp, self.v_y, self.is_airborne, self.burn_timer = self.max_hp, 0, False, 0
                self.split_timer, self.death_type = 0, "NORMAL"
                self.boss_state = "IDLE" if self.etype not in ["brother",
                                                               "true_boss"] else "HOVER" if self.etype == "brother" else "IDLE"
                self.phase = 1
                self.phase2 = False
                self.lasers.clear()
                self.bullet_timer = 300
                self.aura_lifetime = 0

        if self.state == "ALIVE":
            dist = math.hypot(px - self.x, py - self.y)

            if self.etype == "turret":
                self.bullet_timer -= 1
                if self.bullet_timer <= 0:
                    if projs is not None:
                        projs.append(
                            EnemyProjectile(self.x, self.y, px, py, speed=5, dmg=15, color=(255, 0, 0), radius=8,
                                            is_missile=True, parryable=True))
                    self.bullet_timer = 300
                return

            if self.has_shield:
                target_ang = math.atan2(py - self.y, px - self.x)
                ang_diff = (target_ang - self.shield_ang + math.pi) % (2 * math.pi) - math.pi
                self.shield_ang += max(-0.005, min(0.005, ang_diff))

                sx = self.x + math.cos(self.shield_ang) * self.shield_dist
                sy = self.y + math.sin(self.shield_ang) * self.shield_dist

                if math.hypot(px - sx, py - sy) < 35 and p_stun_timer <= 0:
                    hit_player(5, d_texts, px, py, stun_time=30)
                    p_x += 60 if px > sx else -60
                    v_y = -8

            if not self.is_special:
                if self.etype == "shield_guard":
                    if dist > 300:
                        self.x += 2 if px > self.x else -2
                    elif dist < 200:
                        self.x -= 2 if px > self.x else -2
                else:
                    if dist > 150:
                        self.x += 2 if px > self.x else -2
                    else:
                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            ang = math.atan2(py - self.y, px - self.x)
                            if boss_effs is not None: boss_effs.append(BossSlashEffect(self.x, self.y, ang))
                            hit_player(5, d_texts, px, py)
                            self.attack_timer = 120

            elif self.etype == "true_boss":
                if self.boss_state == "IDLE":
                    self.attack_timer -= 1
                    self.x += (px - self.x) * 0.015
                    if self.attack_timer <= 0:
                        choice = random.random()
                        if choice < 0.25:
                            self.boss_state = "SMASH_PREP"
                            self.attack_timer = 50
                        elif choice < 0.5:
                            self.boss_state = "THRUST_PREP"
                            self.attack_timer = 50
                        elif choice < 0.75:
                            self.boss_state = "SPRAY_PREP"
                            self.attack_timer = 40
                        else:
                            self.boss_state = "CANNON_PREP"
                            self.attack_timer = 60
                elif self.boss_state == "SMASH_PREP":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.boss_state = "SMASH_EXECUTE"
                        self.attack_timer = 20
                elif self.boss_state == "SMASH_EXECUTE":
                    self.attack_timer -= 1
                    if self.attack_timer == 15:
                        if boss_effs is not None:
                            boss_effs.append(
                                BossSlashEffect(self.x, self.y, math.pi / 2, scale=4.0, color=(255, 50, 0)))
                        if abs(px - self.x) < 300:
                            hit_player(40, d_texts, px, py, stun_time=60)
                        for _ in range(10):
                            ex, ey = self.x + random.randint(-150, 150), ground_y
                            explosions.append(
                                [ex, ey, random.uniform(-2, 2), random.uniform(-5, 0), random.randint(30, 60)])
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE"
                        self.attack_timer = 60
                elif self.boss_state == "THRUST_PREP":
                    self.attack_timer -= 1
                    self.dash_dir = math.atan2(py - self.y, px - self.x)
                    if ghost_list is not None and self.attack_timer % 5 == 0:
                        ghost_list.append(Ghost(self.x, self.y, self.img, 150, (150, 0, 0, 100)))
                    if self.attack_timer <= 0:
                        self.boss_state = "THRUST_EXECUTE"
                        self.attack_timer = 30
                elif self.boss_state == "THRUST_EXECUTE":
                    self.attack_timer -= 1
                    if self.attack_timer == 25:
                        proj = EnemyProjectile(self.x, self.y, px, py, speed=25, dmg=0, color=(255, 0, 0), radius=40,
                                               parryable=True)
                        proj.is_thrust = True
                        if projs is not None: projs.append(proj)
                        for _ in range(5):
                            explosions.append([self.x, self.y, random.uniform(-5, 5), random.uniform(-5, 5), 50])
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE"
                        self.attack_timer = 60
                elif self.boss_state == "SPRAY_PREP":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.boss_state = "SPRAY_EXECUTE"
                        self.attack_timer = 20
                elif self.boss_state == "SPRAY_EXECUTE":
                    self.attack_timer -= 1
                    if self.attack_timer % 4 == 0:
                        ang = math.atan2(py - self.y, px - self.x)
                        for i in range(-2, 3):
                            spread = ang + (i * 0.2)
                            tx = self.x + math.cos(spread) * 100
                            ty = self.y + math.sin(spread) * 100
                            if projs is not None:
                                projs.append(
                                    EnemyProjectile(self.x, self.y, tx, ty, speed=18, dmg=15, color=(255, 100, 0),
                                                    radius=8, parryable=False))
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE"
                        self.attack_timer = 60
                elif self.boss_state == "CANNON_PREP":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.boss_state = "CANNON_EXECUTE"
                        self.attack_timer = 20
                elif self.boss_state == "CANNON_EXECUTE":
                    self.attack_timer -= 1
                    if self.attack_timer == 15:
                        ang = math.atan2(py - self.y, px - self.x)
                        tx = self.x + math.cos(ang) * 100
                        ty = self.y + math.sin(ang) * 100
                        if projs is not None:
                            proj = EnemyProjectile(self.x, self.y, tx, ty, speed=30, dmg=50, color=(255, 50, 0),
                                                   radius=50, parryable=False)
                            proj.is_cannon = True
                            projs.append(proj)
                        explosions.append([self.x, self.y, 0, 0, 100])
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE"
                        self.attack_timer = 90

            elif self.etype == "boss":
                if self.boss_state == "IDLE":
                    self.attack_timer -= 1
                    if self.x < px:
                        self.x += 1
                    else:
                        self.x -= 1
                    if self.attack_timer <= 0:
                        choice = random.random()
                        if choice < 0.25:
                            self.boss_state = "PARRY"
                            self.attack_timer = 90
                        elif dist < 180:
                            self.boss_state = "COMBO"
                            self.combo_step = 0
                            self.attack_timer = 20
                        else:
                            self.boss_state = "BATTO"
                            self.attack_timer = 40
                elif self.boss_state == "PARRY":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE";
                        self.attack_timer = random.randint(60, 120)
                elif self.boss_state == "COMBO":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        ang = math.atan2(py - self.y, px - self.x)
                        if boss_effs is not None: boss_effs.append(BossSlashEffect(self.x, self.y, ang))
                        if dist < 180: hit_player(10, d_texts, px, py)
                        self.combo_step += 1
                        if self.combo_step >= 3:
                            self.boss_state = "IDLE";
                            self.attack_timer = random.randint(60, 120)
                        else:
                            self.attack_timer = 25
                elif self.boss_state == "BATTO":
                    self.attack_timer -= 1
                    if self.attack_timer > 15:
                        self.dash_dir = math.atan2(py - self.y, px - self.x)
                        self.has_hit_batto = False
                    elif self.attack_timer == 15:
                        pass
                    elif self.attack_timer < 0:
                        self.x += math.cos(self.dash_dir) * 35
                        self.y += math.sin(self.dash_dir) * 35
                        if self.y > ground_y: self.y = ground_y
                        if ghost_list is not None and self.attack_timer % 2 == 0:
                            ghost_list.append(Ghost(self.x, self.y, player_img_left, 150, (255, 50, 50, 100)))
                        if not getattr(self, 'has_hit_batto', False) and math.hypot(px - self.x, py - self.y) < 60:
                            hit_player(5, d_texts, px, py)
                            self.has_hit_batto = True
                        if self.attack_timer < -15:
                            self.boss_state = "IDLE";
                            self.attack_timer = random.randint(60, 120)

            elif self.etype == "komainu":
                if not self.phase2 and self.hp <= self.max_hp * 0.5:
                    self.phase2 = True
                    heal_amount = self.max_hp * 0.10
                    self.hp = min(self.max_hp, self.hp + heal_amount)
                    self.boss_state = "SKY_JUMP"
                    self.v_y = -30
                    self.scale = 2.2
                    orig_w, orig_h = player_img_left.get_size()
                    self.img = pygame.transform.smoothscale(player_img_left,
                                                            (int(orig_w * self.scale), int(orig_h * self.scale)))
                    self.rect = self.img.get_rect(center=(self.x, self.y))
                    d_texts.append(DamageText(self.x, self.y - 80, "+RECOVER", (0, 255, 0)))

                if self.boss_state == "SKY_JUMP":
                    self.v_y -= 1
                    self.y += self.v_y
                    if self.y < -500:
                        self.x = current_stage["width"] // 2
                        self.boss_state = "FALLING"
                        self.v_y = 0
                elif self.boss_state == "FALLING":
                    self.v_y += 1.5
                    self.y += self.v_y
                    if draw_surf:
                        pygame.draw.circle(draw_surf, (255, 50, 50), (int(self.x - cx), int(ground_y - cy)), 300, 2)
                    if self.y >= ground_y:
                        self.y = ground_y
                        self.boss_state = "STUNNED"
                        self.attack_timer = 300
                        for _ in range(30): explosions.append(
                            [self.x, self.y, random.uniform(-15, 15), random.uniform(-10, 0), 40])
                        if math.hypot(px - self.x, py - self.y) < 300: hit_player(30, d_texts, px, py)
                elif self.boss_state == "IDLE":
                    self.attack_timer -= 1
                    if self.attack_timer <= 0:
                        if self.phase2:
                            if random.random() < 0.6:
                                self.boss_state = "CHARGE_PREP"
                                self.charge_count = 0
                                self.attack_timer = 40
                            else:
                                self.boss_state = "JUMP_PREP"
                                self.jump_count = 0
                                self.attack_timer = 30
                        else:
                            self.boss_state = "JUMP_PREP"
                            self.jump_count = 0
                            self.attack_timer = 30
                elif self.boss_state == "JUMP_PREP":
                    self.attack_timer -= 1
                    self.target_x = px
                    if draw_surf:
                        pygame.draw.circle(draw_surf, (255, 50, 50), (int(self.target_x - cx), int(ground_y - cy)),
                                           int(150 * (30 - self.attack_timer) / 30), 2)
                    if self.attack_timer <= 0:
                        self.boss_state = "JUMP"
                        self.v_y = -25
                elif self.boss_state == "JUMP":
                    self.v_y += 0.8
                    self.y += self.v_y
                    if self.v_y < 0:
                        if self.x < self.target_x:
                            self.x += 8
                        elif self.x > self.target_x:
                            self.x -= 8
                    else:
                        self.v_y += 1.5
                    if self.y >= ground_y:
                        self.y = ground_y
                        self.v_y = 0
                        for _ in range(20): explosions.append(
                            [self.x, self.y, random.uniform(-5, 5), random.uniform(-3, 0), 25])
                        if math.hypot(px - self.x, py - self.y) < 150: hit_player(5, d_texts, px, py)
                        self.jump_count += 1
                        if self.jump_count >= 3:
                            self.boss_state = "IDLE"
                            self.attack_timer = 120
                        else:
                            self.boss_state = "JUMP_PREP"
                            self.attack_timer = 30
                elif self.boss_state == "CHARGE_PREP":
                    self.attack_timer -= 1
                    self.dash_dir = 0 if px > self.x else math.pi

                    if draw_surf:
                        alpha_v = int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.02))
                        pygame.draw.line(draw_surf, (255, 0, 0, alpha_v), (int(self.x - cx), int(self.y - cy)),
                                         (int(self.x - cx + math.cos(self.dash_dir) * 2000),
                                          int(self.y - cy + math.sin(self.dash_dir) * 2000)), 5)

                    if self.attack_timer % 5 == 0 and ghost_list is not None:
                        ghost_list.append(Ghost(self.x, self.y, self.img, 150, (255, 255, 0, 100)))
                    if self.attack_timer <= 0:
                        self.boss_state = "CHARGE"
                        self.has_hit_batto = False
                elif self.boss_state == "CHARGE":
                    self.x += math.cos(self.dash_dir) * 25
                    if ghost_list is not None:
                        ghost_list.append(Ghost(self.x, self.y, self.img, 150, (255, 100, 50, 100)))
                    if not getattr(self, 'has_hit_batto', False) and dist < 120:
                        hit_player(15, d_texts, px, py, stun_time=240)
                        self.has_hit_batto = True
                    if self.x <= 50 or self.x >= current_stage["width"] - 50:
                        self.charge_count += 1
                        for _ in range(15): explosions.append(
                            [self.x, self.y, random.uniform(-6, 6), random.uniform(-6, 6), 25])
                        if self.charge_count >= 2:
                            self.boss_state = "STUNNED"
                            self.x = current_stage["width"] // 2
                            self.y = ground_y - 200
                            self.v_y = 0
                            self.attack_timer = 300
                        else:
                            self.boss_state = "CHARGE_PREP"
                            self.attack_timer = 40
                elif self.boss_state == "STUNNED":
                    self.v_y += 0.8
                    self.y += self.v_y
                    if self.y >= ground_y:
                        self.y = ground_y
                        self.v_y = 0
                    self.attack_timer -= 1
                    if self.attack_timer % 10 == 0 and draw_surf:
                        pygame.draw.circle(draw_surf, (255, 255, 0), (int(self.x - cx), int(self.y - 80 - cy)), 15, 2)
                    if self.attack_timer <= 0:
                        self.boss_state = "IDLE"
                        self.attack_timer = 60

            elif self.etype == "brother":
                if self.hp <= 0:
                    if self.phase == 2:
                        self.boss_state = "DEFEATED"
                        self.hp = 1
                        game_state = "ENDING_CHOICE"
                        self.lasers.clear()
                    else:
                        self.hp = 0
                        self.state = "DYING"
                        self.timer = 60

                if self.phase == 1:
                    if self.hp <= 666 and self.boss_state != "DEFEATED":
                        self.phase = 2
                        self.boss_state = "BLUE_SHOCKWAVE"
                        self.timer = 60
                        self.hp = min(self.max_hp, self.hp + 300)
                        d_texts.append(DamageText(self.x, self.y - 80, "+300 HEAL", (0, 255, 0)))
                        self.lasers.clear()

                        hit_player(20, d_texts, px, py, stun_time=18)
                        push_dir = 1 if px > self.x else -1
                        p_x += push_dir * 400

                    elif self.boss_state == "IDLE":
                        self.boss_state = "HOVER"
                        self.attack_timer = 60
                        self.bullet_timer = 300

                    elif self.boss_state == "HOVER":
                        self.hover_angle += 0.05
                        target_y = ground_y - 250 + math.sin(self.hover_angle) * 20
                        self.y += (target_y - self.y) * 0.1
                        self.x += (px - self.x) * 0.03

                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            is_red = random.random() < 0.25
                            target_x = px + random.randint(-150, 150)
                            self.lasers.append({'x': target_x, 'warn': 60, 'timer': 30, 'is_red': is_red,
                                                'width': 30 if is_red else 20})
                            self.attack_timer = random.randint(40, 80)

                        self.bullet_timer -= 1
                        if self.bullet_timer <= 0:
                            if projs is not None:
                                for _ in range(4):
                                    tx = px + random.randint(-400, 400);
                                    ty = py + random.randint(-100, 100)
                                    spd = random.uniform(4, 8)
                                    projs.append(EnemyProjectile(self.x, self.y, tx, ty, speed=spd, dmg=20, stun=18,
                                                                 color=(200, 0, 255), radius=8))
                            self.bullet_timer = 300

                    elif self.boss_state == "STUNNED":
                        self.v_y += 0.8
                        self.y += self.v_y
                        if self.y >= ground_y: self.y = ground_y; self.v_y = 0
                        self.attack_timer -= 1
                        if self.attack_timer % 10 == 0 and draw_surf:
                            pygame.draw.circle(draw_surf, (255, 255, 0), (int(self.x - cx), int(self.y - 80 - cy)), 15,
                                               2)
                        if self.attack_timer <= 0:
                            self.boss_state = "HOVER"
                            self.attack_timer = 60
                            self.bullet_timer = 300
                            self.lasers.clear()

                elif self.phase == 2 and self.boss_state != "DEFEATED":
                    if self.boss_state == "BLUE_SHOCKWAVE":
                        self.timer -= 1
                        if self.timer <= 0:
                            self.boss_state = "IDLE"
                            self.attack_timer = 60

                    if getattr(self, 'aura_lifetime', 0) > 0:
                        self.aura_lifetime -= 1
                        self.aura_timer += 1
                        if self.aura_timer >= 180:
                            self.aura_timer = 0
                            hit_player(2, d_texts, px, py)

                    if self.boss_state == "IDLE":
                        self.x += (px - self.x) * 0.03
                        self.y += (ground_y - 200 - self.y) * 0.05

                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            choices = [1, 2, 5]
                            if dist < 200:
                                choices.append(3)
                            else:
                                choices.append(4)
                            pattern = random.choice(choices)

                            if pattern == 1:
                                self.boss_state = "P1_GRID_PREP"
                                self.attack_timer = 60
                                self.grid_target = (px, py)
                            elif pattern == 2:
                                self.aura_lifetime = 360
                                self.aura_timer = 0
                                self.boss_state = "IDLE"
                                self.attack_timer = 60
                            elif pattern == 3:
                                self.boss_state = "P3_MELEE_PREP"
                                self.attack_timer = 40
                            elif pattern == 4:
                                self.boss_state = "P4_LASER_PREP"
                                self.attack_timer = 180
                                self.prep_hp = self.hp
                            elif pattern == 5:
                                self.boss_state = "P5_BULLET_HELL"
                                self.attack_timer = 180

                    elif self.boss_state == "P1_GRID_PREP":
                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            self.boss_state = "P1_GRID_FIRE"
                            self.attack_timer = 15
                            gx, gy = self.grid_target
                            if abs(px - gx) < 120 and abs(py - gy) < 120:
                                hit_player(15, d_texts, px, py)
                                p_bind_timer = 60
                    elif self.boss_state == "P1_GRID_FIRE":
                        self.attack_timer -= 1
                        if self.attack_timer <= 0: self.boss_state = "IDLE"; self.attack_timer = 60

                    elif self.boss_state == "P3_MELEE_PREP":
                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            if dist < 180: hit_player(15, d_texts, px, py)
                            if projs is not None:
                                projs.append(
                                    EnemyProjectile(self.x, self.y, px, py, speed=15, dmg=15, color=(0, 200, 255),
                                                    radius=25, is_crescent=True))
                            self.boss_state = "IDLE";
                            self.attack_timer = 60

                    elif self.boss_state == "P4_LASER_PREP":
                        self.attack_timer -= 1
                        self.dash_dir = math.atan2(py - self.y, px - self.x)
                        if self.hp < self.prep_hp:
                            self.boss_state = "STUNNED"
                            self.attack_timer = 180
                            d_texts.append(DamageText(self.x, self.y - 80, "INTERRUPTED!", (0, 255, 255)))
                        elif self.attack_timer <= 0:
                            self.boss_state = "P4_LASER_FIRE"
                            self.attack_timer = 20
                    elif self.boss_state == "P4_LASER_FIRE":
                        self.attack_timer -= 1
                        if self.attack_timer == 10:
                            p_ang = math.atan2(py - self.y, px - self.x)
                            if abs((p_ang - self.dash_dir + math.pi) % (2 * math.pi) - math.pi) < 0.2:
                                hit_player(40, d_texts, px, py, stun_time=18)
                        if self.attack_timer <= 0:
                            self.boss_state = "IDLE";
                            self.attack_timer = 60

                    elif self.boss_state == "P5_BULLET_HELL":
                        self.attack_timer -= 1
                        if self.attack_timer % 20 == 0 and projs is not None:
                            for i in range(5):
                                ang = (i * math.pi * 2 / 5) + (self.attack_timer * 0.1)
                                tx = self.x + math.cos(ang) * 100;
                                ty = self.y + math.sin(ang) * 100
                                projs.append(
                                    EnemyProjectile(self.x, self.y, tx, ty, speed=5, dmg=7, color=(0, 255, 255),
                                                    radius=8))
                        if self.attack_timer <= 0:
                            self.boss_state = "IDLE";
                            self.attack_timer = 60

                    elif self.boss_state == "STUNNED":
                        self.v_y += 0.8;
                        self.y += self.v_y
                        if self.y >= ground_y:
                            self.y = ground_y
                            self.v_y = 0
                        self.attack_timer -= 1
                        if self.attack_timer <= 0:
                            self.boss_state = "IDLE";
                            self.attack_timer = 60

                for l in getattr(self, 'lasers', []):
                    if l['warn'] > 0:
                        l['warn'] -= 1
                    else:
                        l['timer'] -= 1
                        if not l.get('is_red', False) and l['timer'] > 0:
                            if abs(px - l['x']) < l['width'] / 2 + 10 and p_stun_timer <= 0:
                                hit_player(10, d_texts, px, py, stun_time=18)
                                l['timer'] = 0
                self.lasers = [l for l in getattr(self, 'lasers', []) if l['timer'] > 0]

            if (self.etype != "komainu" or self.boss_state not in ["JUMP", "SKY_JUMP", "FALLING", "STUNNED"]) and \
                    (self.etype != "brother" or self.boss_state not in ["HOVER", "BLUE_SHOCKWAVE", "IDLE",
                                                                        "P1_GRID_PREP", "P1_GRID_FIRE", "P3_MELEE_PREP",
                                                                        "P4_LASER_PREP", "P4_LASER_FIRE",
                                                                        "P5_BULLET_HELL", "P2_AWAKEN", "DEFEATED"]):
                if self.etype != "turret":
                    self.v_y += 0.5
                    self.y += self.v_y
                    if self.y >= ground_y:
                        self.y = ground_y
                        self.v_y = 0
                        self.is_airborne = False

            self.rect.center = (int(self.x), int(self.y))
            if self.burn_timer > 0:
                self.burn_timer -= 1
                if self.burn_timer % 30 == 0:
                    self.hp -= 2
                    d_texts.append(DamageText(self.rect.centerx + random.randint(-15, 15), self.rect.top - 10, "2"))

            if self.hp <= 0 and self.boss_state != "DEFEATED":
                if self.etype == "true_boss":
                    self.boss_state = "DEFEATED"
                    self.hp = 0
                    global hidden_end_timer
                    game_state = "HIDDEN_ENDING"
                    hidden_end_timer = 0
                elif self.etype == "brother" and self.phase == 2:
                    self.boss_state = "DEFEATED"
                    self.hp = 1
                    game_state = "ENDING_CHOICE"
                elif self.etype != "brother":
                    self.hp, self.state, self.timer, self.death_type = 0, "DYING", 60, "NORMAL"

    def draw(self, screen, cx, cy):
        screen_x, screen_y = self.rect.x - cx, self.rect.y - cy

        if getattr(self, 'has_shield', False) and self.state == "ALIVE":
            pts = []
            for i in range(-5, 6):
                a = self.shield_ang + (i * 0.15)
                pts.append((self.x - cx + math.cos(a) * self.shield_dist, self.y - cy + math.sin(a) * self.shield_dist))
            if pts:
                pygame.draw.lines(alpha_surf, (0, 200, 255, 200), False, pts, 8)
                pygame.draw.lines(alpha_surf, (255, 255, 255, 255), False, pts, 3)

        if self.state == "DYING":
            if getattr(self, 'death_type', 'NORMAL') == "THREAD":
                ratio = self.timer / 60.0
                w, h = self.img.get_size()
                scaled_w, scaled_h = max(1, int(w * ratio)), max(1, int(h * ratio))
                scaled_img = pygame.transform.smoothscale(self.img, (scaled_w, scaled_h))
                scaled_img.set_alpha(int(255 * ratio))
                overlay = pygame.Surface((scaled_w, scaled_h)).convert_alpha()
                overlay.fill((255, 0, 0, int(150 * (1 - ratio))))
                scaled_img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                new_rect = scaled_img.get_rect(center=(int(self.x) - cx, int(self.y) - cy))
                screen.blit(scaled_img, new_rect)
            else:
                draw_img = self.img.copy()
                draw_img.set_alpha(max(0, int(255 * (self.timer / 60))))
                overlay = pygame.Surface(draw_img.get_size()).convert_alpha()
                overlay.fill((255, 0, 0, 180))
                draw_img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(draw_img, (screen_x, screen_y))

        elif self.state != "DEAD":
            if self.etype == "turret":
                pygame.draw.rect(screen, (50, 50, 60), (screen_x - 15, screen_y - 15, 30, 30))
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 10)
                pygame.draw.line(screen, (255, 0, 0, 100), (screen_x, screen_y), (p_x - cx, p_y - cy), 1)
            elif not (self.etype == "komainu" and self.boss_state in ["SKY_JUMP", "FALLING"] and self.y < -100):
                screen.blit(self.img, (screen_x, screen_y))

            if self.state == "ALIVE":
                if self.etype == "true_boss":
                    if self.boss_state == "GREATSWORD_PREP":
                        ang = getattr(self, 'dash_dir', 0)
                        bw, dash_len = 80, 800
                        p1x = self.x - cx + math.cos(ang + math.pi / 2) * bw / 2
                        p1y = self.y - cy + math.sin(ang + math.pi / 2) * bw / 2
                        p2x = self.x - cx + math.cos(ang - math.pi / 2) * bw / 2
                        p2y = self.y - cy + math.sin(ang - math.pi / 2) * bw / 2
                        p3x, p3y = p2x + math.cos(ang) * dash_len, p2y + math.sin(ang) * dash_len
                        p4x, p4y = p1x + math.cos(ang) * dash_len, p1y + math.sin(ang) * dash_len
                        color = (139, 0, 0, 100)
                        pygame.draw.polygon(alpha_surf, color, [(p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y)])

                elif self.etype == "boss":
                    if self.boss_state == "PARRY":
                        glow_rect = self.rect.copy()
                        glow_rect.inflate_ip(20, 20)
                        pygame.draw.ellipse(screen, (255, 255, 100), glow_rect.move(-cx, -cy), 3)
                    elif self.boss_state == "BATTO" and self.attack_timer > 0:
                        ang = getattr(self, 'dash_dir', 0)
                        bw, dash_len = 60, 600
                        p1x = self.x - cx + math.cos(ang + math.pi / 2) * bw / 2
                        p1y = self.y - cy + math.sin(ang + math.pi / 2) * bw / 2
                        p2x = self.x - cx + math.cos(ang - math.pi / 2) * bw / 2
                        p2y = self.y - cy + math.sin(ang - math.pi / 2) * bw / 2
                        p3x, p3y = p2x + math.cos(ang) * dash_len, p2y + math.sin(ang) * dash_len
                        p4x, p4y = p1x + math.cos(ang) * dash_len, p1y + math.sin(ang) * dash_len
                        alpha_val = 100 if self.attack_timer <= 15 else int(60 + 40 * math.sin(self.attack_timer * 0.5))
                        color = (255, 0, 0, alpha_val) if self.attack_timer <= 15 else (255, 50, 50, alpha_val)
                        pygame.draw.polygon(alpha_surf, color, [(p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y)])
                        pygame.draw.circle(screen, (255, 50, 50), (int(self.x - cx), int(self.y - cy)), 40, 2)

                elif self.etype == "brother":
                    if self.phase in [1, 2] and self.boss_state != "DEFEATED":
                        if self.boss_state != "STUNNED":
                            pygame.draw.circle(screen, (0, 255, 255), (screen_x + 10, screen_y + 60),
                                               random.randint(5, 10))
                            pygame.draw.circle(screen, (0, 255, 255), (screen_x + 30, screen_y + 60),
                                               random.randint(5, 10))

                        gun_y = 100 + math.sin(pygame.time.get_ticks() * 0.005) * 10 - cy
                        pygame.draw.rect(screen, (200, 200, 200), (self.x - 150 - cx, gun_y, 10, 30))
                        pygame.draw.rect(screen, (100, 100, 100), (self.x - 150 - cx, gun_y + 20, 20, 10))
                        pygame.draw.rect(screen, (50, 50, 50), (self.x + 150 - cx, gun_y, 10, 30))
                        pygame.draw.rect(screen, (30, 30, 30), (self.x + 140 - cx, gun_y + 20, 20, 10))

                        if self.phase == 2:
                            pygame.draw.circle(screen, (0, 150, 255), (screen_x + 20, screen_y + 30),
                                               50 + random.randint(-5, 5), 2)

                    if self.phase == 1:
                        for l in getattr(self, 'lasers', []):
                            lx = int(l['x'] - cx)
                            lw = int(l['width'])
                            if l['warn'] > 0:
                                color = (255, 50, 50, 100) if l.get('is_red', False) else (50, 255, 255, 100)
                                pygame.draw.rect(alpha_surf, color, (lx - lw // 2, 0, lw, screen_height))
                            else:
                                color = (255, 0, 0) if l.get('is_red', False) else (0, 200, 255)
                                pulse = int(random.randint(int(lw * 0.6), lw))
                                pygame.draw.rect(screen, color, (lx - pulse // 2, 0, pulse, screen_height))
                                pygame.draw.rect(screen, (255, 255, 255), (lx - 2, 0, 4, screen_height))

                    elif self.phase == 2 and self.boss_state != "DEFEATED":
                        if self.boss_state == "BLUE_SHOCKWAVE":
                            radius = (60 - self.timer) * 25
                            pygame.draw.circle(screen, (0, 150, 255), (screen_x, screen_y), int(radius),
                                               max(1, 20 - int(radius / 40)))
                            pygame.draw.circle(screen, (0, 255, 255), (screen_x, screen_y), int(radius) + 20, 5)
                            for i in range(16):
                                angle = (i * math.pi / 8) + (self.timer * 0.05)
                                end_x = screen_x + math.cos(angle) * (radius * 1.2)
                                end_y = screen_y + math.sin(angle) * (radius * 1.2)
                                pygame.draw.line(screen, (0, 200, 255), (screen_x, screen_y), (end_x, end_y), 4)

                        elif self.boss_state in ["P1_GRID_PREP", "P1_GRID_FIRE"]:
                            gx, gy = self.grid_target
                            gx, gy = int(gx - cx), int(gy - cy)
                            alpha = 100 if self.boss_state == "P1_GRID_PREP" else 255
                            w = 2 if self.boss_state == "P1_GRID_PREP" else 8
                            color = (0, 200, 255, alpha)
                            for off in [-75, 0, 75]:
                                pygame.draw.line(alpha_surf, color, (gx - 150, gy + off), (gx + 150, gy + off), w)
                                pygame.draw.line(alpha_surf, color, (gx + off, gy - 150), (gx + off, gy + 150), w)

                        elif self.boss_state == "P3_MELEE_PREP":
                            pygame.draw.circle(screen, (0, 200, 255), (screen_x + 20, screen_y + 30), 180, 2)

                        elif self.boss_state in ["P4_LASER_PREP", "P4_LASER_FIRE"]:
                            ang = getattr(self, 'dash_dir', 0)
                            bw, 60, 2000
                            p1x = self.x - cx + math.cos(ang + math.pi / 2) * bw / 2
                            p1y = self.y - cy + math.sin(ang + math.pi / 2) * bw / 2
                            p2x = self.x - cx + math.cos(ang - math.pi / 2) * bw / 2
                            p2y = self.y - cy + math.sin(ang - math.pi / 2) * bw / 2
                            p3x, p3y = p2x + math.cos(ang) * dash_len, p2y + math.sin(ang) * dash_len
                            p4x, p4y = p1x + math.cos(ang) * dash_len, p1y + math.sin(ang) * dash_len
                            alpha_val = 100 if self.boss_state == "P4_LASER_PREP" else 255
                            pygame.draw.polygon(alpha_surf, (0, 150, 255, alpha_val),
                                                [(p1x, p1y), (p2x, p2y), (p3x, p3y), (p4x, p4y)])

                if not self.is_special and self.etype != "turret":
                    bw, bh = 70, 8;
                    bx, by = self.rect.centerx - bw // 2 - cx, self.rect.top - 20 - cy
                    pygame.draw.rect(screen, (30, 30, 30), (bx - 2, by - 2, bw + 4, bh + 4))
                    pygame.draw.rect(screen, (80, 0, 0), (bx, by, bw, bh))
                    pygame.draw.rect(screen, (255, 50, 50), (bx, by, int(bw * (max(0, self.hp) / self.max_hp)), bh))


# ==========================================
# 6. 전역 게임 상태 및 초기화
# ==========================================
p_lives = 3
game_state = "PLAYING"

v_y, grav = 0, 0.5
p_hp, p_max_hp = 100, 100
is_ground, cur_img = False, player_img_right
attack_mode = "RUSH"
amaterasu_unlocked = False
sys_msg_timer, sys_msg = 0, ""
dash_timer, dash_angle, dash_cooldown, infinite_dash_timer = 0, 0, 0, 0
slash_cooldown, execution_flash, akai = 0, 0, None
mask_active, mask_fill_progress = False, 0
combo_step, combo_timer, attack_lock, combo_cooldown, attack_interval = 0, 0, 0, 0, 0
akai_stack = 0
p_dodge_stacks = 0
p_dodge_cooldown = 0
p_stun_timer = 0
p_bind_timer = 0

bad_end_timer = 0
true_end_timer = 0
true_end_state = 0
escape_timer = 0
escape_state = 0
hidden_end_timer = 0
kill_end_timer = 0
kill_end_state = 0

kill_end_texts = [
    "형: '저승에서 만나자고 이 질긴 악연의 실을 끊어내지 못하고...'"
]

true_end_texts = [
    "형: '이 도시는 질긴 악연이 많지, 너와 나도 같을거고.'",
    "형: '부모를 죽인건 내가 아니다. 이 회사는 그 양반의 돈으로 만들어졌어.'"
]

escape_texts = [
    "의식이 흐려진다...",
    "압도적인 힘의 격차. 이길 수 없다...",
    "(챙!!!)",
    "푸른 안광이 흑막의 대검을 튕겨냈다.",
    "형: '일어나라, 멍청한 놈! 놈은 지금의 네가 상대할 수 없다!'",
    "형이 터뜨린 섬광탄이 시야를 가린다.",
    "형에게 이끌려, 우리는 깊은 어둠 속으로 도망쳤다.",
    "--- TO BE CONTINUED ---"
]

run_intro(screen)
run_title_screen(screen)
load_stage(current_stage_id)

clock = pygame.time.Clock()
running = True

# ==========================================
# 7. 메인 게임 루프
# ==========================================
while running:
    clock.tick(60)
    old_p_y = p_y

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

        if game_state == "PLAYING" and p_stun_timer <= 0:
            if event.type == pygame.KEYDOWN:
                if is_typing:
                    if event.key == pygame.K_ESCAPE:
                        is_typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_password = input_password[:-1]
                    elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if active_terminal == "cheat":
                            if input_password == "1211":
                                sys_msg = "CHEAT ACTIVATED: 보스룸 워프"
                                sys_msg_timer = 120
                                amaterasu_unlocked = True
                                load_stage("final_boss")
                            else:
                                sys_msg = "ACCESS DENIED: 비밀번호 오류"
                                sys_msg_timer = 90
                        elif active_terminal == "puzzle":
                            if input_password == puzzle_password:
                                security_disabled = True
                                sys_msg = "ACCESS GRANTED: 보안 해제"
                                sys_msg_timer = 120
                            elif input_password == "0311":
                                snapshot_surf = screen.copy()
                                game_state = "TRUE_ENDING_WARNING"
                                true_end_timer = 0
                                is_typing = False
                                input_password = ""
                                p_hp = p_max_hp
                                amaterasu_unlocked = True
                            else:
                                sys_msg = "ACCESS DENIED: 비밀번호 오류"
                                sys_msg_timer = 90
                        if is_typing:
                            input_password = ""
                            is_typing = False
                    elif len(input_password) < 4:
                        if pygame.K_0 <= event.key <= pygame.K_9:
                            input_password += str(event.key - pygame.K_0)
                        elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                            input_password += str(event.key - pygame.K_KP0)
                    continue

                if event.key == pygame.K_SPACE and is_ground and p_bind_timer <= 0: v_y = -13; is_ground = False
                if event.key == pygame.K_q:
                    if amaterasu_unlocked:
                        attack_mode = "AMATERASU" if attack_mode == "RUSH" else "RUSH"
                        for _ in range(25): wire_spawn.append(WireSpawnParticle(p_x, p_y))
                    else:
                        sys_msg = "아직 자격이 없는듯 하다"
                        sys_msg_timer = 90
                if event.key == pygame.K_t: mask_active = not mask_active
                if event.key == pygame.K_y:
                    if p_dodge_cooldown <= 0:
                        p_dodge_stacks = 4
                        p_dodge_cooldown = 780
                        sys_msg = "회피 활성화! (4회)"
                        sys_msg_timer = 60

                if event.key == pygame.K_e and not is_typing:
                    temp_p_rect = cur_img.get_rect(center=(int(p_x), int(p_y)))
                    if current_stage_id == "company_hall" and terminal_rect and temp_p_rect.colliderect(
                            terminal_rect) and not security_disabled:
                        is_typing = True
                        input_password = ""
                        active_terminal = "puzzle"
                    elif current_stage_id == "alley" and cheat_terminal_rect and temp_p_rect.colliderect(
                            cheat_terminal_rect):
                        is_typing = True
                        input_password = ""
                        active_terminal = "cheat"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not is_typing:
                m_pos = (pygame.mouse.get_pos()[0] + cam_x, pygame.mouse.get_pos()[1] + cam_y)
                if attack_mode == "RUSH":
                    if not akai:
                        akai = AkaiIto(p_x, p_y, m_pos[0], m_pos[1])
                    else:
                        akai = None
                else:
                    if dash_timer <= 0 and dash_cooldown <= 0 and p_bind_timer <= 0:
                        dash_timer, dash_angle = 7, math.atan2(m_pos[1] - p_y, m_pos[0] - p_x);
                        dash_cooldown = 60

        elif game_state == "ENDING_CHOICE":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cx, cy = screen_width // 2, screen_height // 2
                if pygame.Rect(cx - 200, cy, 150, 50).collidepoint(pygame.mouse.get_pos()):
                    game_state = "KILL_CUTSCENE"
                    kill_end_timer = 0
                    kill_end_state = 0
                elif pygame.Rect(cx + 50, cy, 150, 50).collidepoint(pygame.mouse.get_pos()):
                    snapshot_surf = screen.copy()
                    game_state = "TRUE_ENDING_INTRO"
                    true_end_timer = 0
                    true_end_state = 0

    m_pos_screen = pygame.mouse.get_pos()
    m_click = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()
    m_pos = (m_pos_screen[0] + cam_x, m_pos_screen[1] + cam_y)

    # ==============================
    # 게임 상태별 업데이트 로직
    # ==============================
    if game_state == "PLAYING":
        if p_hp <= 0:
            if current_stage_id == "hidden_abyss":
                game_state = "ESCAPE_CUTSCENE"
                escape_timer = 0
                escape_state = 0
                continue
            else:
                p_lives -= 1
                if p_lives > 0:
                    p_hp = p_max_hp
                    p_x = 100
                    p_y = current_stage["ground_y"]
                    p_stun_timer = 0
                    p_bind_timer = 0
                    load_stage(current_stage_id)
                    sys_msg = f"사망했습니다. (남은 목숨: {p_lives})"
                    sys_msg_timer = 120
                    continue
                else:
                    p_hp = 0

        if p_lives <= 0:
            screen.fill((20, 0, 0))
            go_surf = title_font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(go_surf, (screen_width // 2 - go_surf.get_width() // 2, screen_height // 2 - 100))
            restart_surf = intro_font.render("Press 'R' to Restart or 'ESC' to Quit", True, (255, 255, 255))
            screen.blit(restart_surf, (screen_width // 2 - restart_surf.get_width() // 2, screen_height // 2 + 50))

            if keys[pygame.K_r]:
                p_lives = 3
                p_hp = p_max_hp
                amaterasu_unlocked = False
                current_stage_id = "alley"
                load_stage(current_stage_id)
                game_state = "PLAYING"
            pygame.display.flip()
            continue

        alpha_surf.fill((0, 0, 0, 0))

        if current_stage_id == "turret_room" and turret_timer > 0:
            turret_timer -= 1
            if turret_timer == 0:
                turrets_alive = any(d for d in dummies if d.etype == "turret" and d.state == "ALIVE")
                if turrets_alive:
                    sys_msg = "제한시간 초과! 경비 병력 배치!"
                    sys_msg_timer = 120
                    for _ in range(5):
                        dummies.append(DummyBot(p_x + random.choice([-300, -200, 200, 300]), ground_y, is_special=False,
                                                etype="shield_guard"))

        if p_stun_timer > 0: p_stun_timer -= 1
        if p_bind_timer > 0: p_bind_timer -= 1
        if dash_cooldown > 0: dash_cooldown -= 1
        if slash_cooldown > 0: slash_cooldown -= 1
        if combo_cooldown > 0: combo_cooldown -= 1
        if attack_lock > 0: attack_lock -= 1
        if attack_interval > 0: attack_interval -= 1
        if combo_timer > 0:
            combo_timer -= 1
            if combo_timer == 0: combo_step = 0
        if infinite_dash_timer > 0: infinite_dash_timer -= 1; dash_cooldown = 0
        if p_dodge_cooldown > 0: p_dodge_cooldown -= 1

        if mask_active:
            mask_fill_progress = min(100, mask_fill_progress + 4)
        else:
            mask_fill_progress = max(0, mask_fill_progress - 6)

        if p_stun_timer <= 0 and not is_typing:
            if attack_mode == "AMATERASU":
                if infinite_dash_timer > 0:
                    if random.random() < 0.25: steam.append(SteamParticle(p_x, p_y, (139, 0, 0)))
                elif dash_cooldown > 0 and random.random() < 0.1:
                    steam.append(SteamParticle(p_x, p_y, (100, 100, 100)))
                elif dash_cooldown == 0 and random.random() < 0.05:
                    steam.append(SteamParticle(p_x, p_y, (255, 255, 255)))

            if m_click[0]:
                if attack_mode == "RUSH":
                    if attack_lock == 0 and combo_cooldown == 0 and attack_interval == 0:
                        combo_step += 1
                        if combo_step > 3: combo_step = 1

                        combo_timer, attack_lock, attack_interval = 40, 15, 10
                        if combo_step == 3: combo_cooldown, combo_timer = 60, 0

                        facing_dir = -1 if cur_img == player_img_left else 1
                        eff = ComboEffect(combo_step, (p_x, p_y), m_pos, facing_dir);
                        combo_effects.append(eff)

                        for ep in enemy_projectiles:
                            if not getattr(ep, 'is_reflected', False) and math.hypot(ep.x - p_x, ep.y - p_y) < 180:
                                ang_to_ep = math.atan2(ep.y - p_y, ep.x - p_x)
                                ang_diff = (ang_to_ep - eff.angle + math.pi) % (2 * math.pi) - math.pi
                                if abs(ang_diff) < 1.0:
                                    if getattr(ep, 'parryable', False):
                                        ep.is_reflected = True
                                        ep.color = (255, 255, 255)
                                        ep.speed = 25
                                        d_texts.append(DamageText(ep.x, ep.y, "REFLECT!", (255, 255, 0)))
                                        for _ in range(10): sparkles.append(AmaterasuSparkle(ep.x, ep.y))
                                    else:
                                        ep.active = False
                                        d_texts.append(DamageText(ep.x, ep.y, "BLOCK!", (200, 200, 200)))
                                        for _ in range(5): sparkles.append(AmaterasuWhiteCoreParticle(ep.x, ep.y, True))

                        for d in dummies:
                            if d.state == "ALIVE" and d.etype == "brother":
                                if getattr(d, 'phase', 1) == 1:
                                    for l in list(d.lasers):
                                        if l.get('is_red', False):
                                            if abs(l['x'] - p_x) < 500:
                                                d.hp -= 50;
                                                d_texts.append(
                                                    DamageText(d.rect.centerx, d.rect.top - 30, "PARRY COUNTER!",
                                                               (255, 255, 0)))
                                                d.lasers.clear();
                                                d.boss_state = "STUNNED";
                                                d.attack_timer = 240;
                                                d.v_y = 0
                                elif getattr(d, 'phase', 1) == 2 and d.boss_state == "P4_LASER_PREP":
                                    d.hp -= 50;
                                    d_texts.append(
                                        DamageText(d.rect.centerx, d.rect.top - 30, "PARRY COUNTER!", (255, 255, 0)))
                                    d.boss_state = "STUNNED";
                                    d.attack_timer = 180;
                                    d.v_y = 0

                        for d in dummies:
                            if d.state != "ALIVE": continue
                            hit = False
                            dist, ang_to_d = math.hypot(d.x - p_x, d.y - p_y), math.atan2(d.y - p_y, d.x - p_x)
                            if combo_step == 1:
                                ang_diff = (ang_to_d - eff.angle + math.pi) % (2 * math.pi) - math.pi
                                if dist < 150 and abs(ang_diff) < 1.0: hit = True
                            elif combo_step == 2:
                                if dist < 150: hit = True
                            elif combo_step == 3:
                                ang_diff = (ang_to_d - eff.angle + math.pi) % (2 * math.pi) - math.pi
                                if dist < 350 and abs(ang_diff) < 0.3: hit = True

                            if hit:
                                if getattr(d, 'has_shield', False):
                                    ang_to_hit = math.atan2(p_y - d.y, p_x - d.x)
                                    ang_diff = (ang_to_hit - d.shield_ang + math.pi) % (2 * math.pi) - math.pi
                                    if abs(ang_diff) < 0.8:
                                        hit = False
                                        d_texts.append(DamageText(d.x, d.y - 30, "BLOCKED", (0, 255, 255)))
                                        for _ in range(5): sparkles.append(
                                            AmaterasuWhiteCoreParticle(d.x + math.cos(d.shield_ang) * d.shield_dist,
                                                                       d.y + math.sin(d.shield_ang) * d.shield_dist,
                                                                       True))

                                if hit:
                                    if d.etype == "boss" and d.boss_state == "PARRY":
                                        p_stun_timer = 120
                                        d_texts.append(DamageText(p_x, p_y - 50, "PARRIED!", (255, 255, 0)))
                                    else:
                                        d.hp -= 10;
                                        d_texts.append(DamageText(d.rect.centerx, d.rect.top - 20, "10"))
                                        akai_stack = min(9, akai_stack + 1)
                                        if d.hp <= 0 and not (d.etype == "brother" and getattr(d, 'phase', 1) == 2):
                                            if d.etype == "true_boss":
                                                d.boss_state = "DEFEATED"
                                                d.hp = 0
                                            else:
                                                d.hp, d.state, d.timer, d.death_type = 0, "DYING", 60, "THREAD"

                elif attack_mode == "AMATERASU":
                    if slash_cooldown <= 0 and attack_lock <= 0:
                        p_size_h = player_img_right.get_height()
                        slashes.append(
                            CrescentSlash((p_x, p_y), m_pos, sparkles, black_flames, p_size_h, dummies, d_texts))
                        slash_cooldown, attack_lock = 180, 18

                        target_angle = math.atan2(m_pos[1] - p_y, m_pos[0] - p_x)

                        for ep in enemy_projectiles:
                            if not getattr(ep, 'is_reflected', False) and math.hypot(ep.x - p_x, ep.y - p_y) < 300:
                                ang_to_ep = math.atan2(ep.y - p_y, ep.x - p_x)
                                ang_diff = (ang_to_ep - target_angle + math.pi) % (2 * math.pi) - math.pi
                                if abs(ang_diff) < 0.8:
                                    if getattr(ep, 'parryable', False):
                                        ep.is_reflected = True
                                        ep.color = (255, 255, 255)
                                        ep.speed = 25
                                        d_texts.append(DamageText(ep.x, ep.y, "REFLECT!", (255, 255, 0)))
                                        for _ in range(10): sparkles.append(AmaterasuSparkle(ep.x, ep.y))
                                    else:
                                        ep.active = False
                                        d_texts.append(DamageText(ep.x, ep.y, "BLOCK!", (200, 200, 200)))
                                        for _ in range(5): sparkles.append(AmaterasuWhiteCoreParticle(ep.x, ep.y, True))

                        for d in dummies:
                            if d.state == "ALIVE" and d.etype == "brother":
                                if getattr(d, 'phase', 1) == 1:
                                    for l in list(d.lasers):
                                        if l.get('is_red', False):
                                            if abs(l['x'] - p_x) < 500:
                                                d.hp -= 50;
                                                d_texts.append(
                                                    DamageText(d.rect.centerx, d.rect.top - 30, "PARRY COUNTER!",
                                                               (255, 255, 0)))
                                                d.lasers.clear();
                                                d.boss_state = "STUNNED";
                                                d.attack_timer = 240;
                                                d.v_y = 0
                                elif getattr(d, 'phase', 1) == 2 and d.boss_state == "P4_LASER_PREP":
                                    d.hp -= 50;
                                    d_texts.append(
                                        DamageText(d.rect.centerx, d.rect.top - 30, "PARRY COUNTER!", (255, 255, 0)))
                                    d.boss_state = "STUNNED";
                                    d.attack_timer = 180;
                                    d.v_y = 0

        if akai:
            akai.update(platforms)
            if getattr(akai, 'is_dead', False):
                akai = None
            else:
                if not akai.pulling:
                    if current_stage_id == "company_hall" and not security_disabled and hidden_button_rect:
                        if hidden_button_rect.collidepoint(akai.curr_x, akai.curr_y):
                            security_disabled = True
                            sys_msg = "보안 시스템 무력화 완료"
                            sys_msg_timer = 120
                            akai.pulling = True
                            for _ in range(20): sparkles.append(AmaterasuSparkle(akai.curr_x, akai.curr_y, False))

                    if not akai.pulling and akai_stack == 9:
                        for d in dummies:
                            if d.state == "ALIVE" and math.hypot(d.x - akai.curr_x, d.y - akai.curr_y) < 40:
                                akai.pulling, damage = True, 20
                                if getattr(d, 'has_shield', False):
                                    ang_to_hit = math.atan2(p_y - d.y, p_x - d.x)
                                    ang_diff = (ang_to_hit - d.shield_ang + math.pi) % (2 * math.pi) - math.pi
                                    if abs(ang_diff) < 0.8:
                                        d_texts.append(DamageText(d.x, d.y - 30, "BLOCKED", (0, 255, 255)))
                                        akai.pulling = False
                                        akai = None
                                        break

                                if d.etype == "boss" and d.boss_state == "PARRY":
                                    p_stun_timer = 120
                                    d_texts.append(DamageText(p_x, p_y - 50, "PARRIED!", (255, 255, 0)))
                                else:
                                    d.hp -= damage;
                                    d_texts.append(DamageText(d.rect.centerx, d.rect.top - 30, str(damage)))
                                    akai_stack = 0
                                    if d.hp <= 0 and not (d.etype == "brother" and getattr(d, 'phase', 1) == 2):
                                        if d.etype == "true_boss":
                                            d.boss_state = "DEFEATED"
                                            d.hp = 0
                                        else:
                                            d.hp, d.state, d.timer, d.death_type = 0, "DYING", 60, "NORMAL"
                                break

            if akai and akai.pulling:
                ang = math.atan2(akai.curr_y - p_y, akai.curr_x - p_x)
                p_x += math.cos(ang) * 25;
                p_y += math.sin(ang) * 25
                v_y = 0;
                is_ground = False
                if math.hypot(akai.curr_y - p_y, akai.curr_x - p_x) < 30: akai = None
            elif akai and p_stun_timer <= 0 and p_bind_timer <= 0 and not is_typing:
                if keys[pygame.K_a]: p_x -= 5; cur_img = player_img_left
                if keys[pygame.K_d]: p_x += 5; cur_img = player_img_right
                v_y += grav;
                p_y += v_y

        elif dash_timer > 0:
            p_x += math.cos(dash_angle) * 28;
            p_y += math.sin(dash_angle) * 28
            ghosts.append(Ghost(p_x, p_y, cur_img, 180, tint=(150, 0, 0, 100) if infinite_dash_timer > 0 else None))
            if attack_mode == "AMATERASU": dash_effects.append(DashThrustEffect(p_x, p_y, dash_angle))
            for d in dummies:
                if d.state == "ALIVE" and cur_img.get_rect(center=(int(p_x), int(p_y))).colliderect(d.rect):
                    if d.etype == "true_boss":
                        continue
                    elif d.etype == "boss" and d.boss_state == "PARRY":
                        p_stun_timer = 120
                        dash_timer = 0
                        d_texts.append(DamageText(p_x, p_y - 50, "PARRIED!", (255, 255, 0)))
                    else:
                        d.hp -= 2.0
                        if d.hp <= 0 and not (d.etype == "brother" and getattr(d, 'phase', 1) == 2):
                            if d.etype == "true_boss":
                                d.boss_state = "DEFEATED"
                                d.hp = 0
                            else:
                                d.hp, d.state, d.timer, d.split_timer, d.death_type = 0, "DYING", 60, 1, "NORMAL"
                                if d.is_special: execution_flash, infinite_dash_timer = 12, 180
            dash_timer -= 1
        else:
            if p_stun_timer <= 0 and p_bind_timer <= 0 and not is_typing:
                if keys[pygame.K_a]: p_x -= 6; cur_img = player_img_left
                if keys[pygame.K_d]: p_x += 6; cur_img = player_img_right
            v_y += grav;
            p_y += v_y
            if v_y > 25: v_y = 25

        is_ground = False
        if p_y >= ground_y: p_y, v_y, is_ground = ground_y, 0, True
        if p_x < 40:
            p_x = 40
        elif p_x > current_stage["width"] - 40:
            p_x = current_stage["width"] - 40

        p_rect = cur_img.get_rect(center=(int(p_x), int(p_y)))

        for plat in platforms:
            if p_rect.colliderect(plat) and v_y > 0 and old_p_y + 32 <= plat.top:
                if not keys[pygame.K_s] and p_stun_timer <= 0:
                    p_y, v_y, is_ground = plat.top - 32, 0, True
                    p_rect.centery = int(p_y)

        if current_stage_id == "company_hall" and not security_disabled and p_stun_timer <= 0:
            laser_zone = pygame.Rect(1200, 0, 400, ground_y)
            if p_rect.colliderect(laser_zone):
                hit_player(10, d_texts, p_x, p_y, stun_time=30)
                p_x -= 100
                v_y = -5
                dash_timer = 0
                for _ in range(15): sparkles.append(AmaterasuSparkle(p_x, p_y, is_static=False))

        # 🔥 적이 한 마리라도 살아있으면 다음 맵으로 못 넘어감 (잔몹 강제 전투)
        locking_enemies = [d for d in dummies if d.state in ["ALIVE", "DYING"]]
        barrier_x = current_stage["width"] - 120

        if locking_enemies:
            if p_x > barrier_x:
                p_x = barrier_x
                sys_msg = "아직 적이 남아있다!"
                sys_msg_timer = 60
                dash_timer = 0

        if current_stage["next"]:
            if p_x >= current_stage["width"] - 60:
                load_stage(current_stage["next"])
            elif not locking_enemies and any(d.is_special and d.state == "DEAD" for d in dummies):
                load_stage(current_stage["next"])

        if current_stage_id == "early_boss":
            for d in dummies:
                if d.is_special and d.state != "ALIVE": amaterasu_unlocked = True

        bx_val, by_val = p_x, p_y
        for d in dummies:
            if d.etype in ["brother", "true_boss"]: bx_val, by_val = d.x, d.y; break

        for ep in enemy_projectiles:
            ep.update(px=p_x, py=p_y, bx=bx_val, by=by_val)

            ep_rect = pygame.Rect(ep.x - ep.radius, ep.y - ep.radius, ep.radius * 2, ep.radius * 2)
            if any(p.colliderect(ep_rect) for p in platforms) and not getattr(ep, 'is_reflected', False):
                ep.active = False
                for _ in range(5): sparkles.append(AmaterasuSparkle(ep.x, ep.y, True))
                continue

            if not getattr(ep, 'is_reflected', False):
                if math.hypot(ep.x - p_x, ep.y - p_y) < (ep.radius + 15):
                    ep.active = False
                    if getattr(ep, 'is_thrust', False):
                        dmg = max(1, p_hp // 2)
                        hit_player(dmg, d_texts, p_x, p_y, stun_time=60)
                        for _ in range(15): explosions.append(
                            [p_x, p_y, random.uniform(-5, 5), random.uniform(-5, 5), 40])
                    else:
                        hit_player(ep.dmg, d_texts, p_x, p_y, stun_time=ep.stun)
                elif ep.x < 0 or ep.x > current_stage["width"] or (
                        ep.y > current_stage["ground_y"] and current_stage["ground_y"] < 90000):
                    ep.active = False
            else:
                for d in dummies:
                    if d.state == "ALIVE" and d.etype == "brother":
                        if math.hypot(ep.x - d.x, ep.y - d.y) < 120:
                            ep.active = False
                            d.hp -= 50
                            if getattr(d, 'phase', 1) == 2:
                                d.parry_count += 1
                            else:
                                d.boss_state = "STUNNED"
                                d.attack_timer = 180
                            d_texts.append(DamageText(d.rect.centerx, d.rect.top - 30, "PARRY HIT!", (255, 255, 0)))
                            for _ in range(20): explosions.append(
                                [d.x, d.y, random.uniform(-10, 10), random.uniform(-10, 10), 30])
                    elif d.state == "ALIVE" and d.etype == "true_boss":
                        if math.hypot(ep.x - d.x, ep.y - d.y) < 120:
                            ep.active = False
                            if getattr(ep, 'is_thrust', False):
                                d.hp -= 150
                                d_texts.append(
                                    DamageText(d.rect.centerx, d.rect.top - 30, "PARRY COUNTER!", (255, 255, 0)))
                                for _ in range(20): explosions.append(
                                    [d.x, d.y, random.uniform(-10, 10), random.uniform(-10, 10), 30])
                            else:
                                d.hp -= 50
                                d_texts.append(DamageText(d.rect.centerx, d.rect.top - 30, "50", (255, 255, 255)))
            if ep.x < 0 or ep.x > current_stage["width"] or ep.y < -1000 or ep.y > 200000:
                ep.active = False

        enemy_projectiles = [ep for ep in enemy_projectiles if ep.active]

        ghosts = [g for g in ghosts if not g.is_vanished()];
        [g.update() for g in ghosts]
        combo_effects = [e for e in combo_effects if e.lifetime > 0];
        [e.update() for e in combo_effects]
        slashes = [s for s in slashes if s.lifetime > 0];
        [s.update() for s in slashes]
        wire_spawn = [w for w in wire_spawn if not w.is_vanished()];
        [w.update() for w in wire_spawn]
        steam = [s for s in steam if not s.is_vanished()];
        [s.update() for s in steam]
        black_flames = [f for f in black_flames if f.alpha > 0];
        [f.update() for f in black_flames]
        d_texts = [t for t in d_texts if t.life > 0];
        [t.update() for t in d_texts]
        dash_effects = [d for d in dash_effects if d.lifetime > 0];
        [d.update() for d in dash_effects]
        boss_effects = [b for b in boss_effects if b.life > 0];
        [b.update() for b in boss_effects]

        if mask_active and dummies and dummies[0].state == "ALIVE": black_flames.append(
            BlackFlameParticle(dummies[0].x, dummies[0].y))
        sparkles = [s for s in sparkles if not s.is_vanished()];
        [s.update() for s in sparkles]

        explosions = [e for e in explosions if e[4] > 0]
        for e in explosions: e[0] += e[2]; e[1] += e[3]; e[4] -= 1

        bg_with_telegraph = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        for d in dummies:
            d.update(explosions, d_texts, p_x, p_y, enemy_projectiles, boss_effects, ghosts, bg_with_telegraph, cam_x,
                     cam_y)
            if d.etype == "brother" and d.state == "ALIVE" and getattr(d, 'phase',
                                                                       1) == 2 and d.boss_state != "DEFEATED":
                if getattr(d, 'aura_lifetime', 0) > 0:
                    rad = 60 + math.sin(pygame.time.get_ticks() * 0.01) * 10
                    pygame.draw.circle(bg_with_telegraph, (0, 150, 255, 100), (int(p_x - cam_x), int(p_y - cam_y)),
                                       int(rad), 4)
                    pygame.draw.circle(bg_with_telegraph, (0, 255, 255, 50), (int(p_x - cam_x), int(p_y - cam_y)),
                                       int(rad + 10), 2)

            # 🔥 진 최종보스 격파 트리거 확인 (전역 변수 처리)
            if getattr(d, 'boss_state', None) == "DEFEATED" and getattr(d, 'hp', 1) == 0 and d.etype == "true_boss":
                game_state = "HIDDEN_ENDING"
                hidden_end_timer = 0
                d.state = "DEAD"  # 중복 실행 방지

        update_camera()
        c_x, c_y = int(cam_x), int(cam_y)

        if execution_flash > 0:
            screen.fill((0, 0, 0)); execution_flash -= 1
        else:
            screen.blit(bg_surf, (-c_x, -c_y))
            for plat in platforms: pygame.draw.rect(screen, (40, 40, 50),
                                                    (plat.x - c_x, plat.y - c_y, plat.width, plat.height))
            shade = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA);
            shade.fill(current_stage["lighting"]);
            screen.blit(shade, (0, 0))
            screen.blit(bg_with_telegraph, (0, 0))

            if current_stage_id == "alley" and cheat_terminal_rect:
                t_screen_r = cheat_terminal_rect.move(-c_x, -c_y)
                pygame.draw.rect(screen, (40, 40, 50), t_screen_r)
                pygame.draw.rect(screen, (255, 150, 0), t_screen_r.inflate(-20, -40))
                if p_rect.colliderect(cheat_terminal_rect):
                    prompt = small_font.render("[E] Fast Travel", True, (255, 255, 255))
                    screen.blit(prompt, (t_screen_r.centerx - prompt.get_width() // 2, t_screen_r.top - 20))

            if current_stage_id == "company_hall" and terminal_rect:
                t_screen_r = terminal_rect.move(-c_x, -c_y)
                pygame.draw.rect(screen, (40, 40, 50), t_screen_r)
                pygame.draw.rect(screen, (0, 255, 0) if security_disabled else (255, 0, 0),
                                 t_screen_r.inflate(-20, -40))
                if not security_disabled and p_rect.colliderect(terminal_rect):
                    prompt = small_font.render("[E] Access Terminal", True, (255, 255, 255))
                    screen.blit(prompt, (t_screen_r.centerx - prompt.get_width() // 2, t_screen_r.top - 20))

            if current_stage_id == "company_hall" and not security_disabled:
                laser_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                pulse = int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.01))
                for line in laser_lines:
                    px1, py1 = line[0][0] - c_x, line[0][1] - c_y
                    px2, py2 = line[1][0] - c_x, line[1][1] - c_y
                    pygame.draw.line(screen, (255, 0, 0, pulse), (px1, py1), (px2, py2), 3)
                    pygame.draw.line(screen, (255, 100, 100), (px1, py1), (px2, py2), 1)
                screen.blit(laser_surf, (0, 0))

            for g in ghosts: g.draw(screen, c_x, c_y)
            if akai and not getattr(akai, 'is_dead', False):
                pygame.draw.line(screen, (255, 0, 0), (int(p_x) - c_x, int(p_y) - c_y),
                                 (int(akai.curr_x) - c_x, int(akai.curr_y) - c_y), 2)

            if locking_enemies:
                bx_screen = barrier_x - c_x
                if -50 <= bx_screen <= screen_width + 50:
                    laser_surf = pygame.Surface((30, screen_height), pygame.SRCALPHA)
                    laser_alpha = int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.01))
                    pygame.draw.line(laser_surf, (255, 0, 0, laser_alpha), (15, 0), (15, screen_height), 20)
                    pygame.draw.line(laser_surf, (255, 100, 100, laser_alpha), (15, 0), (15, screen_height), 8)
                    pygame.draw.line(laser_surf, (255, 255, 255, laser_alpha), (15, 0), (15, screen_height), 3)
                    screen.blit(laser_surf, (bx_screen - 15, 0))

            for d in dummies: d.draw(screen, cx=c_x, cy=c_y)

            for sm in (wire_spawn + steam + black_flames + sparkles): sm.draw(alpha_surf, c_x, c_y)
            for be in boss_effects: be.draw(alpha_surf, c_x, c_y)
            for e in combo_effects: e.draw(alpha_surf, c_x, c_y)
            for s in slashes: s.draw(alpha_surf, c_x, c_y)
            for de in dash_effects: de.draw(alpha_surf, c_x, c_y)

            screen.blit(alpha_surf, (0, 0))

            for ep in enemy_projectiles: ep.draw(screen, c_x, c_y)

            for e in explosions:
                pygame.draw.circle(screen, (220, 20, 30), (int(e[0]) - c_x, int(e[1]) - c_y), e[4] // 3)
                pygame.draw.circle(screen, (255, 100, 100), (int(e[0]) - c_x, int(e[1]) - c_y), max(1, e[4] // 6))

            for t in d_texts: t.draw(screen, c_x, c_y)
            screen.blit(cur_img, (p_rect.x - c_x, p_rect.y - c_y))

            if current_stage_id == "company_hall" and hidden_button_rect and not security_disabled:
                if mask_active:
                    btn_screen_r = hidden_button_rect.move(-c_x, -c_y)
                    alpha_val = int((mask_fill_progress / 100) * 255)
                    pygame.draw.rect(screen, (0, 200, 255, alpha_val), btn_screen_r, 4)
                    pygame.draw.line(screen, (0, 255, 255, alpha_val), (btn_screen_r.centerx, btn_screen_r.top - 10),
                                     (btn_screen_r.centerx, btn_screen_r.bottom + 10), 2)
                    pygame.draw.line(screen, (0, 255, 255, alpha_val), (btn_screen_r.left - 10, btn_screen_r.centery),
                                     (btn_screen_r.right + 10, btn_screen_r.centery), 2)
                    target_text = small_font.render("TARGET", True, (0, 255, 255))
                    target_text.set_alpha(alpha_val)
                    screen.blit(target_text, (btn_screen_r.x, btn_screen_r.y - 20))

            if current_stage_id == "turret_room" and turret_timer >= 0:
                m = int(turret_timer // 3600)
                s = int((turret_timer % 3600) // 60)
                timer_str = f"{m:02d}:{s:02d}"
                t_color = (255, 50, 50) if turret_timer <= 600 else (255, 255, 255)
                timer_surf = title_font.render(timer_str, True, t_color)
                screen.blit(timer_surf, (screen_width // 2 - timer_surf.get_width() // 2, 20))

            if p_stun_timer > 0:
                if p_stun_timer % 10 == 0: sparkles.append(AmaterasuSparkle(p_x, p_y - 40, True))
                stun_text = small_font.render("STUNNED!", True, (255, 255, 0))
                screen.blit(stun_text, (int(p_x) - c_x - 30, int(p_y) - c_y - 60))

            if p_bind_timer > 0:
                bind_text = small_font.render("BOUND!", True, (0, 255, 255))
                screen.blit(bind_text, (int(p_x) - c_x - 20, int(p_y) - c_y - 80))

            if p_dodge_stacks > 0:
                pygame.draw.circle(screen, (0, 255, 255), (int(p_x) - c_x, int(p_y) - c_y), 45, 1)
                for i in range(p_dodge_stacks):
                    ang = pygame.time.get_ticks() * 0.005 + (i * (math.pi * 2 / p_dodge_stacks))
                    ox = int(p_x) - c_x + math.cos(ang) * 45
                    oy = int(p_y) - c_y + math.sin(ang) * 45
                    pygame.draw.circle(screen, (0, 255, 255), (int(ox), int(oy)), 6)

            if mask_fill_progress > 0:
                h = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA);
                h.fill((0, 191, 255, int((mask_fill_progress / 100) * 60)));
                screen.blit(h, (0, 0))

            if is_typing:
                overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))
                box_w, box_h = 400, 200
                bx, by = screen_width // 2 - box_w // 2, screen_height // 2 - box_h // 2
                pygame.draw.rect(screen, (20, 20, 30), (bx, by, box_w, box_h))
                pygame.draw.rect(screen, (0, 255, 255), (bx, by, box_w, box_h), 4)
                title = intro_font.render("ENTER PASSWORD", True, (255, 255, 255))
                screen.blit(title, (bx + box_w // 2 - title.get_width() // 2, by + 30))
                pw_display = input_password + "_" if pygame.time.get_ticks() % 1000 < 500 else input_password
                pw_surf = title_font.render(pw_display, True, (0, 255, 255))
                screen.blit(pw_surf, (bx + box_w // 2 - pw_surf.get_width() // 2, by + 80))
                esc_hint = small_font.render("Press ESC to cancel", True, (150, 150, 150))
                screen.blit(esc_hint, (bx + box_w // 2 - esc_hint.get_width() // 2, by + 160))

            b_alive_list = [d for d in dummies if d.is_special and d.state in ["ALIVE", "DYING"]]
            if b_alive_list:
                main_boss = b_alive_list[0]

                if main_boss.etype == "true_boss":
                    b_max = main_boss.max_hp
                    b_hp = max(0, main_boss.hp)
                    bar_w = 800;
                    bar_h = 30
                    bbx = screen_width // 2 - bar_w // 2;
                    bby = 30
                    pygame.draw.rect(screen, (150, 120, 0), (bbx - 4, bby - 4, bar_w + 8, bar_h + 8))
                    pygame.draw.rect(screen, (30, 0, 0), (bbx, bby, bar_w, bar_h))
                    pygame.draw.rect(screen, (150, 0, 0), (bbx, bby, int(bar_w * (b_hp / b_max)), bar_h))
                    name_surf = title_font.render("[ 진정한 흑막 : THE DON ]", True, (255, 200, 50))
                    screen.blit(name_surf, (bbx + bar_w // 2 - name_surf.get_width() // 2, bby + 40))
                    hp_text = title_font.render(f"{int(b_hp)} / {b_max}", True, (255, 255, 255))
                    screen.blit(hp_text, (bbx + bar_w - hp_text.get_width() - 10, bby - 5))
                else:
                    b_max = main_boss.max_hp
                    b_hp = max(0, main_boss.hp)
                    bar_w = 600;
                    bar_h = 24
                    bbx = screen_width // 2 - bar_w // 2;
                    bby = 40
                    pygame.draw.rect(screen, (30, 30, 30), (bbx - 2, bby - 2, bar_w + 4, bar_h + 4))
                    pygame.draw.rect(screen, (150, 0, 150), (bbx, bby, int(bar_w * (b_hp / b_max)), bar_h))
                    pygame.draw.rect(screen, (200, 200, 200), (bbx - 2, bby - 2, bar_w + 4, bar_h + 4), 3)
                    name_map = {"boss": "[검은 개 간부 요시토미]", "komainu": "[mk.4 {코마이누}]", "brother": "[히카리의 수장 츠쿠]"}
                    name_str = name_map.get(main_boss.etype, "BOSS")
                    name_surf = boss_font.render(name_str, True, (255, 255, 255))
                    screen.blit(name_surf, (bbx + bar_w // 2 - name_surf.get_width() // 2, bby - 30))
                    hp_text = small_font.render(f"{int(b_hp)} / {b_max}", True, (255, 255, 255))
                    screen.blit(hp_text, (bbx + bar_w - hp_text.get_width() - 5, bby + 4))

            ui_x, ui_y = 30, 30;
            p_size = 70
            p_pts = [(ui_x, ui_y + p_size // 2), (ui_x + 15, ui_y), (ui_x + p_size - 15, ui_y),
                     (ui_x + p_size, ui_y + p_size // 2), (ui_x + p_size - 15, ui_y + p_size),
                     (ui_x + 15, ui_y + p_size)]
            pygame.draw.polygon(screen, (20, 10, 30), p_pts);
            pygame.draw.lines(screen, (255, 0, 255), True, p_pts, 3)
            screen.blit(yomi_face_img, (ui_x + 10, ui_y + 10))
            bar_x, bar_y, bar_w, bar_h = ui_x + p_size + 10, ui_y + 20, 250, 24
            pygame.draw.rect(screen, (0, 255, 255), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 2)
            pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 30, 100), (bar_x, bar_y, int(bar_w * (max(0, p_hp) / p_max_hp)), bar_h))
            screen.blit(small_font.render("HP", True, (255, 255, 255)), (bar_x + 5, bar_y + 2))
            lives_text = small_font.render(f"LIVES: {p_lives}/3", True, (255, 150, 150))
            screen.blit(lives_text, (bar_x + bar_w + 15, bar_y + 2))

            stack_y = bar_y + bar_h + 12
            for i in range(9):
                icx, icy = bar_x + i * 22 + 10, stack_y
                pygame.draw.circle(screen, (50, 10, 10), (icx, icy), 8)
                if i < akai_stack:
                    pygame.draw.circle(screen, (255, 30, 50), (icx, icy), 8)
                    for _ in range(4):
                        tx1, ty1 = icx + random.randint(-5, 5), icy + random.randint(-5, 5)
                        tx2, ty2 = icx + random.randint(-5, 5), icy + random.randint(-5, 5)
                        pygame.draw.line(screen, (255, 150, 150), (tx1, ty1), (tx2, ty2), 1)
            screen.blit(small_font.render(f"STACK: {akai_stack}/9", True, (255, 100, 100)),
                        (bar_x + 9 * 22 + 5, stack_y - 8))

            mode_y = stack_y + 15
            screen.blit(font.render(f"MODE: {attack_mode}", True, (255, 255, 255)), (bar_x, mode_y))

            if p_dodge_cooldown > 0:
                pygame.draw.rect(screen, (0, 255, 255), (bar_x, mode_y + 25, int(bar_w * (p_dodge_cooldown / 780)), 4))
                screen.blit(small_font.render("DODGE COOLDOWN", True, (0, 255, 255)), (bar_x, mode_y + 30))

            if attack_mode == "RUSH" and combo_cooldown > 0:
                pygame.draw.rect(screen, (255, 100, 100),
                                 (p_rect.x - c_x - 10, p_rect.y - c_y - 30, int(60 * (combo_cooldown / 60)), 4))
            elif attack_mode == "AMATERASU" and slash_cooldown > 0:
                pygame.draw.rect(screen, (255, 255, 255),
                                 (p_rect.x - c_x - 10, p_rect.y - c_y - 30, int(60 * (slash_cooldown / 180)), 4))

            if sys_msg_timer > 0:
                sys_msg_timer -= 1
                if "보안" in sys_msg or "ACCESS" in sys_msg or "CHEAT" in sys_msg:
                    msg_color = (100, 200, 255)
                elif "회피" in sys_msg or "사망" in sys_msg:
                    msg_color = (0, 255, 255)
                else:
                    msg_color = (255, 50, 50)
                msg_surf = intro_font.render(sys_msg, True, msg_color)
                msg_surf.set_alpha(min(255, sys_msg_timer * 5))
                screen.blit(msg_surf, (screen_width // 2 - msg_surf.get_width() // 2, 100))

    # ==============================
    # 엔딩 분기 연출 및 컷씬
    # ==============================
    elif game_state == "ENDING_CHOICE":
        screen.fill((0, 0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        c_text = title_font.render("형의 숨통을 끊겠습니까?", True, (255, 255, 255))
        screen.blit(c_text, (screen_width // 2 - c_text.get_width() // 2, screen_height // 2 - 150))

        cx, cy = screen_width // 2, screen_height // 2
        left_btn = pygame.Rect(cx - 200, cy, 150, 50)
        right_btn = pygame.Rect(cx + 50, cy, 150, 50)

        l_color = (255, 50, 50) if left_btn.collidepoint(pygame.mouse.get_pos()) else (150, 30, 30)
        r_color = (0, 255, 255) if right_btn.collidepoint(pygame.mouse.get_pos()) else (0, 150, 150)

        pygame.draw.rect(screen, l_color, left_btn, border_radius=5)
        pygame.draw.rect(screen, r_color, right_btn, border_radius=5)

        l_txt = intro_font.render("[ 죽인다 ]", True, (255, 255, 255))
        r_txt = intro_font.render("[ 살려둔다 ]", True, (255, 255, 255))
        screen.blit(l_txt, (left_btn.centerx - l_txt.get_width() // 2, left_btn.centery - l_txt.get_height() // 2))
        screen.blit(r_txt, (right_btn.centerx - r_txt.get_width() // 2, right_btn.centery - r_txt.get_height() // 2))

    elif game_state == "KILL_CUTSCENE":
        screen.fill((0, 0, 0))
        kill_end_timer += 1
        if kill_end_state < len(kill_end_texts):
            alpha = min(255, kill_end_timer * 3) if kill_end_timer < 150 else max(0, 255 - (kill_end_timer - 150) * 5)
            txt = intro_font.render(kill_end_texts[kill_end_state], True, (255, 100, 100))
            txt.set_alpha(alpha)
            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, screen_height // 2))
            if kill_end_timer > 200:
                kill_end_timer = 0
                kill_end_state += 1
        else:
            game_state = "BAD_ENDING"
            bad_end_timer = 0

    elif game_state == "BAD_ENDING":
        bad_end_timer += 1
        shake_x = random.randint(-15, 15) if bad_end_timer < 180 else 0
        shake_y = random.randint(-15, 15) if bad_end_timer < 180 else 0

        screen.fill((20, 10, 10))
        if bad_end_timer < 180:
            for _ in range(5):
                tx = screen_width // 2 + random.randint(-40, 40) + shake_x
                ty = screen_height // 2 + random.randint(-50, 50) + shake_y
                pygame.draw.circle(screen, random.choice([(255, 50, 0), (0, 0, 0), (200, 0, 0)]), (tx, ty),
                                   random.randint(10, 30))
            w_txt = intro_font.render("회사가 붕괴합니다...", True, (255, 100, 100))
            screen.blit(w_txt,
                        (screen_width // 2 - w_txt.get_width() // 2 + shake_x, screen_height // 2 - 150 + shake_y))
        else:
            screen.fill((0, 0, 0))
            b_text = title_font.render("BAD ENDING", True, (255, 50, 50))
            sub_text = intro_font.render("복수는 이루어졌으나, 남은 것은 재뿐이었다.", True, (150, 150, 150))
            alpha = min(255, (bad_end_timer - 180) * 2)
            b_text.set_alpha(alpha);
            sub_text.set_alpha(alpha)
            screen.blit(b_text, (screen_width // 2 - b_text.get_width() // 2, screen_height // 2 - 50))
            screen.blit(sub_text, (screen_width // 2 - sub_text.get_width() // 2, screen_height // 2 + 50))

    elif game_state == "TRUE_ENDING_INTRO":
        if snapshot_surf: screen.blit(snapshot_surf, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        true_end_timer += 1
        if true_end_state < len(true_end_texts):
            alpha = min(255, true_end_timer * 3) if true_end_timer < 150 else max(0, 255 - (true_end_timer - 150) * 5)
            txt = intro_font.render(true_end_texts[true_end_state], True, (255, 255, 255))
            txt.set_alpha(alpha)
            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, screen_height // 2))
            if true_end_timer > 200:
                true_end_timer = 0
                true_end_state += 1
        else:
            game_state = "TRUE_ENDING_WARNING"
            true_end_timer = 0

    elif game_state == "TRUE_ENDING_WARNING":
        if snapshot_surf: screen.blit(snapshot_surf, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        true_end_timer += 1
        alpha = int(abs(math.sin(true_end_timer * 0.1)) * 255)

        alarm_txt = title_font.render("침입 경보", True, (255, 0, 0))
        alarm_txt.set_alpha(alpha)
        screen.blit(alarm_txt, (screen_width // 2 - alarm_txt.get_width() // 2, 150))

        warn_txt = title_font.render("강한 살기가 느껴진다...", True, (255, 50, 50))
        warn_txt.set_alpha(alpha)
        screen.blit(warn_txt, (screen_width // 2 - warn_txt.get_width() // 2, screen_height // 2))

        if true_end_timer > 180:
            game_state = "TRUE_ENDING_CLEAVE"
            true_end_timer = 0

    elif game_state == "TRUE_ENDING_CLEAVE":
        true_end_timer += 1
        screen.fill((0, 0, 0))
        offset = max(0, (true_end_timer - 30) * 8)

        if snapshot_surf:
            top_rect = pygame.Rect(0, 0, screen_width, screen_height // 2)
            bot_rect = pygame.Rect(0, screen_height // 2, screen_width, screen_height // 2)
            screen.blit(snapshot_surf.subsurface(top_rect), (0, -offset))
            screen.blit(snapshot_surf.subsurface(bot_rect), (0, screen_height // 2 + offset))

            if offset > 0:
                gap_rect = pygame.Rect(0, screen_height // 2 - offset, screen_width, offset * 2)
                pygame.draw.rect(screen, (40, 0, 0), gap_rect)
                pygame.draw.line(screen, (255, 50, 50), (0, screen_height // 2 - offset),
                                 (screen_width, screen_height // 2 - offset), 4)
                pygame.draw.line(screen, (255, 50, 50), (0, screen_height // 2 + offset),
                                 (screen_width, screen_height // 2 + offset), 4)

        if true_end_timer < 60:
            shake_x, shake_y = random.randint(-15, 15), random.randint(-15, 15)
            s_copy = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(s_copy, (shake_x, shake_y))
            pygame.draw.line(screen, (255, 0, 0), (0, screen_height // 2), (screen_width, screen_height // 2), 30)
            pygame.draw.line(screen, (255, 255, 255), (0, screen_height // 2), (screen_width, screen_height // 2), 10)

        if true_end_timer > 120:
            game_state = "PLAYING"
            load_stage("hidden_abyss")
            sys_msg = "압도적인 살기가 느껴진다..."
            sys_msg_timer = 180

    elif game_state == "ESCAPE_CUTSCENE":
        screen.fill((0, 0, 0))
        escape_timer += 1
        if escape_state < len(escape_texts):
            alpha = min(255, escape_timer * 3) if escape_timer < 150 else max(0, 255 - (escape_timer - 150) * 5)
            if escape_state == 5 and escape_timer < 20: screen.fill((255, 255, 255))
            txt = intro_font.render(escape_texts[escape_state], True,
                                    (255, 255, 255) if escape_state != 2 else (0, 255, 255))
            txt.set_alpha(alpha)
            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, screen_height // 2))
            if escape_timer > 200:
                escape_timer = 0
                escape_state += 1
        else:
            screen.fill((0, 0, 0))
            fin_txt = title_font.render("TO BE CONTINUED...", True, (255, 255, 255))
            screen.blit(fin_txt, (screen_width // 2 - fin_txt.get_width() // 2, screen_height // 2))

    elif game_state == "HIDDEN_ENDING":
        screen.fill((10, 0, 5))
        hidden_end_timer += 1

        if hidden_end_timer < 180:
            for _ in range(5):
                pygame.draw.polygon(screen, (200, 255, 255), [
                    (random.randint(0, screen_width), random.randint(0, screen_height)),
                    (random.randint(0, screen_width), random.randint(0, screen_height)),
                    (random.randint(0, screen_width), random.randint(0, screen_height))
                ], 1)

            txt = title_font.render("거울세계의 경계가 붕괴한다...", True, (255, 100, 100))
            alpha = min(255, hidden_end_timer * 2)
            txt.set_alpha(alpha)
            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, screen_height // 2))
        else:
            txt = title_font.render("히든 엔딩: [어떠한 거울세계]", True, (255, 50, 50))
            sub_txt = intro_font.render("진정한 흑막을 쓰러뜨리고 균형을 되찾았다.", True, (150, 150, 150))

            alpha = min(255, (hidden_end_timer - 180) * 2)
            txt.set_alpha(alpha)
            sub_txt.set_alpha(alpha)

            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, screen_height // 2 - 50))
            screen.blit(sub_txt, (screen_width // 2 - sub_txt.get_width() // 2, screen_height // 2 + 50))

    pygame.display.flip()
pygame.quit()
