from game_brain.client import GameClient

client = GameClient()
client.new_game()

print(f"Начальная позиция: {client.get_fen()}")
print(f"Ход: {client.get_turn()}")
print(f"Легальные ходы: {client.get_legal_moves()[:5]}...")

# Тест хода
print(f"\nХод e2e4 валиден? {client.is_valid_move('e2e4')}")
client.make_move("e2e4")
print(f"После e2e4: {client.get_fen()}")

print(f"Ход e7e5 валиден? {client.is_valid_move('e7e5')}")
client.make_move("e7e5")
print(f"После e7e5: {client.get_fen()}")

# Нелегальный ход
print(f"\nХод e2e4 валиден? {client.is_valid_move('e2e4')} (должно быть False)")

print(f"\nИгра закончена? {client.is_game_over()}")
print(f"Результат: {client.get_result()}")
