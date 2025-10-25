#!/usr/bin/env python
# Display a runtext with double-buffering.
# TO TEST: python rgbtext.py --top="Top Line Text" --center="Center Line Text" --bottom="Bottom Line Text"
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import argparse
import time
import sys

class RunText:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--top", help="The text to scroll on the top line of the RGB LED panel", default="Top Line")
        self.parser.add_argument("--center", help="The text to scroll on the center line of the RGB LED panel", default="Center Line")
        self.parser.add_argument("--bottom", help="The text to scroll on the bottom line of the RGB LED panel", default="Bottom Line")

        # LED panel configuration
        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
        self.parser.add_argument("--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=20, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'regular-pi1', 'adafruit-hat', 'adafruit-hat-pwm'], default="adafruit-hat")
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=1, type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int)
        self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kal", default=0, type=int)
        self.parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)
        self.parser.add_argument("--led-no-drop-privs", dest="drop_privileges", help="Don't drop privileges from 'root' after initializing the hardware.", action='store_false')
        self.parser.set_defaults(drop_privileges=True)

    def usleep(self, value):
        time.sleep(value / 1000000.0)

    def process(self):
        self.args = self.parser.parse_args()

        options = RGBMatrixOptions()

        if self.args.led_gpio_mapping != None:
            options.hardware_mapping = self.args.led_gpio_mapping
        options.rows = self.args.led_rows
        options.cols = self.args.led_cols
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.row_address_type = self.args.led_row_addr_type
        options.multiplexing = self.args.led_multiplexing
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.led_brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence
        options.pixel_mapper_config = self.args.led_pixel_mapper
        options.panel_type = self.args.led_panel_type

        if self.args.led_show_refresh:
            options.show_refresh_rate = 1

        if self.args.led_slowdown_gpio != None:
            options.gpio_slowdown = self.args.led_slowdown_gpio
        if self.args.led_no_hardware_pulse:
            options.disable_hardware_pulsing = True
        if not self.args.drop_privileges:
            options.drop_privileges = False

        self.matrix = RGBMatrix(options=options)
        return True

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("./fonts/7x13.bdf")
        textColor1 = graphics.Color(255, 255, 0)
        textColor2 = graphics.Color(170, 20, 184)
        textColor3 = graphics.Color(255, 255, 255)
        pos = offscreen_canvas.width

        topLineText = self.args.top
        centerLineText = self.args.center
        bottomLineText = self.args.bottom

        while True:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor1, topLineText)
            graphics.DrawText(offscreen_canvas, font, pos, 21, textColor2, centerLineText)
            graphics.DrawText(offscreen_canvas, font, pos, 32, textColor3, bottomLineText)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width - 16

            time.sleep(0.03)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

if __name__ == "__main__":
    run_text = RunText()
    if run_text.process():
        run_text.run()
    else:
        run_text.print_help()

