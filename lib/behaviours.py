import time
import random
import cozmo
from cozmo.util import degrees
from threading import Thread


def finished():
    print('finished animation triggered')
    play_list = [
        'anim_codelab_chicken_01',
        'anim_codelab_getout_01',
        'anim_codelab_rooster_01',
        'anim_codelab_tasmanian_devil_01',
        'anim_energy_cubeshake_01',
        'anim_greeting_happy_01',
        'anim_greeting_happy_03',
        'anim_hiking_react_04',
        'anim_keepaway_wingame_01',
        'anim_keepaway_wingame_02',
        'anim_keepaway_wingame_03',
        'anim_majorwin',
        'anim_meetcozmo_celebration_02',
        'anim_memorymatch_successhand_cozmo_01',
        'anim_memorymatch_successhand_cozmo_02',
        'anim_memorymatch_successhand_cozmo_03',
        'anim_memorymatch_successhand_cozmo_04',
        'anim_peekaboo_success_01',
        'anim_peekaboo_success_02',
        'anim_peekaboo_success_03'
    ]
    play = play_list[random.randint(0, len(play_list) - 1)]
    print(play)
    robot.play_anim(play).wait_for_completed()
    robot_default_position()


def start():
    print('start animation triggered')
    robot.say_text("I love math, let's play!", in_parallel=True)
    robot_default_position()


def disappointed():
    print('disappointed animation triggered')
    play_list = [
        'anim_peekaboo_fail_01',
        'anim_peekaboo_failgetout_01',
        'anim_poked_01',
        'anim_poked_02',
        'anim_pyramid_reacttocube_frustrated_high_01',
        'anim_reacttoblock_frustrated_01',
        'anim_reacttoblock_frustrated_int1_01',
        'anim_reacttoblock_frustrated_int2_01'
    ]
    play = play_list[random.randint(0, len(play_list) - 1)]
    print(play)
    robot.play_anim(play).wait_for_completed()
    robot_default_position()


def robot_default_position():
    # return to position, z angle, head and lift position as before the action started
    robot.go_to_pose(pose, in_parallel=True).wait_for_completed()
    if (robot.head_angle.degrees <= 40.0):
        robot.set_head_angle(degrees(44.0), in_parallel=True)
    robot.set_lift_height(0.0, in_parallel=True)


def run_action(action, _robot=None):
    global pose
    # First trigger of this function needs a robot argument
    if _robot != None:
        global robot
        robot = _robot
    pose = robot.pose
    action()

