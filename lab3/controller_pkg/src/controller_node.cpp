#include <cmath>
#include <eigen3/Eigen/Dense>
#include <mav_msgs/Actuators.h>
#include <nav_msgs/Odometry.h>
#include <ros/ros.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <tf2/utils.h>
#include <trajectory_msgs/MultiDOFJointTrajectoryPoint.h>

class Controller {
  using Vec = Eigen::Vector3d;
  using Mat = Eigen::Matrix3d;

 public:
  Controller() {
    nh_.param("kx", kx_, 0.16);
    nh_.param("kv", kv_, 0.55);
    nh_.param("kr", kr_, 0.65);
    nh_.param("komega", kw_, 0.34);

    // TESSE rotors 1..4: (+,+), (-,+), (-,-), (+,-).
    constexpr double cf = 1e-3;
    constexpr double cd = 1e-5;
    const double arm = 0.3 * cf / std::sqrt(2.0);
    Eigen::Matrix4d allocation;
    allocation << cf, cf, cf, cf,
                  arm, arm, -arm, -arm,
                  -arm, arm, arm, -arm,
                  cd, -cd, cd, -cd;
    wrench_to_rotors_ = allocation.inverse();

    desired_sub_ = nh_.subscribe("desired_state", 1, &Controller::desired, this);
    current_sub_ = nh_.subscribe("current_state", 1, &Controller::current, this);
    motors_ = nh_.advertise<mav_msgs::Actuators>("rotor_speed_cmds", 1);
    timer_ = nh_.createTimer(ros::Duration(0.02), &Controller::update, this);
  }

 private:
  void desired(const trajectory_msgs::MultiDOFJointTrajectoryPoint& msg) {
    if (msg.transforms.empty() || msg.velocities.empty() || msg.accelerations.empty()) return;
    const auto& p = msg.transforms.front().translation;
    const auto& v = msg.velocities.front().linear;
    const auto& a = msg.accelerations.front().linear;
    pd_ = Vec(p.x, p.y, p.z);
    vd_ = Vec(v.x, v.y, v.z);
    ad_ = Vec(a.x, a.y, a.z);
    yaw_ = tf2::getYaw(msg.transforms.front().rotation);
    yaw_rate_ = msg.velocities.front().angular.z;
    have_desired_ = true;
  }

  void current(const nav_msgs::Odometry& msg) {
    const auto& p = msg.pose.pose.position;
    const auto& q = msg.pose.pose.orientation;
    const auto& v = msg.twist.twist.linear;
    const auto& w = msg.twist.twist.angular;
    const Eigen::Quaterniond attitude(q.w, q.x, q.y, q.z);
    if (!attitude.coeffs().allFinite() || attitude.squaredNorm() < 1e-12) return;
    p_ = Vec(p.x, p.y, p.z);
    v_ = Vec(v.x, v.y, v.z);
    R_ = attitude.normalized().toRotationMatrix();
    omega_ = R_.transpose() * Vec(w.x, w.y, w.z);
    have_current_ = true;
  }

  void update(const ros::TimerEvent&) {
    if (!have_current_ || !have_desired_) return;
    // Unit mass and identity inertia, as specified by the simulator starter.
    Vec force = -kx_ * (p_ - pd_) - kv_ * (v_ - vd_) + ad_ + 9.81 * Vec::UnitZ();
    force.z() = -2.4 * (p_.z() - pd_.z()) - 2.6 * (v_.z() - vd_.z()) + ad_.z() + 9.81;
    if (!force.allFinite() || force.squaredNorm() < 1e-12) return;

    const Vec b3 = force.normalized();
    const Vec heading(std::cos(yaw_), std::sin(yaw_), 0.0);
    const Vec lateral = b3.cross(heading);
    if (!lateral.allFinite() || lateral.squaredNorm() < 1e-12) return;
    const Vec b2 = lateral.normalized();
    Mat Rd;
    Rd.col(0) = b2.cross(b3);
    Rd.col(1) = b2;
    Rd.col(2) = b3;

    const Mat skew_error = 0.5 * (Rd.transpose() * R_ - R_.transpose() * Rd);
    const Vec attitude_error(skew_error(2, 1), skew_error(0, 2), skew_error(1, 0));
    const Vec desired_omega = R_.transpose() * (yaw_rate_ * Vec::UnitZ());
    const Vec moment = -kr_ * attitude_error - kw_ * (omega_ - desired_omega);
    Eigen::Vector4d wrench;
    wrench << force.dot(R_.col(2)), moment;
    const Eigen::Vector4d signed_squared_speed = wrench_to_rotors_ * wrench;
    if (!signed_squared_speed.allFinite()) return;

    mav_msgs::Actuators cmd;
    cmd.header.stamp = ros::Time::now();
    for (double value : {signed_squared_speed[0], signed_squared_speed[1],
                         signed_squared_speed[2], signed_squared_speed[3]}) {
      cmd.angular_velocities.push_back(std::copysign(std::sqrt(std::abs(value)), value));
    }
    motors_.publish(cmd);
  }

  ros::NodeHandle nh_;
  ros::Subscriber desired_sub_, current_sub_;
  ros::Publisher motors_;
  ros::Timer timer_;
  Vec p_, v_, omega_, pd_, vd_, ad_;
  Mat R_;
  Eigen::Matrix4d wrench_to_rotors_;
  double kx_, kv_, kr_, kw_, yaw_, yaw_rate_;
  bool have_desired_ = false, have_current_ = false;
};

int main(int argc, char** argv) {
  ros::init(argc, argv, "controller_node");
  Controller controller;
  ros::spin();
}


