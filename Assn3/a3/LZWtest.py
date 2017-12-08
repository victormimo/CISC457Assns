data = "aabbaabababbaaaaaba"

library = [data[0]]
i=0

comp = []
sampleLength = 1

print data[i:5]

while i<len(data):
    try:
        sample = data[i:i+sampleLength]
        print i
        index = library.index(sample)
        sampleLength += 1
        pass
    except:
        sample = data[i:i+sampleLength]
        print sample
        print library
        if sampleLength>1:
            index = library.index(sample[:-1])
            comp.append(index)
        library.append(sample)
        i += sampleLength-1
        sampleLength=1
sample = data[i:i+sampleLength]
index = library.index(sample)
comp.append(index)
print comp
print "Done"
