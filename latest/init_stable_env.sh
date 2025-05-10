
# Initialization for MRI processing

ss;
. neuro-fs stable 6.0;
FSLDIR=/neuro/users/${USER}/arch/Linux64/packages/fsl/6.0;
. ${FSLDIR}/etc/fslconf/fsl.sh;
PATH=${FSLDIR}/bin:${PATH};
export FSLDIR PATH;
source /neuro/labs/grantlab/research/HyukJin_MRI/CIVET/quarantines/Linux-x86_64/init.sh

