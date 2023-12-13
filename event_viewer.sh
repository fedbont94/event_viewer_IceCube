#! /bin/bash 
ENV_ICETRAY=/home/bontempo/work/icetray/build/env-shell.sh
GCD_FILE=/home/bontempo/work/gcd/GeoCalibDetectorStatus_2012.56063_V1_OctSnow.i3
# i3File=/home/bontempo/work/data_icetop/2012/Level3_IC86.2012_data_Run00122200_Subrun00000000_00000010.i3.bz2
i3File=/home/bontempo/work/data_icetop/2012/Level3_IC86.2012_SIBYLL2.1_p_12360_E6.9_0.i3.bz2

$ENV_ICETRAY python3 event_viewer.py $GCD_FILE $i3File \
--inice \
--particlekeys Laputop3s3s MCPrimary \
--paramskeys Laputop3s3sParams \
--frames P \
--IceTopKeys Laputop3s3sTankPulsesSelectedHLC Laputop3s3sTankPulsesSelectedSLC \
--InIceKeys Laputop3s3sCleanInIcePulses

# Laputop3s3sCleanInIcePulses
# Laputop3s3sTankPulsesSelectedHLC Laputop3s3sTankPulsesSelectedSLC