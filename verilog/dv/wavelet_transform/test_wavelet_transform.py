import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout
from test_wavelet_transform import Encoder
import math
import random
import wave
import struct

clocks_per_phase = 10

# takes ~60 seconds on my PC

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    # TODO: chip level reset goes to wishbone wb_rst_i
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

    # wait for the project to become active
    # QUESTION: do I trigger the following test with this? (to make sure the project is online?)
    # QUESTION: what to rename wrapped_rgb_mixer_3 for wavelet_transform?
    # ANSWER: explore the trace, and get the vcd (will produce even if crashes), this will give the "path"
    # ANSWER: better to write test benches without this, b/c gate level sim
    # ANSWER: better to set io pin high when design is on, replace with below.
    # TODO: replace this with new gpio pin from module, call it "active" path with vcd trace under mprj
    # in the testbench use a utility wire
    await with_timeout(RisingEdge(dut.active), 500, 'us')


@cocotb.test()
async def test_cwt(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())

    # TODO: Assert proper starting values for wavelet_transform
    # # e.g. these should all be low at start
    # assert dut.pwm0_out.value == 0
    # assert dut.pwm1_out.value == 0
    # assert dut.pwm1_out.value == 0

    # open audio files for read and write
    # audio_in = wave.open("./test/middle_c.wav")
    # QUESTION: what path should these wavs be in? (relative to which directory? makefile dir?)
    audio_in = wave.open("./wavs/hello.wav")
    audio_out = wave.open("./wavs/out.wav", "wb")
    audio_out.setnchannels(audio_in.getnchannels())
    audio_out.setsampwidth(audio_in.getnchannels())
    audio_out.setframerate(audio_in.getframerate())

    nframes = audio_in.getnframes()
    print("sending %d frames" % nframes)

    dut.i_data_clk.value = 0
    counter = 0

    # process audio through dut
    for i in range(nframes):
        await RisingEdge(dut.clk)
        frame = audio_in.readframes(1)
        # print(frame)
        (val,) = struct.unpack("h", frame)

        dut.i_value.value = int(math.sin(0.1*counter*(1 + 0.01*counter))  * 127)
        counter = 1 +counter

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
