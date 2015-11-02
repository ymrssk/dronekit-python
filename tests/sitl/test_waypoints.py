import time
import math
from dronekit import connect, VehicleMode, LocationGlobal, Command
from dronekit.tools import with_sitl
from nose.tools import assert_not_equals, assert_equals

@with_sitl
def test_empty_clear(connpath):
    vehicle = connect(connpath)

    # Calling clear() on an empty object should not crash.
    vehicle.commands.clear()
    vehicle.commands.upload()

    assert_equals(len(vehicle.commands), 0)

@with_sitl
def test_parameter(connpath):
    vehicle = connect(connpath, await_params=True)

    # Home should be None at first.
    assert_equals(vehicle.home_location, None)
    
    # Wait for home position to be real and not 0, 0, 0
    # once we request it via cmds.download()
    time.sleep(10)

    # Initial
    vehicle.commands.download()
    vehicle.commands.wait_valid()
    assert_equals(len(vehicle.commands), 0)
    assert_not_equals(vehicle.home_location, None)

    # Save home for comparison.
    home = vehicle.home_location

    # After clearing
    vehicle.commands.clear()
    vehicle.commands.upload()
    vehicle.commands.download()
    vehicle.commands.wait_valid()
    assert_equals(len(vehicle.commands), 0)

    # Upload
    for command in [
        Command(0, 0, 0, 0, 16, 1, 1, 0.0, 0.0, 0.0, 0.0, -35.3605, 149.172363, 747.0),
        Command(0, 0, 0, 3, 22, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.359831, 149.166334, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.363489, 149.167213, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355491, 149.169595, 100.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.355071, 149.175839, 100.0),
        Command(0, 0, 0, 3, 113, 0, 1, 0.0, 0.0, 0.0, 0.0, -35.362666, 149.178715, 22222.0),
        Command(0, 0, 0, 3, 115, 0, 1, 2.0, 22.0, 1.0, 3.0, 0.0, 0.0, 0.0),
        Command(0, 0, 0, 3, 16, 0, 1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]:
        vehicle.commands.add(command)
    vehicle.commands.upload()

    # After upload
    vehicle.commands.download()
    vehicle.commands.wait_valid()
    assert_equals(len(vehicle.commands), 8)

    # Test iteration.
    count = 0
    for cmd in vehicle.commands:
        assert_not_equals(cmd, None)
        count += 1
    assert_equals(count, 8)

    # Test slicing
    count = 3
    for cmd in vehicle.commands[2:5]:
        assert_not_equals(cmd, None)
        assert_equals(cmd.seq, count)
        count += 1
    assert_equals(count, 6)

    # Test next property
    assert_equals(vehicle.commands.next, 0)
    vehicle.commands.next = 3
    while vehicle.commands.next != 3:
        time.sleep(0.1)
    assert_equals(vehicle.commands.next, 3)

    # Home should be preserved
    assert_equals(home.lat, vehicle.home_location.lat)
    assert_equals(home.lon, vehicle.home_location.lon)
    assert_equals(home.alt, vehicle.home_location.alt)
