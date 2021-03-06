print(__file__)

"""plans"""


def demo_darks_flats_images(det, darks=1, whites=1, images=1):
    """
    plan: test that detector is configured to take darks, flats, then images
    
    demo of issue #27
    
    RE(demo_darks_flats_images())
    """

    def shoot(fr_type, num=1, expected=None):
        expected = expected or num
        yield from bps.mv(
            det.cam.frame_type, fr_type,
            det.cam.num_images, num,
            det.cam.trigger_mode, "Internal",
        )
        yield from bps.trigger(det)
        while det.hdf1.num_captured.value < expected:
            yield from bps.sleep(0.01)
   
    yield from bps.mv(
        det.hdf1.num_capture, darks+whites+images,
        det.hdf1.compression, "zlib",
    )
    print("det.hdf1.num_capture", det.hdf1.num_capture.value)
    yield from bps.stage(det)

    print("%d dark frames" % darks)
    yield from shoot(1, darks, darks)

    print("%d white frames" % whites)
    yield from shoot(2, whites, darks+whites)

    print("%d image frames" % images)
    yield from shoot(0, images, darks+whites+images)

    print("waiting for HDF5 writer to finish")
    # instead of setting det.hdf1.blocking_callbacks to "Yes"
    while det.hdf1.capture.value != 0:
        yield from bps.sleep(0.01)

    yield from bps.unstage(det)

    yield from bps.mv(
        det.hdf1.num_capture, 1,
        det.cam.num_images, 1,
        det.hdf1.compression, "None",
    )
