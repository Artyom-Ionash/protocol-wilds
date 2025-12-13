class_name HealthComponent
extends Node

signal health_changed(current_value, max_value, diff)
signal died()

@export var max_health: float = 100.0
@export var regen_rate: float = 0.0

var current_health: float

func _ready() -> void:
	current_health = max_health
	# Сообщаем UI начальное состояние
	call_deferred("emit_signal", "health_changed", current_health, max_health, 0)

func _process(delta: float) -> void:
	if regen_rate > 0 and current_health < max_health:
		heal(regen_rate * delta)

func take_damage(amount: float):
	var old_health = current_health
	current_health -= amount
	current_health = clamp(current_health, 0, max_health)
	
	emit_signal("health_changed", current_health, max_health, current_health - old_health)
	
	if current_health <= 0:
		emit_signal("died")

func heal(amount: float):
	var old_health = current_health
	current_health += amount
	current_health = clamp(current_health, 0, max_health)
	
	# Отправляем сигнал, только если здоровье реально изменилось
	if old_health != current_health:
		emit_signal("health_changed", current_health, max_health, current_health - old_health)