#! /bin/bash

aws s3 create bucket --bucket license-plates --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1