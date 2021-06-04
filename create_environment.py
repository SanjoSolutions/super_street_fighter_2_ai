import os
import retro

from RyuDiscretizer import RyuDiscretizer
from SuperStreetFigher2ObservationSpaceWrapper import SuperStreetFighter2ObservationSpaceWrapper


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_environment(
    state='ryu_vs_fei_long_highest_difficulty',
    players=1
):
    retro.data.Integrations.add_custom_path(SCRIPT_DIR)
    environment = retro.make(
        game='SuperStreetFighter2-Snes',
        state=state,
        scenario=None,
        inttype=retro.data.Integrations.CUSTOM_ONLY,
        obs_type=None,
        players=players,
        use_restricted_actions=retro.Actions.FILTERED,
    )
    environment = SuperStreetFighter2ObservationSpaceWrapper(environment)
    environment = RyuDiscretizer(environment)
    return environment
