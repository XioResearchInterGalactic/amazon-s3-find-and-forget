#!/usr/bin/env bash

set -e

PROFILE=$1

declare -A repos=(["dev"]="309039828602.dkr.ecr.us-east-1.amazonaws.com" 
                  ["stg"]="" 
                  ["prd"]="")
declare -A images=(["dev"]="s3f2-delstack-45732gi7anfc-ecrrepository-rfudawrs3n9d:latest" 
                   ["stg"]=""
                   ["prd"]="")

REPO=${repos[$PROFILE]}
IMAGE=${images[$PROFILE]}

aws --profile $PROFILE ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REPO
docker build -t $IMAGE -f backend/ecs_tasks/delete_files/Dockerfile .
docker tag $IMAGE $REPO/$IMAGE
docker push $REPO/$IMAGE
