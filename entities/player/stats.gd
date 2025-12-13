extends CanvasLayer

@onready var health_bar = $HealthBar
@onready var stamina_bar = $stamina

# Явное внедрение зависимостей
@export var health_component: HealthComponent
@export var stamina_component: StaminaComponent

func _ready():
	# Валидация
	if not health_component or not stamina_component:
		printerr("ERROR: StatsUI: Не назначены компоненты (Health или Stamina)!")
		hide()
		return
	
	# Подписка на Здоровье
	health_component.health_changed.connect(_on_health_changed)
	_on_health_changed(health_component.current_health, health_component.max_health, 0)
	
	# Подписка на Стамину
	stamina_component.stamina_changed.connect(_on_stamina_changed)
	_on_stamina_changed(stamina_component.current_stamina, stamina_component.max_stamina)

func _on_health_changed(current, max_val, _diff):
	if health_bar:
		health_bar.max_value = max_val
		health_bar.value = current

func _on_stamina_changed(current, max_val):
	if stamina_bar:
		stamina_bar.max_value = max_val
		stamina_bar.value = current