[app]
title = Detector de Metais
package.name = metaldetector
package.domain = org.metal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.0,plyer
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1