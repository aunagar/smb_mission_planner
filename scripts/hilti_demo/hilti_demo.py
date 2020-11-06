#!/usr/bin/env python

import smach
import smach_ros
from smb_mission_planner.grinding_mission.demo_states import *

rospy.init_node('hilti_demo')

# Build the state machine
state_machine = smach.StateMachine(outcomes=['Success', 'Failure'])
with state_machine:
    smach.StateMachine.add('MISSION_START', MissionStarter(ns="mission_start"),
                           transitions={'Completed': 'NAV_TO_WALL',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('NAV_TO_WALL', NavigateToWall(ns="nav_to_wall"),
                           transitions={'Completed': 'ARM_RECORDED_MOTION',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('ARM_RECORDED_MOTION', ArmPosesVisitor(ns="arm_recorded_motion"),
                           transitions={'PoseReached': 'HAL_DATA_COLLECTION',
                                        'NoMorePoses': 'HAL_OPTIMIZATION',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('HAL_DATA_COLLECTION', HALDataCollection(ns="hal_data_collection"),
                           transitions={'Completed': 'ARM_RECORDED_MOTION',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('HAL_OPTIMIZATION', HALOptimization(ns="hal_optimization"),
                           transitions={'Completed': 'INIT_GRINDING',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('INIT_GRINDING', InitializeGrinding(ns="init_grinding"),
                           transitions={'Completed': 'DO_GRINDING',
                                        'Aborted': 'Failure'})

    smach.StateMachine.add('DO_GRINDING', DoGrinding(ns="grinding"),
                           transitions={'Completed': 'Success',
                                        'Aborted': 'Failure'})


# Create and start the introspection server
introspection_server = smach_ros.IntrospectionServer('mission_server', state_machine, '/mission_planner')
introspection_server.start()

# Execute state machine.
outcome = state_machine.execute()
rospy.loginfo("Mission plan terminated with outcome {}.".format(outcome))

# Wait for ctrl-c to stop the application
introspection_server.stop()