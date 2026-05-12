# -*- coding: utf-8 -*-

"""
DETECTOR DE METAIS — SUPER GAIN
PYDROID 3 + ANDROID

NOVA VERSÃO:
- SUPER GANHO
- resposta ultra rápida
- retorno rápido do gauge
- filtro inteligente
- suavização dinâmica
- detecção amplificada
- vibração proporcional
- interface otimizada
"""

# =========================================================
# CONFIG
# =========================================================

import os
os.environ["KIVY_NO_ENV_CONFIG"] = "1"

from kivy.config import Config

Config.set("graphics", "resizable", "0")
Config.set("graphics", "multisamples", "0")

# =========================================================
# IMPORTS
# =========================================================

import math
import threading

# =========================================================
# SENSOR
# =========================================================

SENSOR_BACKEND = "mock"

_sensor_lock = threading.Lock()
_sensor_xyz = [0.0, 0.0, 0.0]

# =========================================================
# PLYER
# =========================================================

try:

    from plyer import compass as _compass

    _compass.enable()

    def _read_sensor():

        try:

            field = _compass.field

            if field and len(field) >= 3:

                return (
                    float(field[0]),
                    float(field[1]),
                    float(field[2]),
                )

        except:
            pass

        return None

    def sensor_start():

        try:
            _compass.enable()
        except:
            pass

    def sensor_stop():

        try:
            _compass.disable()
        except:
            pass

    SENSOR_BACKEND = "plyer"

except:
    _read_sensor = None

# =========================================================
# JNIUS
# =========================================================

if SENSOR_BACKEND == "mock":

    try:

        from jnius import autoclass
        from jnius import PythonJavaClass
        from jnius import java_method

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Context = autoclass(
            "android.content.Context"
        )

        SensorManager = autoclass(
            "android.hardware.SensorManager"
        )

        Sensor = autoclass(
            "android.hardware.Sensor"
        )

        class MagneticListener(PythonJavaClass):

            __javainterfaces__ = [
                "android/hardware/SensorEventListener"
            ]

            __javacontext__ = "app"

            @java_method("(Landroid/hardware/SensorEvent;)V")
            def onSensorChanged(self, event):

                with _sensor_lock:

                    _sensor_xyz[0] = float(event.values[0])
                    _sensor_xyz[1] = float(event.values[1])
                    _sensor_xyz[2] = float(event.values[2])

            @java_method("(Landroid/hardware/Sensor;I)V")
            def onAccuracyChanged(self, sensor, accuracy):
                pass

        activity = PythonActivity.mActivity

        sensor_mgr = activity.getSystemService(
            Context.SENSOR_SERVICE
        )

        magnetic_sensor = sensor_mgr.getDefaultSensor(
            Sensor.TYPE_MAGNETIC_FIELD
        )

        listener = MagneticListener()

        def _read_sensor():

            with _sensor_lock:

                return (
                    _sensor_xyz[0],
                    _sensor_xyz[1],
                    _sensor_xyz[2]
                )

        def sensor_start():

            sensor_mgr.registerListener(
                listener,
                magnetic_sensor,
                SensorManager.SENSOR_DELAY_FASTEST
            )

        def sensor_stop():

            sensor_mgr.unregisterListener(listener)

        SENSOR_BACKEND = "jnius"

    except:
        _read_sensor = None

# =========================================================
# MOCK
# =========================================================

if SENSOR_BACKEND == "mock":

    _mock_t = 0

    def _read_sensor():

        global _mock_t

        _mock_t += 0.03

        base = 45

        pulse = 0

        if int(_mock_t * 2) % 10 < 2:

            pulse = (
                math.sin(_mock_t * 10)
                * 90
            )

        x = base + pulse
        y = base * 0.6 + pulse * 0.5
        z = base * 0.3 + pulse * 0.4

        return x, y, z

    def sensor_start():
        pass

    def sensor_stop():
        pass

# =========================================================
# VIBRAÇÃO
# =========================================================

_vibration_enabled = True

def do_vibrate(ms=80):

    if not _vibration_enabled:
        return

    try:

        from plyer import vibrator

        vibrator.vibrate(ms)

    except:
        pass

# =========================================================
# KIVY
# =========================================================

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from kivy.graphics import (
    Color,
    Line,
    Ellipse,
)

from kivy.graphics import RoundedRectangle

from kivy.properties import NumericProperty

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.scrollview import ScrollView

# =========================================================
# GAUGE
# =========================================================

class Gauge(Widget):

    value = NumericProperty(0)

    display_value = NumericProperty(0)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        Clock.schedule_interval(
            self.animate,
            1 / 60
        )

        self.bind(
            size=self.redraw,
            pos=self.redraw
        )

    def animate(self, dt):

        # subida rápida
        if self.display_value < self.value:

            speed = 0.30

        # descida ainda mais rápida
        else:

            speed = 0.45

        self.display_value += (
            self.value - self.display_value
        ) * speed

        self.redraw()

    def redraw(self, *args):

        self.canvas.clear()

        w, h = self.size

        if w < 10:
            return

        cx = self.x + w / 2
        cy = self.y + h * 0.18

        radius = min(w * 0.38, h * 0.75)

        ratio = min(
            self.display_value / 100,
            1
        )

        angle = math.radians(
            210 - 240 * ratio
        )

        with self.canvas:

            Color(0.10,0.10,0.15,1)

            Line(
                ellipse=(
                    cx-radius,
                    cy-radius,
                    radius*2,
                    radius*2,
                    -30,
                    210
                ),
                width=18
            )

            segs = int(ratio * 90)

            for i in range(segs):

                t = i / 90

                if t < 0.5:

                    r = t * 2
                    g = 1
                    b = 0

                else:

                    r = 1
                    g = 1 - (t - 0.5) * 2
                    b = 0

                Color(r,g,b,1)

                a0 = -30 + 240 * (i / 90)

                Line(
                    ellipse=(
                        cx-radius,
                        cy-radius,
                        radius*2,
                        radius*2,
                        a0,
                        a0 + 3
                    ),
                    width=18
                )

            Color(1,0.5,0,1)

            length = radius - 35

            Line(
                points=[
                    cx,
                    cy,
                    cx + length * math.cos(angle),
                    cy + length * math.sin(angle)
                ],
                width=5
            )

            Color(1,1,1,1)

            Ellipse(
                pos=(cx-10, cy-10),
                size=(20,20)
            )

# =========================================================
# BOTÃO
# =========================================================

class BigButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.font_size = "18sp"

        self.bold = True

        self.background_color = (0,0,0,0)

        self.size_hint_y = None

        self.height = 72

        self.bind(
            pos=self.draw,
            size=self.draw
        )

    def draw(self, *args):

        self.canvas.before.clear()

        with self.canvas.before:

            Color(0.12,0.14,0.22,1)

            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[18]
            )

# =========================================================
# APP
# =========================================================

class MetalDetectorApp(App):

    def build(self):

        Window.clearcolor = (0.04,0.04,0.07,1)

        self.threshold = 12
        self.gain = 2.0
        self.super_gain = 1.0

        self.baseline = None

        self.history = []

        self.cooldown = 0

        self.scanning = False

        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            spacing=16,
            padding=16,
            size_hint_y=None
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        # =================================================
        # TÍTULO
        # =================================================

        title = Label(
            text="DETECTOR SUPER GAIN",
            font_size="24sp",
            bold=True,
            color=[0,1,0.7,1],
            size_hint_y=None,
            height=50
        )

        root.add_widget(title)

        # =================================================
        # STATUS
        # =================================================

        self.status = Label(
            text=f"PARADO [{SENSOR_BACKEND}]",
            font_size="15sp",
            color=[1,0.7,0,1],
            size_hint_y=None,
            height=35
        )

        root.add_widget(self.status)

        # =================================================
        # GAUGE
        # =================================================

        self.gauge = Gauge(
            size_hint_y=None,
            height=320
        )

        root.add_widget(self.gauge)

        # =================================================
        # VALOR
        # =================================================

        self.lbl_value = Label(
            text="0.0",
            font_size="44sp",
            bold=True,
            color=[0,1,0.7,1],
            size_hint_y=None,
            height=70
        )

        root.add_widget(self.lbl_value)

        # =================================================
        # ALERTA
        # =================================================

        self.alert = Label(
            text="INICIAR",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=50
        )

        root.add_widget(self.alert)

        # =================================================
        # SENSIBILIDADE
        # =================================================

        root.add_widget(
            Label(
                text="SENSIBILIDADE",
                size_hint_y=None,
                height=25
            )
        )

        self.sens_label = Label(
            text="12",
            size_hint_y=None,
            height=20
        )

        root.add_widget(self.sens_label)

        sens = Slider(
            min=2,
            max=40,
            value=self.threshold,
            size_hint_y=None,
            height=50
        )

        sens.bind(
            value=self.on_sens
        )

        root.add_widget(sens)

        # =================================================
        # GANHO
        # =================================================

        root.add_widget(
            Label(
                text="GANHO",
                size_hint_y=None,
                height=25
            )
        )

        self.gain_label = Label(
            text="2.0",
            size_hint_y=None,
            height=20
        )

        root.add_widget(self.gain_label)

        gain = Slider(
            min=0.5,
            max=8,
            value=self.gain,
            size_hint_y=None,
            height=50
        )

        gain.bind(
            value=self.on_gain
        )

        root.add_widget(gain)

        # =================================================
        # SUPER GAIN
        # =================================================

        root.add_widget(
            Label(
                text="SUPER GAIN",
                size_hint_y=None,
                height=25
            )
        )

        self.super_label = Label(
            text="1.0",
            size_hint_y=None,
            height=20
        )

        root.add_widget(self.super_label)

        super_gain = Slider(
            min=1,
            max=25,
            value=1,
            size_hint_y=None,
            height=50
        )

        super_gain.bind(
            value=self.on_super_gain
        )

        root.add_widget(super_gain)

        # =================================================
        # VIBRAÇÃO
        # =================================================

        row = BoxLayout(
            size_hint_y=None,
            height=60
        )

        row.add_widget(
            Label(
                text="VIBRAÇÃO"
            )
        )

        sw = Switch(active=True)

        sw.bind(
            active=self.on_vibration
        )

        row.add_widget(sw)

        root.add_widget(row)

        # =================================================
        # BOTÕES
        # =================================================

        row2 = BoxLayout(
            spacing=12,
            size_hint_y=None,
            height=80
        )

        self.btn = BigButton(
            text="INICIAR"
        )

        self.btn.bind(
            on_press=lambda x: self.toggle()
        )

        row2.add_widget(self.btn)

        calib = BigButton(
            text="CALIBRAR"
        )

        calib.bind(
            on_press=lambda x: self.calibrate()
        )

        row2.add_widget(calib)

        root.add_widget(row2)

        # =================================================
        # DEBUG
        # =================================================

        self.debug = Label(
            text="",
            font_size="11sp",
            color=[0.5,0.5,0.6,1],
            size_hint_y=None,
            height=40
        )

        root.add_widget(self.debug)

        scroll.add_widget(root)

        return scroll

    # =====================================================
    # CALLBACKS
    # =====================================================

    def on_sens(self, instance, value):

        self.threshold = float(value)

        self.sens_label.text = f"{value:.1f}"

    def on_gain(self, instance, value):

        self.gain = float(value)

        self.gain_label.text = f"{value:.2f}"

    def on_super_gain(self, instance, value):

        self.super_gain = float(value)

        self.super_label.text = f"{value:.1f}"

    def on_vibration(self, instance, value):

        global _vibration_enabled

        _vibration_enabled = value

    # =====================================================
    # CALIBRAR
    # =====================================================

    def calibrate(self):

        if len(self.history) > 0:

            self.baseline = (
                sum(self.history)
                / len(self.history)
            )

            self.alert.text = "CALIBRADO"

            do_vibrate(120)

    # =====================================================
    # START / STOP
    # =====================================================

    def toggle(self):

        if not self.scanning:
            self.start()
        else:
            self.stop()

    def start(self):

        self.scanning = True

        self.btn.text = "PARAR"

        self.status.text = f"ATIVO [{SENSOR_BACKEND}]"

        self.status.color = [0,1,0.7,1]

        sensor_start()

        self.loop = Clock.schedule_interval(
            self.tick,
            1 / 30
        )

        do_vibrate(80)

    def stop(self):

        self.scanning = False

        self.btn.text = "INICIAR"

        self.status.text = "PARADO"

        self.status.color = [1,0.7,0,1]

        if hasattr(self, "loop"):
            self.loop.cancel()

        sensor_stop()

        self.alert.text = "PARADO"

    # =====================================================
    # LOOP
    # =====================================================

    def tick(self, dt):

        raw = _read_sensor()

        if raw is None:
            return

        x, y, z = raw

        self.debug.text = (
            f"X:{x:.1f} "
            f"Y:{y:.1f} "
            f"Z:{z:.1f}"
        )

        mag = math.sqrt(
            x*x + y*y + z*z
        )

        # =================================================
        # FILTRO
        # =================================================

        self.history.append(mag)

        if len(self.history) > 6:
            self.history.pop(0)

        smooth = (
            sum(self.history)
            / len(self.history)
        )

        # =================================================
        # BASELINE
        # =================================================

        if self.baseline is None:
            self.baseline = smooth

        self.baseline = (
            self.baseline * 0.985
            + smooth * 0.015
        )

        # =================================================
        # DELTA
        # =================================================

        delta = smooth - self.baseline

        fast = 0

        if len(self.history) >= 2:

            fast = (
                self.history[-1]
                - self.history[-2]
            )

        # =================================================
        # SUPER DETECÇÃO
        # =================================================

        signal = abs(

            (
                delta * self.gain
            )

            +

            (
                fast
                * 5
                * self.super_gain
            )

        )

        # compressão dinâmica
        signal = math.sqrt(signal) * 8

        # limitador
        signal = min(signal, 100)

        # =================================================
        # DISPLAY
        # =================================================

        self.gauge.value = signal

        self.lbl_value.text = f"{signal:.1f}"

        # =================================================
        # ALERTA
        # =================================================

        if signal >= self.threshold:

            ratio = min(
                signal / (self.threshold * 2),
                1
            )

            if ratio > 0.7:

                self.alert.text = "METAL DETECTADO"

                self.alert.color = [1,0.2,0.2,1]

            elif ratio > 0.4:

                self.alert.text = "CAMPO ALTERADO"

                self.alert.color = [1,0.8,0.2,1]

            else:

                self.alert.text = "SINAL FRACO"

                self.alert.color = [0.4,1,0.4,1]

            if self.cooldown <= 0:

                do_vibrate(
                    int(80 + ratio * 150)
                )

                self.cooldown = 6

            else:

                self.cooldown -= 1

        else:

            self.alert.text = "CAMPO NORMAL"

            self.alert.color = [0.7,0.7,0.8,1]

    # =====================================================
    # STOP
    # =====================================================

    def on_stop(self):

        try:
            sensor_stop()
        except:
            pass

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    MetalDetectorApp().run()