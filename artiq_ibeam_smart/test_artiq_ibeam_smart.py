import sys

from sipyco.test.generic_rpc import GenericRPCCase


class GenericIbeamSmartTest:
    def test_set_channel_on(self):
        channel_on = True
        channel = 1
        self.artiq_ibeam_smart.set_channel_on(channel, channel_on)
        self.assertEqual(channel_on, self.artiq_ibeam_smart.get_channel_on(channel))

    def test_set_channel_power(self):
        power = 30
        channel = 2
        self.artiq_ibeam_smart.set_channel_power(channel, power)
        self.assertEqual(power, self.artiq_ibeam_smart.get_channel_power(channel))


class TestIbeamSmartSim(GenericRPCCase, GenericIbeamSmartTest):
    def setUp(self):
        GenericRPCCase.setUp(self)
        command = (
            sys.executable.replace("\\", "\\\\")
            + " -m artiq_ibeam_smart.aqctl_artiq_ibeam_smart"
            + " -p 3281 --simulation"
        )
        self.artiq_ibeam_smart = self.start_server("artiq_ibeam_smart", command, 3281)
