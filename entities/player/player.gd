extends CharacterBody2D

enum {MOVE, ATTACK, ATTACK2, ATTACK3, BLOCK, SLIDE, DAMAGE, DEATH}

const SPEED = 100.0
const JUMP_VELOCITY = -200.0

var gravity = ProjectSettings.get_setting('physics/2d/default_gravity')
var state = MOVE
var run_speed = 1
var combo = false
var attack_cooldown = false
var damage_basic = 10
var damage_multiplier = 1
var damage_current

# БАЛАНС (Стоимость действий)
var attack_cost: float = 10.0
var block_cost: float = 0.5 # Тратитя каждый кадр
var slide_cost: float = 20.0
var run_cost: float = 0.4 # Тратится каждый кадр

@onready var anim = $AnimatedSprite2D
@onready var animPlayer = $AnimationPlayer
@onready var health_text = $HealthText
@onready var health_anim = $HealthAnim

# ЗАВИСИМОСТИ
@export var health_component: HealthComponent
@export var stamina_component: StaminaComponent

func _ready() -> void:
	add_to_group("player")
	
	if not health_component or not stamina_component:
		printerr("CRITICAL: Компоненты не назначены в Player! Проверьте Инспектор.")
		set_physics_process(false)
		return

	health_component.health_changed.connect(_on_health_changed)
	health_component.died.connect(start_death_sequence)
	Signals.enemy_attack.connect(_on_damage_received)
	
	if health_text: health_text.modulate.a = 0

# --- UI ОБРАБОТЧИКИ ---
func _on_health_changed(_current, _max, diff):
	if health_text: health_text.text = str(diff)
	if health_anim:
		if diff < 0: health_anim.play("damage_received")
		elif diff > 0: health_anim.play("health_received")

func _on_damage_received(enemy_damage):
	if state == DEATH: return
	
	if state == BLOCK:
		# При блоке урон режется
		enemy_damage /= 4
	elif state == SLIDE:
		# В слайде неуязвимость (i-frames)
		enemy_damage = 0
	else:
		state = DAMAGE
	
	if enemy_damage > 0:
		health_component.take_damage(enemy_damage)

func _physics_process(delta: float) -> void:
	# Машина состояний
	match state:
		MOVE: move_state()
		ATTACK: attack_state()
		ATTACK2: attack2_state()
		ATTACK3: attack3_state()
		BLOCK: block_state()
		SLIDE: slide_state()
		DAMAGE: damage_state()
		DEATH: death_state()
	
	# Гравитация
	if not is_on_floor():
		velocity += get_gravity() * delta
	if velocity.y > 0:
		animPlayer.play("fall")
		
	move_and_slide()
	damage_current = damage_basic * damage_multiplier

# --- СОСТОЯНИЯ ---

func move_state():
	var direction := Input.get_axis("left", "right")
	
	# Движение
	if direction:
		velocity.x = direction * SPEED * run_speed
		if velocity.y == 0:
			animPlayer.play('walk' if run_speed == 1 else 'Run')
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)
		if velocity.y == 0: animPlayer.play('Idle')
			
	if direction != 0:
		$AnimatedSprite2D.flip_h = (direction == -1)
		$AttackDirection.rotation_degrees = 180 if (direction == -1) else 0
		
	# БЕГ
	if Input.is_action_pressed("run") and stamina_component.has_stamina(run_cost):
		run_speed = 2
		stamina_component.consume(run_cost)
	else:
		run_speed = 1
		
	# БЛОК
	if Input.is_action_pressed("block"):
		if velocity.x == 0 and stamina_component.has_stamina(5.0):
			state = BLOCK
			
	# СЛАЙД
	if Input.is_action_pressed("slide") and velocity.x != 0:
		if stamina_component.has_stamina(slide_cost):
			stamina_component.consume(slide_cost)
			state = SLIDE
				
	# АТАКА
	if Input.is_action_just_pressed('attack') and not attack_cooldown:
		if stamina_component.has_stamina(attack_cost):
			stamina_component.consume(attack_cost)
			state = ATTACK
	
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY
		animPlayer.play("jump")
		
func block_state():
	# Постоянная трата при удержании блока
	if stamina_component.has_stamina(block_cost):
		stamina_component.consume(block_cost)
		velocity.x = 0
		animPlayer.play('block')
	else:
		# Если силы кончились во время блока - выходим
		state = MOVE
		
	if Input.is_action_just_released('block'):
		state = MOVE

func slide_state():
	# Стамина уже потрачена при входе в move_state
	animPlayer.play('slide')
	await animPlayer.animation_finished
	state = MOVE
	
func death_state():
	velocity.x = 0

func attack_state():
	damage_multiplier = 1
	# Проверяем комбо
	if Input.is_action_just_pressed('attack') and combo:
		if stamina_component.has_stamina(attack_cost): # Проверяем
			stamina_component.consume(attack_cost) # Тратим
			state = ATTACK2
			
	velocity.x = 0
	animPlayer.play('attack')
	await animPlayer.animation_finished
	attack_freeze()
	state = MOVE

func attack2_state():
	damage_multiplier = 1.5
	if Input.is_action_just_pressed('attack') and combo:
		if stamina_component.has_stamina(attack_cost): # Проверяем
			stamina_component.consume(attack_cost) # Тратим
			state = ATTACK3
			
	animPlayer.play('attack2')
	await animPlayer.animation_finished
	state = MOVE

func attack3_state():
	damage_multiplier = 2
	animPlayer.play('attack3')
	# Тут комбо заканчивается, ничего не проверяем
	await animPlayer.animation_finished
	state = MOVE

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

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
	SceneManager.load_menu()

func _on_hit_box_area_entered(_area: Area2D) -> void:
	Signals.emit_signal('player_attack', damage_current)