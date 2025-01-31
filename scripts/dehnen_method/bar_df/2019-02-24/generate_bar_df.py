# ----------------------------------------------------------------------------
#
# TITLE - generate_triaxial_df.py
# AUTHOR - James Lane
# PROJECT - AST 1501
#
# ----------------------------------------------------------------------------

### Docstrings and metadata:
''' Script to run parallelized bar DF evaluation

Run February 24, 2019

Evaluate the Dehnen bar over a grid similar to that from Jo's power 
spectrum paper in order to make sure the program works nicely.
'''
__author__ = "James Lane"

### Imports

## Basic
import numpy as np
import sys, os, pdb, time, copy

## galpy and Astropy
from astropy import units as apu
from galpy import orbit, potential, df, actionAngle

## Project specific
sys.path.append('../../../src')
import ast1501.df
import ast1501.potential
import ast1501.util

# ----------------------------------------------------------------------------

### Parameters

# General
_NCORES = 10                         # Number of cores to use
_LOGFILE = open('./log.txt','w')    # Name of the output log file
_VERBOSE = 0                        # Degree of verbosity
_PLOT_DF = True                    # Plot the output DF
_COORD_IN_XY = True                # Input coordinate grid in XY or polar?

# Timing
_T_EVOLVE = 2
_TIMES = -np.array([0,_T_EVOLVE]) * apu.Gyr

# Spatial
# _RRANGE = [5,7]                    # Range in galactocentric R
# _PHIRANGE = [-np.pi,np.pi]          # Range in galactocentric phi
# _DR = 2                             # Bin size in R
# _DPHI = 15                           # Bin size in Phi (arc in kpc)
# _GRIDR, _GRIDPHI = ast1501.df.generate_grid_radial( _RRANGE, 
#                                                     _PHIRANGE, 
#                                                     _DR, 
#                                                     _DPHI, 
#                                                     delta_phi_in_arc=True )

_XRANGE = [5,12]
_YRANGE = [-3,3]
_DX = 0.75
_DY = 0.75
_GRIDX, _GRIDY = ast1501.df.generate_grid_rect( _XRANGE,
                                                _YRANGE,
                                                _DX,
                                                _DY,
                                                return_polar_coords=False)


# Distribution Function
_VPARMS = [5,5,8,8]   # dvT,dvR,nsigma,nsigma
_SIGMAPARMS = ast1501.df.get_vsigma()
_SIGMA_VR,_SIGMA_VT,_SIGMA_VZ = _SIGMAPARMS
_SCALEPARMS =  ast1501.df.get_scale_lengths()
_RADIAL_SCALE, _SIGMA_VR_SCALE, _SIGMA_VZ_SCALE = _SCALEPARMS
_EVAL_THRESH = 0.0001   # DF evaluation threshold

# ----------------------------------------------------------------------------

### Make potentials and DFs
_POT = [potential.MWPotential2014,potential.DehnenBarPotential()]
_AA = actionAngle.actionAngleAdiabatic( pot=potential.MWPotential2014, 
                                        c=True)
_QDF = df.quasiisothermaldf(hr= _RADIAL_SCALE*apu.kpc, 
                            sr= _SIGMA_VR*(apu.km/apu.s),
                            sz= _SIGMA_VZ*(apu.km/apu.s),
                            hsr= _SIGMA_VR_SCALE*(apu.kpc), 
                            hsz= _SIGMA_VZ_SCALE*(apu.kpc),
                            pot= potential.MWPotential2014, 
                            aA= _AA)

# ----------------------------------------------------------------------------

### Evaluate the DF

# Write the parameters in the log
_LOGFILE.write(str(len(_GRIDX))+' evaluations\n')
write_params = [_NCORES,_TIMES,_XRANGE,_YRANGE,_DX,_DY,_VPARMS,
                _SIGMAPARMS,_SCALEPARMS,_EVAL_THRESH,]
write_param_names = ['NCORES','TIMES','XRANGE','YRANGE','DX',
                     'DY','VPARMS','SIGMAPARMS','SCALEPARMS','EVAL_THRESH']
_LOGFILE = ast1501.util.df_evaluator_write_params(_LOGFILE,write_params,
                                                    write_param_names)

# Run the program
t1 = time.time()
results = ast1501.df.evaluate_df_polar_parallel(_GRIDX, 
                                                _GRIDY, 
                                                _POT, 
                                                _QDF, 
                                                _VPARMS, 
                                                _TIMES, 
                                                _NCORES,
                                                sigma_vR=_SIGMA_VR,
                                                sigma_vT=_SIGMA_VT,
                                                evaluator_threshold=_EVAL_THRESH,
                                                plot_df=_PLOT_DF,
                                                coords_in_xy=_COORD_IN_XY,
                                                logfile=_LOGFILE,
                                                verbose=_VERBOSE)
t2 = time.time()    
                                
# Write in the log
_LOGFILE.write('\n'+str(round(t2-t1))+' s total')
_LOGFILE.close()

# Write results to file
np.save('data.npy',np.array(results))

# ----------------------------------------------------------------------------
