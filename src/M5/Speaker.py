import math

import pygame
import numpy


BITS = 16
SAMPLE_RATE = 44100


def init():
    global BITS
    global SAMPLE_RATE
    pygame.mixer.pre_init(SAMPLE_RATE, -BITS, 2)


def setChannelVolume(channel: int, percentage: int):
    pygame.mixer.music.set_volume(percentage / 1000)


def tone(frequency: int, duration_ms: int):
    global BITS
    global SAMPLE_RATE
    duration_s = duration_ms / 1e3

    n_samples = int(round(duration_s * SAMPLE_RATE))

    # setup our numpy array to handle 16 bit ints,
    # which is what we set our mixer to expect with "bits" up above
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2 ** (BITS - 1) - 1

    for s in range(n_samples):
        t = float(s) / SAMPLE_RATE  # time in seconds

        # grab the x-coordinate of the sine wave at a given time,
        # while constraining the sample to what our mixer is set to with "bits"
        # left
        buf[s][0] = int(
            round(0.01 * max_sample * math.sin(2 * math.pi * frequency * t))
        )
        # right
        buf[s][1] = int(
            round(0.01 * max_sample * math.sin(2 * math.pi * frequency * t))
        )

    sound = pygame.sndarray.make_sound(buf)
    sound.play()
