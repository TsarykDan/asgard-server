[app]

# (str) Title of your application
title = Asgard

# (str) Package name
package.name = asgardmobile

# (str) Package domain (needed for android/ios packaging)
package.domain = org.asgard

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (include news paths)
source.include_exts = py,png,jpg,kv,atlas,txt

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# Додай сюди бібліотеки, якщо використовуєш KivyMD або інші (наприклад: python3,kivy,kivymd)
requirements = python3,kivy,kivymd,requests,urllib3,chardet,idna,certifi


orientation = portrait

# (str) Custom source code for Android main entry point
# Якщо твоє головне ім'я файлу ASGARD_MOBILE.py:
# (або перейменуй файл у репозиторії на main.py)

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private = True

# (list) List of inclusions using pattern matching
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
