#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: niels
# GNU Radio version: 3.10.1.1

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
import sys
import signal
import osmosdr
import time
from bitarray import bitarray


def tail_f_bits_with_delimiters(file_path, start_bits, end_bits):
    with open(file_path, 'rb') as f:
        f.seek(0, 2)  # Move to the end of file

        bit_buffer = bitarray()
        collecting = False
        data_bits_buffer = bitarray()

        # Convert start and end bits to bitarray
        start_bitarray = bitarray(start_bits)
        end_bitarray = bitarray(end_bits)

        while True:
            chunk = f.read(1024)
            if not chunk:
                time.sleep(0.1)
                continue

            # Convert bytes to bits and append to bit_buffer
            bits = bitarray()
            bits.frombytes(chunk)
            bit_buffer.extend(bits)

            # Process the bit buffer
            while True:
                if not collecting:
                    # Search for start_bits in bit_buffer
                    idx = bit_buffer.search(start_bitarray)
                    if idx:
                        collecting = True
                        index = idx[0] + len(start_bitarray)
                        bit_buffer = bit_buffer[index:]
                        data_bits_buffer.clear()
                    else:
                        # Keep last len(start_bits)-1 bits in case start_bits is split
                        bit_buffer = bit_buffer[-(len(start_bitarray) - 1):]
                        break  # Need more data
                else:
                    # Search for end_bits in bit_buffer
                    idx = bit_buffer.search(end_bitarray)
                    if idx:
                        data_bits_buffer.extend(bit_buffer[:idx[0]])
                        # Convert bits to bytes
                        data_bytes = data_bits_buffer.tobytes()
                        # Output the collected data
                        print(data_bytes.decode('utf-8', errors='replace'))
                        # Reset for next sequence
                        collecting = False
                        index = idx[0] + len(end_bitarray)
                        bit_buffer = bit_buffer[index:]
                        data_bits_buffer.clear()
                    else:
                        # Accumulate data bits
                        data_bits_buffer.extend(bit_buffer)
                        # Clear bit_buffer to read more data
                        bit_buffer.clear()
                        break  # Need more data


class bfsk_recv(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=100,
                decimation=500,
                taps=[],
                fractional_bw=0.4)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'rtlsdr'
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(2e6)
        self.osmosdr_source_0.set_center_freq(438e6, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.digital_gfsk_demod_0 = digital.gfsk_demod(
            samples_per_symbol=2,
            sensitivity=0.6,
            gain_mu=0.175,
            mu=0.5,
            omega_relative_limit=0.005,
            freq_error=0.0,
            verbose=False,
            log=False)
        self.blocks_pack_k_bits_bb_0 = blocks.pack_k_bits_bb(8)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, '/home/niels/top_block_data_f3jntn34y654y_', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_pack_k_bits_bb_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.digital_gfsk_demod_0, 0), (self.blocks_pack_k_bits_bb_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.digital_gfsk_demod_0, 0))


def main(options=None):

    tb = bfsk_recv()

    tb.start()
    file_path = '/home/niels/top_block_data_f3jntn34y654y_'

    # Define the start and end bit patterns for "AAAA" and "BBBB"
    start_bits = '01000001010000010100000101000001'  # "AAAA"
    end_bits = '01000010010000100100001001000010'  # "BBBB"

    while True:
        try:
            tail_f_bits_with_delimiters(file_path, start_bits, end_bits)
            time.sleep(1)
        except KeyboardInterrupt:
            tb.stop()
            break

if __name__ == '__main__':
    main()
