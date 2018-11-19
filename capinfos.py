import subprocess

def capinfos(filename):
  # generates wireshark's capinfos like stats
  # limited features
  # needs additional testing
  output = subprocess.run(['capinfos',filename],stdout=subprocess.PIPE)
  return output.stdout