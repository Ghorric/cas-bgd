#!/bin/bash
PROJECT_ID=bgd-recommender
CLUSTER_NAME=bgd-cluster
ZONE=europe-west3-a
REGION=europe-west3
DOCKER_IMAGE=wengle/image-labels

echo "Info..."
CURRENT_PROJECT_ID="$(gcloud config get-value project -q)"
echo "Current project ID: $CURRENT_PROJECT_ID"

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -i|--init)
      INIT="true"
      shift # past argument
      # shift # past value
      ;;
    -l|--login)
      LOGIN="true"
      shift # past argument
      # shift # past value
      ;;
    -h|--halt)
      HALT="true"
      shift # past argument
      # shift # past value
      ;;
    -c|--credentials)
      CREDENTIALS="true"
      shift # past argument
      # shift # past value
      ;;
    -p|--push)
      PUSH="true"
      shift # past argument
      # shift # past value
      ;;
    *)    # unknown option
      POSITIONAL+=("$1") # save it in an array for later
      shift # past argument
      ;;
  esac
done

# Login
if [ "$LOGIN" == "true" ] ; then
  echo "Stop Cluster Nodes..."
  gcloud auth login
fi

# INIT
if [ "$INIT" == "true" ] ; then
  echo "Start init..."
  gcloud config set project $PROJECT_ID
  gcloud config get-value project
  gcloud config set compute/zone $ZONE
  gcloud config set compute/region $REGION
  gcloud container clusters create $CLUSTER_NAME --num-nodes=1
  gcloud container clusters list
fi

# Delete Cluster
if [ "$HALT" == "true" ] ; then
  echo "Delete Cluster..."
  gcloud container clusters delete $CLUSTER_NAME
fi

# Set gke kubectl credentials
if [ "$CREDENTIALS" == "true" ] ; then
  echo "Set gke kubectl credentials..."
  gcloud container clusters get-credentials $CLUSTER_NAME --region $ZONE --project $PROJECT_ID
  echo "kubectl config current-context:"
  kubectl config current-context
fi

if [ "$PUSH" == "true" ] ; then
  echo "Tag Docker Image $DOCKER_IMAGE"
  docker tag $DOCKER_IMAGE gcr.io/$PROJECT_ID/$DOCKER_IMAGE
  echo "Push Image to GKE..."
  docker push gcr.io/$PROJECT_ID/$DOCKER_IMAGE
fi
