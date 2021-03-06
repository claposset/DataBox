#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
    MCC 118 Functions Demonstrated:
        mcc118.trigger_mode
        mcc118.a_in_status
        mcc118.a_in_scan_start
        mcc118.a_in_scan_read

    Purpose:
        Perform a triggered finite acquisition on 1 or more channels.

    Description:
        Waits for an external trigger to occur and then acquires blocks
        of analog input data for a user-specified group of channels.  The
        last sample of data for each channel is displayed for each block
        of data received from the device.  The acquisition is stopped when
        the specified number of samples is acquired for each channel.
"""
from __future__ import print_function
from time import sleep
from sys import stdout
from daqhats import mcc118, OptionFlags, TriggerModes, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask

CURSOR_BACK_2 = '\x1b[2D'
ERASE_TO_END_OF_LINE = '\x1b[0K'

def main():
    """
    This function is executed automatically when the module is run directly.
    """
    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    channels = [0, 1, 2, 3]
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)

    samples_per_channel = 10000
    scan_rate = 1000.0
    options = OptionFlags.EXTTRIGGER
    trigger_mode = TriggerModes.RISING_EDGE

    try:
        # Select an MCC 118 HAT device to use.
        address = select_hat_device(HatIDs.MCC_118)
        hat = mcc118(address)

        print('\nSelected MCC 118 HAT device at address', address)

        actual_scan_rate = hat.a_in_scan_actual_rate(num_channels, scan_rate)

        print('\nMCC 118 continuous scan example')
        print('    Functions demonstrated:')
        print('         mcc118.trigger_mode')
        print('         mcc118.a_in_scan_status')
        print('         mcc118.a_in_scan_start')
        print('         mcc118.a_in_scan_read')
        print('    Channels: ', end='')
        print(', '.join([str(chan) for chan in channels]))
        print('    Requested scan rate: ', scan_rate)
        print('    Actual scan rate: ', actual_scan_rate)
        print('    Samples per channel', samples_per_channel)
        print('    Options: ', enum_mask_to_string(OptionFlags, options))
        print('    Trigger Mode: ', trigger_mode.name)

        #try:
            #input('\nPress ENTER to continue ...')
        #except (NameError, SyntaxError):
            #pass

        hat.trigger_mode(trigger_mode)

        # Configure and start the scan.
        hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,
                            options)

        try:
            # wait for the external trigger to occur
            print('\nWaiting for trigger ... hit Ctrl-C to cancel the trigger')
            wait_for_trigger(hat)

            print('\nStarting scan ... Press Ctrl-C to stop\n')

            # Display the header row for the data table.
            print('Samples Read    Scan Count', end='')
            for chan in channels:
                print('    Channel ', chan, sep='', end='')
            print('')

            read_and_display_data(hat, samples_per_channel, num_channels)

        except KeyboardInterrupt:
            # Clear the '^C' from the display.
            print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)


def wait_for_trigger(hat):
    """
    Monitor the status of the specified HAT device in a loop until the
    triggered status is True or the running status is False.

    Args:
        hat (mcc118): The mcc118 HAT device object on which the status will
            be monitored.

    Returns:
        None

    """
    # Read the status only to determine when the trigger occurs.
    is_running = True
    is_triggered = False
    while is_running and not is_triggered:
        status = hat.a_in_scan_status()
        is_running = status.running
        is_triggered = status.triggered


def read_and_display_data(hat, samples_per_channel, num_channels):
    """
    Reads data from the specified channels on the specified DAQ HAT devices
    and updates the data on the terminal display.  The reads are executed in a
    loop that continues until either the scan completes or an overrun error
    is detected.

    Args:
        hat (mcc118): The mcc118 HAT device object.
        samples_per_channel: The number of samples to read for each channel.
        num_channels (int): The number of channels to display.

    Returns:
        None

    """
    total_samples_read = 0
    read_request_size = 500
    timeout = 5.0

    # Continuously update the display value until Ctrl-C is pressed
    # or the number of samples requested has been read.
    while total_samples_read < samples_per_channel:
        read_result = hat.a_in_scan_read(read_request_size, timeout)

        # Check for an overrun error
        if read_result.hardware_overrun:
            print('\n\nHardware overrun\n')
            break
        elif read_result.buffer_overrun:
            print('\n\nBuffer overrun\n')
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel

        # Display the last sample for each channel.
        print('\r{:12}'.format(samples_read_per_channel),
              ' {:12} '.format(total_samples_read), end='')

        if samples_read_per_channel > 0:
            index = samples_read_per_channel * num_channels - num_channels

            for i in range(num_channels):
                print('{:10.5f}'.format(read_result.data[index + i]), 'V ',
                      end='')
            stdout.flush()

            sleep(0.1)

    print('\n')


if __name__ == '__main__':
    main()
