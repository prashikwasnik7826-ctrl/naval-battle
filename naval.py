import pygame
import sys
import random
import math
import io
import wave
import struct

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Naval Battle")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


# Generate retro sound effects in memory (no external files needed)
def create_shoot_sound():
    sample_rate = 22050
    duration = 0.12
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            freq = 650 * math.exp(-t * 22)
            val = int(14000 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wf.writeframes(frames)
    buf.seek(0)
    return pygame.mixer.Sound(buf)


def create_explosion_sound():
    sample_rate = 22050
    duration = 0.30
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            noise = random.uniform(-1, 1)
            envelope = (1 - t / duration) ** 2
            val = int(18000 * noise * envelope)
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wf.writeframes(frames)
    buf.seek(0)
    return pygame.mixer.Sound(buf)


shoot_sound = create_shoot_sound()
explosion_sound = create_explosion_sound()

player_x = 340
player_speed = 6
score = 0

ships = [[800 + 250 * i, 120] for i in range(3)]
shots = []
explosions = []

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            shots.append([player_x + 60, 330])
            shoot_sound.play()

    # Move player left and right with arrow keys (or A/D)
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0:
        player_x -= player_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < 680:
        player_x += player_speed

    screen.fill((10, 40, 90))

    # Draw player ship
    pygame.draw.rect(screen, "gray", (player_x, 330, 120, 30))

    # Move shots upward and remove off-screen shots
    for s in shots[:]:
        s[1] -= 10
        if s[1] < 0:
            shots.remove(s)
        else:
            pygame.draw.circle(screen, "orange", (s[0], s[1]), 5)

    # Move ships, check for hits, and draw ships
    for ship in ships:
        ship[0] -= 2
        if ship[0] < -80:
            ship[0] = 850

        ship_rect = pygame.Rect(ship[0], ship[1], 80, 25)
        hit = False

        for s in shots[:]:
            shot_rect = pygame.Rect(s[0] - 5, s[1] - 5, 10, 10)
            if ship_rect.colliderect(shot_rect):
                shots.remove(s)
                hit = True
                score += 10
                explosion_sound.play()
                # Spawn 18 explosion particles at the ship's center
                for _ in range(18):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(1.5, 5.5)
                    explosions.append({
                        "x": ship[0] + 40,
                        "y": ship[1] + 12,
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed,
                        "life": random.randint(18, 30),
                        "color": random.choice(["yellow", "orange", "red", "white"])
                    })
                break

        if hit:
            ship[0] = 850
        else:
            pygame.draw.rect(screen, "red", ship_rect)

    # Update and draw explosion particles
    for p in explosions[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] <= 0:
            explosions.remove(p)
        else:
            radius = max(1, p["life"] // 5)
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), radius)

    # Draw score in the top-left corner
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (15, 15))

    pygame.display.flip()
    clock.tick(60)