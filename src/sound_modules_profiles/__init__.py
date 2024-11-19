from pathlib import Path


for path in sorted(Path(__file__).parent.iterdir()):
    if path.name.startswith('_') or path.name == "resources":
        continue

    __import__(path.stem, globals(), level=1)


from .resources import UNSORTED_SOUND_MODULES_PROFILE_SPECS

SOUND_MODULES_PROFILE_SPECS = sorted(
    UNSORTED_SOUND_MODULES_PROFILE_SPECS, key=lambda x: x.priority
)
