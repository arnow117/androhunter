#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/system_properties.h>
#include <jni.h>
#include <android/log.h>

// common macro
#ifdef RELEASE
	#define APPLICATION_CLASSPATH "com/qihoo/permmgr/RootMan"
	#define JNI_FUNCTION(FUNCNAME) Java_com_qihoo_permmgr_RootMan_ ## FUNCNAME
#else
	#define APPLICATION_CLASSPATH "com/example/test/Global"
	#define JNI_FUNCTION(FUNCNAME) Java_com_example_test_Global_ ## FUNCNAME
#endif

#ifdef DEBUG
	#ifdef STANDALONE
		#define LOG_DKOM(format, arg...)  if (printf) printf(format, ##arg)
		#define LOG(format, arg...)  if (printf) printf(format, ##arg)
		#define LOGD(format, arg...)  if (printf) printf(format, ##arg)
	#else
		#define LOG(...)  __android_log_print(ANDROID_LOG_INFO, "JMAIN",__VA_ARGS__)
		#define LOG_DKOM(...)  __android_log_print(ANDROID_LOG_INFO, "JMAIN",__VA_ARGS__)
		#define LOGD(...)  __android_log_print(ANDROID_LOG_INFO, "JMAIN",__VA_ARGS__)
	#endif
#else
	#define LOG(format, arg...)
	#define LOG_DKOM(format, arg...)
	#ifdef STANDALONE
		#define LOGD(format, arg...)  if (printf) printf(format, ##arg)
	#else
		#define LOGD(...)  __android_log_print(ANDROID_LOG_INFO, "JMAIN",__VA_ARGS__)
	#endif
#endif

#define DEVICE_EXIST			0
#define DEVICE_NOT_EXIST		1

// for CVE-2014-7911
#define CVE_2014_7911_EXIST		0
#define CVE_2014_7911_PATCHED		1
#define CVE_2014_7911_OTHER_PROBLEM	2
#define CVE_2014_7911_OPEN_LIBDVM	3
#define CVE_2014_7911_NO_JVMFUNC	4
#define CVE_2014_7911_JVM_CREATEFAIL	5

// for FUTex
#define FUTEX_EXIST			0
#define FUTEX_NOT_EXIST			1

// for MSM-isp
#define	MSM_isp_EXIST			0
#define MSM_isp_NO_DEVICE		1
#define MSM_isp_CANT_OPEN		2
#define MSM_isp_CANT_MMAP		3
#define MSM_isp_IOCTL_FAIL1		4
#define MSM_isp_IOCTL_FAIL2		5
#define	MSM_isp_NOT_EXIST		6

// for CVE-2015-3636
#define CVE_2015_3636_CAN_TRY		0
#define CVE_2015_3636_EACCES		1
#define CVE_2015_3636_ENFILE		2
#define CVE_2015_3636_EPROTONOSUPPORT	3
#define CVE_2015_3636_ERROR		4

// for CVE-2014-4322
#define QSEECOM_DEV			"/dev/qseecom"
#define QSEECOM_EXIST			0
#define QSEECOM_DEVICE			1
#define QSEECOM_NO_ION			2
#define QSEECOM_ION_ALLOC		3
#define QSEECOM_ION_MAP			4
#define QSEECOM_IOCTL			5
#define QSEECOM_MMAP1			6
#define QSEECOM_MMAP2			7
#define QSEECOM_FIXED			8

// for CVE-2013-6123
#define CVE_2013_6123_DEV		"/dev/video100"
#define CVE_2013_6123_EXIST		0
#define CVE_2013_6123_NOT_ADAPTED	1
#define CVE_2013_6123_NO_DEVICE		2
#define CVE_2013_6123_NOT_EXIST		3

// for WCNSS_WLAN
#define WCNSS_WLAN_DEV			"/dev/wcnss_wlan"
#define WCNSS_WLAN_EXIST		0
#define WCNSS_WLAN_NO_DEVICE		1
#define WCNSS_WLAN_NO_PERM		2
#define WCNSS_WLAN_NOT_USABLE		3

// for PUT_USER
#define PUT_USER_EXIST			0
#define PUT_USER_NOT_EXIST		1

// for OABI 
#define OABI_EXIST			0
#define OABI_NOT_EXIST			1
#define OABI_SYSTEM_PROP_ERROR		2

// for CVE-2015-4421
#define TC_NS_CLIENT			"/dev/tc_ns_client"
#define CVE_2015_4421_EXIST		0
#define CVE_2015_4421_NO_DEVICE		1
#define CVE_2015_4421_SES_OPEN1		2
#define CVE_2015_4421_SES_OPEN2		3
#define CVE_2015_4421_SEND_CMD		4

// for MSM-ois
#define	MSM_ois_EXIST			0
#define MSM_ois_NO_DEVICE		1
#define MSM_ois_CANT_OPEN		2
#define MSM_ois_CANT_MMAP		3
#define MSM_ois_IOCTL_FAIL1		4
#define MSM_ois_IOCTL_FAIL2		5
#define	MSM_ois_NOT_EXIST		6

//for keen_mtk
#ifdef KEEN_MTK
	#define EXP_EXIST 			0	
	#define EXP_NOT_EXIST			1
#endif
//for gralloc_pwn
#ifdef GRALLOC_PWN
	#define EXP_EXIST			0
	#define EXP_NOT_EXIST			1
#endif
//for upload_client
#ifdef UPLOAD_CLIENT
	#define ALL_RIGHT			0
	#define NOT_ROOT			1
	#define NET_ERROR			2
	#define SESSION_ERROR			3
	#define COOKIE_ERROR			4
	#define ENCRYPT_ERROR			5
	#define DECRYPT_ERROR			6
	#define TARGET_ERROR			7
	#define COUNT_ERROR			8	
	#define UNDEFINE_ERROR			9
#endif
