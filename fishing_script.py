from PIL import Image, ImageGrab
from enum import Enum
import time, math
import keyboard

## Enum Class to store RGB values of the different possible colors
class Color(Enum):

    WHITE = (240, 250, 250)
    GREEN = (45, 235, 43)
    PURPLE = (173, 49, 207)
    ORANGE = (245, 197, 67)
    BLUE = (52, 144, 246)
    RED = (225, 50, 50)

    # Determines if the RGB value pixel matches the called Enum color (default tolerance of 50 per channel
    def is_color(self, pixel, tolerance = 50):
        return all([math.isclose(pixel[i], self.value[i], abs_tol = tolerance) for i in range(3)])

    # Converts the Color into the key using the color_map supplied by Fishing_Bot
    @classmethod
    def get_action(cls, pixel):
        res = [cls.color_map[x] for x in cls.color_map if x.is_color(pixel)]
        return res[0] if res else "space"

## Plays the Holocure Fishing simulator for theoretically forever
class Fishing_Bot:

    def __init__(self, activate_char = 'z', terminate_char = 'x'):
        Color.color_map = {Color.PURPLE : "space", Color.RED : "w", Color.GREEN : "d", Color.ORANGE : "a", Color.BLUE : "s", Color.WHITE : None} # Mapping from colors to key-presses
        self.box = (1100, 680, 1240, 820) # Square around the hit circle
        self.activate_char = activate_char # Key to activate / deactivate the bot
        self.terminate_char = terminate_char # Key to terminate the bot
        print("Welcome to the Holocure Fishing Bot, where we fish for as long as your screen doesn't minimize on accident xD.\nTo toggle, press", self.activate_char, "and to end the program, press", self.terminate_char, "\nHave fun!")
        self.activate_bot()

    # Captures the screen using self.box as the bounding box
    def capture(self):
        return ImageGrab.grab(bbox = self.box)

    def activate_bot(self):
        self.arrow_count = 0
        self.is_active = False
        while True:
            if self.is_active:
                if not self.check_fish(self.capture()):
                    self.press_and_release('space')
                if keyboard.is_pressed(self.activate_char):
                    self.check_key(self.activate_char)
                elif keyboard.is_pressed(self.terminate_char):
                    self.check_key(self.terminate_char)
                    return

            else:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN and self.check_key(event.name):
                    return

    def check_key(self, hotkey):
        if hotkey == self.activate_char:
            self.is_active = not self.is_active
            self.wait_for_release(hotkey)
            print("Bot activated!" if self.is_active else "Bot deactivated!")
            return False
        elif hotkey == self.terminate_char:
            self.wait_for_release(hotkey)
            print("Bye bye!")
            return True

    def wait_for_release(self, hotkey):
        while True:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_UP and event.name == hotkey:
                return

    # If an arrow is found, presses the button. Returns true if in the minigame, false if waiting for new game (getting fish or waiting for new fish
    def check_fish(self, im):
        # Checks for the white center of the arrow on a band across the middle of the circle
        for initial_x in range(60, 90, 2):
            if Color.WHITE.is_color(im.getpixel( (initial_x, 70) )):
                new_pixel = self.get_new_color(im, initial_x)
                self.press_and_release(Color.get_action(new_pixel))
                # im.save(f"arrow_{self.arrow_count}.jpg")
                # self.arrow_count += 1
                return True
        # Checks for the white arrow above the circle to determine if the minigame is active
        return Color.WHITE.is_color(im.getpixel((80, 15)))

    # press_and_release with a 0.1s delay in order for Holocure to register the press
    def press_and_release(self, action):
        if not action:
            return None
        keyboard.press(action)
        time.sleep(0.1)
        keyboard.release(action)

    # Moves right pixel-by-pixel until the arrow outline color is found (first non-white color) and returns that pixel
    def get_new_color(self, im, initial_x):
        x_offset = 1
        new_pixel = im.getpixel( (initial_x + x_offset, 70) )
        while Color.WHITE.is_color(new_pixel):
            x_offset += 1
            try:
                new_pixel = im.getpixel( (initial_x + x_offset, 70) )
            except:
                return (255, 255, 255)
        return new_pixel

if __name__ == "__main__":
    obj = Fishing_Bot()

