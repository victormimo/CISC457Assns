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
  startTime = time.time()
  dictionary = {} # create a dictionary
  dictsize = 0
  for i in range(-255, 256):
    dictionary[str(i)] = dictsize
    dictsize += 1

  channelsN = img.shape[2]
  outputlist = []
  outputBytes = bytearray()
  listSize = 0
  for y in range(img.shape[0]):
    for x in range(img.shape[1]):
      for c in range(channelsN):
        outputlist.append(img[y,x,c])
        listSize += 1
  print listSize, sys.getsizeof(outputlist)
  lastStr = ''
  current = outputlist[0]
  lastStr = str(int(current))
  for i in range(1, listSize):
    if dictsize >= 65536:
      dictionary = {} # create a dictionary
      dictsize = 0
      for i in range(-255, 256):
        dictionary[str(i)] = dictsize
        dictsize += 1

    current = outputlist[i]
    entry = lastStr+","+str(int(current))
    if entry in dictionary:
      lastStr = entry
    else:
      outBits = dictionary[lastStr]
      outLow = outBits & 0xFF
      outHigh = (outBits >> 8) & 0xFF
      outputBytes.append(outLow)
      outputBytes.append(outHigh)
      dictionary[entry] = dictsize
      dictsize += 1
      lastStr = str(int(current))

  if lastStr in dictionary:
    outBits = dictionary[lastStr]
    outLow = outBits & 0xFF
    outHigh = (outBits >> 8) & 0xFF
    outputBytes.append(outLow)
    outputBytes.append(outHigh)


  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )
  inSize  = img.shape[0] * img.shape[1] * img.shape[2]
  outSize = len(outputBytes)

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )



# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)

  # Read the rows, columns, and channels.

  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # print inputBytes
  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.
  inputBytes = bytearray(inputFile.read())
  inputlen = len(inputBytes)/2
  startTime = time.time()

  result = []
  dictionary = {}
  dictsize = 0
  for i in range(-255, 256):
    dictionary[dictsize] = [i]
    dictsize += 1

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  byteIter = iter(inputBytes)
  currentbyte = byteIter.next()
  nextbyte = byteIter.next()
  phrase = (nextbyte << 8) + currentbyte
  lastStr = dictionary[phrase]
  result.append(lastStr)

  for i in range(1, inputlen):

    # again reset the dictionary if it reaches the limit
    if dictsize >= 65536:
      dictionary = {} # create a dictionary
      dictsize = 0
      # pre-fill dictionary with single characters
      for i in range(-255, 256):
        dictionary[dictsize] = [i]
        dictsize += 1

    currentbyte = byteIter.next()
    nextbyte = byteIter.next()
    phrase = (nextbyte << 8) + currentbyte
    if phrase in dictionary:
      entry = dictionary[phrase]
    else:
      entry = []
      for j in lastStr:
        entry.append(j)
      entry.append(lastStr[0])
    temp = []
    for j in lastStr:
      temp.append(j)
    temp.append(lastStr[0])
    dictionary[dictsize] = temp
    dictsize += 1
    for k in range(len(entry)):
      result.append(entry[k])
    lastStr = entry
  imgSize = rows*columns*channels
  counter = 1
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        if (counter < len(result)):
          img[y,x,c] = result[counter]
        counter += 1
  endTime = time.time()
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
