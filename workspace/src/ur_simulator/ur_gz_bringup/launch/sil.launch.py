from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    ExecuteProcess,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.actions import SetParameter

# Define launch arguments
ARGUMENTS = [
    DeclareLaunchArgument("world", default_value="basic_world", description="GZ World"),
    DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        choices=["true", "false"],
        description="Use sim time",
    ),
    DeclareLaunchArgument(
        "spawn_model",
        default_value="true",
        choices=["true", "false"],
        description="Spawn Model",
    ),
    DeclareLaunchArgument(
        "model",
        default_value="ur5",
        description="URDF or Xacro model file",
    ),
    DeclareLaunchArgument(
        "world_sdf",
        default_value=[LaunchConfiguration("world"), ".sdf"],
        description="World file for simulation",
    ),
]


def generate_launch_description():

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    get_package_share_directory("ros_gz_sim"),
                    "launch",
                    "gz_sim.launch.py",
                ]
            )
        ),
        launch_arguments={"gz_args": LaunchConfiguration("world_sdf")}.items(),
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        arguments=[
            "-name",
            LaunchConfiguration("model"),
            "-topic",
            "robot_description",
        ],
        output="screen",
        condition=IfCondition(LaunchConfiguration("spawn_model")),
    )

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    get_package_share_directory("ur_moveit_bringup"),
                    "launch",
                    "rsp.launch.py",
                ]
            )
        ),
        launch_arguments={"model": LaunchConfiguration("model")}.items(),
    )

    controller = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    get_package_share_directory("ur_moveit_bringup"),
                    "launch",
                    "spawn_controllers.launch.py",
                ]
            )
        ),
        launch_arguments={"model": LaunchConfiguration("model")}.items(),
    )
    demo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    get_package_share_directory("ur_moveit_bringup"),
                    "launch",
                    "demo.launch.py",
                ]
            )
        ),
        launch_arguments={"model": LaunchConfiguration("model")}.items(),
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # Clock (IGN -> ROS2)
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen",
    )

    useSimTime = ExecuteProcess(
        cmd=["ros2", "param", "set", "/move_group", "use_sim_time", "true"],
        output="screen",
    )

    return LaunchDescription(ARGUMENTS + [demo, gz_sim, spawn_robot, bridge, useSimTime])
