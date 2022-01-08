#!/bin/bash
#export DOCKER_IMAGE_CONFLUENT=wengle/image-labels
export RELEASE_NAME_CONFLUENT=image-labels
#export DOCKER_IMAGE_IMG=wengle/image-labels
export RELEASE_NAME_IMG=image-labels
export LABEL_KEY=app
export LABEL_VAL=img
export RELEASE_NAME=bgd-rel

BUILD="FALSE"

# Args
if [ $# -eq 0 ] ; then
    START="true"
fi

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -s|--start)
      START="true"
      shift # past argument
      # shift # past value
      ;;
    -b|--build)
      BUILD="true"
      shift # past argument
      # shift # past value
      ;;
    -d|--dry-run)
      DRY="--dry-run"
      START="true"
      shift # past argument
      # shift # past value
      ;;
    -h|--halt)
      HALT="true"
      shift # past argument
      # shift # past value
      ;;
    -r|--restart)
      HALT="true"
      START="true"
      shift # past argument
      # shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

# BUILD
pushd . && cd ./../confluent-client/ && echo 'Build confluent-client' && bash -c "./docker-start.sh $BUILD" && popd
pushd . && cd ./../image-labels/ && echo 'Build image-labels' && bash -c "./docker-start.sh $BUILD" && popd
if [ "$BUILD" == "true" ] ; then exit ; fi


# Stop
if [ "$HALT" == "true" ] ; then helm delete $RELEASE_NAME ; fi

# RUN
if [ "$START" == "true" ] ; then
  set -x;
  helm install $RELEASE_NAME ./../cas-bgd-chart/ $DRY
  #./shell/await-pod-startup.sh $(./shell/helm-pod-by-label.sh -l "$LABEL_KEY=$LABEL_VAL" -p pod/)
  set +x;
fi
