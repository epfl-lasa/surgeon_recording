#!/bin/bash
NAME=$(echo "${PWD##*/}" | tr _ -)
ROS2_VERSION="eloquent"

ROS_MASTER_URI="http://localhost:11311/"
ROS_IP="127.0.0.1"

#create a shared volume to store the source folder
docker volume create --driver local \
    --opt type=none \
    --opt device=$PWD/config \
    --opt o=bind \
    ${NAME}_config_vol

docker run \
    --rm \
	--net=host \
	--env="ROS_MASTER_URI=$ROS_MASTER_URI" \
	--env="ROS_IP=$ROS_IP" \
	--volume="${NAME}_config_vol:/config/:rw" \
	osrf/ros:${ROS2_VERSION}-ros1-bridge \
    "sh /config/start_bridge.sh"
