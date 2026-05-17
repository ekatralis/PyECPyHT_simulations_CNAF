import numpy as np
import pylab as pl
import matplotlib.gridspec as gridspec
import glob

import os,sys
BIN = os.path.expanduser("./template_stability_LHC/tools/")
sys.path.append(BIN)
import myfilemanager as mfm
import propsort as ps
import mystyle as ms

from scipy.constants import c as clight
from matplotlib.ticker import SymmetricalLogLocator
import argparse

parser = argparse.ArgumentParser(description='Generate instability plots.')
parser.add_argument('--show', action='store_true', help='Show the plots after generation.')
parser.add_argument('--root_folder', type=str, default='/home/evangeloskatralis/Documents/simulations/chromaticity_LHC_Collision', help='Root folder containing the simulation data.')
parser.add_argument('--chroma', required=True, type=float, help='Chromaticity value for the simulations.')
parser.add_argument('--cmap', type=str, default='magma', choices = ('magma', 'tab20'), help='Colormap for the plots.')
args = parser.parse_args()


pl.close('all')


# scan parameters

# 1. Drift Length
# fraction_device_dip_vect = np.arange(2,20.1,0.5)*1e-2
if args.chroma == 0:
    el_densities = np.sort(np.concatenate([np.array([3.75e+12]),np.array([1e12]),np.arange(2e12, 4.01e12,5e11),np.arange(5e12, 1.01e13,1e12)],axis = 0))
elif args.chroma == 5:
    el_densities = np.sort(np.concatenate([np.array([3.75e+12,4.50e+12]),np.array([1e12]),np.arange(2e12, 4.01e12,5e11),np.arange(5e12, 1.01e13,1e12)],axis = 0))
else:
    el_densities = np.concatenate([np.array([1e12]),np.arange(2e12, 4.01e12,5e11),np.arange(5e12, 1.01e13,1e12)],axis = 0)
# el_densities = np.array([8.00e+12,9.00e+12])
#~ fraction_device_dip_vect = np.arange(15,20.1,1.)*1e-2


#~ # Simulation Parameters
#~ PyPICmode_tag = 'T0'
#~ macroparticles_per_slice = 2500.
#~ n_segments = 8


# If you want to save the figures with all the scan parameters choose: savefigures = True
savefigures = True
#~ # Comment this part if you want to save the plots. You can choose only some scan parameters
#~ savefigures = False
#~ fraction_device_quad_vect = [0.26]
#~ n_slices_vect = np.array([1000])
#~ betax_vect = [150.]

folder_plot = 'plots_latest/'
if not os.path.exists(folder_plot) and savefigures:
    os.makedirs(folder_plot)
    

# If you want to save the plots with the centroid choose: charge_weight_centroid_plots_flag = True
# with this option the script is slow
charge_weight_centroid_plots_flag = True

figNumber = 0

    
figNumber = figNumber + 1

# Figure settings
fig = pl.figure(figNumber, figsize=(14,20))
fig.patch.set_facecolor('w')
gs1 = gridspec.GridSpec(5, 2)

sp1 = fig.add_subplot(gs1[0])
sp2 = fig.add_subplot(gs1[1], sharex=sp1, sharey=sp1 )
sp3 = fig.add_subplot(gs1[2], sharex=sp1)
sp4 = fig.add_subplot(gs1[3], sharex=sp1, sharey=sp3)
sp5 = fig.add_subplot(gs1[4], sharex=sp1) 
sp6 = fig.add_subplot(gs1[5], sharex=sp1, sharey=sp5)
sp7 = fig.add_subplot(gs1[8], sharex=sp1)
sp8 = fig.add_subplot(gs1[9], sharex=sp1)
sp9 = fig.add_subplot(gs1[6], sharex=sp1)
sp10 = fig.add_subplot(gs1[7], sharex=sp1, sharey=sp9)

if args.cmap == 'magma':
    colorcurr = pl.cm.magma(np.linspace(0, 1, len(el_densities)))
elif args.cmap == 'tab20':
    colorcurr = pl.cm.tab20(np.linspace(0, 1, len(el_densities)))

jj=0    
# 1. Drift Length
for el_dens in el_densities:         
            epsn_x_from_bunch_monitor = []
            epsn_y_from_bunch_monitor = []          
            sigma_z_from_bunch_monitor = []
            mean_x_from_bunch_monitor = []
            mean_y_from_bunch_monitor = []          
            N_mp_from_bunch_monitor = []
            
            folder_curr_sim = os.path.join(args.root_folder, f"chroma_{args.chroma:02.0f}/sims/chroma_{args.chroma:02.0f}_eldens_{el_dens:.2e}")
            # print(folder_curr_sim)
            sim_curr_list = ps.sort_properly(glob.glob(folder_curr_sim+'/bunch_evolution_*.h5'))
            # print(sim_curr_list)

            if charge_weight_centroid_plots_flag:
                mean_x_from_slice_monitor = []
                mean_y_from_slice_monitor = []
                N_mp_from_slice_monitor = []
                sim_curr_list_slice_ev = ps.sort_properly(glob.glob(folder_curr_sim+'/slice_evolution_*.h5'))
                        
            print(sim_curr_list[0])
            
            try:                
                ob = mfm.monitorh5list_to_obj(sim_curr_list)
                epsn_x_from_bunch_monitor.append(ob.epsn_x)
                epsn_y_from_bunch_monitor.append(ob.epsn_y)
                mean_x_from_bunch_monitor.append(ob.mean_x)
                mean_y_from_bunch_monitor.append(ob.mean_y)
                sigma_z_from_bunch_monitor.append(ob.sigma_z)               
                N_mp_from_bunch_monitor.append(ob.macroparticlenumber)
                                
                # Compute the rms of the bunch centroid position weighted on the particle number per slice
                if charge_weight_centroid_plots_flag:                   
                    ob_slice = mfm.monitorh5list_to_obj(sim_curr_list_slice_ev, key='Slices', flag_transpose=True)
                    w_slices = ob_slice.n_macroparticles_per_slice
                    rms_x = np.sqrt(np.mean((ob_slice.mean_x * w_slices)**2, axis=0))
                    rms_y = np.sqrt(np.mean((ob_slice.mean_y * w_slices)**2, axis=0))               
                    mean_x_from_slice_monitor.append(rms_x)
                    mean_y_from_slice_monitor.append(rms_y)
                    N_mp_from_slice_monitor.append(np.sum(ob_slice.n_macroparticles_per_slice, axis=0))


            except IOError as goterror:
                print('Skipped. Got:',  goterror)
                
                epsn_x_from_bunch_monitor.append(-1) 
                epsn_y_from_bunch_monitor.append(-1)                
                mean_x_from_bunch_monitor.append(-1)
                mean_y_from_bunch_monitor.append(-1)                
                sigma_z_from_bunch_monitor.append(-1)               
                N_mp_from_bunch_monitor.append(-1)

                if charge_weight_centroid_plots_flag:   
                    mean_x_from_slice_monitor.append(-1)
                    mean_y_from_slice_monitor.append(-1)
                    N_mp_from_slice_monitor.append(-1)
                    
            epsn_x_from_bunch_monitor = np.squeeze(np.array(epsn_x_from_bunch_monitor))
            epsn_y_from_bunch_monitor = np.squeeze(np.array(epsn_y_from_bunch_monitor))
            mean_x_from_bunch_monitor = np.squeeze(np.array(mean_x_from_bunch_monitor))
            mean_y_from_bunch_monitor = np.squeeze(np.array(mean_y_from_bunch_monitor))
            sigma_z_from_bunch_monitor = np.squeeze(np.array(sigma_z_from_bunch_monitor))       
            N_mp_from_bunch_monitor = np.squeeze(np.array(N_mp_from_bunch_monitor))         
            mask_from_bunch = N_mp_from_bunch_monitor>0.
            mask_from_bunch = np.flatnonzero(mask_from_bunch)
            
            if charge_weight_centroid_plots_flag:   
                mean_x_from_slice_monitor = np.squeeze(np.array(mean_x_from_slice_monitor))
                mean_y_from_slice_monitor = np.squeeze(np.array(mean_y_from_slice_monitor))         
                N_mp_from_slice_monitor = np.squeeze(np.array(N_mp_from_slice_monitor))         
                mask_from_slice = N_mp_from_slice_monitor>0.            
            
            
            # check the successful sims 
            if epsn_x_from_bunch_monitor.size == 1:

                print(f"ERROR, SIMULATION FAILED. eldens_{el_dens:.2e})")
            
            else:

                # Moving average filter applied to the rms signal
                if charge_weight_centroid_plots_flag:
                    from scipy import signal
                    n_turns_win = 20
                    sig_x = mean_x_from_slice_monitor#[mask_from_slice]
                    sig_y = mean_y_from_slice_monitor#[mask_from_slice]
                    win = signal.windows.boxcar(n_turns_win)
                    filtered_x = signal.convolve(sig_x, win, mode='same') / np.sum(win)
                    filtered_y = signal.convolve(sig_y, win, mode='same') / np.sum(win)


                # Plot              
                tt = np.arange(0,ob.mean_x.shape[0],1)
                tt_from_slice = np.arange(0,ob_slice.mean_x.shape[1],1)

                sp1.plot(tt[mask_from_bunch], mean_x_from_bunch_monitor[mask_from_bunch]*1e3, color = colorcurr[jj])
                sp2.plot(tt[mask_from_bunch], mean_y_from_bunch_monitor[mask_from_bunch]*1e3, color = colorcurr[jj], 
                        label=f"{el_dens:.2e}")

                if charge_weight_centroid_plots_flag:               
                    sp3.plot(tt_from_slice[mask_from_slice], filtered_x[mask_from_slice], color = colorcurr[jj])
                    sp4.plot(tt_from_slice[mask_from_slice], filtered_y[mask_from_slice], color = colorcurr[jj])
                
                sp5.plot(tt[mask_from_bunch], epsn_x_from_bunch_monitor[mask_from_bunch]*1e6, color = colorcurr[jj])
                #sp4.set_ylim(2.9,3.5)
               
                sp6.plot(tt[mask_from_bunch], epsn_y_from_bunch_monitor[mask_from_bunch]*1e6, color = colorcurr[jj])

                # d(epsn_x/y)/dt
                dt = 1.0  # one turn; replace with physical time per turn

                epsx = epsn_x_from_bunch_monitor[mask_from_bunch]
                epsy = epsn_y_from_bunch_monitor[mask_from_bunch]
                t    = tt[mask_from_bunch] * dt

                depsx_dt = np.gradient(epsx, t)
                depsy_dt = np.gradient(epsy, t) 

                sp9.plot(t, depsx_dt * 1e6, color=colorcurr[jj])
                sp10.plot(t, depsy_dt * 1e6, color=colorcurr[jj])
                
                sp7.plot(tt[mask_from_bunch], N_mp_from_bunch_monitor[mask_from_bunch], color = colorcurr[jj])
                sp8.plot(tt[mask_from_bunch], sigma_z_from_bunch_monitor[mask_from_bunch]*4/clight*1e9, color = colorcurr[jj])



                legend = sp2.legend(bbox_to_anchor=(1.05, 1.03),  
                            loc='upper left', 
                            title='Electron Density [$m^{-1}$]', 
                            prop={'size':14}, ncol=1, 
                            borderpad=0.5, columnspacing=0.9, handlelength=0.16)
                
                
                
                legend.get_title().set_fontsize('16')
                jj=jj+1

                
# Set limits
sp1.set_ylim(-0.06, 0.06) 
sp3.set_ylim(0., 0.35) 
sp5.set_ylim(2.9, 3.4)          

for sp in [sp1, sp2]:
    sp.set_ylim(-2.0, 2.0)
    # sp.set_yscale('symlog',linthresh = 1) 

for sp in [sp3, sp4]:
    sp.set_ylim(0, 15.) 
    sp.set_yscale('symlog',linthresh = 1)  
    
for sp in [sp5, sp6]:
    sp.set_ylim(2.,70.) 
    sp.set_yscale('log')
    

# Set the label 
sp1.set_ylabel('Horizontal centroid position [mm]')
sp2.set_ylabel('Vertical centroid position [mm]')
sp3.set_ylabel('Charge weighted\nhorizontal centroid rms [a.u]')
sp4.set_ylabel('Charge weighted\nvertical centroid rms [a.u]')
sp5.set_ylabel('Normalized emittance x [um]')
sp6.set_ylabel('Normalized emittance y [um]')
sp7.set_ylabel('Number of macroparticles')
sp8.set_ylabel('Bunch length (4$\sigma$) [ns]')
sp9.set_ylabel(r'$d\epsilon_{n,x}/dt$ [$\mu$m/turn]')
sp10.set_ylabel(r'$d\epsilon_{n,y}/dt$ [$\mu$m/turn]')


#sp1.set_xlim(0, 1.0)
for sp in [sp1, sp2, sp3, sp4, sp5, sp6, sp7, sp8, sp9, sp10]:
    sp.set_xscale('symlog', linthresh=10)
    sp.set_xlim(left=0)
    # sp.ticklabel_format(useOffset=False)
    sp.set_xlabel('Turns')
    sp.minorticks_on()  # ensure minor ticks are on
    sp.xaxis.set_minor_locator(SymmetricalLogLocator(linthresh=10, base=10.0, subs=[1,2,3,4,5,6,7,8,9]))

    sp.grid(which='major', axis='both', linestyle='-', linewidth=0.5)
    sp.grid(which='minor', axis='both', linestyle=':', linewidth=0.3)
    # ms.sciy()
    #~ sp.set_xlim(0, 20000)

ms.mystyle_arial(14)  
gs1.tight_layout(fig, rect=[0.02, 0, 0.86, .95], w_pad=.2, h_pad=1.5)
#~ title = fig.suptitle(os.getcwd().split('/')[-2])
# title = fig.suptitle('Drift: Initial Kick yes   Initial e$^-$ Density = 12e11   V$_{RF}$ = 6 MV')
title = fig.suptitle(f'LHC 6.8 TeV, Dipole ecloud only, Chromaticity = {args.chroma:02.0f}, Intensity = 1.0e11 p+/bunch, Octupole = OFF')
#~ pl.title('ArcQuad Drift    Length = %.2f'%(fraction_device_quad))
if savefigures:
    fig.savefig(folder_plot + f'LHC_6.8TeV_Dipole_Instability_chroma_{args.chroma:02.0f}_electron_density_scan_cmap_{args.cmap}.png', dpi=500, 
        bbox_inches='tight', bbox_extra_artists=[legend, title])

if args.show:
    pl.show()

