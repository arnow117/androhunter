
#ifndef TRACE_H_
#define TRACE_H_

#include <android/log.h>

#define ENABLE_DEBUG
#define LOG_TAG "CVE"

#ifdef ENABLE_DEBUG
#define LOGD(args...) ((void) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, ##args))
#define LOGE(args...) ((void) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, ##args))
#define logd(format, args...) LOGD("[+ %s] Line :-> %.4d :-> " format "\n", __FUNCTION__, __LINE__, ##args)
#define loge(format, args...) LOGE("[+ %s] Line :-> %.4d :-> " format "\n", __FUNCTION__, __LINE__, ##args)
#endif

#endif /* TRACE_H_ */
