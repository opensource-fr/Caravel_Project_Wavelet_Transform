import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout
import math
import random
import wave
import struct

# takes ~60 seconds on my PC

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    dut.RSTB.value = 0
    dut.power1.value = 0;
    dut.power2.value = 0;
    dut.power3.value = 0;
    dut.power4.value = 0;

    await ClockCycles(dut.clk, 8)
    dut.power1.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power2.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power3.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power4.value = 1;

    await ClockCycles(dut.clk, 80)
    dut.RSTB.value = 1

    # Before starting first module test wait for sequence of falling then
    # running edge of 'o_active' signal.
    await with_timeout(FallingEdge(dut.o_active), 700, 'us')
    await with_timeout(RisingEdge(dut.o_active), 700, 'us')

@cocotb.test()
async def test_audio(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    # These should be held low by default
    dut.i_data_clk.value = 0
    dut.i_value.value = 0
    dut.i_select_output_channel.value = 0

    await RisingEdge(dut.clk)

    # output should be zero if prior values are zero
    assert dut.o_multiplexed_wavelet_out == 0

    # audio input setup
    audio_in = wave.open("./wavs/hello.wav")
    nframes = audio_in.getnframes()
    print("sending %d frames" % nframes)

    # audio output setup
    audio_out = wave.open("./wavs/out.wav", "wb")
    audio_out.setnchannels(audio_in.getnchannels())
    audio_out.setsampwidth(audio_in.getnchannels())
    audio_out.setframerate(audio_in.getframerate())

    # values for switching the output channel
    channel_select = 0
    channel_select_counter = 200

    # process audio through dut
    for i in range(nframes):
        await RisingEdge(dut.clk)

        frame = audio_in.readframes(1)
        (val,) = struct.unpack("h", frame)

        if channel_select_counter == 0:
            channel_select += 1
            dut.i_select_output_channel.value = channel_select % 8
            channel_select_counter = 200
        else:
            channel_select_counter -= 1

        # print(dut.i_value.value)
        # if val > 0:
        #     dut.i_value.value = min(int((val / 32768.0 * 127)), 127)
        # elif val < 0:
        #     dut.i_value.value = max(int((val / 32768.0 * 127)), -127)
        # else:
        #     dut.i_value.value = 0

        # clk in data
        dut.i_data_clk.value = 1

        # print(val, dut.i_value.value)
        # print(dut.i_value)
        await RisingEdge(dut.clk)

        dut.i_data_clk.value = 0

        # print(int(str(dut.o_sum),2))
        # s = int(str(dut.o_sum[0:31]), 2)

        # if s > 2147483647:
        #     s = s - 4294967295 - 1

        # input = 0
        # if int(dut.i_value) > 127:
        #     input = int(str(dut.i_value), 2) - 255 - 1
        # else:
        #     input = int(str(dut.i_value), 2)


#         print(val, input, s)
        # print(val, dut.i_value, s)

        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        # assert(True)
        # raw_out, = struct.pack('i', dut.o_sum[0].value.signed_integer)
        # audio_out.writeframes(raw_out)

@cocotb.test()
async def test_modulated_sine(dut):

    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    # These should be held low by default
    dut.i_data_clk.value = 0
    dut.i_value.value = 0
    dut.i_select_output_channel.value = 0

    await RisingEdge(dut.clk)

    # output should be zero if prior values are zero
    assert dut.o_multiplexed_wavelet_out == 0

    counter = 0
    channel_select = 0
    channel_select_counter = 200

    # process audio through dut
    for i in range(5000):
        await RisingEdge(dut.clk)

        if channel_select_counter == 0:
            channel_select += 1
            dut.i_select_output_channel.value = channel_select % 8
            channel_select_counter = 200
        else:
            channel_select_counter -= 1

        dut.i_value.value = max(min(int(math.sin(0.1*counter*(1 + 0.01*counter))  * 128), 127),-128)
        counter = 1 + counter

        # clk in data
        dut.i_data_clk.value = 1

        await RisingEdge(dut.clk)

        dut.i_data_clk.value = 0

        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

@cocotb.test()
async def test_modulated_sine_overflow(dut):

    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    # These should be held low by default
    dut.i_data_clk.value = 0
    dut.i_value.value = 0
    dut.i_select_output_channel.value = 0

    await RisingEdge(dut.clk)

    # output should be zero if prior values are zero
    assert dut.o_multiplexed_wavelet_out == 0

    counter = 0
    channel_select = 0
    channel_select_counter = 200

    # process audio through dut
    for i in range(5000):
        await RisingEdge(dut.clk)

        # create sine wave value within [127, -128] (signed 8-bit int)
        dut.i_value.value = max(min(int(math.sin(0.1*counter*(1 + 0.001*counter))  * 128), 127),-128)

        if channel_select_counter == 0:
            channel_select += 1
            dut.i_select_output_channel.value = channel_select % 8
            channel_select_counter = 200
        else:
            channel_select_counter -= 1

        counter = 1 + counter

        # clk in data
        dut.i_data_clk.value = 1

        # print(val, dut.i_value.value)
        # print(dut.i_value)
        await RisingEdge(dut.clk)

        dut.i_data_clk.value = 0

        # print(int(str(dut.o_sum),2))
        # s = int(str(dut.o_sum[0:31]), 2)

        # if s > 2147483647:
        #     s = s - 4294967295 - 1

        # input = 0
        # if int(dut.i_value) > 127:
        #     input = int(str(dut.i_value), 2) - 255 - 1
        # else:
        #     input = int(str(dut.i_value), 2)


#         print(val, input, s)
        # print(val, dut.i_value, s)

        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)
