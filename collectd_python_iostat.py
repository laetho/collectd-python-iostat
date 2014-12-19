"""
Original code for parsing iostat output is made by jakamkon@gmail.com
under the MIT-license.

Project page: https://bitbucket.org/jakamkon/python-iostat/overview 
"""

import sys
import subprocess

class IOStatError(Exception):
    pass

class CmdError(IOStatError):
    pass

class ParseError(IOStatError):
    pass

def parse_diskstats(input, disks=[]):
    """
    Parse iostat -d and -dx output.If there are more
    than one series of statistics, get the last one.
    By default parse statistics for all avaliable block devices.

    @type input: C{string}
    @param input: iostat output

    @type disks: list of C{string}s
    @param input: lists of block devices that
    statistics are taken for.

    @return: C{dictionary} contains per block device statistics.
    Statistics are in form of C{dictonary}.
    Main statistics:
    tps   Blk_read/s   Blk_wrtn/s   Blk_read   Blk_wrtn
    Extended staistics (available with post 2.5 kernels):
    rrqm/s wrqm/s   r/s   w/s  rsec/s  wsec/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
    See I{man iostat} for more details.
    """
    dstats = {}
    dsi = input.rfind('Device:')
    if dsi == -1:
        raise ParseError('Unknown input format: %r' % input)

    ds = input[dsi:].splitlines()
    hdr = ds.pop(0).split()[1:]
    
    for d in ds:
        if d:
            d = d.split()
            dev = d.pop(0)
            if (dev in disks) or not disks:
                dstats[dev] = dict([(k,float(v)) for k,v in zip(hdr, d)])
    return dstats

"""
This fucntion is modified from it's original form for running inside collectd in a threaded enviroment.
"""
def _run(interval, count, disks=[], options=[]):
    cmd = ["/usr/bin/iostat -y "+''.join(options)+' '+str(interval)+' '+str(count)]
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    out = p.stdout.read()
    p.stdout.close()
    return out


def get_diskstats(disks=[], interval=1, count=1, options=[''] ):
    dstats = _run(interval, count, disks, ['-d'])
    extdstats = _run(interval, count, disks, ['-x'])
    ds = parse_diskstats(dstats)
    eds = parse_diskstats(extdstats)
    for dk, dv in ds.iteritems():
        if dk in eds:
            ds[dk].update(eds[dk])
    return ds


"""
Implementation of collectd_python_iostat starts here.
"""

import collectd

def log_verbose(msg):
  if not IOSTAT_VERBOSE:
    return
  collectd.info('collectd_python_iostat [verbose]: %s' % msg )

def configure_callback(conf):
  global IOSTAT_INTERVAL, IOSTAT_VERBOSE, IOSTAT_HOST, IOSTAT_UNIT
  for node in conf.children:
    if node.key == 'Verbose':
      IOSTAT_VERBOSE = node.values[0]
    elif node.key == 'Host':
      IOSTAT_HOST = node.values[0]
    elif node.key == 'Interval':
      IOSTAT_INTERVAL = node.values[0]
    elif node.key == 'Unit':
      IOSTAT_UNIT = node.values[0]
    else:
      collectd.warning('collectd_python_iostat plugin: Unknown config key: %s.' % node.key )

def dispatch_item(dev,key, value, type, type_instance=None):
  if not type_instance:
    type_instance = key
  vl = collectd.Values() 
  vl.type = type
  vl.type_instance = type_instance
  vl.plugin = 'iostat'
  vl.plugin_instance = dev
  vl.values = [value]
  vl.dispatch()

def read_callback(stats=None):
  log_verbose('Read callback called')

  stats = get_diskstats()

  if not stats:
    collectd.error('collectd_python_iostat plugin: No statistics received')
    return

  for (dev,items) in stats.items():
    for (key,item) in items.items():
      if key == 'wrqm/s':
        dispatch_item(dev,'wrqms',item,'gauge')
      elif key == 'await':
        dispatch_item(dev, 'await',item,'gauge')
      elif key == 'Blk_wrtn/s':
        dispatch_item(dev,'blkwrtns',item,'gauge')
      elif key == 'svctm':
        dispatch_item(dev,'svctm',item,'gauge')
      elif key == 'Blk_wrtn':
        dispatch_item(dev,'blkwrtn',item,'counter')
      elif key == 'avgrq-sz':
        dispatch_item(dev,'avgrqsz',item,'gauge')
      elif key == 'r/s':
        dispatch_item(dev,'rs',item,'gauge')
      elif key == 'Blk_read':
        dispatch_item(dev,'blkread',item,'counter') 
      elif key == 'w/s':
        dispatch_item(dev,'ws',item,'gauge')
      elif key == 'avgqu-sz':
        dispatch_item(dev,'avgqusz',item,'gauge')
      elif key == 'wsec/s':
        dispatch_item(dev,'wsecs',item,'gauge')
      elif key == 'tps':
        dispatch_item(dev,'tps',item,'gauge')
      elif key == 'rrqm/s':
        dispatch_item(dev,'rrqms',item,'gauge')
      elif key == 'Blk_read/s':
        dispatch_item(dev,'blkreads',item,'gauge')
      elif key == '%util':
        dispatch_item(dev,'util',item,'percent')
      elif key == 'rsec/s':
        dispatch_item(dev,'rsecs',item,'gauge')
      elif key == 'kB_read/s':
        dispatch_item(dev,'kBreads',item,'gauge')
      elif key == 'kB_wrtn/s':
        dispatch_item(dev,'kBwrtns',item,'gauge')
      elif key == 'kB_read':
        dispatch_item(dev,'kBread',item,'gauge')
      elif key == 'kB_wrtn':
        dispatch_item(dev,'kBwrtn',item,'gauge')
      elif key == 'MB_read/s':
        dispatch_item(dev,'MBreads',item,'gauge')
      elif key == 'MB_wrtn/s':
        dispatch_item(dev,'MBwrtns',item,'gauge')
      elif key == 'MB_read':
        dispatch_item(dev,'MBread',item,'gauge')
      elif key == 'MB_wrtn':
        dispatch_item(dev,'MBwrtn',item,'gauge')
      else:
        log_verbose('Current key: %s' % key)

collectd.register_config(configure_callback)
collectd.register_read(read_callback,10)

