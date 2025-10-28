[app]

# Podstawowe informacje
title = AcestreamVLC
package.name = acestreamvlc
package.domain = org.acestream

# Wersja
version = 1.0

# Kod źródłowy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Główny plik
source.main = main.py

# Wymagania (KLUCZOWE - bez requests/bs4!)
requirements = python3,kivy==2.3.0,urllib3,certifi

# Ikona i presplash (opcjonalne)
#icon.filename = %(source.dir)s/icon.png
#presplash.filename = %(source.dir)s/presplash.png

# Orientacja
orientation = portrait

# Uprawnienia Android (KLUCZOWE!)
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# API Android
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# Architektura
android.archs = arm64-v8a,armeabi-v7a

# Nazwa wyświetlana
android.name = Acestream VLC

# Dopuszczenie HTTP (WAŻNE dla Acestream!)
android.add_manifest_application = <uses-library android:name="org.apache.http.legacy" android:required="false" />
android.add_manifest = <uses-permission android:name="android.permission.INTERNET" />

[buildozer]

# Logi
log_level = 2
warn_on_root = 1

# Cache
android.gradle_dependencies = 
android.enable_androidx = True
