# !/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
#  - The code is incomplete and over-simplified, as it ignores the 3rd order
#    bezier curve bit and always intepolate between off-curve points.
#    This is only correct for truetype fonts (which only use 2nd order bezier curves).
#  - Also it seems to assume the first point is always on curve; this is
#    unusual but legal.
#
# -----------------------------------------------------------------------------
'''
Show how to access glyph outline description.
'''
from freetype import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from PIL import Image
import binascii
import codecs


def toStr( num, base ):
    convertString = "0123456789ABCDEF"  # 最大转换为16进制
    if num < base:
        return convertString[ num ]
    else:
        return toStr( num // base, base ) + convertString[ num % base ]

# 渲染的字体只有黑白两色，线条较简单
def gray_char( char, index, size, font, outDir ):
    face = Face( font )
    face.set_pixel_sizes( size, size )
    flags = FT_LOAD_MONOCHROME | FT_LOAD_RENDER
    if char == '':
        return
    glyph_index = face.get_char_index( char )
    if glyph_index == 0:
        return
    face.load_char( char, flags )  # 要显示的字
    bitmap = face.glyph.bitmap
    width, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
    buff = np.empty( (size + 4, size + 4), dtype=np.ubyte )
    buff.fill( 255 )    #初始化成全黑

    for iRow in range( 0, rows ):
        for iCol in range( 0, width ):
            if bitmap.buffer[ iRow * pitch + int( iCol / 8 ) ] & (0x80 >> (iCol % 8)) != 0:
                buff[ 2 + iRow ][ 2 + iCol ] = 0

    im = Image.fromarray( buff, 'L' )
    if outDir != ' ':
        im.save( outDir + '/gray_' + str( index ) + '.bmp' )

    # plt.figure( figsize=(6, 8) )
    # plt.imshow( buff, interpolation='nearest', cmap=plt.cm.gray_r, origin='upper' )
    # plt.show( )

# 渲染的字体有灰度，线条较平滑
def normal_char( char, index, size, font, outDir ):
    # Plain
    face = Face( font )
    face.set_pixel_sizes( size, size )
    if char == '':
        return
    glyph_index = face.get_char_index( char )
    if glyph_index == 0:
        return
    face.load_char( char, FT_LOAD_RENDER )
    bitmap = face.glyph.bitmap
    width = face.glyph.bitmap.width
    rows = face.glyph.bitmap.rows
    pitch = face.glyph.bitmap.pitch
    buff = np.empty( (size + 4, size + 4), dtype=np.ubyte )
    buff.fill( 255 )  # 初始化成全黑

    for iRow in range( rows ):
        for iCol in range(width):
            buff[ 2 + iRow ][ 2 + iCol ] = 255 - bitmap.buffer[ iRow * pitch + iCol ]

    im = Image.fromarray( buff, 'L' )
    if outDir != ' ':
        im.save( outDir + '/normal_' + str( index ) + '.bmp' )

    # Z = np.array( data, dtype=np.ubyte ).reshape( size+4, size+4 )
    # plt.imshow( Z, interpolation='nearest', cmap=plt.cm.gray, origin='upper' )
    # plt.show( )


def test( char, size, font ):
    test2( char, size, font )
    face = Face( font )
    face.set_char_size( size * 64 )
    face.load_char( char )  # 要显示的字
    slot = face.glyph
    # 这个 outline 就是从字库提取出来的字体轮廓
    outline = slot.outline
    points = np.array( outline.points, dtype=[ ('x', float), ('y', float) ] )
    x, y = points[ 'x' ], points[ 'y' ]

    figure = plt.figure( figsize=(8, 10) )
    axis = figure.add_subplot( 111 )
    # axis.scatter(points['x'], points['y'], alpha=.25)
    start, end = 0, 0

    VERTS, CODES = [ ], [ ]
    # Iterate over each contour
    for i in range( len( outline.contours ) ):
        end = outline.contours[ i ]
        points = outline.points[ start:end + 1 ]
        points.append( points[ 0 ] )
        tags = outline.tags[ start:end + 1 ]
        tags.append( tags[ 0 ] )

        segments = [ [ points[ 0 ], ], ]
        for j in range( 1, len( points ) ):
            segments[ -1 ].append( points[ j ] )
            if tags[ j ] & (1 << 0) and j < (len( points ) - 1):
                segments.append( [ points[ j ], ] )
        verts = [ points[ 0 ], ]
        codes = [ Path.MOVETO, ]
        for segment in segments:
            if len( segment ) == 2:
                verts.extend( segment[ 1: ] )
                codes.extend( [ Path.LINETO ] )
            elif len( segment ) == 3:
                verts.extend( segment[ 1: ] )
                codes.extend( [ Path.CURVE3, Path.CURVE3 ] )
            else:
                verts.append( segment[ 1 ] )
                codes.append( Path.CURVE3 )
                for i in range( 1, len( segment ) - 2 ):
                    A, B = segment[ i ], segment[ i + 1 ]
                    C = ((A[ 0 ] + B[ 0 ]) / 2.0, (A[ 1 ] + B[ 1 ]) / 2.0)
                    verts.extend( [ C, B ] )
                    codes.extend( [ Path.CURVE3, Path.CURVE3 ] )
                verts.append( segment[ -1 ] )
                codes.append( Path.CURVE3 )
        VERTS.extend( verts )
        CODES.extend( codes )
        start = end + 1

    # Draw glyph lines
    path = Path( VERTS, CODES )
    glyph = patches.PathPatch( path, facecolor='.75', lw=1 )

    # Draw "control" lines
    for i, code in enumerate( CODES ):
        if code == Path.CURVE3:
            CODES[ i ] = Path.LINETO
    path = Path( VERTS, CODES )
    patch = patches.PathPatch( path, ec='.5', fill=False, ls='dashed', lw=1 )

    axis.add_patch( patch )
    axis.add_patch( glyph )
    # axis1.add_patch(char)
    # CODES = [1]
    # for i in range(1,len(points)):
    #    CODES.append(Path.LINETO)

    # path = Path(points, CODES)
    # patch = patches.PathPatch(path, ec='.5', fill=False, ls='dashed', lw=2 )
    # axis.add_patch(patch)

    axis.set_xlim( x.min( ) - 100, x.max( ) + 100 )
    plt.xticks( [ ] )  # 隐藏坐标
    axis.set_ylim( y.min( ) - 100, y.max( ) + 100 )
    plt.yticks( [ ] )
    # plt.show()


def read_file_list( inputFile, encoding ):
    results = [ ]
    fin = open( inputFile, 'r', encoding=encoding )
    for eachLiine in fin.readlines( ):
        line = eachLiine.strip( ).replace( '\ufeff', '' )
        results.append( line )
    fin.close( )
    return results
def work():
    char_list = read_file_list( './char_std_5913.txt', 'utf-8' )
    i = 0
    for char in char_list:
        gray_char( char, i, 32, './simsun.ttc', 'e:/tmp/chars' )
        normal_char( char, i, 32, './simsun.ttc', 'e:/tmp/chars_simple' )
        i += 1

def test():
    gray_char( '钙', 0, 32, './simsun.ttc', 'e:/tmp/chars' )
    normal_char( '钙', 0, 32, './simsun.ttc', 'e:/tmp/chars_simple' )

if __name__ == '__main__':
    test()
    # work()


