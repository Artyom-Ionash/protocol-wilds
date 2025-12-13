extends CanvasLayer

@onready var gold_text = $Control/PanelContainer/HBoxContainer/goldText

func _process(delta: float) -> void:
	gold_text.text = str(Global.gold)
