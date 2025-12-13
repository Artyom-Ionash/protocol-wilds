extends CanvasLayer

# Сигналы для обновления UI
signal health_changed(new_value, diff)
signal stamina_changed(new_value)
signal no_stamina()

@onready var health_bar = $HealthBar
@onready var stamina_bar = $stamina
# УДАЛЕНО: Прямые ссылки на внешние узлы (health_text, health_anim)

var max_health = 100
var stamina_cost 
var attack_cost = 10
var block_cost = .5
var slide_cost = 20
var run_cost = .4
var old_health = max_health

var stamina = 50:
	set(value):
		stamina = value
		emit_signal("stamina_changed", stamina)
		if stamina < 1:
			emit_signal("no_stamina")	

var health:
	set(value):
		health = clamp(value, 0, max_health)
		health_bar.value = health
		
		var difference = health - old_health
		# Вместо прямого управления текстом и анимацией, эмитим сигнал
		emit_signal("health_changed", health, difference)
		
		old_health = health

func _ready():
	health = max_health
	health_bar.max_value = health
	health_bar.value = health

func _process(delta):
	stamina_bar.value = stamina
	if stamina < 100:
		stamina += 10 * delta

func stamina_consumption():
	stamina -= stamina_cost

func _on_heakth_regen_timeout() -> void:
	self.health += 10 # Используем self, чтобы сработал сеттер
