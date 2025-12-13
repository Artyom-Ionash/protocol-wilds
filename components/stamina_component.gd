class_name StaminaComponent
extends Node

signal stamina_changed(current_value, max_value)
signal stamina_depleted() # Когда упала до 0
signal stamina_recovered() # Когда восстановилась достаточно для действий

@export var max_stamina: float = 100.0
@export var regen_rate: float = 10.0
@export var regen_delay: float = 1.0 # Задержка регена после траты

var current_stamina: float
var can_regen: bool = true
var _regen_timer: Timer

func _ready() -> void:
	current_stamina = max_stamina
	
	# Создаем таймер задержки регенерации кодом (чтобы не мусорить в сцене)
	_regen_timer = Timer.new()
	_regen_timer.one_shot = true
	_regen_timer.timeout.connect(_on_regen_timer_timeout)
	add_child(_regen_timer)

func _process(delta: float) -> void:
	if can_regen and current_stamina < max_stamina:
		current_stamina += regen_rate * delta
		if current_stamina > max_stamina:
			current_stamina = max_stamina
		emit_signal("stamina_changed", current_stamina, max_stamina)

# Метод проверки: "Хватит ли сил на удар?"
func has_stamina(amount: float) -> bool:
	return current_stamina >= amount

# Метод траты
func consume(amount: float):
	current_stamina -= amount
	current_stamina = max(0, current_stamina)
	
	emit_signal("stamina_changed", current_stamina, max_stamina)
	
	if current_stamina <= 0:
		emit_signal("stamina_depleted")
	
	# Сбрасываем регенерацию
	can_regen = false
	_regen_timer.start(regen_delay)

func _on_regen_timer_timeout():
	can_regen = true
	emit_signal("stamina_recovered")