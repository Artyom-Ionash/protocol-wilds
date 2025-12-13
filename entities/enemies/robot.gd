extends CharacterBody2D

var gravity: float = ProjectSettings.get_setting('physics/2d/default_gravity')

@export var speed: float = 100.0

var chase: bool = false
var alive: bool = true
var player_ref: Node2D = null # Кэшируем ссылку на игрока

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D

func _ready() -> void:
	# Находим игрока один раз при старте
	player_ref = get_tree().get_first_node_in_group("player")
	if not player_ref:
		printerr("Robot: Player not found in group 'player'")

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta
	
	# Проверка валидности ссылки перед использованием
	if alive and is_instance_valid(player_ref):
		var direction = (player_ref.position - self.position).normalized()
		
		if chase:
			velocity.x = direction.x * speed
			anim.play('Run')
		else:
			velocity.x = 0
			anim.play('Idle')
			
		# Поворот спрайта
		if direction.x < 0:
			anim.flip_h = true
		else:
			anim.flip_h = false
			
		move_and_slide()
	elif not alive:
		velocity.x = 0
		# Анимация смерти проигрывается в функции death()

func _on_area_2d_body_entered(body: Node2D) -> void:
	# Используем группы для надежности
	if body.is_in_group("player"):
		chase = true

func _on_area_2d_body_exited(body: Node2D) -> void:
	if body.is_in_group("player"):
		chase = false
		
func _on_death_2_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		if alive:
			# Безопасное нанесение урона
			if body.get("health") != null:
				body.health -= 40
			elif body.has_method("take_damage"):
				body.take_damage(40)
		death()

func _on_death_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		death()
		
func death() -> void:
	if not alive: return # Защита от двойного вызова
	
	alive = false
	velocity.x = 0
	
	# Отключаем коллизии
	$CollisionShape2D.set_deferred("disabled", true)
	$detector/CollisionShape2D.set_deferred("disabled", true)
	$death/CollisionShape2D.set_deferred("disabled", true)
	
	anim.play("death")
	await anim.animation_finished
	queue_free()
