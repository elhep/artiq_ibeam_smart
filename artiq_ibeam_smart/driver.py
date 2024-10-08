#!/usr/bin/env python3

import abc
import asyncio
import logging
import re
import serial_asyncio
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
        self.reader = None
        self.writer = None
        self.available_channels = [1, 2]

    async def _ensure_connection(self):
        """Ensure the serial connection is established."""
        if self.reader is None or self.writer is None:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.serial_device,
                baudrate=115200,
                bytesize=8,          # EIGHTBITS equivalent
                parity='N',          # PARITY_NONE equivalent
                stopbits=1           # STOPBITS_ONE equivalent
            )

    async def send_command(self, command):
        """Send the command via serial connection."""
        await self._ensure_connection()
        self.writer.write((command + "\r\n").encode())
        await self.writer.drain()  # Ensure the command is sent out
        await asyncio.sleep(5)  # Give some time for the device to process the command
        response = await self._read_response()
        return response

    async def _read_response(self):
        """Read the response from the serial connection asynchronously."""
        response = await self.reader.read(1024)
        return response.decode()

    async def set_channel_on(self, channel, channel_on):
        """Change state of the channel."""
        if channel not in self.available_channels:
            raise ValueError("Channel out of range")
        if channel_on:
            await self.send_command(f"en {channel}")
        else:
            await self.send_command(f"di {channel}")

    async def set_channel_power(self, channel, power):
        """Set power[uW] of the channel."""
        if channel not in self.available_channels:
            raise ValueError("Channel out of range")
        await self.send_command(f"ch {channel} pow {power} mic")

    async def get_channel_on(self, channel):
        """Read the state of the channel."""
        if channel not in self.available_channels:
            raise ValueError("Channel out of range")
        ret = await self.send_command(f"sta ch {channel}")
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
        pattern = rf"CH{channel}, PWR:\s*([\d\.]+)\s*(\w+)"
        match = re.search(pattern, response)

        if match:
            power_value = match.group(1)
            units = match.group(2)
            return f"{power_value} {units}"
        else:
            raise ValueError(
                f"Power output for channel {channel} not found in the response."
            )

    async def get_channel_power(self, channel):
        """Read the power of the channel."""
        if channel not in self.available_channels:
            raise ValueError("Channel out of range")
        ret = await self.send_command("sh level pow")
        power = self.extract_channel_power(channel, ret)
        return power

    async def close(self):
        """Close the serial connection asynchronously."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = None
            self.writer = None



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
