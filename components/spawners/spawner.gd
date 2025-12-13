extends Node2D

@export var mob_scene: PackedScene
@export var spawn_container: Node2D

@onready var animation_player: AnimationPlayer = $AnimationPlayer
var is_spawning = false

func _ready() -> void:
	if not spawn_container:
		spawn_container = get_parent()
		
	if not mob_scene:
		printerr("ERROR: [Spawner] mob_scene not assigned!")
	
	animation_player.play("idle")
	Signals.connect('day_time', Callable(self, "_on_time_changed"))

func _on_time_changed(state, _day_count):
	if state == 1 and not is_spawning:
		start_spawning(_day_count)

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
	mob.position = self.global_position
	spawn_container.add_child(mob)
