#!/usr/bin/env python3

import abc
import asyncio
import logging
import re
import time

import serial


class ArtiqIbeamSmartInterface(abc.ABC):
    @abc.abstractmethod
    async def set_channel_on(self, channel, channel_on):
        pass

    @abc.abstractmethod
    async def set_laser_on(self, laser_on):
        pass

    @abc.abstractmethod
    async def set_channel_power(self, channel, power):
        pass

    @abc.abstractmethod
    async def get_channel_on(self, channel):
        pass

    @abc.abstractmethod
    async def get_channel_power(self, channel):
        pass

    async def ping(self):
        return True

    def close(self):
        pass


class ArtiqIbeamSmart(ArtiqIbeamSmartInterface):
    def __init__(self, serial_device):
        self.serial_device = serial_device
        """
        Configure the serial connection.
        """
        self.serial_connection = serial.Serial(
            port=serial_device,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
        )

    def send_command(self, command):
        """
        Send the command via serial connection.
        """
        self.serial_connection.write((command + "\r\n").encode())
        time.sleep(0.5)
        response = self.serial_connection.read_all().decode()
        self.check_for_errors(response)
        return response

    def check_for_errors(self, response):
        """
        Checks for any warning, error, or fatal in the response and raises an exception
        if found.
        """
        keywords = ["%SYS-W-", "%SYS-E-", "%SYS-F-"]
        lines = response.splitlines()

        for line in lines:
            for keyword in keywords:
                if keyword in line:
                    message = line.strip()
                    raise ValueError(f"{message}")

    async def set_channel_on(self, channel, channel_on):
        """
        Change state of the channel.
        """
        if channel_on:
            self.send_command(f"en {channel}")
        else:
            self.send_command(f"di {channel}")

    async def set_laser_on(self, laser_on):
        """
        Change state of the laser diode.
        """
        if laser_on:
            self.send_command(f"la on")
        else:
            self.send_command(f"la off")

    async def set_channel_power(self, channel, power):
        """
        Set power[uW] of the channel .
        """
        self.send_command(f"ch {channel} pow {power} mic")

    async def get_channel_on(self, channel):
        """
        Reading the state of the channel.
        """
        ret = self.send_command(f"sta ch {channel}")
        if "ON" in ret:
            return 1
        elif "OFF" in ret:
            return 0
        else:
            raise ValueError(f"Unexpected return value: {ret}")

    def extract_channel_power(self, channel, response):
        """
        Extract the power output for a specified channel from the response.
        :param response: The response string from the device.
        :param channel: The channel number (e.g., 1 or 2).
        :return: The power output as a float.
        :raises ValueError: If the channel is not found or the power value is invalid.
        """
        pattern = rf"CH{channel}, PWR:\s*(-?[\d\.]+)\s*(\w+)"
        match = re.search(pattern, response)

        if match:
            power_value = match.group(1)
            units = match.group(2)
            if units == "mW":
                return float(power_value)
            elif units == "uW":
                return float(power_value) / 1000
            else:
                raise ValueError(f"Invalid units: {units}")
        else:
            # Raise an error if the channel's power output is not found.
            raise ValueError(
                f"Power output for channel {channel} not found in the response."
            )

    async def get_channel_power(self, channel):  # TODO check actual output
        """
        Reading the power of the channel.
        """
        ret = self.send_command("sh level pow")
        power = self.extract_channel_power(channel, ret)
        return power
    
    def ping(self):
        """
        Sends a "serial" command to the device and checks if the response 
        starts with "SN: iBEAM-SMART".

        :return: True if the response identifier starts with "SN: iBEAM-SMART", 
                  False otherwise.
        """
        identifier = self.send_command("serial")
        return identifier.startswith("SN: iBEAM-SMART")

    def close(self):
        self.serial_connection.close()


class ArtiqIbeamSmartSim(ArtiqIbeamSmartInterface):
    def __init__(self):
        self.channel_on = 2 * [None]
        self.channel_power = 2 * [None]

    def convert_channel(self, channel):
        conv_channel = channel - 1
        if conv_channel not in [0, 1]:
            raise ValueError("Channel out of range")
        return conv_channel

    async def set_channel_on(self, channel, channel_on):
        """
        Simulate changing state of the channel.
        """
        self.channel_on[self.convert_channel(channel)] = channel_on
        if channel_on:
            logging.warning(f"Simulated: Turning channel {channel} ON")
        else:
            logging.warning(f"Simulated: Turning channel {channel } OFF")

    async def set_channel_power(self, channel, power):
        """
        Simulate changing power of the channel.
        """
        self.channel_power[self.convert_channel(channel)] = power
        logging.warning(f"Simulated: Setting channel {channel} power to {power}[uW]")

    async def get_channel_on(self, channel):
        """
        Simulate reading the state of the channel.
        """
        conv_channel = self.convert_channel(channel)
        logging.warning(
            f"Simulated: Channel {channel} state redout {self.channel_on[conv_channel]}"
        )
        return self.channel_on[conv_channel]

    async def get_channel_power(self, channel):
        """
        Simulate reading the power of the channel.
        """
        conv_channel = self.convert_channel(channel)
        logging.warning(
            f"Simulated: Channel {channel} power redout "
            f"{self.channel_power[conv_channel]}[uW]"
        )
        return self.channel_power[conv_channel]
