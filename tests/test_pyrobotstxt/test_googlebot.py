
import pyrobotstxt.googlebot


def test_init_RobotsMatcher() -> None:
    instance = pyrobotstxt.googlebot.RobotsMatcher()
    assert isinstance(instance, pyrobotstxt.googlebot.RobotsMatcher)
