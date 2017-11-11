# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy

try:  # Pillow
    from PIL import Image
except:
    print 'Error: Pillow has not been installed.'
    sys.exit(0)

try:  # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print 'Error: PyOpenGL has not been installed.'
    sys.exit(0)

# Globals

windowWidth = 600  # window dimensions
windowHeight = 800

factor = 1  # factor by which luminance is scaled
contrast = 1

h = [0] * 256
newh = [0] * 256

# Image directory and path to image file

imgDir = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join(imgDir, imgFilename)

# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()
root.withdraw()


# Read and modify an image.

def buildImage():
    # Read image and convert to YCbCr

    print imgPath
    src = Image.open(imgPath).convert('YCbCr')
    srcPixels = src.load()

    width = src.size[0]
    height = src.size[1]

    # Set up a new, blank image of the same size

    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()

    for i in range(width):
        for j in range(height):

            # read source pixel
            y, cb, cr = srcPixels[i, j]

            # convolution filter  set up


            # ---- MODIFY PIXEL ----
            # brightness
            y = int(contrast * y + 10 * factor)
            # write destination pixel (while flipping the image in the vertical direction)
            if y < 0:
                y = 0
            elif y > 255:
                y = 255
            dstPixels[i, height - j - 1] = (y, cb, cr)
    # Done

    return dst.convert('RGB')


# Set up the display and draw the current image

def display():
    # Clear window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebuild the image

    img = currentImg
    width = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image
    # what does this mean?
    baseX = (windowWidth - width) / 2
    baseY = (windowHeight - height) / 2

    glWindowPos2i(baseX, baseY)

    # Get pixels and draw
    imageData = numpy.array(list(img.getdata()), numpy.uint8)

    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    glutSwapBuffers()


# Convolution Filter

def convolutionFilter():
    global currentImg, filterData
    img = currentImg.convert('YCbCr')
    srcPixels = img.load()
    width = img.size[0]
    height = img.size[1]

    # Set up a new, blank image of the same size
    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()

    # Set up pixels for convolution
    convolvePix = numpy.zeros([width, height])

    # this loop is just to set up initial values
    for i in range(width):
        for j in range(height):
            # read source pixels
            y, cb, cr = srcPixels[i, j]
            convolvePix[i, j] = y

    # build destination img from src img
    for i in range(width):
        for j in range(height):
            # read source pixels
            y, cb, cr = srcPixels[i, j]

            # ---- MODIFY PIXEL ----
            # convolution
            conv = 0
            yRadius = (filterData.shape[0] - 1) / 2
            xRadius = (filterData.shape[1] - 1) / 2
            for k in range(0, filterData.shape[1]):
                for p in range(0, filterData.shape[0]):
                    if ((i + k - xRadius) >= 0) and ((j + p - yRadius) < height) and ((i + k - xRadius) < width) and (
                        (j + p - yRadius) >= 0):
                        conv = conv + convolvePix[i + k - xRadius, j + p - yRadius] * filterData[k, p]


            if (conv < 0):
                conv = 0
            elif (conv > 255):
                conv = 255
            else:
                if (conv % 1) > 0.5:
                    conv = int(conv) + 1
                else:
                    conv = int(conv)
                    convolvePix[i, j] = conv

            #write destination pixel (while flipping image in vertical direction)
            dstPixels[i, height - j - 1] = convolvePix[i, j], cb, cr

            currentImg = dst.convert('RGB')
            glutPostRedisplay()
    print 'Done conv'

# Histogram eq

def histogramEq():
    global currentImg, h, newh
    img = currentImg.convert('YCbCr')
    srcPixels = img.load()

    width = img.size[0]
    height = img.size[1]

    # Set up a new, blank image of the same size

    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()
    # Build destination image from source image
    for i in range(width):
        for j in range(height):
            y, cb, cr = srcPixels[i, j]
            h[y] += 1
    print h
    for i in range(width):
        for j in range(height):
            hsum = 0
            # read source pixel

            y, cb, cr = srcPixels[i, j]
            for x in range(0, y):
                hsum += h[x]
            # ---- MODIFY PIXEL ----
            # hist equalization
            y = int((256 * hsum / (width * height)) - 1)
            newh[y] += 1
            # write destination pixel (while flipping the image in the vertical direction)
            dstPixels[i, j] = (y, cb, cr)
    print newh
    h = [0] * 256
    newh = [0] * 256
    # Done

    currentImg = dst.convert('RGB')
    glutPostRedisplay()


# Loading Filter

def loadFilter():

    filterDir = 'filters'

    filterPath = os.path.join(filterDir, filterFilename)
    print filterPath

    filterFileName = tkFileDialog.askopenfilename(initialdir=filterDir)
    with open(filterName, 'r') as data:
        content = data.readlines()

    [xdim, ydim] = content[0].split()
    [xdim, ydim] = [int(xdim), int(ydim)]
    scaleFactor = float(content[1].split()[0])
    filterData = numpy.zeros([ydim, xdim])

    for i in range(0, ydim):
        for j in range(0, xdim):
            filterData[i, j] = scaleFactor * float(content[i + 2].split()[j])

    print filterFilename, filterData
    return filterData


# Handle keyboard input

def keyboard(key, x, y):
    if key == '\033':  # ESC = exit
        sys.exit(0)

    elif key == 'h':
        histogramEq()

    elif key == 'l':
        path = tkFileDialog.askopenfilename(initialdir=imgDir)
        if path:
            loadImage(path)

    elif key == 's':
        outputPath = tkFileDialog.asksaveasfilename(initialdir='.')
        if outputPath:
            saveImage(outputPath)
    elif key == 'f':
        global filterData
        filterData = loadFilter()
    elif key == 'a':
        convolutionFilter()
    else:
        print 'key =', key  # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

    glutPostRedisplay()


# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage(path):
    global imgPath, currentImg
    imgPath = path
    currentImg = buildImage()
    glutPostRedisplay()


def saveImage(path):
    buildImage().save(path)


# Handle window reshape

def reshape(newWidth, newHeight):
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight

    glutPostRedisplay()


# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactor = 0
initFac = 1


# Handle mouse click/unclick

def mouse(btn, state, x, y):
    global button, initX, initY, initFactor

    if state == GLUT_DOWN:

        button = btn
        initX = x
        initY = y
        initFactor = factor

    elif state == GLUT_UP:

        button = None


# Handle mouse motion

def motion(x, y):
    diffX = x - initX
    diffY = y - initY

    global factor, contrast, currentImg

    factor = initFactor + diffX / float(windowWidth)
    # print "factor"
    # print factor
    contrast = initFac - diffY / float(windowHeight)
    # print "contrast"
    # print contrast
    if factor < 0:
        factor = 0
    if contrast < 0:
        contrast = 0
    currentImg = buildImage()
    glutPostRedisplay()


# Store global images
# originalImg = buildImage()
currentImg = buildImage()
# Run OpenGL

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(windowWidth, windowHeight)
glutInitWindowPosition(50, 50)

glutCreateWindow('imaging')

glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)

glutMainLoop()
# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow

import sys, os, numpy

try:  # Pillow
    from PIL import Image
except:
    print 'Error: Pillow has not been installed.'
    sys.exit(0)

try:  # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print 'Error: PyOpenGL has not been installed.'
    sys.exit(0)

# Globals

windowWidth = 600  # window dimensions
windowHeight = 800

factor = 1  # factor by which luminance is scaled
contrast = 1

h = [0] * 256
newh = [0] * 256

# Image directory and path to image file

imgDir = 'images'
imgFilename = 'mandrill.png'

imgPath = os.path.join(imgDir, imgFilename)

# Filter loading globals
filterDir = 'filters'
filterFilename = 'box3'

# File dialog

import Tkinter, tkFileDialog

root = Tkinter.Tk()
root.withdraw()


# Read and modify an image.

def buildImage():
    # Read image and convert to YCbCr

    print imgPath
    src = Image.open(imgPath).convert('YCbCr')
    srcPixels = src.load()

    width = src.size[0]
    height = src.size[1]

    # Set up a new, blank image of the same size

    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()

    for i in range(width):
        for j in range(height):

            # read source pixel
            y, cb, cr = srcPixels[i, j]

            # convolution filter  set up


            # ---- MODIFY PIXEL ----
            # brightness
            y = int(contrast * y + 10 * factor)
            # write destination pixel (while flipping the image in the vertical direction)
            if y < 0:
                y = 0
            elif y > 255:
                y = 255
            dstPixels[i, height - j - 1] = (y, cb, cr)
    # Done

    return dst.convert('RGB')


# Set up the display and draw the current image

def display():
    # Clear window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebuild the image

    img = currentImg
    width = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image
    # what does this mean?
    baseX = (windowWidth - width) / 2
    baseY = (windowHeight - height) / 2

    glWindowPos2i(baseX, baseY)

    # Get pixels and draw
    imageData = numpy.array(list(img.getdata()), numpy.uint8)

    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    glutSwapBuffers()


# Convolution Filter

def convolutionFilter():
    global currentImg, filterData
    img = currentImg.convert('YCbCr')
    srcPixels = img.load()
    width = img.size[0]
    height = img.size[1]

    # Set up a new, blank image of the same size
    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()

    # Set up pixels for convo
    convolvePix = numpy.zeros([width, height])

    # this loop is just to set up convol
    for i in range(width):
        for j in range(height):
            # read source pixels
            y, cb, cr = srcPixels[i, j]
            convolvePix[i, j] = y

    # build destination img from src img
    for i in range(width):
        for j in range(height):
            # read source pixels
            y, cb, cr = srcPixels[i, j]

            # ---- MODIFY PIXEL ----
            # convolution
            sum = 0
            yRadius = (filterData.shape[0] - 1) / 2
            xRadius = (filterData.shape[1] - 1) / 2
            for k in range(0, filterData.shape[1]):
                for p in range(0, filterData.shape[0]):
                    if ((i + k - xRadius) >= 0) and ((j + p - yRadius) < height) and ((i + k - xRadius) < width) and (
                        (j + p - yRadius) >= 0):
                        sum = sum + convolvePix[i + k - xRadius, j + p - yRadius] * filterData[k, p]
            print sum

            if (sum < 0):
                sum = 0
            elif (sum > 255):
                sum = 255
            else:
                if (sum % 1) > 0.5:
                    sum = int(sum) + 1
                else:
                    sum = int(sum)
                    convolvePix[i, j] = sum

            dstPixels[i, height - j - 1] = convolvePix[i, j], cb, cr
            currentImg = dst.convert('RGB')
            glutPostRedisplay()


# Histogram eq

def histogramEq():
    global currentImg, h, newh
    img = currentImg.convert('YCbCr')
    srcPixels = img.load()

    width = img.size[0]
    height = img.size[1]

    # Set up a new, blank image of the same size

    dst = Image.new('YCbCr', (width, height))
    dstPixels = dst.load()
    # Build destination image from source image
    for i in range(width):
        for j in range(height):
            y, cb, cr = srcPixels[i, j]
            h[y] += 1
    print h
    for i in range(width):
        for j in range(height):
            hsum = 0
            # read source pixel

            y, cb, cr = srcPixels[i, j]
            for x in range(0, y):
                hsum += h[x]
            # ---- MODIFY PIXEL ----
            # hist equalization
            y = int((256 * hsum / (width * height)) - 1)
            newh[y] += 1
            # write destination pixel (while flipping the image in the vertical direction)
            dstPixels[i, j] = (y, cb, cr)
    print newh
    h = [0] * 256
    newh = [0] * 256
    # Done

    currentImg = dst.convert('RGB')
    glutPostRedisplay()


# Loading Filter

def loadFilter():
    # global filterDir, filterFilename
    filterDir = 'filters'
    filterFilename = 'box3'

    filterPath = os.path.join(filterDir, filterFilename)
    print filterPath

    filterName = tkFileDialog.askopenfilename(initialdir=filterDir)
    with open(filterName, 'r') as data:
        content = data.readlines()

    [xdim, ydim] = content[0].split()
    [xdim, ydim] = [int(xdim), int(ydim)]
    scaleFactor = float(content[1].split()[0])
    filterData = numpy.zeros([ydim, xdim])

    for i in range(0, ydim):
        for j in range(0, xdim):
            filterData[i, j] = scaleFactor * float(content[i + 2].split()[j])

    print filterFilename, filterData
    return filterData


# Handle keyboard input

def keyboard(key, x, y):
    if key == '\033':  # ESC = exit
        sys.exit(0)

    elif key == 'h':
        histogramEq()

    elif key == 'l':
        path = tkFileDialog.askopenfilename(initialdir=imgDir)
        if path:
            loadImage(path)

    elif key == 's':
        outputPath = tkFileDialog.asksaveasfilename(initialdir='.')
        if outputPath:
            saveImage(outputPath)
    elif key == 'f':
        global filterData
        filterData = loadFilter()
    elif key == 'a':
        convolutionFilter()
    else:
        print 'key =', key  # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

    glutPostRedisplay()


# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.

def loadImage(path):
    global imgPath, currentImg
    imgPath = path
    currentImg = buildImage()
    glutPostRedisplay()


def saveImage(path):
    buildImage().save(path)


# Handle window reshape

def reshape(newWidth, newHeight):
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight

    glutPostRedisplay()


# Mouse state on initial click

button = None
initX = 0
initY = 0
initFactor = 0
initFac = 1


# Handle mouse click/unclick

def mouse(btn, state, x, y):
    global button, initX, initY, initFactor

    if state == GLUT_DOWN:

        button = btn
        initX = x
        initY = y
        initFactor = factor

    elif state == GLUT_UP:

        button = None


# Handle mouse motion

def motion(x, y):
    diffX = x - initX
    diffY = y - initY

    global factor, contrast, currentImg

    factor = initFactor + diffX / float(windowWidth)
    # print "factor"
    # print factor
    contrast = initFac - diffY / float(windowHeight)
    # print "contrast"
    # print contrast
    if factor < 0:
        factor = 0
    if contrast < 0:
        contrast = 0
    currentImg = buildImage()
    glutPostRedisplay()


# Store global images
# originalImg = buildImage()
currentImg = buildImage()
# Run OpenGL

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(windowWidth, windowHeight)
glutInitWindowPosition(50, 50)

glutCreateWindow('imaging')

glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)

glutMainLoop()
