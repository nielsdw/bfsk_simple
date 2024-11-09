#!/home/niels/svenv/bin/python
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.10.1.1

# from packaging.version import Version as StrictVersion

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio import digital
import pmt
import osmosdr
import time
import json
from amqpwrap.consumer import amqp_listener


class top_block_bfsk(gr.top_block):

    def __init__(self,
                 center_freq=435200E3,
                 input_=None):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        self.center_freq = center_freq
        self.input_ = input_

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000

        ##################################################
        # Blocks
        ##################################################

        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=500,
                decimation=100,
                taps=[],
                fractional_bw=0.4)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + 'hackrf'
        )
        self.osmosdr_sink_0.set_time_now(osmosdr.time_spec_t(time.time()), osmosdr.ALL_MBOARDS)
        self.osmosdr_sink_0.set_sample_rate(2e6)
        self.osmosdr_sink_0.set_center_freq(self.center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(45, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.digital_gfsk_mod_0 = digital.gfsk_mod(
            samples_per_symbol=2,
            sensitivity=0.6,
            bt=0.3,
            verbose=False,
            log=False,
            do_unpack=False)
        self.blocks_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(8)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, self.input_, True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_unpack_k_bits_bb_0, 0))
        self.connect((self.blocks_unpack_k_bits_bb_0, 0), (self.digital_gfsk_mod_0, 0))
        self.connect((self.digital_gfsk_mod_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))




class top_block_fm(gr.top_block):

    def __init__(self,
                 center_freq=435200E3,
                 max_dev=50e3,
                 dec=10,
                 ctcss=0.0,
                 ctcss_freq=88.5,
                 input_=None,
                 repeat=False):

        gr.top_block.__init__(self, "Top Block", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 9000E3
        self.center_freq = center_freq
        self.max_dev = max_dev
        self.input_ = input_
        self.dec = int(dec)
        self.ctcss = float(ctcss)
        self.ctcss_freq = float(ctcss_freq)
        self.repeat = repeat
        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=375,
                decimation=self.dec,
                taps=[],
                fractional_bw=0)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + 'hackrf'
        )
        self.osmosdr_sink_0.set_time_now(osmosdr.time_spec_t(time.time()), osmosdr.ALL_MBOARDS)
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(center_freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(0, 0)
        self.osmosdr_sink_0.set_if_gain(200, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_source_0 = blocks.wavfile_source(self.input_, self.repeat) \
            if self.input_ != 'monitor' \
            else audio.source(48000, 'default', True)
        self.analog_wfm_tx_0 = analog.wfm_tx(
            audio_rate=int(48E3),
            quad_rate=int(480E3),
            tau=50E-6,
            max_dev=self.max_dev,
            fh=-1.0,
        )
        self.analog_sig_source_x_0 = analog.sig_source_f(48000, analog.GR_COS_WAVE, self.ctcss_freq, self.ctcss, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_wfm_tx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.audio_source_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_wfm_tx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.osmosdr_sink_0, 0))


tb = None

def main(options=None):
    repeat = True

    @amqp_listener(queue='hackrf')
    def set_freq(body, _):
        global tb
        values = json.loads(body.decode())
        print(values)
        # {'mod': 5000,
        #  'freq': 470000000,
        #  'name': 'HackRF',
        #  'input': 'silence.wav',
        #  'state': True,
        #  'ctcss_freq': 88.5,
        #  'ctcss_part': 0.0}
        if values.get("state") is False and tb is not None:
            tb.stop()
            tb.wait()
            tb = None
        if values.get("state") and tb is None and values.get("name") == "hackrf fm":
            dev = values.get("mod")
            frequency = values.get("freq")
            dec = 20
            ctcss = values.get("ctcss_part")
            ctcss_freq = values.get("ctcss_freq")
            input_ = values.get("input")
            tb = top_block_fm(center_freq=frequency,
                               max_dev=dev, dec=dec,
                               ctcss=ctcss, ctcss_freq=ctcss_freq,
                               input_=input_, repeat=repeat)
            tb.start()
        if values.get("state") and tb is None and values.get("name") == "hackrf bfsk":
            frequency = values.get("freq")
            input_ = values.get("input")
            tb = top_block_bfsk(center_freq=frequency,
                                input_=input_)
            tb.start()

if __name__ == '__main__':
    main()
