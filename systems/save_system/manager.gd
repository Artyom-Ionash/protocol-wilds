extends Node

# Вместо $"../CanvasLayer/pausemenu" используем экспорт.
# В Инспекторе нажмите "Assign" и выберите узел pausemenu в дереве сцены.
@export var pause_menu: Control

var game_paused: bool = false
var save_path = 'user://savegame.save'

func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("ui_cancel"):
		toggle_pause()

func toggle_pause() -> void:
	game_paused = !game_paused
	get_tree().paused = game_paused
	
	if pause_menu:
		pause_menu.visible = game_paused

# --- Сигналы кнопок ---

func _on_resume_pressed() -> void:
	toggle_pause()

func _on_quit_pressed() -> void:
	get_tree().paused = false 
	
	# ИЗМЕНЕНИЕ:
	SceneManager.load_menu()

func _on_menu_button_pressed() -> void:
	toggle_pause()

# --- Сохранение и Загрузка ---

# 3. ИСПРАВЛЕНИЕ: Поиск игрока
# Вместо @onready var player = $"../player/Player"
# Мы ищем игрока динамически только в момент сохранения/загрузки.
# Убедитесь, что у игрока добавлена группа "player".

func save_game():
	var file = FileAccess.open(save_path, FileAccess.WRITE)
	file.store_var(Global.gold)
	
	var player = get_tree().get_first_node_in_group("player")
	if player:
		file.store_var(player.position.x)
		file.store_var(player.position.y)
		print("Игра сохранена. Позиция игрока: ", player.position)
	else:
		print("Игрок не найден, сохранено только золото.")
	
func load_game():
	if not FileAccess.file_exists(save_path):
		print("Файл сохранения не найден.")
		return

	var file = FileAccess.open(save_path, FileAccess.READ)		
	Global.gold = file.get_var()
	
	var player = get_tree().get_first_node_in_group("player")
	if player:
		var x = file.get_var()
		var y = file.get_var()
		# Проверка на null (если в сохранении не было координат)
		if x != null and y != null:
			player.position.x = x
			player.position.y = y
			print("Игра загружена. Позиция игрока: ", player.position)
	else:
		print("Игрок не найден на сцене, позиция не загружена.")

# Сигналы кнопок сохранения
func _on_save_pressed() -> void:
	save_game()
	toggle_pause()

func _on_load_pressed() -> void:
	load_game()
	toggle_pause()
