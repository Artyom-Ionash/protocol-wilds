extends CharacterBody2D

enum State {
	IDLE,
	ATTACK,
	CHASE,
	DAMAGE,
	DEATH,
	RECOVER
}

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
			State.CHASE: chase_state()

var direction: Vector2 = Vector2.ZERO
var health: int
var received_damage_amount: int = 0

# Кэшируем ссылку на игрока
var player_ref: Node2D = null

@onready var anim_player: AnimationPlayer = $AnimationPlayer
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var damage_text: Label = $Damage_text
@onready var attack_direction_node: Node2D = $AttackDirection

func _ready() -> void:
	health = max_health
	current_state = State.CHASE
	
	# ИСПРАВЛЕНИЕ: Находим игрока один раз при спавне
	player_ref = get_tree().get_first_node_in_group("player")
	if not player_ref:
		printerr("Mushroom: Игрок не найден! Убедитесь, что Player в группе 'player'.")
	
	# Сигнал player_position_update УДАЛЕН
	
	Signals.connect('player_attack', Callable(self, '_on_damage_received_signal'))
	
	if damage_text:
		damage_text.modulate.a = 0

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	
	if current_state == State.CHASE:
		_process_chase_movement()
	
	move_and_slide()

# УДАЛЕНО: func _on_player_position_update(pos: Vector2)

func _on_attack_range_body_entered(_body: Node2D) -> void:
	if current_state != State.DEATH:
		current_state = State.ATTACK

# --- Состояния ---

func idle_state() -> void:
	velocity.x = 0
	anim_player.play('Idle')
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
	# ИСПРАВЛЕНИЕ: Используем прямую ссылку на позицию игрока
	if not is_instance_valid(player_ref):
		velocity.x = 0
		return

	# Напрямую берем global_position игрока
	var player_pos = player_ref.global_position
	
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
	$CollisionShape2D.set_deferred("disabled", true)
	
	anim_player.play('death')
	await anim_player.animation_finished
	queue_free()

# --- Обработка урона ---

func _on_hit_box_area_entered(_area: Area2D) -> void:
	Signals.emit_signal('enemy_attack', damage)

func _on_damage_received_signal(player_dmg_amount: int) -> void:
	received_damage_amount = player_dmg_amount

func _on_hurt_box_area_entered(_area: Area2D) -> void:
	await get_tree().create_timer(0.05).timeout
	if not is_instance_valid(self): return
	
	health -= received_damage_amount
	
	if damage_text:
		damage_text.text = str(received_damage_amount)
		
	anim_player.stop()
	
	if health <= 0:
		current_state = State.DEATH
	else:
		current_state = State.DAMAGE

func apply_knockback() -> void:
	velocity.x = 0
	if is_instance_valid(player_ref):
		var knockback_dir = -1 if (player_ref.global_position.x - position.x) > 0 else 1
		velocity.x = knockback_dir * 200
	
	var tween = get_tree().create_tween()
	tween.tween_property(self, "velocity", Vector2.ZERO, 0.1)

func _on_run_timeout() -> void:
	move_speed = move_toward(move_speed, randi_range(120, 170), 100)