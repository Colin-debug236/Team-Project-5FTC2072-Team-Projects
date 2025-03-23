import asyncio
import logging
import time

from mini import mini_sdk as MiniSdk
from mini.apis.api_sound import StartPlayTTS, StopPlayTTS, ControlTTSResponse
from mini.apis.api_sound import StopAllAudio, StopAudioResponse
from mini.apis.api_observe import ObserveFaceRecognise
from mini.pb2.codemao_facerecognisetask_pb2 import FaceRecogniseTaskResponse
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
from test.test_connect import test_get_device_by_name 

MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
MiniSdk.set_log_level(logging.DEBUG)

authorised = 0  #variable to be used when an authorised user was detected

#--------function to connect to the robot ------------------------------------------------------------------------------------------------------

async def get_device_by_name():
    result: WiFiDevice = await MiniSdk.get_device_by_name("00418", 10) # Please enter AlphaMini-Robot ID "00418"
    print(f"test_get_device_by_name result:{result}")
    return result

#--------function to move robot clockwise 3 steps--------------------------------------------------------------------------------------------

async def test_move_robot_right():
    block: MoveRobot = MoveRobot(step=3, direction=MoveRobotDirection.RIGHTWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'

#--------function to move robot backward--------------------------------------------------------------------------------------------

async def test_move_robot_back():
    block: MoveRobot = MoveRobot(step=3, direction=MoveRobotDirection.BACKWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'

#--------function to move robot forward--------------------------------------------------------------------------------------------

async def test_move_robot_forward():
    block: MoveRobot = MoveRobot(step=3, direction=MoveRobotDirection.FORWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'

#--------function to move robot counterclockwise 3 steps-------------------------------------------------------------------------------------


async def test_move_robot_left():
    block: MoveRobot = MoveRobot(step=5, direction=MoveRobotDirection.LEFTWARD)
    (resultType, response) = await block.execute()
    print(f'test_move_robot result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_move_robot timetout'
    assert response is not None and isinstance(response, MoveRobotResponse), 'test_move_robot result unavailable'
    assert response.isSuccess, 'move_robot failed'

#--------function for bowing action after identifying an authorised person--------------------------------------------------------------------------

async def test_play_action_recognised_user():
    block: PlayAction = PlayAction(action_name='bow_avatar')
    (resultType, response) = await block.execute()
    print(f'test_play_action result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_play_action timetout'
    assert response is not None and isinstance(response, PlayActionResponse), 'test_play_action result unavailable'
    assert response.isSuccess, 'play_action failed'

#--------function for action after identifying an unauthorised person--------------------------------------------------------------------------------

async def test_play_action_unauthorised_user():
    block: PlayAction = PlayAction(action_name='face_029')
    (resultType, response) = await block.execute()
    print(f'test_play_action result:{response}')
    assert resultType == MiniApiResultType.Success, 'test_play_action timetout'
    assert response is not None and isinstance(response, PlayActionResponse), 'test_play_action result unavailable'
    assert response.isSuccess, 'play_action failed'

#--------function for text to speech welcome message at the beginning---------------------------------------------------------------------------------

async def _play_tts_welcome():
    block: StartPlayTTS = StartPlayTTS(text="Welcome to test facility. Standby for identification.")
    (resultType, response) = await block.execute()
    print(f'{response}')

#--------function for text to speech unauthorized person ---------------------------------------------------------------------------------

async def _play_tts_unauthorised():
    block: StartPlayTTS = StartPlayTTS(text="You are not authorised to enter this facility. Access denied. Please leave the premises immediately")
    (resultType, response) = await block.execute()
    print(f'{response}')

#--------function for text to speech authorised user---------------------------------------------------------------------------------

async def _play_tts_authorised():
    block: StartPlayTTS = StartPlayTTS(text="Authorised user detected. You may enter the facility.")
    (resultType, response) = await block.execute()
    print(f'{response}')

#--------function for facial recognition---------------------------------------------------------------------------------

async def facial_recognition():
    global authorised  # Use the global variable
    observer: ObserveFaceRecognise = ObserveFaceRecognise()

    def handler(msg: FaceRecogniseTaskResponse):
        global authorised  
        if msg.isSuccess and msg.faceInfos:
            if msg.faceInfos[0].name == "vidura":
                authorised = 1
                observer.stop()

    observer.set_handler(handler)
    observer.start()
    await asyncio.sleep(0)

#--------main---------------------------------------------------------------------------------


async def main():
    global authorised 
    device: WiFiDevice = await get_device_by_name()

    while device:
        await MiniSdk.connect(device)
        await MiniSdk.enter_program()
        await _play_tts_welcome()
        await facial_recognition()
	await asyncio.sleep(10) # 10s delay for facial recognition to complete

        if authorised == 1:
            await _play_tts_authorised()
            await test_play_action_recognised_user()
            await test_move_robot_right()
            await asyncio.sleep(1)
	          await test_move_robot_back()
 	          await asyncio.sleep(1)
	          await test_move_robot_forward()
      	    await asyncio.sleep(1)
            await test_move_robot_left()
        else:
            await _play_tts_unauthorised()
	          await test_move_robot_forward()
            await test_play_action_unauthorised_user()
	          await asyncio.sleep(1)
	          await test_move_robot_back()

        
        await MiniSdk.quit_program()
        await MiniSdk.release()

if __name__ == '__main__':
    asyncio.run(main())
