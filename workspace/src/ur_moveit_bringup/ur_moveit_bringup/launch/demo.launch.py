from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare

# Define launch arguments
ARGUMENTS = [
    DeclareLaunchArgument(
        "model",
        default_value="ur5",
        description="URDF or Xacro model file",
    ),
    DeclareLaunchArgument(
        "model_package",
        default_value=[LaunchConfiguration("model"), "_moveit_config"],
        description="Moveit Package for robotic arm",
    ),
]


def generate_launch_description():
    demo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare(LaunchConfiguration("model_package")),
                    "launch",
                    "demo.launch.py",
                ]
            )
        )
    )
    return LaunchDescription(ARGUMENTS + [demo_launch])
