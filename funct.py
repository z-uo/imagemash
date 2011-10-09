#!/usr/bin/python3
#-*- coding: utf-8 -*-
#
#Copyright pops (pops451@gmail.com), 2010-2011
#
#This file is part of imagemash.
#
#    imagemash is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    imagemash is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with imagemash.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

def return_new_filename(orifn, fn, incr=1):
    """ return filename after processing
        replaces %F by the original filename
        replaces %E by the original extension
        replaces %III... by an increment """
    fn = fn.replace('%F', os.path.splitext(orifn)[0])
    fn = fn.replace('%E', os.path.splitext(orifn)[1])
    for i in reversed(range(1, 15)):
        if re.search("%I{" + str(i) + "}", fn):
            fn = fn.replace("%"+("I"*i), str(incr).zfill(i))
    return fn

def verif_images(url):
    """ verify that the url is a file and that the file is an image """
    images = []
    for i in url:
        ext = os.path.splitext(i) [1].lower()
        if (os.path.isfile(i) and
           (ext == ".png" or ext == ".gif" or
            ext == ".jpg" or ext == ".jpeg" or
            ext == ".tif" or ext == ".tiff")):
            images.append(i)
    images.sort()
    return images

if __name__=="__main__":
    fichiers = [os.path.join("test/imgs", i)
                for i in os.listdir("test/imgs")]
    print(verif_images(fichiers))
    print(return_new_filename("truc.bidule", "%Fmachin%E%IIII", 34))
