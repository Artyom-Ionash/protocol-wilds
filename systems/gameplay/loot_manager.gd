extends Node2D

# BEST PRACTICE: Используем @export для сцен.
# Это позволяет менять структуру папок без поломки кода.
@export var coin_scene: PackedScene

func _ready() -> void:
	# Проверка зависимостей при старте
	if not coin_scene:
		printerr("ERROR: [Collectables] coin_scene is not assigned in Inspector!")
		set_physics_process(false) # Остановить логику, чтобы избежать крэша
		return

	Signals.connect('enemy_died', Callable(self, "_on_enemy_died"))
	
func _on_enemy_died(enemy_position: Vector2) -> void:
	if not coin_scene: return
	
	var amount = randi_range(1, 5)
	for i in amount:
		var random_offset = Vector2(randf_range(-10, 10), randf_range(-10, 10))
		coin_spawn(enemy_position + random_offset)
		
		await get_tree().create_timer(0.05).timeout
		if not is_instance_valid(self): return

func coin_spawn(pos: Vector2) -> void:
	if not coin_scene: return

	var coin = coin_scene.instantiate()
	coin.position = pos
	call_deferred("add_child", coin)
