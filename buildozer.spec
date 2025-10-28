[app]

title = Acestream VLC
package.name = acestreamvlc
package.domain = org.acestream

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec

version = 1.0

requirements = python3,kivy==2.3.0,requests,beautifulsoup4,lxml,pyjnius,android

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
