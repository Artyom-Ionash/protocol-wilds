extends Node

# Сигналы используются в коде, предупреждения можно игнорировать
# или добавить комментарии чтобы убрать warnings

signal player_position_update(player_pos)
signal enemy_attack(enemy_damage) 
signal player_attack(player_damage)
signal day_time(state, day_count)
signal enemy_died(enemy_position)
