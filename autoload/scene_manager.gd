extends Node

# Централизованное хранилище путей.
# Если вы захотите переместить файлы, поменяйте пути только здесь.
const MENU_SCENE_PATH = "res://scenes/main_menu.tscn"
const GAME_SCENE_PATH = "res://scenes/game.tscn"

# Функция для безопасной смены сцены с отложенным вызовом
func change_scene(scene_path: String) -> void:
	# call_deferred ждет, пока текущий кадр закончится, чтобы безопасно удалить текущую сцену
	call_deferred("_deferred_change_scene", scene_path)

func _deferred_change_scene(path: String) -> void:
	var error = get_tree().change_scene_to_file(path)
	if error != OK:
		printerr("[SceneManager] Ошибка загрузки сцены: ", path)

# Удобные методы-обертки
func load_menu() -> void:
	change_scene(MENU_SCENE_PATH)

func load_game() -> void:
	change_scene(GAME_SCENE_PATH)

func reload_current_scene() -> void:
	get_tree().reload_current_scene()
