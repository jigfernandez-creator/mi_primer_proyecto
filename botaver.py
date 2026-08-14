import asyncio
import json
import sys
import random
import websockets
import threading
from collections import deque

# --- CONEXIÓN CON EL VISUALIZADOR ---
from interfaz import iniciar_interfaz_multitab

juegos_en_vivo = {}

def obtener_datos_partidas():
    return juegos_en_vivo
# ------------------------------------

def parse_board(board_str):
    return [list(row) for row in board_str.strip().split('\n')]

def get_snake_length(board, side):
    head_char = side.upper()
    body_char = side.lower()
    return sum(1 for row in board for cell in row if cell in (head_char, body_char))

def get_enemy_threats(board, my_side):
    """Detecta las casillas que el enemigo puede pisar en el próximo turno."""
    enemy_head = 'B' if my_side == 'A' else 'A'
    threats = set()
    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r][c] == enemy_head:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                        threats.add((nr, nc))
    return threats

def flood_fill(board, start_r, start_c, threats=None):
    if threats is None:
        threats = set()
    if not (0 <= start_r < len(board) and 0 <= start_c < len(board[0])): return 0
    if board[start_r][start_c] not in (' ', '*'): return 0
    
    visited = set([(start_r, start_c)])
    queue = deque([(start_r, start_c)])
    count = 0
    
    while queue:
        r, c = queue.popleft()
        count += 1
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                if (nr, nc) not in visited and board[nr][nc] in (' ', '*'):
                    if (nr, nc) not in threats:  # Evita pisar la lava
                        visited.add((nr, nc))
                        queue.append((nr, nc))
    return count

def bfs_to_food(board, start_r, start_c, threats=None):
    if threats is None:
        threats = set()
    queue = deque([(start_r, start_c, [])])
    visited = set([(start_r, start_c)])
    
    while queue:
        r, c, path = queue.popleft()
        if board[r][c] == '*': return path[0] if path else None
        
        for move, (dr, dc) in [("up", (-1, 0)), ("down", (1, 0)), ("left", (0, -1)), ("right", (0, 1))]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                if (nr, nc) not in visited and board[nr][nc] in (' ', '*'):
                    if (nr, nc) not in threats:
                        visited.add((nr, nc))
                        queue.append((nr, nc, path + [move]))
    return None

def choose_direction(board_str, side):
    board = parse_board(board_str)
    my_head = side.upper()
    head_r, head_c = -1, -1
    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r][c] == my_head:
                head_r, head_c = r, c
                break
    if head_r == -1: return "up"
    
    my_length = get_snake_length(board, side)
    threats = get_enemy_threats(board, side) 
    
    directions = {"up": (head_r - 1, head_c), "down": (head_r + 1, head_c), "left": (head_r, head_c - 1), "right": (head_r, head_c + 1)}
    
    move_spaces = {}
    for move, (r, c) in directions.items():
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            if board[r][c] in (' ', '*'):
                if (r, c) in threats:
                    move_spaces[move] = 0 # Valor 0 si es lava enemiga
                else:
                    move_spaces[move] = flood_fill(board, r, c, threats)
                    
    # Si de verdad no hay ninguna jugada sin amenazas, chocamos irremediablemente
    if not move_spaces or max(move_spaces.values()) == 0: 
        return "up"
    
    max_space = max(move_spaces.values())
    food_move = bfs_to_food(board, head_r, head_c, threats)
    
    # Solo va por la comida si el movimiento inicial hacia ella NO es una amenaza (su espacio es > 0)
    if food_move and food_move in move_spaces and move_spaces[food_move] > 0:
        espacio_hacia_comida = move_spaces[food_move]
        if espacio_hacia_comida >= min(my_length, 8) or espacio_hacia_comida == max_space:
            return food_move
            
    best_survival_moves = [m for m, space in move_spaces.items() if space == max_space]
    return random.choice(best_survival_moves)

async def process_message(websocket, message):
    global juegos_en_vivo
    data = json.loads(message)
    event = data.get("event")
    event_data = data.get("data", {})

    if event == "challenge":
        challenge_id = event_data.get("challenge_id")
        response = {"action": "accept_challenge", "data": {"challenge_id": challenge_id}}
        await websocket.send(json.dumps(response))
        print(f"[*] Desafío aceptado: {challenge_id}")

    elif event == "your_turn":
        game_id = event_data.get("game_id")
        turn_token = event_data.get("turn_token")
        board = event_data.get("board")
        side = event_data.get("side")
        
        player_1 = event_data.get("player_1", "P1")
        player_2 = event_data.get("player_2", "P2")
        score_1 = event_data.get("score_1", 0)
        score_2 = event_data.get("score_2", 0)
        
        juegos_en_vivo[game_id] = {
            "tablero": board,
            "side": side,
            "marcador": f"{player_1} ({score_1}) vs {player_2} ({score_2})",
            "game_over": False
        }

        direction = choose_direction(board, side)
        response = {"action": "move", "data": {"game_id": game_id, "turn_token": turn_token, "direction": direction}}
        await websocket.send(json.dumps(response))
        print(f"[+] Turno enviado: {direction} | Juego: {game_id}")

    elif event == "game_over":
        game_id = event_data.get("game_id")
        winner = event_data.get("winner", "Empate/Ninguno")
        print(f"[!] Juego terminado. Ganador: {winner}")
        
        if game_id in juegos_en_vivo:
            juegos_en_vivo[game_id]["game_over"] = True
            juegos_en_vivo[game_id]["marcador"] += f"  -> GANÓ: {winner}"
        
    elif event == "error":
        print(f"[X] Error del servidor: {event_data}")

async def main_bot(token):
    uri = f"wss://codechallenge-server.up.railway.app:443/ws?token={token}"
    print(f"Conectando al servidor con token...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado exitosamente. Esperando eventos...")
            async for message in websocket:
                await process_message(websocket, message)
    except Exception as e:
        print(f"Se perdió la conexión o hubo un error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python codigobot.py <TU_BOT_TOKEN>")
        sys.exit(1)
        
    token = sys.argv[1]
    
    ui_thread = threading.Thread(target=iniciar_interfaz_multitab, args=(obtener_datos_partidas,), daemon=True)
    ui_thread.start()
    asyncio.run(main_bot(token))
