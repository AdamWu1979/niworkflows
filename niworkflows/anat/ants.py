#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Nipype translation of ANTs workflows
------------------------------------

"""
from __future__ import print_function, division, absolute_import, unicode_literals

from multiprocessing import cpu_count
from ..nipype.pipeline import engine as pe
from ..nipype.interfaces import ants


def brain_extraction(name='antsBrainExtraction',
                     float=True,
                     debug=False,
                     random_seeding=True,
                     omp_nthreads=None,):
    """
    The official antsBrainExtraction.sh workflow converted into Nipype,
    only for 3D images.

    Inputs
    ------

    `in_file`
        The input anatomical image to be segmented, typically T1-weighted.
        If a list of anatomical images is provided, subsequently specified
        images are used during the segmentation process.
        However, only the first image is used in the registration of priors.
        Our suggestion would be to specify the T1w as the first image.


    `in_template`
        The brain template from which regions will be projected
        Anatomical template created using e.g. LPBA40 data set with
        buildtemplateparallel.sh in ANTs.

    `in_mask`
        Brain probability mask created using e.g. LPBA40 data set which
        have brain masks defined, and warped to anatomical template and
        averaged resulting in a probability image.

    Optional Inputs
    ---------------

    `in_segmentation_model`
        A k-means segmentation is run to find gray or white matter around
        the edge of the initial brain mask warped from the template.
        This produces a segmentation image with K classes, ordered by mean
        intensity in increasing order. With this option, you can control
        K and tell the script which classes represent CSF, gray and white matter.
        Format (K, csfLabel, gmLabel, wmLabel)
        Examples:
        -c 3,1,2,3 for T1 with K=3, CSF=1, GM=2, WM=3 (default)
        -c 3,3,2,1 for T2 with K=3, CSF=3, GM=2, WM=1
        -c 3,1,3,2 for FLAIR with K=3, CSF=1 GM=3, WM=2
        -c 4,4,2,3 uses K=4, CSF=4, GM=2, WM=3

    `registration_mask`
        Mask used for registration to limit the metric computation to
        a specific region.


    """
    wf = pe.Workflow(name)

    if omp_nthreads is None or omp_nthreads < 1:
        omp_nthreads = cpu_count()


    inputnode = pe.Node(niu.IdentityInterface(fields=['in_file', 'in_template', 'in_mask']),
                        name='inputnode')
    outputnode = pe.Node(niu.IdentityInterface(
        fields=['bias_corrected', 'out_file', 'out_mask', 'bias_image']), name='outputnode')

    inu_n4 = pe.MapNode(
        ants.N4BiasFieldCorrection(
            dimension=3, save_bias=True, num_threads=omp_nthreads, copy_header=True),
        n_procs=omp_nthreads, name='inu_n4', iterfield=['input_image'])



    return wf


def _list(in_files):
    if isinstance(in_files, (bytes, str)):
        return [in_files]
    return in_files
