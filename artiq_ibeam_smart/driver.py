#!/usr/bin/env python3

import abc
import asyncio
import logging
import time

import serial


class ArtiqIbeamSmartInterface(abc.ABC):
    @abc.abstractmethod
    async def set_channel_on(self, channel, channel_on):
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
        return response

    async def set_channel_on(self, channel, channel_on):
        """
        Change state of the channel.
        """
        if channel_on:
            self.send_command(f"en {channel}")
        else:
            self.send_command(f"di {channel}")

    async def set_channel_power(self, channel, power):
        """
        Set power[uW] of the channel .
        """
        self.send_command(f"ch {channel} pow {power} mic")

    async def get_channel_on(self, channel):
        """
        Reading the state of the channel.
        """
        return self.send_command(f"sta ch {channel}")

    async def get_channel_power(self, channel):  # TODO check actual output
        """
        Reading the power of the channel.
        """
        return self.send_command("sh level pow")

    def close(self):
        self.client.close()


class ArtiqIbeamSmartSim(ArtiqIbeamSmartInterface):
    def __init__(self):
        self.channel_on = 5 * [None]
        self.channel_power = 5 * [None]

    async def set_channel_on(self, channel, channel_on):
        """
        Simulate changing state of the channel.
        """
        self.channel_on[channel] = channel_on
        if channel_on:
            logging.warning(f"Simulated: Turning channel {channel} ON")
        else:
            logging.warning(f"Simulated: Turning channel {channel } OFF")

    async def set_channel_power(self, channel, power):
        """
        Simulate changing power of the channel.
        """
        self.channel_power[channel] = power
        logging.warning(f"Simulated: Setting channel {channel} power to {power}[uW]")

    async def get_channel_on(self, channel):
        """
        Simulate reading the state of the channel.
        """
        logging.warning(
            f"Simulated: Channel {channel} state redout {self.channel_on[channel]}"
        )
        return self.channel_on[channel]

    async def get_channel_power(self, channel):
        """
        Simulate reading the power of the channel.
        """
        logging.warning(
            f"Simulated: Channel {channel} power redout "
            f"{self.channel_power[channel]}[uW]"
        )
        return self.channel_power[channel]
