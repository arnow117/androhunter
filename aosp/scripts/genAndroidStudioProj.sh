#!/bin/bash

cd $ANDROID_BUILD_TOP/development/tools/idegen/ && mm
cd $ANDROID_BUILD_TOP
java -cp $OUT/../../../host/linux-x86/framework/idegen.jar Main
