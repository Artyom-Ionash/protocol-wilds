extends PointLight2D

@onready var timer: Timer = $Timer
var day_state = 0

func _ready() -> void:
	# Лучшая практика в Godot 4: использовать сам метод вместо строки с Callable, если возможно
	Signals.day_time.connect(_on_time_changed)

func _on_timer_timeout() -> void:
	if day_state == 3:
		var rng = randf_range(0.8, 1.2)
		var tween = get_tree().create_tween()
		tween.parallel().tween_property(self, "texture_scale", rng, timer.wait_time)
		tween.parallel().tween_property(self, "energy", rng, timer.wait_time)
		timer.wait_time = randf_range(0.4, 0.8)

# ИСПРАВЛЕНИЕ: Добавлен второй аргумент _day_count
func _on_time_changed(state, _day_count):
	day_state = state
	if state == 0:
		light_off()
	elif state == 2:
		light_on()

func light_on():
	var tween = get_tree().create_tween()
	tween.tween_property(self, "energy", 1.5, randi_range(10, 20))
	
func light_off():
	var tween = get_tree().create_tween()
	tween.tween_property(self, "energy", 0, randi_range(10, 20))