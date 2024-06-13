
import rospy
from duckietown_msgs.msg import Twist2DStamped, FSMState, WheelEncoderStamped
from sensor_msgs.msg import Range

class SquareDriver:
    def _init_(self):
        # Initialize ROS node and class variables
        rospy.init_node('square_driver_node', anonymous=True)
        self.cmd_msg = Twist2DStamped()
        self.tick_count = 0
        self.front_distance = 0

        # Set up publishers and subscribers
        self.pub = rospy.Publisher('/duckiebot/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/duckiebot/fsm_node/mode', FSMState, self.on_fsm_state_change, queue_size=1)
        rospy.Subscriber('/duckiebot/left_wheel_encoder_node/tick', WheelEncoderStamped, self.on_encoder_update, queue_size=1)
        rospy.Subscriber('/duckiebot/front_center_tof_driver_node/range', Range, self.on_range_update, queue_size=1)

    def on_fsm_state_change(self, msg):
        rospy.loginfo("FSM State: %s", msg.state)
        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop()
        elif msg.state == "LANE_FOLLOWING":
            rospy.sleep(1)
            self.execute_square_drive()

    def on_encoder_update(self, msg):
        self.tick_count = msg.data

    def on_range_update(self, msg):
        self.front_distance = msg.range

    def drive_distance(self, distance, speed):
        initial_ticks = self.tick_count
        while abs(self.tick_count - initial_ticks) < (distance * 100):
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = speed
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Driving forward")
        self.stop()

    def rotate_angle(self, angle, speed):
        initial_ticks = self.tick_count
        while abs(self.tick_count - initial_ticks) < (angle * 100):
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = speed
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Rotating")
        self.stop()

    def stop(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    def execute_square_drive(self):
        for _ in range(4):
            self.drive_forward()
            self.turn_in_place()
        self.stop()

    def drive_forward(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.5
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)
        rospy.loginfo("Driving forward")
        rospy.sleep(1)

    def turn_in_place(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 1.0
        self.pub.publish(self.cmd_msg)
        rospy.loginfo("Turning")
        rospy.sleep(0.7)
        self.stop()

    def run(self):
        rospy.spin()

if _name_ == '_main_':
    try:
        driver = SquareDriver()
        driver.run()
    except rospy.ROSInterruptException:
        pass
