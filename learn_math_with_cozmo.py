import cozmo
import random
import time
import asyncio
import logging
import sys
import json
from threading import Thread
from lib import flask_socket_helpers
from PIL import Image, ImageDraw, ImageFont
import lib.behaviours as behaviours

try:
    from flask import Flask, render_template, request
except ImportError:
    sys.exit("Cannot import from flask: Do `pip3 install --user flask` to install")

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    logging.warning("Cannot import from PIL: Do `pip3 install --user Pillow` to install")


app = Flask(__name__)
msg = ''
x = 0
y = 0
math_string = ''
robot = None
is_busy = False
questions = 10
current_question = 0
game_type = ''
game_range = 0
display_action = None


@app.route('/')
def index():
    global x, y
    return render_template(
        'index.html'
    )


@app.route('/answer', methods=['POST'])
def answer_eval():
    global is_busy
    global math_string
    global current_question
    global game_type

    is_busy = False

    if game_type == '+':
        correct_answer = x + y
    elif game_type == '-':
        correct_answer = x - y
    elif game_type == '*':
        correct_answer = x * y

    answer = int(json.loads(request.data.decode("utf-8")))
    if answer == correct_answer:
        msg = 'Correct!'
        math_string = create_math_calculation()
        current_question = current_question + 1
    else:
        msg = 'Wrong'
    print(msg)
    robot_create_img(msg)
    robot.say_text(msg, in_parallel=True).wait_for_completed()
    if current_question >= questions:
        current_question = 0
        behaviours.run_action(behaviours.finished)
        return 'done'
    else: 
        ask_question(math_string)
        return ''


@app.route('/game_start', methods=['POST'])
def game_start():
    global robot
    global math_string
    global game_type
    global game_range

    msg = json.loads(request.data.decode("utf-8"))
    game_type = msg['type']
    game_range = msg['range']
    math_string = create_math_calculation()
    ask_question(math_string)
    return game_type


@app.route('/again', methods=['POST'])
def again():
    global current_question
    current_question = 0
    ask_question(math_string)
    return ''


def ask_question(msg):
    global is_busy

    is_busy = True
    robot_create_img(msg)
    if game_type == '-':
        msg2 = str(x) + ' minus ' + str(y)
    else:
        msg2 = str(x) + ' ' + game_type + ' ' + str(y)
    robot.say_text(msg2, in_parallel=True).wait_for_completed()
    # recreate image because both say_text and display_oled_face_image are considered animations and only one can run at the same time
    robot_create_img(msg)     
    while is_busy:
        time.sleep(0.1)


def create_math_calculation():
    global x,y
    global game_type
    global game_range

    if game_type == '+':
        x = random.randint(0, game_range)
        y_range = game_range - x
    elif game_type == '-':
        x = random.randint(1,int(game_range*1.5))
        if x > game_range:
            x = x - int(game_range/2)
        y_range = x
    elif game_type == '*':
        x = random.randint(1, game_range)
        y_range = random.randint(1, game_range)
    y = random.randint(0, y_range)

    msg = str(x) + ' ' + game_type + ' ' + str(y)
    return msg

def robot_create_img(msg):
    global pixel_bytes
    global display_action

    color = (255,255,255)
    progress = str(current_question) + ' / ' + str(questions)
    W, H = (128,32)
    fnt1 = ImageFont.truetype('../static/fonts/Roboto-Bold.ttf', 24)
    fnt2 = ImageFont.truetype('../static/fonts/Roboto-Bold.ttf', 12)
    img = Image.new("RGBA",(W,H),color = (50, 50, 50))
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(msg, font=fnt1)

    draw.text(((W-w)/2,(H-h)/2+4), msg, font=fnt1, fill=color)
    draw.text((0,0), progress, font=fnt2, fill=color)

    pixel_bytes = cozmo.oled_face.convert_image_to_screen_data(img)
    if display_action != None and display_action.is_running == True:
        display_action.abort()
    display_action = robot.display_oled_face_image(pixel_bytes, 600000, in_parallel=True)


def run(_robot: cozmo.robot.Robot):
    global robot

    robot = _robot
    behaviours.run_action(behaviours.start, _robot=robot)
    robot.say_text("I love math", in_parallel=True)

    robot_create_img('I love math')
    print(display_action)
    time.sleep(3)
    print(display_action)
    robot_create_img("Let's play")
    robot.say_text("Let's play!", in_parallel=True)

    flask_socket_helpers.run_flask(None, app)


if __name__ == '__main__':
    try:
        cozmo.run_program(run)
    except KeyboardInterrupt as e:
        sys.exit("Program aborted: %s" % e)
    except cozmo.exceptions.NoDevicesFound as e:
        # Test server mode without active Vector
        print('test mode')
        flask_socket_helpers.run_flask(None, app)
    except cozmo.exceptions.CozmoSDKException as e:
        sys.exit("An error occurred: %s" % e)