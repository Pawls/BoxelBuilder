from os import listdir
from os.path import isfile, join
from itertools import groupby
    
mypath = "assets/textures/boxels/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

onlyfiles.sort()

onlyfiles = [list(i) for j, i in groupby(onlyfiles, 
                  lambda a: a.split('_')[0])]
print(onlyfiles)
