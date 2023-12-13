#!/usr/bin/env python3

"""
----- IceTop / IceCube event viewer standalone -----
how to run:
    activate the IceTop environment
    python3 event_viewer.py GCDfile.i3(.gz) dataFile.i3(.gz)

    make sure to have the GCD file first (with and I3Geometry frame. NO I3GeometryDiff supported) and then the file(s) with Q and P frames..

In the MainLoop the files fed are read and the canvas in surface_canvas.py is called where all the plots are made.

__authors__ = 
    Federico Bontempo
    Alan Coleman
    Alex Olivas
Contact us on slack
"""

import argparse
from icecube.icetray.i3logging import log_fatal
from icecube import icetray, dataio

from util import surface_canvas

# Load the detector types
from util.Scintillator import Scintillator
from util.IceTop import IceTop
from util.Antenna import Antenna
from util.InIce import InIce

"""
This are the main 3 detectors on IceTop. 
In each class all the information are stored and the plots are updated.
e.g. IceTop are the all cherenkov tanks and in the class are stored info (geometry or the recorded pulses in the frame)
and plots like ldf are updated.
"""


def check_matplotlib_version():
    """
    Checks that the matplotlib version is at least 3.5.1
    The inice plots require this version to work
    """
    import matplotlib

    required_version = "3.5.1"
    if matplotlib.__version__ >= required_version:
        print("matplotlib version is at least 3.5.1")
    else:
        print(
            f"Error: matplotlib version {matplotlib.__version__} is below 3.5.1 (only version tested and working for the inice plots)"
        )
        print(f"Please upgrade matplotlib to version {required_version} or higher.")
        print("You can upgrade using the following command:")
        print("pip install --upgrade matplotlib")
        exit(1)


def get_args():
    parser = argparse.ArgumentParser(
        description="Render IceTop in matplotlib independent of steamshovel."
    )
    parser.add_argument("infile", nargs="+", help="Input I3File(s)")
    # Add the inice option
    parser.add_argument(
        "--inice", action="store_true", help="Do you want to show the inice plots?"
    )
    parser.add_argument(
        "--particlekeys",
        nargs="+",
        default=["Laputop", "LaputopSmall", "ScintReco", "MCPrimary", "CoREASPrimary"],
        help="Particle keys to show",
    )
    parser.add_argument(
        "--paramskeys",
        nargs="+",
        default=["LaputopParams", "LaputopSmallParams"],
        help="Parameter keys to show",
    )
    parser.add_argument(
        "--frames",
        default="QP",
        help="Frames to show. Q for DAQ, P for Physics, QP for both",
        type=str,
    )
    parser.add_argument(
        "--IceTopKeys",
        help="IceTop keys to show",
        nargs="+",
    )
    parser.add_argument(
        "--InIceKeys",
        help="InIce keys to show",
        nargs="+",
    )
    parser.add_argument(
        "--AntennaKeys",
        help="Antenna keys to show",
        nargs="+",
    )
    parser.add_argument(
        "--ScintillatorKeys",
        help="Scintillator keys to show",
        nargs="+",
    )
    args = parser.parse_args()
    return args


def ParseOptions(frame, particleKeys, paramsKeys, detectors, framesOfChoise):
    print("Option to change:")
    print("0: keys in frame")
    print("1: particles and parameters")
    print("2: frames")

    nNonDetectorOptions = 3
    for idet, det in enumerate(detectors):
        print("{}: {}".format(idet + nNonDetectorOptions, det.GetKeyName()))

    user_response = input("Enter number: ")
    print("")

    choice = int(user_response)

    if choice == 0:
        print(frame.keys())
    elif choice == 1:
        print("0: particles" + "\n1: parameters")
        user_response = input("Enter number: ")
        if int(user_response) == 0:
            print("Available particles:")
            for line in str(frame).split("\n"):
                if "I3Particle" in line:
                    print("\t", line.split()[0])
            print("Current particles are", particleKeys)
            user_response = input(
                "Enter desired keys. Note first particle will be used to draw LDFs: "
            )
            partKeys = user_response.split()
            particleKeys.clear()
            for key in partKeys:
                if key != "":
                    particleKeys.append(key)
            print("Particle keys set to", particleKeys)
        elif int(user_response) == 1:
            print("Current parameters keys are", paramsKeys)
            user_response = input("Enter desired parameters keys: ")
            parKeys = user_response.split()
            paramsKeys.clear()
            for key in parKeys:
                if key != "":
                    print(key)
                    paramsKeys.append(key)
            print("Parameters keys set to", paramsKeys)
        else:
            return
    elif choice == 2:
        print("Currently viewing frames:", framesOfChoise)
        user_response = input(
            "Chose:\n1: (Q) Frames\n2: (P) Frames\n3: (Q) and (P) Frames\nEnter number: "
        )
        framesOfChoise = [
            [icetray.I3Frame.DAQ],
            [icetray.I3Frame.Physics],
            [icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
        ]
        # global framesToView
        framesToView = framesOfChoise[int(user_response) - 1]
        return framesToView
    elif nNonDetectorOptions <= choice < len(detectors) + nNonDetectorOptions:
        detectors[choice - nNonDetectorOptions].GetDrawOptions(frame)
    else:
        return


def set_detector_keys(detectors, args):
    for det in detectors:
        if (det.GetKeyName() == "IceTop") & (args.IceTopKeys is not None):
            det.pulsekeys = args.IceTopKeys
        elif (det.GetKeyName() == "InIce") & (args.InIceKeys is not None):
            det.pulsekeys = args.InIceKeys
        elif (det.GetKeyName() == "Antenna") & (args.AntennaKeys is not None):
            det.pulsekeys = args.AntennaKeys
        elif (det.GetKeyName() == "Scintillator") & (args.ScintillatorKeys is not None):
            det.pulsekeys = args.ScintillatorKeys
        else:
            Warning("No keys for detector: ", det.GetKeyName())
            continue
    return detectors


def MainLoop():
    args = get_args()
    detectors = [Scintillator(), IceTop(), Antenna()]
    if args.inice:
        check_matplotlib_version()
        detectors.append(InIce())
    detectors = set_detector_keys(detectors, args)

    particleKeys = args.particlekeys
    paramsKeys = args.paramskeys

    framesToView = []
    if "Q" in args.frames.upper():
        framesToView.append(icetray.I3Frame.DAQ)
    if "P" in args.frames.upper():
        framesToView.append(icetray.I3Frame.Physics)

    canvas = surface_canvas.SurfaceCanvas(detectors, particleKeys, paramsKeys)
    canvas.fig.show()
    cid = canvas.fig.canvas.mpl_connect("button_press_event", canvas.ArrayOnClick)
    gFrameSeen = False
    for file in args.infile:
        for frame in dataio.I3File(file):
            if frame.Stop == icetray.I3Frame.Geometry:
                if "I3GeometryDiff" in frame.keys():
                    Warning(
                        "I3GeometryDiff is not supported. Please use a GCD file without I3GeometryDiff."
                    )
                    continue
                gFrameSeen = True
                print("You are visualizing a %s frame" % frame.Stop)

                canvas.update_geometry_frame(frame)
            elif frame.Stop in framesToView:
                if not gFrameSeen:
                    log_fatal(
                        "While reading {}, hit a {} frame before finding a Geometry frame. \n"
                        "Please feed a GCD file first.".format(file, frame.Stop)
                    )
                print("You are visualizing a %s frame" % frame.Stop)

                canvas.update_DAQ_or_P_frame(frame)
            else:
                continue

            canvas.fig.canvas.draw()

            while True:
                user_response = input(
                    "Enter:\n "
                    "q to quit,\n "
                    "return to continue,\n "
                    "r to refresh,\n "
                    "s to save,\n "
                    "or o for options:\n"
                )

                if user_response.lower() == "q":
                    exit()
                elif user_response.lower() == "o":
                    temp_frames = ParseOptions(
                        frame,
                        canvas.particleKeys,
                        canvas.paramsKeys,
                        canvas.detectors,
                        framesToView,
                    )
                    if temp_frames is not None:
                        framesToView = temp_frames

                elif user_response.lower() == "r":
                    if frame.Stop == icetray.I3Frame.Geometry:
                        canvas.update_geometry_frame(frame)
                    elif frame.Stop in framesToView:
                        canvas.update_DAQ_or_P_frame(frame)
                    canvas.fig.canvas.draw()
                elif user_response.lower() == "s":
                    user_response = input(
                        "Enter path to save + file name (e.g. /home/user/img.png(.pdf)): "
                    )
                    canvas.fig.savefig(str(user_response), bbox_inches="tight")
                    print("Image saved to: ", str(user_response))
                else:
                    break


if __name__ == "__main__":
    print("Welcome to the IceTop / IceCube event viewer!")

    MainLoop()

    print("Last frame of last file completed!")
