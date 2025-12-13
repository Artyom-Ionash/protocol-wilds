extends CanvasLayer

@onready var health_bar = $HealthBar
@onready var stamina_bar = $stamina

# Явное внедрение зависимостей (Drag & Drop в редакторе)
@export var health_component: HealthComponent
@export var stamina_component: StaminaComponent

func _ready():
	# 1. Если компоненты не назначены вручную, пытаемся найти их автоматически
	if not health_component or not stamina_component:
		_find_components_automatically()

	# 2. Если все равно не нашли — отключаем UI, чтобы не было краша
	if not health_component or not stamina_component:
		printerr("ERROR: StatsUI: Компоненты не найдены! Убедитесь, что Player есть на сцене и находится в группе 'player'.")
		hide()
		set_process(false)
		return
	
	# 3. Инициализация (Принудительное обновление при старте)
	health_bar.max_value = health_component.max_health
	health_bar.value = health_component.current_health # Важно: используем current_health, а не health
	
	stamina_bar.max_value = stamina_component.max_stamina
	stamina_bar.value = stamina_component.current_stamina
	
	# 4. Подписка на сигналы
	health_component.health_changed.connect(_on_health_changed)
	stamina_component.stamina_changed.connect(_on_stamina_changed)

func _find_components_automatically():
	# Попытка 1: Ищем у родителя (если UI внутри игрока)
	var parent = get_parent()
	if parent and parent.is_in_group("player"):
		_try_assign_from_node(parent)
		if health_component and stamina_component: return

	# Попытка 2: Ищем глобально игрока в группе (если UI отдельно в Game.tscn)
	var player = get_tree().get_first_node_in_group("player")
	if player:
		_try_assign_from_node(player)

func _try_assign_from_node(node: Node):
	# Ищем узлы по их типу или имени
	if not health_component:
		if node.has_node("HealthComponent"):
			health_component = node.get_node("HealthComponent")
			
	if not stamina_component:
		if node.has_node("StaminaComponent"):
			stamina_component = node.get_node("StaminaComponent")

func _on_health_changed(current, max_val, _diff):
	if health_bar:
		health_bar.max_value = max_val
		health_bar.value = current

func _on_stamina_changed(current, max_val):
	if stamina_bar:
		stamina_bar.max_value = max_val
		stamina_bar.value = current