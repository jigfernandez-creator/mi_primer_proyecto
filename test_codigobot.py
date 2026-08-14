import unittest
from unittest.mock import AsyncMock, patch
import json

# Importamos las funciones de tu bot
from botaver import (
    parse_board, 
    get_snake_length, 
    get_enemy_threats, 
    flood_fill, 
    bfs_to_food, 
    choose_direction,
    process_message,
    main_bot,
    juegos_en_vivo,
    obtener_datos_partidas
)

class TestSnakeBot(unittest.TestCase):

    def test_parse_board(self):
        tablero_txt = "| A |\n| * |"
        resultado_esperado = [['|', ' ', 'A', ' ', '|'], ['|', ' ', '*', ' ', '|']]
        self.assertEqual(parse_board(tablero_txt), resultado_esperado)

    def test_get_snake_length(self):
        tablero = [['|', 'A', 'a', '|'], ['|', ' ', 'a', '|']]
        self.assertEqual(get_snake_length(tablero, 'A'), 3)
        self.assertEqual(get_snake_length(tablero, 'B'), 0)

    def test_get_enemy_threats(self):
        tablero = [[' ', ' ', ' '], [' ', 'B', ' '], [' ', ' ', ' ']]
        amenazas = get_enemy_threats(tablero, 'A')
        for pos in [(0, 1), (2, 1), (1, 0), (1, 2)]:
            self.assertIn(pos, amenazas)

    def test_flood_fill_espacio_cerrado(self):
        tablero = [['|', '-', '|'], ['|', ' ', '|'], ['|', '-', '|']]
        self.assertEqual(flood_fill(tablero, 1, 1, set()), 1)

    def test_bfs_to_food_libre(self):
        tablero = [['A', ' ', '*']]
        self.assertEqual(bfs_to_food(tablero, 0, 0, set()), "right")

    def test_bfs_to_food_obstaculo(self):
        tablero = [['A', 'a', '*'], [' ', ' ', ' ']]
        self.assertEqual(bfs_to_food(tablero, 0, 0, set()), "down")

    def test_choose_direction_sin_cabeza(self):
        self.assertEqual(choose_direction(" | | \n | | ", 'A'), "up")

    def test_choose_direction_acorralado(self):
        tablero = " a \naAa\n a "
        self.assertEqual(choose_direction(tablero, 'A'), "up")

    def test_choose_direction_supervivencia(self):
        tablero = "|A*B|\n|   |"
        movimiento = choose_direction(tablero, 'A')
        self.assertEqual(movimiento, "down")

    def test_obtener_datos_partidas(self):
        """Cubre la función que conecta con la interfaz gráfica"""
        self.assertEqual(obtener_datos_partidas(), juegos_en_vivo)


class TestSnakeBotAsync(unittest.IsolatedAsyncioTestCase):

    async def test_process_message_challenge(self):
        ws_mock = AsyncMock()
        msg = json.dumps({"event": "challenge", "data": {"challenge_id": "123"}})
        await process_message(ws_mock, msg)
        ws_mock.send.assert_called_once()

    async def test_process_message_turn(self):
        ws_mock = AsyncMock()
        msg = json.dumps({
            "event": "your_turn", 
            "data": {"game_id": "1", "turn_token": "2", "board": "A *", "side": "A"}
        })
        await process_message(ws_mock, msg)
        ws_mock.send.assert_called_once()

    async def test_process_message_game_over(self):
        """Simula que la partida terminó para cubrir esas líneas"""
        ws_mock = AsyncMock()
        # Creamos una partida falsa en vivo
        juegos_en_vivo["juego_test"] = {"tablero": "", "side": "A", "marcador": "", "game_over": False}
        msg = json.dumps({"event": "game_over", "data": {"game_id": "juego_test", "winner": "BotdeJuano"}})
        await process_message(ws_mock, msg)
        # Verificamos que se actualizó el estado a True
        self.assertTrue(juegos_en_vivo["juego_test"]["game_over"])

    async def test_process_message_error(self):
        """Simula un error del servidor"""
        ws_mock = AsyncMock()
        msg = json.dumps({"event": "error", "data": "Se cayó todo"})
        await process_message(ws_mock, msg)

    @patch('botaver.websockets.connect', new_callable=AsyncMock)
    async def test_main_bot(self, mock_connect):
        """Simula la conexión principal para cubrir el try/except"""
        # Prueba 1: Conexión exitosa pero sin mensajes (simulamos que corta rápido)
        mock_ws = AsyncMock()
        mock_ws.__aiter__.return_value = [] 
        mock_connect.return_value.__aenter__.return_value = mock_ws
        await main_bot("token_falso")
        
        # Prueba 2: Simulamos que se cae internet
        mock_connect.side_effect = Exception("Sin internet")
        await main_bot("token_falso")

if __name__ == '__main__':
    unittest.main()