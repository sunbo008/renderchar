#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011-2015 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Glyph colored rendering (with outline)
'''
from freetype import *

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    face = Face( './simsun.ttc' )
    face.set_pixel_sizes(64, 64)
    RGBA = [ ('R', float), ('G', float), ('B', float), ('A', float) ]

    # Outline
    flags = FT_LOAD_DEFAULT | FT_LOAD_NO_BITMAP
    face.load_char( 'C', flags )
    slot = face.glyph
    glyph = slot.get_glyph( )
    stroker = Stroker( )
    stroker.set( 64, FT_STROKER_LINECAP_ROUND, FT_STROKER_LINEJOIN_ROUND, 0 )
    glyph.stroke( stroker, True )
    blyph = glyph.to_bitmap( FT_RENDER_MODE_NORMAL, Vector( 0, 0 ), True )
    bitmap = blyph.bitmap
    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    top, left = blyph.top, blyph.left
    data = [ ]
    for i in range( rows ):
        data.extend( bitmap.buffer[ i * pitch:i * pitch + width ] )
    print(data)
    Z = np.array( data ).reshape( rows, width ) / 255.0
    print(Z)
    O = np.zeros( (rows, width), dtype=RGBA )

    O[ 'R' ] = Z
    O[ 'G' ] = 0
    O[ 'B' ] = 0
    O[ 'A' ] = 1

    # Plain
    flags = FT_LOAD_RENDER
    face.load_char( 'C', flags )
    F = np.zeros( (rows, width), dtype=RGBA )
    Z = np.zeros( (rows, width) )
    bitmap = face.glyph.bitmap
    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    top, left = face.glyph.bitmap_top, face.glyph.bitmap_left
    dy = blyph.top - face.glyph.bitmap_top
    dx = face.glyph.bitmap_left - blyph.left
    data = [ ]
    for i in range( rows ):
        data.extend( bitmap.buffer[ i * pitch:i * pitch + width ] )
    Z[ dx:dx + rows, dy:dy + width ] = np.array( data ).reshape( rows, width ) / 255.
    F[ 'R' ] = 1
    F[ 'G' ] = 1
    F[ 'B' ] = 0
    F[ 'A' ] = Z

    # Draw
    plt.figure( figsize=(12, 5) )
    plt.subplot( 121 )
    plt.title( 'Plain' )
    plt.xticks( [ ] ), plt.yticks( [ ] )
    I = F.view( dtype=float ).reshape( O.shape[ 0 ], O.shape[ 1 ], 4 )
    plt.imshow( I, interpolation='nearest', origin='upper' )

    plt.subplot( 122 )
    plt.title( 'Plain' )
    plt.xticks( [ ] ), plt.yticks( [ ] )
    I = O.view( dtype=float ).reshape( O.shape[ 0 ], O.shape[ 1 ], 4 )
    plt.imshow( I, interpolation='nearest', origin='upper' )

    plt.show( )
