#!/bin/bash

### add arguments 

IN=$1
IN=${IN::-4}

#/neuro/labs/grantlab/research/HyukJin_MRI/code/obj2asc "${IN}.obj" "${IN}.asc"
/neuro/labs/grantlab/research/HyukJin_MRI/code/obj2asc "${IN}.obj" "${IN}.asc"
mris_convert "${IN}.asc" "${IN}.gii"



