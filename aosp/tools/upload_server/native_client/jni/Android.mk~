LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := curl_static
LOCAL_MODULE_FILENAME := curl
LOCAL_SRC_FILES := curl/libcurl.a
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/../../include/android
include $(PREBUILT_STATIC_LIBRARY)

include $(CLEAR_VARS)
LOCAL_SRC_FILES := \
				main.cpp\
				md5.cpp\
				aes.cpp
LOCAL_MODULE := native_client
LOCAL_C_INCLUDES := \
			$(LOCAL_PATH)/curl/include
LOCAL_STATIC_LIBRARIES := curl_static
LOCAL_LDLIBS := -llog -lz
LOCAL_CFLAGS += -DHAVE_PTHREADS \
				-DANDROID \
				-DDEBUG \
				-DECB\
				-fvisibility=hidden \
				-DHAVE_SYS_UIO_H \
				-fPIE
LOCAL_LDFLAGS += -fPIE -pie
include $(BUILD_EXECUTABLE)

include $(CLEAR_VARS)
LOCAL_SRC_FILES := \
				main.cpp\
				md5.cpp\
				aes.cpp
LOCAL_MODULE := native_client_so
LOCAL_C_INCLUDES := \
			$(LOCAL_PATH)/curl/include
LOCAL_STATIC_LIBRARIES := curl_static
LOCAL_LDLIBS := -llog -lz
LOCAL_CFLAGS += -DHAVE_PTHREADS \
				-DANDROID \

				-DECB\
				-fvisibility=hidden \
				-DHAVE_SYS_UIO_H \
				-fPIE
LOCAL_LDFLAGS += -fPIE -pie
include $(BUILD_SHARED_LIBRARY)
