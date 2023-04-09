1. устанавливаем https://github.com/google/atheris
	1. по инструкции для мака устанавливаем фаззер:

```
Building LLVM
git clone https://github.com/llvm/llvm-project.git
cd llvm-project
mkdir build
cd build
cmake -DLLVM_ENABLE_PROJECTS='clang;compiler-rt' -G "Unix Makefiles" ../llvm -DCMAKE_BUILD_TYPE=Release
make -j 10 


CLANG_BIN="$(pwd)/bin/clang" pip3 install <whatever>


```
Устанавливалось долго, потому что на маке все делаем руками.
2. Вручную на маке посыпалось все - пошел ставить в докер на рабочий проект
3. внутри докера обновил все зависимости, скачал убунту версию atheris через `pip install atheris`
4. Запустил соот-ий код для проверки эндпоинтов:
```
#!/usr/bin/env python3  
import os, django  
  
  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mymodule.settings")  
django.setup()  
  
from django.test import Client  
from hypothesis import given, strategies as st  
  
from django.urls import URLPattern, URLResolver  
  
from rerotor2.urls import urlpatterns  
from rerotor2.models import Business, User  
import atheris  
  
IGNORE_APPS = ["rest_framework"]  
  
def flatten_urls(namespace, patterns):  
    res = []  
    for url in patterns:  
        if isinstance(url, URLPattern):  
            res.append((namespace, url))  
        elif isinstance(url, URLResolver):  
            try:  
                if url.urlconf_module.app_name not in IGNORE_APPS:  
                    res += flatten_urls(url.namespace, url.url_patterns)  
            except AttributeError:  
                pass  
    return res  
  
test_urls = flatten_urls(None, urlpatterns)  
  
from model_bakery import baker  
  
business = baker.make(Business)  
password = "pass"  
User.objects.all().delete()  
user = User.objects.create_superuser("myuser", "myemail@test.com", password)  
user.business = business  
user.save()  
  
client = Client()  
client.login(username=user.username, password=password)  
  
methods = ["get", "post", "options", "head", "put", "patch"]  
  
@given(st.sampled_from(test_urls), st.sampled_from(methods), st.data())  
def TestOneInput(test_url, method, data):  
    _, pattern = test_url  
    pattern = pattern.pattern  
    if not isinstance(pattern, django.urls.resolvers.RegexPattern):  
        return  
    # if method in ["post", "put", "patch"]:  
        # payload = data.draw(st.binary(max_size=4096))    # else:    payload = {}  
    url = data.draw(st.from_regex(pattern.regex, fullmatch=True))  
    func = getattr(client, method)  
    response = func('/' + url, data=payload, follow=True)  
    print(response.status_code, method, url, pattern.regex)  
    if response.status_code not in [200, 301, 302, 404, 405]:  
        if response.status_code == 400:  
            # Our API returns 400 on invalid requests, validate response  
            status = str(response.content)  
            print(status)  
            if 'errors' in status:  
                return  
        raise RuntimeError("Badness!")  
    elif response.status_code not in [302, 404]:  
        # not suspicious, but let's see what pages it finds  
        pass  
  
import sys  
  
atheris.Setup(sys.argv, TestOneInput.hypothesis.fuzz_one_input)  
atheris.Fuzz()

```

 здесь сформированы списки урлов для проверки, создается минимальное окружение для запуска фаззера и генерируется ввод в программу с помощью property-based библиотеки hypothesis.

5. Собственно кусок вывода:
```
INFO: Using built-in libfuzzer
WARNING: Failed to find function "__sanitizer_acquire_crash_state".
WARNING: Failed to find function "__sanitizer_print_stack_trace".
WARNING: Failed to find function "__sanitizer_set_death_callback".
INFO: Running with entropic power schedule (0xFF, 100).
INFO: Seed: 2512522377
INFO: -max_len is not provided; libFuzzer will not generate inputs larger than 4096 bytes
INFO: A corpus is not provided, starting from an empty corpus
#2	INITED exec/s: 0 rss: 266Mb

Bad Request: /api/v5/integration/
[WARNING django.request | 00:01:52] Bad Request: /api/endpoint/get/
400 get /api/endpoint/get/ re.compile('^/api/endpoint/get/$')

400 head <api_endpoint_name> re.compile('^bla-bla-bla/$')
b''

 === Uncaught Python exception: ===
RuntimeError: Badness!
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/hypothesis/core.py", line 1443, in fuzz_one_input
    state.execute_once(data)
  File "/usr/local/lib/python3.8/dist-packages/hypothesis/core.py", line 817, in execute_once
    result = self.test_runner(data, run)
  File "/usr/local/lib/python3.8/dist-packages/hypothesis/executors.py", line 47, in default_new_style_executor
    return function(data)
  File "/usr/local/lib/python3.8/dist-packages/hypothesis/core.py", line 813, in run
    return test(*args, **kwargs)
  File "fuzz.py", line 69, in TestOneInput
    raise RuntimeError("Badness!")
RuntimeError: Badness!

==1188== ERROR: libFuzzer: fuzz target exited
SUMMARY: libFuzzer: fuzz target exited
MS: 5 ShuffleBytes-ChangeByte-ChangeByte-InsertByte-CopyPart-; base unit: adc83b19e793491b1c6ea0fd8b46cd9f32e592fc
0x3a,0x3a,0x5b,0x5b,
::[[
artifact_prefix='./'; Test unit written to ./crash-84b5cbd88bd7ac68305a4d0ba89d4d0896578fa6
Base64: OjpbWw==
```
