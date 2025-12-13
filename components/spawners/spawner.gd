extends Node2D

# BEST PRACTICE: Явное назначение зависимостей
@export var mob_scene: PackedScene
@export var spawn_container: Node2D # Куда спавнить мобов (обычно родитель или спец. нода)

@onready var animation_player: AnimationPlayer = $AnimationPlayer
var is_spawning = false

func _ready() -> void:
	# Если контейнер не назначен, используем родителя (но безопасно)
	if not spawn_container:
		spawn_container = get_parent()
		
	if not mob_scene:
		printerr("ERROR: [Spawner] mob_scene not assigned!")
	
	animation_player.play("idle")
	Signals.connect('day_time', Callable(self, "_on_time_changed"))

func _on_time_changed(state, day_count):
	# DAY state check (предполагаем, что 1 это DAY, лучше использовать enum из game.gd, но здесь оставим число)
	if state == 1 and not is_spawning:
		start_spawning(day_count)

func start_spawning(day_count):
	if not mob_scene or not spawn_container: return
	
	is_spawning = true
	var rng = 1
	var spawn_amount = day_count + rng
	
	for i in spawn_amount:
		animation_player.play("spawn")
		await animation_player.animation_finished
		
		mushroom_spawn()
		
		await get_tree().create_timer(0.5).timeout
	
	animation_player.play("idle")
	is_spawning = false
		
func mushroom_spawn():
	if not mob_scene: return
	
	var mob = mob_scene.instantiate()	
	# Спавним относительно позиции спавнера
	mob.position = self.global_position # Лучше использовать global_position
	spawn_container.add_child(mob)
	
	# Обновляем позицию игрока для моба сразу
	var player = get_tree().get_first_node_in_group("player")
	if player:
		Signals.emit_signal("player_position_update", player.global_position)
