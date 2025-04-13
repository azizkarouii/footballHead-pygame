import pygame
import sys
import random
import math
import pygame_textinput  

pygame.init() 


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Football Pygame")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
GOAL_COLOR = (255, 215, 0)  

PLAYER_SIZE = 30
BALL_SIZE = 20
PLAYER_SPEED = 5
BALL_FRICTION = 0.98
GOAL_WIDTH = 25
GOAL_HEIGHT = 100

def load_image(name, size=None):
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except:
        return None

pitch_img = load_image("pitch.png", (WIDTH, HEIGHT))
player1_img = load_image("player1.png", (PLAYER_SIZE*2, PLAYER_SIZE*2))
player2_img = load_image("player2.png", (PLAYER_SIZE*2, PLAYER_SIZE*2))
ball_img = load_image("ball.png", (BALL_SIZE*2, BALL_SIZE*2))

# Joueur
class Player:
    def __init__(self, x, y, color, controls, image, name="Joueur"):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.score = 0
        self.image = image
        self.name = name
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE*2, PLAYER_SIZE*2)
        self.rect.center = (x, y)

    def move(self, keys):
        if keys[self.controls[0]] and self.y > PLAYER_SIZE:
            self.y -= PLAYER_SPEED
        if keys[self.controls[1]] and self.y < HEIGHT - PLAYER_SIZE:
            self.y += PLAYER_SPEED
        if keys[self.controls[2]] and self.x > PLAYER_SIZE:
            self.x -= PLAYER_SPEED
        if keys[self.controls[3]] and self.x < WIDTH - PLAYER_SIZE:
            self.x += PLAYER_SPEED
        self.rect.center = (self.x, self.y)

    def draw(self):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.circle(screen, self.color, (self.x, self.y), PLAYER_SIZE)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BALL_SIZE*2, BALL_SIZE*2)
        self.reset()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = random.choice([-3, 3])
        self.dy = random.choice([-3, 3])

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.dx *= BALL_FRICTION
        self.dy *= BALL_FRICTION

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1

        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self):
        if ball_img:
            screen.blit(ball_img, self.rect)
        else:
            pygame.draw.circle(screen, WHITE, self.rect.center, BALL_SIZE)

# Cage
class Goal:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.post_color = WHITE

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.post_color, pygame.Rect(self.rect.x, self.rect.y, 5, self.rect.height))
        pygame.draw.rect(screen, self.post_color, pygame.Rect(self.rect.right-5, self.rect.y, 5, self.rect.height))
        pygame.draw.rect(screen, self.post_color, pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 5))
        pygame.draw.rect(screen, self.post_color, pygame.Rect(self.rect.x, self.rect.bottom-5, self.rect.width, 5))

def draw_button(screen, rect, text, font, color, hover_color, text_color):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    button_color = hover_color if is_hovered else color
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)
    
    return is_hovered

def draw_input_box(screen, rect, text, font, active, label=""):
    color = BLUE if active else LIGHT_GRAY
    pygame.draw.rect(screen, WHITE, rect, border_radius=5)
    pygame.draw.rect(screen, color, rect, 2, border_radius=5)
    
    if label:
        label_surface = font.render(label, True, BLACK)
        screen.blit(label_surface, (rect.x, rect.y - 25))
    
    text_surface = font.render(text, True, BLACK)
    screen.blit(text_surface, (rect.x + 5, rect.y + 5))
    
    #curseur clignotant
    if active:
        cursor_blink = pygame.time.get_ticks() // 500 % 2 == 0  # Change toutes les 0.5s
        if cursor_blink:
            cursor_x = rect.x + 5 + text_surface.get_width()
            pygame.draw.line(screen, BLACK, (cursor_x, rect.y + 5), 
                            (cursor_x, rect.y + rect.height - 5), 2)
    
    return rect

def get_start_screen():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, 48)
    
    # champs de texte
    textinput_player1 = pygame_textinput.TextInputVisualizer(font_object=font)
    textinput_player2 = pygame_textinput.TextInputVisualizer(font_object=font)
    textinput_time = pygame_textinput.TextInputVisualizer(font_object=font)
    
    textinput_player1.value = "" # champ vide par defaut
    textinput_player2.value = ""
    textinput_time.value = ""  
    
    active_field = None
    fields = [
        {"rect": pygame.Rect(WIDTH//2 - 100, 150, 200, 40), "input": textinput_player1, "label": "Nom Joueur 1:"},
        {"rect": pygame.Rect(WIDTH//2 - 100, 250, 200, 40), "input": textinput_player2, "label": "Nom Joueur 2:"},
        {"rect": pygame.Rect(WIDTH//2 - 100, 350, 200, 40), "input": textinput_time, "label": "Durée (1-5 min):"}
    ]
    
    start_button = pygame.Rect(WIDTH//2 - 150, 450, 300, 50)
    
    while True:
        screen.fill(LIGHT_GRAY)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # verif clic  un champ de texte
                    for field in fields:
                        if field["rect"].collidepoint(event.pos):
                            active_field = field
                            break
                    else:
                        active_field = None
                    
                    # verif clic bouton Start
                    if start_button.collidepoint(event.pos):
                        try:
                            match_time = min(max(1, int(textinput_time.value)), 5) * 60 * 1000
                            return textinput_player1.value, textinput_player2.value, match_time
                        except ValueError:
                            pass
        
        # Gestion de la saisie pour le champ actif
        if active_field:
            active_field["input"].update(events)
        
        # Titre
        title = title_font.render("Football Match", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Champs de saisie
        for field in fields:
            is_active = (field == active_field)
            draw_input_box(screen, field["rect"], field["input"].value, font, is_active, field["label"])
        
        # Bouton Start
        if draw_button(screen, start_button, "Commencer le match", font, GREEN, (0, 200, 0), WHITE):
            pass
        
        pygame.display.flip()
        clock.tick(30)

def main_game(player1_name, player2_name, game_time):

    # Création des objets
    player1 = Player(150, HEIGHT//2, RED, [pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d], player1_img, player1_name)
    player2 = Player(WIDTH-150, HEIGHT//2, BLUE, [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT], player2_img, player2_name)
    ball = Ball()
    goal1 = Goal(0, HEIGHT//2 - GOAL_HEIGHT//2, GOAL_WIDTH, GOAL_HEIGHT, GRAY)
    goal2 = Goal(WIDTH - GOAL_WIDTH, HEIGHT//2 - GOAL_HEIGHT//2, GOAL_WIDTH, GOAL_HEIGHT, GRAY)

    font = pygame.font.Font(None, 36)
    start_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    running = True
    
    goal_animation_time = 0  
    goal_scorer = None       

    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        remaining_time = max(0, game_time - elapsed_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if remaining_time <= 0:
            screen.fill(BLACK)
            
            # gagnant
            if player1.score > player2.score:
                winner_text = font.render(f"{player1.name} gagne {player1.score}-{player2.score}!", True, RED)
            elif player2.score > player1.score:
                winner_text = font.render(f"{player2.name} gagne {player2.score}-{player1.score}!", True, BLUE)
            else:
                winner_text = font.render(f"Match nul! {player1.score}-{player2.score}", True, WHITE)
            
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
            continue

        keys = pygame.key.get_pressed()
        player1.move(keys)
        player2.move(keys)
        ball.move()

        if player1.rect.colliderect(ball.rect):
            angle = math.atan2(ball.rect.centery - player1.y, ball.rect.centerx - player1.x)
            force = 10
            ball.dx = math.cos(angle) * force
            ball.dy = math.sin(angle) * force

        if player2.rect.colliderect(ball.rect):
            angle = math.atan2(ball.rect.centery - player2.y, ball.rect.centerx - player2.x)
            force = 10
            ball.dx = math.cos(angle) * force
            ball.dy = math.sin(angle) * force

        # detection de but
        if ball.rect.colliderect(goal1.rect):
            player2.score += 1
            goal_scorer = player2
            goal_animation_time = current_time
            ball.reset()
        elif ball.rect.colliderect(goal2.rect):
            player1.score += 1
            goal_scorer = player1
            goal_animation_time = current_time
            ball.reset()

        # Collision entre joueurs
        if player1.rect.colliderect(player2.rect):
            dx = player1.x - player2.x
            dy = player1.y - player2.y
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1
            overlap = PLAYER_SIZE * 2 - distance
            dx /= distance
            dy /= distance
            move_x = dx * (overlap / 2)
            move_y = dy * (overlap / 2)

            def clamp(val, min_val, max_val):
                return max(min_val, min(max_val, val))

            player1.x = clamp(player1.x + move_x, PLAYER_SIZE, WIDTH - PLAYER_SIZE)
            player1.y = clamp(player1.y + move_y, PLAYER_SIZE, HEIGHT - PLAYER_SIZE)
            player2.x = clamp(player2.x - move_x, PLAYER_SIZE, WIDTH - PLAYER_SIZE)
            player2.y = clamp(player2.y - move_y, PLAYER_SIZE, HEIGHT - PLAYER_SIZE)

            player1.rect.center = (player1.x, player1.y)
            player2.rect.center = (player2.x, player2.y)

        # Affichage
        if pitch_img:
            screen.blit(pitch_img, (0, 0))
        else:
            screen.fill(GREEN)
            pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 70, 2)
            pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

        goal1.draw()
        goal2.draw()
        player1.draw()
        player2.draw()
        ball.draw()

        if goal_scorer and current_time - goal_animation_time < 2000:  # 2 secondes affich
            # Fond semi-transparent
            overlay = pygame.Surface((300, 100), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (WIDTH//2 - 150, HEIGHT//2 - 50))
            
            # affichage BUT
            font_large = pygame.font.Font(None, 72)
            goal_text = font_large.render("BUT !!", True, GOAL_COLOR)
            screen.blit(goal_text, (WIDTH//2 - goal_text.get_width()//2, HEIGHT//2 - 30))
            
            # Nom du buteur
            scorer_text = font.render(f"{goal_scorer.name} marque !", True, WHITE)
            screen.blit(scorer_text, (WIDTH//2 - scorer_text.get_width()//2, HEIGHT//2 + 20))
        else:
            goal_scorer = None  # re-init

        # Recangle score
        overlay = pygame.Surface((250, 90), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 128), (0, 0, 250, 90), border_radius=15)
        screen.blit(overlay, (WIDTH//2 - 125, 10))

        # Score + temps
        score_text = font.render(f"{player1.name}: {player1.score} - {player2.name}: {player2.score}", True, BLACK)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        minutes = remaining_time // 60000
        seconds = (remaining_time % 60000) // 1000
        time_text = font.render(f"Temps: {minutes:02}:{seconds:02}", True, BLACK)
        screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 60))

        pygame.display.flip()
        clock.tick(60)

# Écran de démarrage
player1_name, player2_name, match_time = get_start_screen()

main_game(player1_name, player2_name, match_time)

pygame.quit()
sys.exit()