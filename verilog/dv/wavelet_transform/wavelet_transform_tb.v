// SPDX-FileCopyrightText: 2020 Efabless Corporation
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

`timescale 1 ns / 1 ps

module wavelet_transform_tb;
    initial begin
        $dumpfile ("wavelet_transform.vcd");
        $dumpvars (0, wavelet_transform_tb);
        #1;
    end

    reg clk;
    // QUESTION: we ahve RSTB and rst, should I rename rst RSTB? or is this handled by .rst(la_data_in[0]) in the user_project_wrapper.v?
    reg RSTB;

    reg power1, power2;
    reg power3, power4;

    // GL design loses the reset signal name, also doesn't keep la1_data_in
    wire design_reset = uut.mprj.la_data_in[32];

    wire gpio;
    wire [37:0] mprj_io;

    ///// convenience signals that match what the cocotb test modules are looking for
    // QUESTION: do I need to change any of these for the cocotb.py test?
    wire active = mprj_io[33];
    // TODO: do this for the i_data_clk, etc. for cocotb readability
    /* wire pwm1_out = mprj_io[15]; */
    /* wire pwm2_out = mprj_io[16]; */

    /* wire enc0_a, enc0_b, enc1_a, enc1_b, enc2_a, enc2_b; */

    // QUESTION: should these match inputs in user_project_wrapper?
    assign mprj_io[8] = i_data_clk;
    assign mprj_io[16:9] = i_value;
    assign mprj_io[32:25] = i_select_output_channel;
    assign mprj_io[24:17] = o_multiplexed_wavelet_out;
    /////

    wire flash_csb;
    wire flash_clk;
    wire flash_io0;
    wire flash_io1;

    wire VDD3V3 = power1;
    wire VDD1V8 = power2;
    wire USER_VDD3V3 = power3;
    wire USER_VDD1V8 = power4;
    wire VSS = 1'b0;

    caravel uut (
        .vddio    (VDD3V3),
        .vssio    (VSS),
        .vdda     (VDD3V3),
        .vssa     (VSS),
        .vccd     (VDD1V8),
        .vssd     (VSS),
        .vdda1    (USER_VDD3V3),
        .vdda2    (USER_VDD3V3),
        .vssa1    (VSS),
        .vssa2    (VSS),
        .vccd1    (USER_VDD1V8),
        .vccd2    (USER_VDD1V8),
        .vssd1    (VSS),
        .vssd2    (VSS),
        .clock    (clk),
        .gpio     (gpio),
        .mprj_io  (mprj_io),
        .flash_csb(flash_csb),
        .flash_clk(flash_clk),
        .flash_io0(flash_io0),
        .flash_io1(flash_io1),
        .resetb   (RSTB)
    );

    spiflash #(
        .FILENAME("wavelet_transform.hex")
    ) spiflash (
        .csb(flash_csb),
        .clk(flash_clk),
        .io0(flash_io0),
        .io1(flash_io1),
        .io2(),         // not used
        .io3()          // not used
    );

endmodule
`default_nettype wire
