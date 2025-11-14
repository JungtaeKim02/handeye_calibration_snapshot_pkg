#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from cv_bridge import CvBridge
import cv2
import os
from datetime import datetime

class Snapshot(Node):
    def __init__(self):
        super().__init__('_snapshot_node')

        # save folder
        self.save_dir = os.path.expanduser('~/handeye_snapshots')
        os.makedirs(self.save_dir, exist_ok=True)

        # topic sub
        self.create_subscription(Image, '/camera/color/image_raw', self.image_callback, 10)
        self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)

        self.bridge = CvBridge()
        self.latest_image = None
        self.latest_joint = None

        # key timer
        self.timer = self.create_timer(0.1, self.key_check)

        self.get_logger().info('📸snapshot Node Started — Press [s] in terminal window to capture.')

    def image_callback(self, msg):
        self.latest_image = msg

    def joint_callback(self, msg):
        self.latest_joint = msg

    def key_check(self):
        import sys, select, termios, tty
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key.lower() == 's':  # press 's' for saving
                self.save_snapshot()

    def save_snapshot(self):
        if self.latest_image is None:
            self.get_logger().warn("⚠️ there's no camera image.")
            return

        if self.latest_joint is None or len(self.latest_joint.name) == 0:
            self.get_logger().warn("⚠️ joint state is empty. try again later")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        
        
        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image, desired_encoding='bgr8')
            img_path = os.path.join(self.save_dir, f"img_{timestamp}.png")
            cv2.imwrite(img_path, cv_image)
        except Exception as e:
            self.get_logger().error(f"❌ image save failed: {e}")
            return

        
        
        try:
            joint_path = os.path.join(self.save_dir, f"joint_{timestamp}.txt")
            with open(joint_path, 'w') as f:
                f.write("name,position,velocity,effort\n")

                names = self.latest_joint.name
                pos = list(self.latest_joint.position) if len(self.latest_joint.position) > 0 else [0.0]*len(names)
                vel = list(self.latest_joint.velocity) if len(self.latest_joint.velocity) > 0 else [0.0]*len(names)
                eff = list(self.latest_joint.effort) if len(self.latest_joint.effort) > 0 else [0.0]*len(names)

                for i, name in enumerate(names):
                    p = pos[i] if i < len(pos) else 0.0
                    v = vel[i] if i < len(vel) else 0.0
                    e = eff[i] if i < len(eff) else 0.0
                    f.write(f"{name},{p},{v},{e}\n")

            self.get_logger().info(f"✅ Snapshot saved:\n  🖼 {img_path}\n  ⚙️ {joint_path}")

        except Exception as e:
            self.get_logger().error(f"❌ joint save failed : {e}")

def main(args=None):
    rclpy.init(args=args)
    node = Snapshot()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 Shutting down Snapshot Node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

