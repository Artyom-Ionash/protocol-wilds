# Архитектура проекта "Protocol Wilds"

## Обзор
2D Action-Platformer с элементами выживания (смена дня/ночи, волны врагов, система прогрессии).

**Технологический стек:**
- **Движок:** Godot 4.5+ (GL Compatibility)
- **Язык:** GDScript с частичной статической типизацией
- **Физика:** CharacterBody2D для сущностей, Area2D для триггеров и боевой системы

### ⚠️ Примечание о Legacy Reference
Папка `_reference_code/` содержит прототип на Python (Pygame). **Это низкокачественный код**, оставленный **только как список механик** для портирования. **Запрещено** копировать архитектурные решения оттуда.

---

## Стандарты именования (Naming Conventions)

Проект следует официальному **Godot Style Guide**:

1. **Файловая структура:** `snake_case` для всех папок и файлов
   - Пример: `res://autoload/scene_manager.gd`
   
2. **Узлы в сцене:** `PascalCase`
   - Пример: `Player`, `DamageBox`, `HealthComponent`

3. **GDScript:**
   - Классы: `PascalCase` 
   - Переменные/функции: `snake_case`
   - Константы: `SCREAMING_SNAKE_CASE`
   - Enums: `PascalCase` (имя), `SCREAMING_SNAKE_CASE` (значения)

---

## Ключевые архитектурные паттерны

### 1. Компонентная система (Composition over Inheritance)

Повторно используемые компоненты инкапсулируют логику:

**Существующие компоненты:**

- **HealthComponent** (`components/health_component.gd`)
  - Управление здоровьем, регенерацией, смертью
  - Сигналы: `health_changed(current, max, diff)`, `died()`
  
- **StaminaComponent** (`components/stamina_component.gd`)
  - Управление выносливостью, регенерацией с задержкой
  - Сигналы: `stamina_changed(current, max)`, `stamina_depleted()`, `stamina_recovered()`
  
- **DamageBox** (`components/damage_box/`)
  - HitBox (наносит урон) + HurtBox (получает урон)
  - Используется как Player'ом, так и врагами

### 2. Finite State Machine (FSM)

Управление состояниями через `enum` + `match`:

**Используется в:**
- `entities/player/player.gd` (состояния: MOVE, ATTACK, ATTACK2, ATTACK3, BLOCK, SLIDE, DAMAGE, DEATH)
- `entities/enemies/mushroom.gd` (состояния: IDLE, CHASE, ATTACK, DAMAGE, DEATH, RECOVER)

### 3. Event Bus (Signals Singleton)

Глобальная шина событий `Signals` (`autoload/signals.gd`):

### 4. Dependency Injection через @export

**Принцип:** Зависимости назначаются в Инспекторе, а не хардкодятся:

```gdscript
@export var health_component: HealthComponent
@export var coin_scene: PackedScene
@export var spawn_container: Node2D
```

**Преимущества:**
- Гибкость файловой структуры
- Godot автоматически обновляет ссылки при перемещении файлов (через UID)

### 5. Управление ресурсами

**Правила:**
1. ❌ Запрет на хардкод путей в логике (`load("res://...")`)
2. ✅ Используйте `@export` переменные
3. ✅ Единственное исключение: `SceneManager` (централизованное хранилище путей к главным сценам)

```gdscript
# ❌ ПЛОХО
var mob = load("res://entities/enemies/mushroom.tscn")

# ✅ ХОРОШО
@export var mob_scene: PackedScene
```

---

## 6. Стратегия работы с AI

### Правила генерации кода

1. **Полный вывод файлов**
   - AI **обязан** выводить код целиком
   - ❌ Запрещены сокращения типа `// ... existing code ...`

2. **Инструкции для Инспектора**
   - После каждого `@export` предоставлять чек-лист действий в Godot Editor
   
   ```markdown
   **Настройка в Инспекторе:**
   1. Выберите узел [Player]
   2. В секции Script Variables найдите [health_component]
   3. Drag & Drop узел HealthComponent из Scene Tree ИЛИ нажмите Assign
   ```

3. **Лаконичность**
   - Удалять закомментированный код
   - Предпочитать простые решения сложным

4. **Обновление документации**
   - При изменении архитектуры обновлять `ARCHITECTURE.md` и `TECH_DEBT.md`

---

## Основные подсистемы

### Глобальные Синглтоны (Autoloads)

1. **Global** (`autoload/global.gd`)
   - Хранит общее состояние: `gold`, `player_pos`, `player_damage`

2. **Signals** (`autoload/signals.gd`)
   - Event Bus для межсистемной коммуникации

3. **SceneManager** (`autoload/scene_manager.gd`)
   - Безопасная смена сцен через `call_deferred`
   - Методы: `load_menu()`, `load_game()`, `reload_current_scene()`

### Игрок (`entities/player/`)

**Файлы:**
- `player.gd` - основная логика (FSM, ввод, комбо-система)
- `player.tscn` - сцена персонажа
- `stats.gd` / `stats.tscn` - UI для здоровья/стамины

**Ключевые механики:**
- Комбо-атаки (3-hit chain)
- Блок (снижает урон в 4 раза, тратит стамину)
- Слайд (защита, тратит 20 стамины)
- Бег (увеличивает скорость в 2x, тратит 0.4 стамины/кадр)

**Компоненты:**
- `HealthComponent` - управление здоровьем
- `StaminaComponent` - управление выносливостью
- `DamageBox` - атака и получение урона

### Враги (`entities/enemies/`)

**Mushroom** (`mushroom.gd`)
- FSM: IDLE → CHASE → ATTACK → RECOVER
- Напрямую получает позицию игрока через кэшированную ссылку
- Использует NavigationAgent2D для преследования

**Robot** (`robot.gd`)
- Упрощенная логика с использованием групп (`is_in_group("player")`)
- Детектирует игрока через Area2D

### Игровой мир (`scenes/game.gd`)

**Day/Night Cycle:**
```gdscript
enum DayState { MORNING, DAY, EVENING, NIGHT }
```

**Механика:**
- Таймер 30 секунд → смена состояния
- Управление глобальным освещением (`DirectionalLight2D`)
- Триггер спавна врагов через сигнал `Signals.day_time`

**Dependency Injection:**
```gdscript
@export var sun_light: DirectionalLight2D
@export var point_light_1: PointLight2D
@export var day_text: Label
@export var player: CharacterBody2D
```

### Система сохранений (`systems/save_system/`)

**Файл:** `user://savegame.save`

**Использует динамический поиск игрока** вместо жесткой ссылки.

---

## Текущие ограничения

1. **Нет системы инвентаря** - только отображение gold
2. **Упрощенная система loot** - только монеты
3. **Отсутствие прогрессии** - нет системы апгрейдов
4. **Статичный баланс** - нет масштабирования сложности по дням

---

## Дальнейшее развитие

См. `TECH_DEBT.md` для приоритетных задач рефакторинга.
