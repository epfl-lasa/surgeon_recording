#!/bin/bash
NAME=$(echo "${PWD##*/}" | tr _ -)
TAG="latest"

#create a shared volume to store the lib folder
docker volume create --driver local \
    --opt type="none" \
    --opt device="${PWD}/source/" \
    --opt o="bind" \
    "${NAME}_src_vol"

#create a shared volume to store the data folder
docker volume create --driver local \
    --opt type="none" \
    --opt device="${PWD}/data/" \
    --opt o="bind" \
    "${NAME}_data_vol"

xhost +
docker run \
    --privileged \
	--net=host \
	-it \
	--rm \
	--env DISPLAY="${DISPLAY}" \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
	--env="XAUTHORITY=$XAUTH" \
    --volume="$XAUTH:$XAUTH" \
    --volume="${NAME}_src_vol:/home/ros2/ros2_ws/src/:rw" \
    --volume="${NAME}_data_vol:/home/ros2/data/:rw" \
    --device=/dev/dri:/dev/dri \
    -v /dev/video \
	$NAME:$TAG