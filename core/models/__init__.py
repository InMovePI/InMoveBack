from .user import User
from .workout_log import WorkoutLog
from .dieta import Dieta
from .exercicio import Exercicio
from .ingestao_agua import IngestaoAgua
from .refeicao import Refeicao
from .relatorio_progresso import RelatorioProgresso
from .treino import Treino
from .treino_exercicio import TreinoExercicio
from .chat import ChatMessage
try:  # import meal models so Django discovers them when the package is imported
	from .meal import Meal, IngredientEntry  # type: ignore
except Exception:
	# keep import-safe in environments where meal module isn't available yet
	Meal = None  # type: ignore
	IngredientEntry = None  # type: ignore

try:
	from .fooditem import FoodItem  # type: ignore
except Exception:
	FoodItem = None  # type: ignore
