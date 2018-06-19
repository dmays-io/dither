from PIL import Image
import math
import numpy
import os
import sys

import palette

DEBUGMODE = False
default_palette = 'cga_mode_4_2_hi'

def open_image(image_filename):
    return Image.open(image_filename).convert('RGB')


def pil2numpy(image):
    matrix = numpy.asarray(image, dtype=numpy.float)
    return matrix/255. 


def numpy2pil(matrix):
    image = Image.fromarray(numpy.uint8(matrix*255))
    return image


def closest_palette_color(value, palette_name, bit_depth=1):
    if DEBUGMODE:
        print '\tvalue = {}'.format(value)

    # compute distance to colors in palette
    min_dist = 10000.
    ci_use = -1
    for ci, color in enumerate(palette.palettes[palette_name]):
        pr, pg, pb = color
        vr, vg, vb = value
        dist = math.sqrt((vr-pr)*(vr-pr)+(vg-pg)*(vg-pg)+(vb-pb)*(vb-pb))

        if DEBUGMODE:
            print '\tcolor = {}'.format(color)
            print '\tdist = {}, min_dist = {}'.format(dist, min_dist)

        if dist < min_dist:
            ci_use = ci
            min_dist = dist

    if ci == -1:
        return [0.0, 0.0, 0.0]
    else:
        return palette.palettes[palette_name][ci_use]


def threshold(image_matrix, palette_name):
    new_matrix = numpy.copy(image_matrix)
    cols, rows, depth = image_matrix.shape
    for y in range(rows):
        for x in range(cols):
            old_pixel = numpy.array(new_matrix[x][y], dtype=numpy.float)
            new_pixel = numpy.array(closest_palette_color(old_pixel, palette_name),
                    dtype=numpy.float)
            new_matrix[x][y] = new_pixel
    return new_matrix


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('image_filename', help='Path to an image file to dither')
    parser.add_argument('-b', '--bit-depth', type=int, default=1, help='Number of bits in dithered image')
    palette_help_str = 'Name of palette to use. Can be one of: ' + ', '.join(palette.available_palettes)
    parser.add_argument('-p', '--palette', type=str, default=default_palette, help=palette_help_str)
    args = parser.parse_args()

    image = open_image(args.image_filename)
    image_matrix = pil2numpy(image)

    threshold_matrix = threshold(image_matrix, args.palette)
    threshold_image = numpy2pil(threshold_matrix)

    threshold_image.show()