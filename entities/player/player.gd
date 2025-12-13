extends CharacterBody2D

enum{
	MOVE,
	ATTACK,
	ATTACK2,
	ATTACK3,
	BLOCK,
	SLIDE,
	DAMAGE,
	DEATH
}

const SPEED = 100.0
const JUMP_VELOCITY = -200.0

var gravity = ProjectSettings.get_setting('physics/2d/default_gravity')
var state = MOVE
var run_speed = 1
var combo = false
var attack_cooldown = false
var player_pos
var damage_basic = 10
var damage_multiplier = 1
var damage_current 
var recovery = false

@onready var anim = $AnimatedSprite2D
@onready var animPlayer = $AnimationPlayer
@onready var stats = $stats # Предполагаем, что имя узла stats
# Ссылки на UI компоненты, которыми владеет Игрок (или CanvasLayer внутри него)
@onready var health_text = $HealthText 
@onready var health_anim = $HealthAnim

func _ready() -> void:
	add_to_group("player")
	
	# Подключаем сигналы от Stats к методам обновления UI
	if stats:
		stats.connect("health_changed", Callable(self, "_on_stats_health_changed"))
		stats.connect("no_stamina", Callable(self, "_on_stats_no_stamina"))
	
	Signals.connect('enemy_attack', Callable(self, '_on_damage_received'))
	
	# Инициализация прозрачности текста
	if health_text:
		health_text.modulate.a = 0

# --- Новая функция для обработки сигнала от Stats ---
func _on_stats_health_changed(new_val, difference):
	if health_text:
		health_text.text = str(difference)
	
	if health_anim:
		if difference < 0:
			health_anim.play("damage_received")
		elif difference > 0:
			health_anim.play("health_received")
			
func _physics_process(delta: float) -> void:
	match state:
		MOVE:
			move_state()
		ATTACK:
			attack_state()	
		ATTACK2:
			attack2_state()	
		ATTACK3:
			attack3_state()	
		BLOCK:
			block_state()
		SLIDE:
			slide_state()	
		DAMAGE:
			damage_state()	
		DEATH:
			death_state()				
	
	# Add the gravity.
	if not is_on_floor():
		velocity += get_gravity() * delta

	if velocity.y > 0:
		animPlayer.play("fall")
						
	move_and_slide()
	
	player_pos = self.position
	Signals.emit_signal('player_position_update', player_pos)
	
	damage_current = damage_basic * damage_multiplier
	
func move_state ():
	var direction := Input.get_axis("left", "right")
	if direction:
		velocity.x = direction * SPEED * run_speed
		if velocity.y == 0:
			if run_speed ==1:	
				animPlayer.play('walk')
			else:
				animPlayer.play('Run')	
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)
		if velocity.y == 0:
			animPlayer.play('Idle')	
	if direction == -1:
		$AnimatedSprite2D.flip_h = true
		$AttackDirection.rotation_degrees = 180
	elif direction == 1:
		$AnimatedSprite2D.flip_h = false 	
		$AttackDirection.rotation_degrees = 0	
	if Input.is_action_pressed("run") and not recovery:
		run_speed = 2
		stats.stamina -= stats.run_cost
	else:
		run_speed = 1	
	if Input.is_action_pressed("block"):
		if not recovery:	
			if velocity.x == 0 and stats.stamina >=1:
				state = BLOCK		
	if Input.is_action_pressed("slide") and velocity.x != 0:
		if recovery == false:	
			stats.stamina_cost = stats.slide_cost
			if stats.stamina > stats.stamina_cost:	
				state = SLIDE
	if Input.is_action_just_pressed('attack') and attack_cooldown == false:
		if recovery == false:	
			stats.stamina_cost = stats.attack_cost
			if stats.stamina > stats.stamina_cost:
				state = ATTACK 			
	# Handle jump.
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
		animPlayer.play("jump")			
		
func block_state():
	
	stats.stamina -= stats.block_cost
	velocity.x = 0
	animPlayer.play('block')	
	if Input.is_action_just_released('block') or recovery == true:
		state = MOVE	
func slide_state():
	stats.stamina_cost = stats.slide_cost
	animPlayer.play('slide')
	await animPlayer.animation_finished
	state = MOVE
	
func death_state():
	# Просто применяем гравитацию и не даем двигаться по X
	velocity.x = 0
	# Больше ничего здесь писать не нужно!
	# Анимация и таймер уже работают сами по себе.

func attack_state():
	stats.stamina_cost = stats.attack_cost
	damage_multiplier = 1
	if Input.is_action_just_pressed('attack') and combo == true and stats.stamina > stats.stamina_cost:	 
		state = ATTACK2
	velocity.x = 0	
	animPlayer.play('attack')
	await animPlayer.animation_finished
	attack_freeze()
	state = MOVE

func attack2_state():
	stats.stamina_cost = stats.attack_cost
	damage_multiplier = 1.5
	if Input.is_action_just_pressed('attack') and combo == true and stats.stamina > stats.stamina_cost:
			state = ATTACK3
	animPlayer.play('attack2')	
	await animPlayer.animation_finished
	state = MOVE

func attack3_state():
	stats.stamina_cost = stats.attack_cost
	damage_multiplier = 2
	animPlayer.play('attack3')	
	await animPlayer.animation_finished
	state = MOVE

func combo1():
	combo = true
	await animPlayer.animation_finished
	combo = false

func attack_freeze():
	attack_cooldown = true
	await get_tree().create_timer(0.5).timeout
	attack_cooldown = false

func damage_state():
	velocity.x = 0
	animPlayer.play('damage')
	await animPlayer.animation_finished
	state = MOVE

func start_death_sequence():
	state = DEATH
	velocity.x = 0
	
	animPlayer.play("death")
	collision_layer = 0
	
	await get_tree().create_timer(1.2).timeout
	
	# ИЗМЕНЕНИЕ: Используем SceneManager
	SceneManager.load_menu()

func _on_damage_received(enemy_damage):
	if state == DEATH: return 
	
	if state == BLOCK:
		enemy_damage /= 4
	elif state == SLIDE:
		enemy_damage = 0
	else:
		state = DAMAGE			
	
	# Обращаемся к health через сеттер stats
	stats.health -= enemy_damage
	
	if stats.health <= 0:
		# Логику обнуления лучше держать в stats, но пока оставим здесь для совместимости
		stats.health = 0 
		start_death_sequence()

func _on_hit_box_area_entered(_area: Area2D) -> void:
	Signals.emit_signal('player_attack', damage_current)

func _on_stats_no_stamina() -> void:
	recovery = true
	await get_tree().create_timer(3).timeout
	recovery = false
