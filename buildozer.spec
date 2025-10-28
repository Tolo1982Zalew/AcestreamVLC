[app]
title = AcestreamVLC
package.name = acestreamvlc
package.domain = org.acestream
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3==3.9.0,hostpython3==3.9.0,kivy==2.2.1,android
source.main = main.py
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Android config
android.api = 33
android.minapi = 21
android.ndk = 25c
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# Package
android.name = AcestreamVLC
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @android:style/Theme.NoTitleBar

# Build
p4a.bootstrap = sdl2
p4a.branch = master
android.gradle_dependencies = 

# Skip unnecessary updates
android.skip_update = False
android.ant_path = 

[buildozer]
log_level = 2
warn_on_root = 1
