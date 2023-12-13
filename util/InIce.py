from .Detector import Detector, PulseData

from .GeometryTools import get_radius

import numpy as np

from icecube import icetray
from icecube.icetray import I3Units
from icecube.dataclasses import I3Constants

from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib import colors, cm

from icecube.recclasses import I3LaputopParams
from icecube.recclasses import LaputopLDF
from icecube.recclasses import LaputopParameter
from icecube.recclasses import LaputopFrontDelay
from icecube.recclasses import LaputopEnergy


class InIce(Detector):
    """docstring for InIce"""

    def __init__(self):
        super(InIce, self).__init__()
        self.pulsekeys = self.GetDefaultPulseKeys()
        self.color = "k"
        self.name = "InIce"
        self.minPatchSize = 5
        self.maxPatchSize = self.minPatchSize * 5
        self.time_delay = []
        self.tanks_position_patches = PatchCollection([])
        self.tanks_pulse_patches = PatchCollection([])

    def GetDefaultPulseKeys(self):
        return ["InIcePulses"]

    def GetKeyName(self):
        return self.name

    def ExtractFromGFrame(self, frame):
        assert frame.Stop == icetray.I3Frame.Geometry

        self.positions.clear()

        # Check all things in geometry frame I3Geometry
        for key in frame.keys():
            if key == "I3GeometryDiff":
                continue
            i3geometry = frame[key]
            for omkey, om in i3geometry.omgeo:
                pos = om.position
                self.positions[(omkey)] = np.asarray((pos.x, pos.y, pos.z))

    def DrawGeometry(self, ax):
        return

    def Draw3dGeometry(self, ax):
        # Get the positions of the tanks
        # as lists of x, y, z coordinates
        x, y, z = zip(*self.positions.values())

        ax.scatter(
            x,
            y,
            z,
            marker="o",
            s=self.minPatchSize,
            edgecolor="None",
            facecolor=self.color,
            alpha=0.5,
        )

        amps = []
        positions = []
        time = []
        pulses_patches = []

        for ikey, framekey in enumerate(self.measuredData.keys()):
            pulses = self.measuredData[framekey]
            for omkey in pulses.keys():
                pulse = pulses[omkey]
                pos = self.positions[(omkey)]
                totalCharge = sum([p.charge for p in pulse])

                positions.append(pos)
                amps.append(totalCharge)
                time.append(pulse[0].t)

        if not len(amps):
            return

        amps = np.log10(amps)
        minAmp = min(amps)
        maxAmp = max(amps)

        relPatchSize = self.minPatchSize * 20.0 + (
            self.maxPatchSize - self.minPatchSize * 20.0
        ) * (amps - minAmp) / (maxAmp - minAmp + 0.01)

        # The color map is used for  showing the time delay of the pulses.
        # The time is set to 0 by subtracting the min and then it is normalized by dividing the max
        cmap = cm.get_cmap(self.colorMapType)
        time = np.subtract(time, min(time))
        time = np.divide(time, max(time))
        time = cmap(time)
        x, y, z = zip(*positions)
        ax.scatter(
            x,
            y,
            z,
            marker="o",
            s=relPatchSize,
            edgecolor="None",
            facecolor=time,
            alpha=0.5,
        )

    def ExtractFromQPFrame(self, frame):
        self.measuredData.clear()
        self.laputopParams = None

        for framekey in self.pulsekeys:
            if framekey in frame.keys():
                # gets Tank Pulses and stores them in a dict with the detector key for the unique geometry match
                try:
                    try:
                        recopulse_map = frame[framekey]
                        _ = len(recopulse_map)
                    except:
                        recopulse_map = frame[framekey].apply(frame)
                        _ = len(recopulse_map)
                except:
                    Warning(f"Could not extract pulses {framekey} from frame")
                    continue

                if not len(recopulse_map):
                    continue
                pulses = {}
                for omkey in recopulse_map.keys():
                    pulses_per_tank = []
                    for pulse in recopulse_map[omkey]:
                        pulses_per_tank.append(
                            PulseData(pulse.time, pulse.charge, True)
                        )

                    pulses[omkey] = pulses_per_tank
                self.measuredData[framekey] = pulses

        if "LaputopParams" in frame.keys():
            self.laputopParams = I3LaputopParams.from_frame(frame, "LaputopParams")

    def DrawLDF(self, ax, particle):
        return

    def DrawShowerFront(self, ax, particle):
        return

    def GetDrawOptions(self, frame):
        print("Current pulse keys are", self.pulsekeys)
        user_response = input("Enter desired keys: ")
        partKeys = user_response.split()

        self.pulsekeys = []
        for key in partKeys:
            if key != "":
                self.pulsekeys.append(key)

        print(self.name, "keys set to", self.pulsekeys)

    def ToggleHidden(self):
        self.shouldDraw = not self.shouldDraw
        self.tanks_position_patches.set_visible(self.shouldDraw)
        self.tanks_pulse_patches.set_visible(self.shouldDraw)
