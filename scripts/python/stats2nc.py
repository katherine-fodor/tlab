# read statistics from ASCII files and put them in netCDF
# Chiel van Heerwaarden,     2012 -- created 
# Cedrick.Ansorge@gmail.com, 2013 -- Some generalizations
#
import gzip as gz
import netCDF4
import subprocess
import array as arr
import string
 
from pylab import *
from operator import itemgetter, attrgetter

class ClassFile: 
    def __init__(self,name,num): 
        self.name=name 
        self.num =num
    def __repr__(self):
        return repr((self.name,self.num)) 


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def avg2dict(avgtype,avgpath,jmax,gzip,tstart=-1, tend=-1,tstep=-1):

  gzip_str   = '.gz'

  files_from_list = 0
  headertotal = 0
  # specify the number of vertical profs and time variables 
  if ( avgtype == 'avg'):
#    headerprof = 199
    headertime = 14 
    headerlength    = 21
  elif ( avgtype == 'avg1s' or avgtype == 'avg2s' or avgtype == 'avg3s' or avgtype == 'avg4s' or avgtype == 'avg5s'): 
#    headerprof = 47
#    headerprof = 45
    headertime = 11
    headerlength = 8
  elif( avgtype == 'int' ):
    headerlength = 4
#    headerprof = 4
    headertime = 0
  elif( avgtype == 'cov' ):
    headerlength = 6
#    headerprof = 6
    headertime = 3
  elif( avgtype == 'cavg' ):
    headerlength = 6
#    headerprof = 6
    headertime = 28
  else :
    print('WARNING : unknown filetype!')
    print('WARNING : assuming all data is vertical profiles')
    headerlength= 4
#    headerprof = -1 
    headertime = -1 
#  headertotal= headerprof + headertime
  
  ###########################################################
  # get times automatically from files in directory 
  ########################################################### 
  if ( tstart == -1 ) : 
    files_from_list=1 
    command = "ls " + avgpath + "/" + avgtype + "*" + " | egrep '" + avgtype + "[0-9]*(" + gzip_str + ")?$" + "'"
    
    p = subprocess.Popen(command, shell=True,  
                         stdout=subprocess.PIPE) 
    file_list = []
    for file in p.stdout.readlines():
        dummy = file.decode('utf8').strip('\n')
        try:
            with open(dummy): 
                if '.nc' not in dummy: 
                    cstart=len('{}/{}'.format(avgpath,avgtype))
                    cend=len(dummy)
                    if gzip_str in dummy:
                        cend=cend-len(gzip_str)

                    filenum = int(dummy[cstart:cend])
                    if ( is_number(filenum) ):
                        file_list.append(ClassFile(dummy,filenum))

        except IOError:
            print('ERROR - File', file, 'does not exist')

    retval = p.wait()
    ntimes = len(file_list)
  else :
    ntimes = (tend - tstart) // tstep + 1

  if ( files_from_list == 1 ) :
      file_list=sorted(file_list,key=lambda ClassFile: ClassFile.num)

  print('FILES for', avgtype,':', ntimes)

  ############################################################ 
  if ( ntimes == 0 ) : 
    return -1 
  for t in range(ntimes): 
    if ( files_from_list == 1 ) :
      filename = file_list[t].name 
      filenum = file_list[t].num 
      #number starts after <path>/<file type>
      tend = filenum
      if (t == 0): 
        tstart = filenum
    else: 
      filenum = tstart+t*tstep
      if ( gzip == 1):
        filename = '{}/{}{}{}'.format(avgpath,avgtype,filenum,gzip_str)
      else:
        filename = '{}/{}{}'.format(avgpath,avgtype,filenum)
  
    # process the file
    if gzip_str in filename:
      f = gz.open(filename,'rt')
    else:
      f= open(filename,'r')
      
    # retrieve the time
    datastring = f.readline()
    time = float(datastring.split()[2])
    print('{}: it{}  Time={}'.format(avgtype, filenum, time))
  
    # process the groups items in the header 
    for i in range(headerlength-2):
      dummy = f.readline()
   
    # read the variable labels
    datastring = f.readline()
    
    if(filenum == tstart): 
      avg = {}
      header = datastring.split()
      if( headertotal > 0 and size(header) != headertotal ): 
        print("ERROR - header size of", size(header))
        print("ERROR   is not as expected (", headertotal, ")")
        return -1 
      elif ( size(header) != headertotal ):
        headertotal = size(header)
        headerprof  = headertotal -headertime

      avg['Time'] = zeros(ntimes)
      avg['Iteration'] = zeros(ntimes)
      for n in range(headerprof):
        avg[header[n]] = zeros((ntimes, jmax))
      for n in range(headerprof, headertotal):
        avg[header[n]] = zeros(ntimes)
  
    # process the data
    # first store the time
    avg['Time'][t] = time 
    avg['Iteration'][t] = filenum
  
    for i in range(jmax):
      datastring = f.readline()
      data = datastring.split()
      magic = 0
      if ( size(data) != headerprof ):
        if ( size(data) != headertotal ): 

############################################################
# WORK AROUND FOR avg1s BUG  in certain versions of the 
# code (ignore the missing two values by setting magic=-2) 
############################################################

          if ( avgtype == 'avg1s' and (size(data) - headertotal == -2 ) ): 
            # this is very likely a case of this bug  
            print("WARNING - encountered avg1s BUG - ignoring missing values")
            magic = -2 
          else :
            print("ERROR - size of data in line", i," (", size(data), \
                ") not as expected:", headertotal, " or", headerprof,".")
            return -1 
      # process the vertical profiles
      for n in range(headerprof):
        avg[header[n]][t,i] = data[n]
  
      # process the time series
      if(len(data) == headertotal+magic):
        for n in range(headerprof, headertotal+magic):
          avg[header[n]][t] = data[n]
  
    f.close()
    
  avg['Iteration'] = [int(f) for f in avg['Iteration'][:]]
  return avg

#############################################################

def dict2nc(dict, ncname, flag=0):
  # process the dictionaries to netcdf files
  avgnc  = netCDF4.Dataset("{}.nc".format(ncname), "w")

  # retrieve dimensions
  time   = dict["Time"]
  ntimes = time.shape[0]

  y    = dict["Y"]
  jmax = y.shape[1]

  print("Creating netCDF file with ntimes = {} and jmax = {}".format(ntimes, jmax))
  
  # create dimensions in netCDF file
  dim_y = avgnc.createDimension('y', jmax)
  dim_t = avgnc.createDimension('t', ntimes)

  # create variables
  var_t = avgnc.createVariable('t', 'f8',('t',)) 
  var_t.units='Days since 0000-01-01 00:00'
  var_y = avgnc.createVariable('y', 'f8',('y',)) 
  var_y.long_name='Height above Surface' 
  var_y.positive='up'
  var_y.standard_name='height' 
  var_y.units='level'

  var_it= avgnc.createVariable('it','i4',('t',))
  # store the data
  # first, handle the dimensions
  var_t[:]  = dict['Time'][:]
  var_y[:]  = dict['Y']   [0,:] 
  var_it[:] = [int(f) for f in dict['Iteration'][:]]
  
  # now make a loop through all vars.
  dictkeys = list(dict.keys())

  for i in range(size(dictkeys)):
    varname = dictkeys[i]
    if(not(  (varname == "Iteration") or (varname == "Y") or \
             (varname == "Time") or (varname == "I") or (varname == "J") ) ):
      vardata = dict[varname]
      if(len(vardata.shape) == 2):
        if( (vardata.shape[0] == ntimes) and (vardata.shape[1] == jmax) ):
          #print("Storing {} in 2D (t,y) array".format(varname))
          var_name = avgnc.createVariable(varname,'f8',('t','y',))
          var_name[:,:] = vardata
      if(len(vardata.shape) == 1):
        if(vardata.shape[0] == ntimes):
          #print("Storing {} in 1D (t) array".format(varname))
          var_name = avgnc.createVariable(varname,'f8',('t',))
          var_name[:] = vardata

  # close the file
  avgnc.close()

