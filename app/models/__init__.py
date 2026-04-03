# Modelos base (sin dependencias)
from .stable import Stable
from .user import User
from .level import Level
from .track import Track

# Perfiles extendidos (dependen de User)
from .client_profile import ClientProfile
from .monitor_profile import MonitorProfile

# Tablas intermedias (MUY IMPORTANTE: antes de Horse y Lesson)
from .links import LessonHorseLink
from .links import LessonUserLink
from .links import HorseLevelLink

# Box debe importarse antes que Horse (Horse tiene FK a Box)
from .box import Box

# Modelos que usan las relaciones
from .horse import Horse

# Lesson depende de Horse, User, Track y links
from .lesson import Lesson

from .feature import FeatureCode
from .stable_feature import StableFeature
