FROM ros2-setup:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV USER ros2
ENV HOME /home/${USER}

ENV QT_X11_NO_MITSHM 1

RUN sudo apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE

RUN sudo add-apt-repository "deb http://realsense-hw-public.s3.amazonaws.com/Debian/apt-repo bionic main" -u

RUN sudo apt update && sudo apt install -y \
  	python3-pip \
  	librealsense2-dkms \
  	librealsense2-utils \
  	librealsense2-dev \
	&& sudo rm -rf /var/lib/apt/lists/*

RUN sudo pip3 install \
	pathlib \
	numpy \
	pandas \
	opencv-python \
	pyrealsense2

WORKDIR ${HOME}/ros2_ws/src
COPY --chown=${USER} ./source/ .
WORKDIR ${HOME}/ros2_ws/
RUN /bin/bash -c "source /opt/ros/$ROS_DISTRO/setup.bash; colcon build --symlink-install"

# change to the home root
WORKDIR ${HOME}

# Clean image
RUN sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]