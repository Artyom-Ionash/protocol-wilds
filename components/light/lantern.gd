extends PointLight2D

@onready var timer: Timer = $Timer
var day_state = 0

func _ready() -> void:
	Signals.connect("day_time",Callable(self, "_on_time_changed"))

func _on_timer_timeout() -> void:
	if day_state == 3:	
		var rng = randf_range(0.8,1.2) 
		var tween = get_tree().create_tween()
		tween.parallel().tween_property(self,"texture_scale", rng, timer.wait_time)
		tween.parallel().tween_property(self,"energy", rng, timer.wait_time)
		timer.wait_time = randf_range(0.4,0.8)

func _on_time_changed(state):
	day_state = state
	if state == 0:
		light_off()
	elif state == 2:
		light_on()		
func light_on():
	var tween = get_tree().create_tween()
	tween.tween_property(self,"energy", 1.5, randi_range(10,20))	
	
func light_off():
	var tween = get_tree().create_tween()
	tween.tween_property(self,"energy", 0, randi_range(10,20))	
