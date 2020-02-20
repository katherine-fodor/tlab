#include "types.h"

MODULE DNS_LOCAL
  USE DNS_TYPES,  ONLY : filter_dt, grid_dt
  USE DNS_GLOBAL, ONLY : MAX_NSP
#ifdef USE_PSFFT  
  USE NB3DFFT,    ONLY : NB3DFFT_SCHEDLTYPE
#endif
  IMPLICIT NONE
  SAVE

  TINTEGER, PARAMETER :: MAX_SAVEPLANES = 20

! ###################################################################
! Iteration
! ###################################################################
  TINTEGER :: rkm_mode, rkm_substep, rkm_endstep
  TREAL    :: cfl, dtime
  TINTEGER :: nitera_first, nitera_last, nitera_save, nitera_stats, nitera_log, nitera_pln
  TINTEGER :: nitera_stats_spa ! Accumulate statistics in spatial mode

  TINTEGER :: idivergence, imode_rhs 

! ###################################################################
! Control 
! ###################################################################
  TINTEGER :: ilimit_flow, ilimit_scal
  TREAL    :: p_bound_min, p_bound_max, r_bound_min, r_bound_max ! pressure and density
  TREAL    :: s_bound_min(MAX_NSP), s_bound_max(MAX_NSP)         ! scalars
  TREAL    :: d_bound_max                                        ! dilatation

! ###################################################################
! Variable viscosity
! ###################################################################
  TREAL    :: visctime, viscstart, viscstop
  TINTEGER :: iviscchg

! ###########################################################
! Filters
! ###########################################################
  TINTEGER :: FilterDomainStep

! ###################################################################
! Output data
! ###################################################################
  TINTEGER                            :: nplanes_i, nplanes_j, nplanes_k, pplanes_j, nplanes_j_aux ! Planes
  TINTEGER, DIMENSION(MAX_SAVEPLANES) :: planes_i,  planes_j,  planes_k
  
  TINTEGER, DIMENSION(3)              :: tower_stride           ! Towers
  TINTEGER                            :: tower_mode  

! ###################################################################
  TREAL    :: logs_data(20)

! ###################################################################
! NB3DFFT library
! ###################################################################
#ifdef USE_PSFFT  
  TYPE(NB3DFFT_SCHEDLTYPE), SAVE :: nbcsetup
#endif 

END MODULE DNS_LOCAL
