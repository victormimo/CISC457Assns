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
  dictionarySize = 0
  # pre-fill dictionary with single characters
  for i in range(-255, 256):
    dictionary[str(i)] = dictionarySize
    dictionarySize += 1
  # print dictionary

  numChannels = img.shape[2]
  outputBytesChannels = [[]]*numChannels # create an array of arrays to store channel intensities separately
  outputBytesList = []
  
 
  outputBytes = bytearray()
  listSize = 0
  for y in range(img.shape[0]):
    for x in range(img.shape[1]):
      for c in range(numChannels):
        # outputBytes.append( img[y,x,c] )
        outputBytesChannels[c].append( img[y,x,c] )
        outputBytesList.append(img[y,x,c])
        listSize += 1

  previous = ''
  current = outputBytesList[0]
  previous = str(int(current))
  # loop through list of intensities
  for i in range(1, listSize):
    
    # if dictionary reaches size limit, clear it and start it again
    if dictionarySize >= 65536:
      dictionary = {} # create a dictionary
      dictionarySize = 0
      # pre-fill dictionary with single characters
      for i in range(-255, 256):
        dictionary[str(i)] = dictionarySize
        dictionarySize += 1

    current = outputBytesList[i]
    entry = previous+","+str(int(current))
    if entry in dictionary:
      previous = entry
    else:
      # if dictionarySize < 65536: # limit of dictionary
      output16bits = dictionary[previous]
      outputLow8bits = output16bits & 0xFF
      outputHigh8bits = (output16bits >> 8) & 0xFF
      # append the 16 digit bit string in 2 steps, first low 8 bits and then high 8 bits
      # this is because it is a bytearray
      outputBytes.append(outputLow8bits)
      outputBytes.append(outputHigh8bits)
      # add to dictionary
      dictionary[entry] = dictionarySize
      dictionarySize += 1
      previous = str(int(current))

  # final check
  if previous in dictionary:
    output16bits = dictionary[previous]
    outputLow8bits = output16bits & 0xFF
    outputHigh8bits = (output16bits >> 8) & 0xFF
    # append the 16 digit bit string in 2 steps, first low 8 bits and then high 8 bits
    # this is because it is a bytearray
    outputBytes.append(outputLow8bits)
    outputBytes.append(outputHigh8bits)


  endTime = time.time()

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write( '%s\n'       % headerText )
  outputFile.write( '%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]) )
  outputFile.write( outputBytes )

  # Print information about the compression
  
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

  # Read the raw bytes.
  inputBytes = bytearray(inputFile.read())
  rangeLength = len(inputBytes)/2 # divide by 2 because every 2 bytes is 1 item
  # print inputBytes
  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  # outputBytes = bytearray() # create an output bytes array
  result = []

  # initialize the dictionary in the opposite was as compress and use an array as the value
  dictionary = {} # create a dictionary
  dictionarySize = 0
  # pre-fill dictionary with single characters
  for i in range(-255, 256):
    dictionary[dictionarySize] = [i]
    dictionarySize += 1

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  byteIter = iter(inputBytes)
  byteCurrent = byteIter.next()
  byteNext = byteIter.next()
  # put together the two bytes to get the 16-bit phrase
  phrase = (byteNext << 8) + byteCurrent # this is done by shifting next into the higher slot
  previous = dictionary[phrase]
  result.append(previous)

  for i in range(1, rangeLength):
    
    # again reset the dictionary if it reaches the limit
    if dictionarySize >= 65536:
      dictionary = {} # create a dictionary
      dictionarySize = 0
      # pre-fill dictionary with single characters
      for i in range(-255, 256):
        dictionary[dictionarySize] = [i]
        dictionarySize += 1

    byteCurrent = byteIter.next()
    byteNext = byteIter.next()
    phrase = (byteNext << 8) + byteCurrent

    if phrase in dictionary:
      entry = dictionary[phrase]
    else:
      entry = []
      for j in previous:
        entry.append(j)
      entry.append(previous[0])
      # entry = [previous + [previous[0]]]

    temp = []
    for j in previous:
      temp.append(j)
    temp.append(previous[0])
    dictionary[dictionarySize] = temp
    dictionarySize += 1

    for k in range(len(entry)):
      result.append(entry[k])

    previous = entry



  # print dictionary
  # print outputBytes
  # byteIter2 = iter(outputBytes)
  imgSize = rows*columns*channels
  counter = 1
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        if (counter < len(result)):
          # print counter
          # print result[counter]
          img[y,x,c] = result[counter]
        counter += 1
        # print img[y,x,c]
  

      

  # print img[0]

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
