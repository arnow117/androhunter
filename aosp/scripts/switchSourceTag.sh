#!/bin/bash

echo "now swtich AOSP to $1"
#repo init -u https://aosp.tuna.tsinghua.edu.cn/platform/manifest -b $1
repo init -u https://android.googlesource.com/platform/manifest -b $1
repo sync
repo forall -c git checkout $1
