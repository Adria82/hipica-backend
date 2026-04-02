# Modelos base (sin dependencias)
from .stable import Stable
from .user import User
from .lesson import Lesson
from .level import Level, NivelEquitacion

# Tablas intermedias (MUY IMPORTANTE: antes de Horse)
from .links import LessonHorseLink
from .links import HorseLevelLink

# Box debe importarse antes que Horse (Horse tiene FK a Box)
from .box import Box

# Modelos que usan las relaciones
from .horse import Horse


from .feature import FeatureCode
from .stable_feature import StableFeature
