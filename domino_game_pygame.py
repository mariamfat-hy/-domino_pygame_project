"""
Dominoes (Double-6) - Player vs Computer (Fixed GUI: Rotation and Scrolling + CLEAR SCORE DISPLAY)
Pygame GUI version
"""

import pygame, sys, random, os
from typing import List, Tuple, Optional

Tile = Tuple[int,int]

# --- Game logic (omitted for brevity, assume the previous logic is here) ---
# ... (DominoGame Class and core functions like pip_count, is_blocked_result, etc., remain unchanged) ...

def make_set(max_pip=6) -> List[Tile]:
    return [(i,j) for i in range(max_pip+1) for j in range(i, max_pip+1)]

def tile_sum(tile: Tile) -> int:
    return tile[0] + tile[1]

def can_place(tile: Tile, end_value: int) -> bool:
    a,b = tile
    return a == end_value or b == end_value

class DominoGame:
    def __init__(self):
        self.stock = make_set()
        random.shuffle(self.stock)
        self.human: List[Tile] = []
        self.computer: List[Tile] = []
        self.board: List[Tile] = []
        self.deal()

    def deal(self):
        for _ in range(7):
            self.human.append(self.stock.pop())
            self.computer.append(self.stock.pop())

    def find_start(self) -> str:
        all_tiles = [('human', t) for t in self.human] + [('computer', t) for t in self.computer]
        doubles = [(owner,t) for owner,t in all_tiles if t[0]==t[1]]
        if doubles:
            owner,tile = max(doubles, key=lambda ot: ot[1][0])
            self._remove_from_hand(owner, tile)
            oriented = tile if tile[0] <= tile[1] else (tile[1], tile[0])
            self.board.append(oriented)
            return owner
        owner,tile = max(all_tiles, key=lambda ot: tile_sum(ot[1]))
        self._remove_from_hand(owner, tile)
        a,b = tile
        oriented = (a,b) if a<=b else (b,a)
        self.board.append(oriented)
        return owner

    def _remove_from_hand(self, owner: str, tile: Tile):
        hand = self.human if owner=='human' else self.computer
        for i,t in enumerate(hand):
            if set(t)==set(tile):
                hand.pop(i)
                return

    def ends(self):
        if not self.board:
            return (-1,-1)
        left = self.board[0][0]
        right = self.board[-1][1]
        return left, right

    def legal_moves(self, hand: List[Tile]) -> List[Tuple[int,str]]:
        moves = []
        if not self.board:
            return [(i,'R') for i in range(len(hand))]
        left,right = self.ends()
        for i,t in enumerate(hand):
            if can_place(t, left):
                moves.append((i,'L'))
            if can_place(t, right):
                moves.append((i,'R'))
        return moves

    def play_from_hand(self, owner: str, idx: int, side: str) -> bool:
        hand = self.human if owner=='human' else self.computer
        if idx<0 or idx>=len(hand):
            return False
        tile = hand.pop(idx)
        if not self.board:
            a,b = tile
            oriented = (a,b) if a<=b else (b,a)
            self.board.append(oriented)
            return True
        left,right = self.ends()
        if side=='L':
            if not can_place(tile, left):
                hand.insert(idx, tile)
                return False
            a,b = tile
            oriented = (a,b) if b==left else (b,a) 
            self.board.insert(0, oriented)
            return True
        else: # side=='R'
            if not can_place(tile, right):
                hand.insert(idx, tile)
                return False
            a,b = tile
            oriented = (a,b) if a==right else (b,a)
            self.board.append(oriented)
            return True

    def draw_tile(self, owner: str) -> Optional[Tile]:
        if not self.stock:
            return None
        tile = self.stock.pop()
        if owner=='human':
            self.human.append(tile)
        else:
            self.computer.append(tile)
        return tile

def pip_count(hand: List[Tile]) -> int:
    return sum(a+b for a,b in hand)

def is_blocked_result(game: DominoGame) -> Optional[str]:
    h = pip_count(game.human)
    c = pip_count(game.computer)
    if h < c:
        return 'human'
    elif c < h:
        return 'computer'
    else:
        return 'draw'

def computer_best_move(game: DominoGame):
    moves = game.legal_moves(game.computer)
    if not moves:
        return None
    best = max(moves, key=lambda m: tile_sum(game.computer[m[0]]))
    return best

def computer_turn_auto(game: DominoGame):
    moves = game.legal_moves(game.computer)
    if moves:
        idx,side = computer_best_move(game)
        tile = game.computer[idx]
        game.play_from_hand('computer', idx, side)
        return 'played', f"Computer played {tile}"
    while game.stock:
        tile = game.draw_tile('computer')
        moves = game.legal_moves(game.computer)
        if moves:
            idx,side = computer_best_move(game)
            tile = game.computer[idx]
            game.play_from_hand('computer', idx, side)
            return 'played', f"Computer drew and played {tile}"
    return 'passed', "Computer passed"

def human_auto_draw_until_playable(game: DominoGame):
    while True:
        moves = game.legal_moves(game.human)
        if moves:
            return 'none', ''
        if game.stock:
            tile = game.draw_tile('human')
            drawn_idx = len(game.human)-1
            moves = game.legal_moves(game.human)
            for idx,side in moves:
                if idx==drawn_idx:
                    game.play_from_hand('human', idx, side)
                    return 'played', f"Auto-played drawn {tile}"
            continue
        else:
            return 'none', ''


# --- Pygame GUI (Adjusted) ---

ASSET_DIR = os.path.join(os.path.dirname(__file__), "images")

pygame.init()
FONT = pygame.font.SysFont("arial", 18)
BIG = pygame.font.SysFont("arial", 36, bold=True) # Increased font size
MEDIUM = pygame.font.SysFont("arial", 24) # New medium font for scores

W, H = 1200, 700 
SCREEN = pygame.display.set_mode((W,H))
pygame.display.set_caption("Dominoes - Player vs Computer (Fixed)")

# Tile display sizes
TILE_W, TILE_H = 100, 60 
BOARD_Y = H//2 - TILE_H//2
HAND_Y = H - TILE_H - 20

# load and preprocess images
TILE_IMAGES = {}
# (Image loading logic remains the same)
for a in range(7):
    for b in range(a,7):
        key = (a,b) 
        fname = f"tile_{a}_{b}.png"
        path = os.path.join(ASSET_DIR, fname)
        
        if not os.path.exists(path):
            base_img = pygame.Surface((TILE_W, TILE_H))
            base_img.fill((255, 255, 255))
            pygame.draw.circle(base_img, (0,0,0), (TILE_W//2, TILE_H//2), 10)
            
        else:
            img = pygame.image.load(path).convert_alpha()
            base_img = pygame.transform.smoothscale(img, (TILE_W, TILE_H))
            
        TILE_IMAGES[key] = base_img 

        flipped_img = pygame.transform.rotate(base_img, 180)
        TILE_IMAGES[(key, 'F')] = flipped_img 


def tile_key(tile: Tile):
    a,b = tile
    return (a,b) if a<=b else (b,a)

def draw_text(s, x, y, font, color=(0,0,0)): 
    SCREEN.blit(font.render(s, True, color), (x,y))

def center_text(s, y, font, color=(0,0,0)): 
    surf = font.render(s, True, color)
    SCREEN.blit(surf, (W//2 - surf.get_width()//2, y))

def draw_board(game: DominoGame, board_offset_x):
    total = len(game.board)
    spacing = TILE_W + 6
    total_board_width = total * spacing
    
    start_x = W // 2 - (total_board_width - spacing) // 2 + board_offset_x 
    
    x = start_x
    if total==0:
        draw_text("<empty board>", W//2-50, BOARD_Y, FONT, (255, 255, 255))
        return

    for i, t in enumerate(game.board):
        base_key = (min(t[0], t[1]), max(t[0], t[1]))
        
        if t[0] > t[1]:
             img_to_draw = TILE_IMAGES.get((base_key, 'F'), TILE_IMAGES[base_key]) 
        else:
             img_to_draw = TILE_IMAGES[base_key] 

        SCREEN.blit(img_to_draw, (x, BOARD_Y))
        x += spacing

def draw_hand(game: DominoGame, selected_idx: Optional[int]):
    # Draw human hand at bottom (Centered)
    x0 = W//2 - (len(game.human)*(TILE_W+8))//2
    spacing = TILE_W + 8
    
    for i,t in enumerate(game.human):
        base_key = tile_key(t)
        img = TILE_IMAGES[base_key]
        x = x0 + i*spacing
        y = HAND_Y
        rect = pygame.Rect(x,y,TILE_W,TILE_H)
        SCREEN.blit(img, (x,y))
        
        if i==selected_idx:
            pygame.draw.rect(SCREEN, (0,150,0), rect, 3)
        
        draw_text(str(i+1), x+TILE_W//2-6, y+TILE_H+2, FONT)
    
    # Draw computer tiles (top center)
    x0_comp = W//2 - (len(game.computer)*(TILE_W+8))//2
    comp_y = 70
    comp_back = pygame.Surface((TILE_W, TILE_H))
    comp_back.fill((100, 100, 100))
    for i in range(len(game.computer)):
        SCREEN.blit(comp_back, (x0_comp + i*spacing, comp_y))


def draw_status(game: DominoGame, msg: str, boneyard_count:int):
    pygame.draw.rect(SCREEN, (56, 118, 29), (0, 0, W, 120), 0) # Green Header

    draw_text(f"Computer tiles: {len(game.computer)}", 20, 20, FONT, (255, 255, 255))
    draw_text(f"Boneyard: {boneyard_count}", 20, 40, FONT, (255, 255, 255))
    if msg:
        center_text(msg, 50, FONT, (255,255,0)) 

def find_tile_at_pos(game: DominoGame, pos):
    x0 = W//2 - (len(game.human)*(TILE_W+8))//2
    spacing = TILE_W + 8
    x,y = pos
    for i,t in enumerate(game.human):
        tx = x0 + i*spacing
        ty = HAND_Y
        rect = pygame.Rect(tx,ty,TILE_W,TILE_H)
        if rect.collidepoint(pos):
            return i
    return None

def announce(game, result):
    human_pips = pip_count(game.human)
    computer_pips = pip_count(game.computer)
    
    if result == 'human':
        winner_msg = "YOU WIN!"
        score_msg = f"Computer's leftover pips: {computer_pips}"
    elif result == 'computer':
        winner_msg = "COMPUTER WINS!"
        score_msg = f"Your leftover pips: {human_pips}"
    else: # Draw or Blocked
        winner = is_blocked_result(game)
        if winner == 'human':
            winner_msg = "YOU WIN BY BLOCK!"
            score_msg = f"Scores: You {human_pips} vs Comp {computer_pips}"
        elif winner == 'computer':
            winner_msg = "COMPUTER WINS BY BLOCK!"
            score_msg = f"Scores: You {human_pips} vs Comp {computer_pips}"
        else:
            winner_msg = "DRAW!"
            score_msg = f"Scores: You {human_pips} vs Comp {computer_pips}"
            
    print(f"{winner_msg} ({score_msg})")
    return winner_msg, score_msg

def main():
    clock = pygame.time.Clock()
    game = DominoGame()
    starter = game.find_start()
    turn = 'computer' if starter == 'human' else 'human'
    selected = None
    msg = f"Starter: {starter} | Your turn: {turn}"
    consecutive_passes = 0
    running = True
    game_over = False
    
    # Store final result messages separately
    final_winner_msg = ""
    final_score_msg = ""
    
    board_offset_x = 0
    scroll_speed = 30 
    
    if turn=='human':
        st, m = human_auto_draw_until_playable(game)
        if st=='played':
            msg = m

    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            
            # Scrolling Control
            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    board_offset_x += scroll_speed
                if event.key == pygame.K_RIGHT:
                    board_offset_x -= scroll_speed
            
            if game_over:
                continue
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                mx,my = event.pos
                if turn=='human':
                    idx = find_tile_at_pos(game, (mx,my))
                    if idx is not None:
                        selected = idx
                        msg = f"Selected tile {game.human[selected]}"
                    else:
                        left_area = pygame.Rect(50, BOARD_Y, 80, TILE_H)
                        right_area = pygame.Rect(W-130, BOARD_Y, 80, TILE_H)
                        pass_area = pygame.Rect(W-130, 70, 80, 30) 
                        
                        if selected is not None:
                            moves = game.legal_moves(game.human)
                            is_playable_L = any(i==selected and side=='L' for i,side in moves)
                            is_playable_R = any(i==selected and side=='R' for i,side in moves)
                            
                            played = False
                            
                            # Try Left
                            if left_area.collidepoint((mx,my)):
                                if is_playable_L:
                                    ok = game.play_from_hand('human', selected, 'L')
                                    if ok:
                                        msg = f"Played {game.board[0]} on L"
                                        played = True
                                else:
                                    msg = "Illegal on L"
                            
                            # Try Right
                            elif right_area.collidepoint((mx,my)):
                                if is_playable_R:
                                    ok = game.play_from_hand('human', selected, 'R')
                                    if ok:
                                        msg = f"Played {game.board[-1]} on R"
                                        played = True
                                else:
                                    msg = "Illegal on R"

                            if played:
                                consecutive_passes = 0
                                selected = None
                                if not game.human:
                                    final_winner_msg, final_score_msg = announce(game, 'human')
                                    game_over = True
                                else:
                                    turn = 'computer'
                            
                        # Check Pass button
                        if pass_area.collidepoint((mx,my)):
                            moves = game.legal_moves(game.human)
                            if moves or game.stock:
                                msg = "Cannot pass yet. Draw or play a tile."
                            else:
                                msg = "You passed."
                                consecutive_passes += 1
                                selected = None
                                turn = 'computer'
                
        # Computer Turn
        if not game_over and turn=='computer':
            st, m = computer_turn_auto(game)
            msg = m
            if st=='played':
                consecutive_passes = 0
            else: 
                consecutive_passes += 1
            
            if not game.computer:
                final_winner_msg, final_score_msg = announce(game, 'computer')
                game_over = True
            else:
                turn = 'human'
                st2, m2 = human_auto_draw_until_playable(game)
                if st2=='played':
                    msg = m2
                    consecutive_passes = 0
                    if not game.human:
                        final_winner_msg, final_score_msg = announce(game, 'human')
                        game_over = True
                    else:
                        turn = 'computer' 

        # Blocked check
        if consecutive_passes >= 2 and not game_over:
            final_winner_msg, final_score_msg = announce(game, 'blocked')
            game_over = True

        # --- DRAWING ---
        SCREEN.fill((56, 118, 29)) 
        
        # 1. Status/Header
        draw_status(game, msg, len(game.stock))
        
        # 2. Board Area (Grey path)
        pygame.draw.rect(SCREEN, (50,50,50), (0, BOARD_Y-5, W, TILE_H+10), 0) 
        draw_board(game, board_offset_x)
        
        # 3. Play/Pass Buttons (Unchanged)
        L_can_play = selected is not None and any(i==selected and side=='L' for i,side in game.legal_moves(game.human))
        R_can_play = selected is not None and any(i==selected and side=='R' for i,side in game.legal_moves(game.human))
        
        L_color = (0, 150, 0) if L_can_play else (150, 0, 0)
        R_color = (0, 150, 0) if R_can_play else (150, 0, 0)
        
        pygame.draw.rect(SCREEN, L_color, (50, BOARD_Y, 80, TILE_H))
        pygame.draw.rect(SCREEN, R_color, (W-130, BOARD_Y, 80, TILE_H))
        draw_text("PLAY L", 60, BOARD_Y+TILE_H//2-8, FONT, (255,255,255))
        draw_text("PLAY R", W-120, BOARD_Y+TILE_H//2-8, FONT, (255,255,255))
        
        pass_enabled = (not game.legal_moves(game.human) and not game.stock)
        pass_col = (180,0,0) if pass_enabled else (150,150,150)
        pygame.draw.rect(SCREEN, pass_col, (W-130, 70, 80, 30))
        draw_text("PASS", W-110, 76, FONT, (255,255,255))
        
        # 4. Hands
        draw_hand(game, selected)
        
        # 5. Game Over Message (IMPROVED DISPLAY)
        if game_over:
            # Draw a translucent background rectangle for better contrast
            overlay = pygame.Surface((W, H))
            overlay.set_alpha(200) # Semi-transparent
            overlay.fill((50, 50, 50))
            SCREEN.blit(overlay, (0, 0))
            
            # Display Big Winner Message
            center_text(final_winner_msg, H//2 - 100, BIG, (255,255,0)) 
            
            # Display Detailed Score
            center_text(final_score_msg, H//2 - 40, MEDIUM, (255,255,255)) 
            
            # Exit instruction
            center_text("Close window to exit", H//2 + 20, FONT, (150,150,150))

        pygame.display.flip()
        clock.tick(30)

if __name__=='__main__':
    main()