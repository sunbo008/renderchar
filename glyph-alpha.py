#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011-2015 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Glyph bitmap monochrome rendering
'''
from freetype import *

if __name__ == '__main__':
    import numpy
    import matplotlib.pyplot as plt

    face = Face('./simsun.ttc')
    face.set_pixel_sizes( 64, 64 )
    face.load_char('a', FT_LOAD_RENDER )
    bitmap = face.glyph.bitmap
    width  = face.glyph.bitmap.width
    rows   = face.glyph.bitmap.rows
    pitch  = face.glyph.bitmap.pitch

    data = []
    for i in range(rows):
        data.insert(0, bitmap.buffer[i*pitch:i*pitch+width])
    Z = numpy.array(data,dtype=numpy.ubyte).reshape(rows, width)
    plt.imshow(Z, interpolation='nearest', cmap=plt.cm.gray, origin='lower')
    plt.show()
