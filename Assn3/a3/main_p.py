# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'

# Compress an image

def initializeDictionary(dict_size) :
  d = dict((chr(i), chr(i)) for i in xrange(dict_size))
  return d

def getfirstbyte(v) :
    return (v & (0xFF << 8)) >> 8

def getsecondbyte(v) :
    return v & 0xFF

def getprediction(img, x, y, c, isMultiChannel):
    f10 = 0
    #f11 = 0
    #f01 = 0
    if(x > 0):
        if(isMultiChannel):
            f10 = img[y,x-1,c]
        else:
            f10 = img[y,x-1]
    #    if(y > 0):
    #        if(isMultiChannel):
    #            f11 = img[y-1,x-1,c]
    #        else:
    #            f11 = img[y-1,x-1]
    #if(y > 0):
    #    if(isMultiChannel):
    #        f01 = img[y-1,x,c]
    #    else:
    #        f01 = img[y-1,x]
           
    #r = np.uint8(f10/3 + f11/3 + f01/3)
    #r = np.uint8(f10/2 + f01/2)
    r = f10
    return r

def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')

  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.

  startTime = time.time()

  outputBytes = bytearray()

  # Initialize dictionary
  maxsize = 65536
  dict_size = 256
  d = initializeDictionary(dict_size)
  s = ''

  for y in range(img.shape[0]):
    for x in range(img.shape[1]):
      for c in range(img.shape[2]):
        fp = 0
        if(len(img.shape) > 2):
            #fp = getprediction(img,x,y,c,True)
            if(x > 0):
                fp = img[y,x-1,c]
            e = img[y,x,c] - fp
        else:
            #fp = getprediction(img,x,y,0,False)
            if(x > 0):
                fp = img[y,x-1]
            e = img[y,x] - fp
        if(s + chr(e) in d):
            s += chr(e)
        else:
            #sq = convertchar2num(d[s])
            sq = d[s]
            if(len(sq) < 2):
                sq = chr(0) + sq
            outputBytes.append(sq[0])
            outputBytes.append(sq[1])
            d[s + chr(e)] = convertnum2char(dict_size)
            dict_size += 1
            if(dict_size > maxsize):
                dict_size = 256
                d = initializeDictionary(dict_size)
            s = chr(e)
  sq = d[s]
  if(len(sq) < 2):
    sq = chr(0) + sq
  outputBytes.append(sq[0])
  outputBytes.append(sq[1])
  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  if len(img.shape) > 2:
      outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  else:
      outputFile.write( '%d %d\n' % (img.shape[0], img.shape[1]))
  outputFile.write( outputBytes )

  # Print information about the compression

  if len(img.shape) > 2:
      inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  else:
      inSize = img.shape[0]*img.shape[1]

  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )

# Get next code

def getnextcode( byteIter ) :
    fb = byteIter.next()
    sb = byteIter.next()
    #return (int(fb) << 8) | sb
    if(fb != 0):
        return chr(fb) + chr(sb)
    return chr(sb)

def convertchar2num( s ):
    if(len(s) > 1) :
        fc = s[0]
        sc = s[1]
        if(ord(fc) != 0):
            return ord(fc)*256 + ord(sc)

    return ord(s)

def convertnum2char( n ):
    s = ""
    fc = getfirstbyte( n )
    sc = getsecondbyte( n )
    if(fc != 0):
        s += chr(fc)
    s += chr(sc)
    return s

# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)

  # Read the rows, columns, and channels.
  img_dims = [ int(x) for x in inputFile.readline().split() ]
  rows = img_dims[0]
  columns = img_dims[1]
  if(len(img_dims) > 2):
      channels = img_dims[2]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  if len(img_dims) > 2:
      img = np.empty( [rows,columns,channels], dtype=np.uint8 )
  else:
      img = np.empty([rows, columns], dtype=np.uint8)
  byteIter = iter(inputBytes)

  # For debugging
  #f = open('debug_decoding.txt', 'w')
  #kf = open('output_codes.txt', 'w')

  # Initialize dictionary
  maxsize = 65536
  dict_size = 256
  d = initializeDictionary(dict_size)
  s = ''
  e = []
  while(True):
    try:
        k = getnextcode(byteIter) # this is
    except StopIteration:
        break
    #kf.write(str(convertchar2num(k)) + '\n')
    #print(k)
    if( convertchar2num(k) == dict_size):
        d[convertnum2char(dict_size)] = s + s[0]
        dict_size += 1
    elif(len(s) > 0):
        d[convertnum2char(dict_size)] = s + d[k][0]
        dict_size += 1
    for q in d[k]:
        e.append(ord(q))
    s = d[k]
    if(dict_size > maxsize):
        dict_size = 256
        d = initializeDictionary(dict_size)

  i = 0
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        fp = 0
        if(len(img_dims) > 2):
            #fp = getprediction(img,x,y,c,True)
            if(x > 0):
                fp = img[y,x-1,c]
            img[y,x,c] = fp + e[i]
        else:
            #fp = getprediction(img,x,y,0,False)
            if(x > 0):
                fp = img[y,x-1]
            img[y,x] = fp + e[i]
        i += 1

  endTime = time.time()
  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )




# The command line is
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file

if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)
