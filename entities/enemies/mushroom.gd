extends CharacterBody2D

enum State {
	IDLE,
	ATTACK,
	CHASE,
	DAMAGE,
	DEATH,
	RECOVER
}

# Используем @export для настройки баланса в инспекторе
@export var damage: int = 10
@export var max_health: int = 100
@export var move_speed: float = 150.0

var gravity: float = ProjectSettings.get_setting('physics/2d/default_gravity')
var current_state: State = State.CHASE:
	set(value):
		current_state = value
		match current_state:
			State.IDLE: idle_state()
			State.ATTACK: attack_state()
			State.DAMAGE: damage_state()
			State.DEATH: death_state()
			State.RECOVER: recover_state()
			State.CHASE: chase_state() # Добавил явный вызов chase при смене состояния

var player_pos: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.ZERO
var health: int
var received_damage_amount: int = 0

@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var damage_text: Label = $Damage_text
@onready var attack_direction_node: Node2D = $AttackDirection

func _ready() -> void:
	health = max_health
	current_state = State.CHASE
	
	# Безопасное подключение сигналов
	if not Signals.player_position_update.is_connected(_on_player_position_update):
		Signals.connect('player_position_update', Callable(self, '_on_player_position_update'))
	# Примечание: player_attack - это глобальный сигнал урона? Лучше передавать урон конкретному мобу,
	# но оставляю как есть для совместимости с вашей текущей архитектурой.
	if not Signals.player_attack.is_connected(_on_damage_received_signal):
		Signals.connect('player_attack', Callable(self, '_on_damage_received_signal'))
	
	if damage_text:
		damage_text.modulate.a = 0
	else:
		printerr("Mushroom: Label 'Damage_text' not found!")

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	
	# Логика движения только в состоянии CHASE
	if current_state == State.CHASE:
		_process_chase_movement()
	
	move_and_slide()

func _on_player_position_update(pos: Vector2) -> void:
	player_pos = pos

func _on_attack_range_body_entered(_body: Node2D) -> void:
	if current_state != State.DEATH:
		current_state = State.ATTACK

# --- Состояния ---

func idle_state() -> void:
	velocity.x = 0
	anim_player.play('Idle')
	# Простая логика: постояли и снова побежали
	await get_tree().create_timer(1.0).timeout
	if current_state != State.DEATH and is_instance_valid(self):
		current_state = State.CHASE

func attack_state() -> void:
	velocity.x = 0
	anim_player.play("attack")
	await anim_player.animation_finished
	if current_state != State.DEATH:
		current_state = State.RECOVER

func recover_state() -> void:
	velocity.x = 0
	anim_player.play('recover')
	await anim_player.animation_finished
	if current_state != State.DEATH:
		current_state = State.IDLE

func chase_state() -> void:
	anim_player.play('run')

func _process_chase_movement() -> void:
	# Вынесено в отдельную функцию для чистоты кода
	direction = (player_pos - self.position).normalized()
	
	if direction.x < 0:
		sprite.flip_h = true
		attack_direction_node.rotation_degrees = 180
	else:
		sprite.flip_h = false
		attack_direction_node.rotation_degrees = 0
		
	velocity.x = direction.x * move_speed

func damage_state() -> void:
	apply_knockback()
	anim_player.play('damage')
	await anim_player.animation_finished
	if current_state != State.DEATH:
		current_state = State.IDLE

func death_state() -> void:
	Signals.emit_signal('enemy_died', position)
	velocity.x = 0
	# Отключаем коллизии, чтобы не мешать
	$CollisionShape2D.set_deferred("disabled", true)
	
	anim_player.play('death')
	await anim_player.animation_finished
	queue_free()

# --- Обработка урона ---

func _on_hit_box_area_entered(_area: Area2D) -> void:
	# Моб бьёт игрока
	Signals.emit_signal('enemy_attack', damage)

func _on_damage_received_signal(player_dmg_amount: int) -> void:
	# Сохраняем значение урона, который будет применен при коллизии HurtBox
	received_damage_amount = player_dmg_amount

func _on_hurt_box_area_entered(_area: Area2D) -> void:
	# Игрок ударил моба
	# Исправление: Безопасный await
	await get_tree().create_timer(0.05).timeout
	
	if not is_instance_valid(self): return # Если моб умер во время паузы
	
	health -= received_damage_amount
	
	if damage_text:
		damage_text.text = str(received_damage_amount)
		# Здесь можно добавить запуск анимации текста, если есть
		
	anim_player.stop()
	
	if health <= 0:
		current_state = State.DEATH
	else:
		current_state = State.DAMAGE

func apply_knockback() -> void:
	velocity.x = 0
	# Отскок в противоположную от игрока сторону
	var knockback_dir = -1 if (player_pos.x - position.x) > 0 else 1
	velocity.x = knockback_dir * 200
	
	var tween = get_tree().create_tween()
	tween.tween_property(self, "velocity", Vector2.ZERO, 0.1)

func _on_run_timeout() -> void:
	# Случайное изменение скорости бега
	move_speed = move_toward(move_speed, randi_range(120, 170), 100)
