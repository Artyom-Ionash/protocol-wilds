extends Node2D

enum DayState {
	MORNING,
	DAY,
	EVENING,
	NIGHT
}

# --- DEPENDENCY INJECTION ---
# Назначьте эти узлы в Инспекторе!
@export_group("Lighting")
@export var sun_light: DirectionalLight2D
@export var point_light_1: PointLight2D
@export var point_light_2: PointLight2D

@export_group("UI")
@export var day_text: Label
@export var anim_player: AnimationPlayer

@export_group("Entities")
@export var player: CharacterBody2D

# --- Переменные ---
var state: DayState = DayState.MORNING
var day_count: int = 0

func _ready() -> void:
	Global.gold = 0
	
	# Fallback для старых сцен, если не назначено в инспекторе (совместимость)
	if not sun_light: printerr("Game: Sun Light not assigned")
	if not point_light_1: printerr("Game: Light 1 not assigned")
	if not point_light_2: printerr("Game: Light 2 not assigned")
	if not day_text: printerr("Game: Day Text not assigned")
	if not anim_player: printerr("Game: Anim Player not assigned")
	if not player: printerr("Game: Player not assigned")

	sun_light.enabled = true
	
	day_count = 0
	morning_state()
	day_text_fade()
		
func morning_state() -> void:	
	day_count += 1
	
	day_text.text = "DAY " + str(day_count)

	var tween = get_tree().create_tween()
	tween.tween_property(sun_light, 'energy', 0.2, 10)
	
	var tween1 = get_tree().create_tween()
	tween1.tween_property(point_light_1, 'energy', 0, 10)
	
	var tween2 = get_tree().create_tween()
	tween2.tween_property(point_light_2, 'energy', 0, 10)
	
func evening_state() -> void:
	var tween = get_tree().create_tween()
	tween.tween_property(sun_light, 'energy', 0.9, 10)
	
	var tween1 = get_tree().create_tween()
	tween1.tween_property(point_light_1, 'energy', 3, 10)
	
	var tween2 = get_tree().create_tween()
	tween2.tween_property(point_light_2, 'energy', 3, 10)
		
func day_text_fade() -> void:
	anim_player.play('day_text_fade_in')
	await get_tree().create_timer(3).timeout
	# Проверка валидности после await
	if is_instance_valid(anim_player):
		anim_player.play('day_text_fade_out')	
	
func _on_day_night_timeout() -> void:
	if state < DayState.NIGHT:
		state += 1
	else:
		state = DayState.MORNING # Сброс на утро
		
	match state:
		DayState.MORNING:
			morning_state()
		DayState.EVENING:
			evening_state()	
	
	Signals.emit_signal("day_time", state, day_count)
