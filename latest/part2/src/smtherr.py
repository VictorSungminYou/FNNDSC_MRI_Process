import os, argparse
from tempfile import NamedTemporaryFile
import numpy as np
import subprocess as sp
import numpy.typing as npt
from bicpl import PolygonObj
from bicpl.math import difference_average


def smtherr(surface):
    """
    Calculate the average change in mean curvature for every vertex and its neighbors.
    """
    data = depth_potential(surface, '-mean_curvature')
    obj = PolygonObj.from_file(surface)
    return np.fromiter(difference_average(obj.neighbor_graph(), data), dtype=np.float32)


def depth_potential(filename: str | os.PathLike, arg: str, command: str = 'depth_potential'):
    if not arg.startswith('-'):
        arg = '-' + arg
    with NamedTemporaryFile() as tmp:
        os.system(command + ' ' + ' ' + arg + ' ' + filename + ' ' +  tmp.name )
        #cmd = (command, arg, filename, tmp.name)
        #sp.run(cmd, check=True)
        data = np.loadtxt(tmp.name, dtype=np.float32)
    return data
    
    
def main(args):
	input_surface=args.input_surface
	output_smoother=args.output_smoother
	
	error=smtherr(input_surface)
	np.savetxt(output_smoother,error,delimiter=',',fmt='%.5f')  
	if os.path.isfile(output_smoother):
		print(output_smoother, 'WRITTEN')
	   

if __name__== '__main__':
	
	parser = argparse.ArgumentParser('   ==========   Calculating smoothness error  ==========   ')
	parser.add_argument('-s', '--input_surface',action='store', dest='input_surface',type=str, required=True, help='Input surface')
	parser.add_argument('-o', '--output_smoother',action='store',dest='output_smoother', type=str, required=True, help='Ouput file with smoothness error')
	args = parser.parse_args()

	main(args)

  

