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

    // BEGIN TB WIRE/REGISTER DECLARATION {{{
    reg clk;
    // QUESTION: we have RSTB and rst, should I rename rst RSTB? or is this handled by .rst(la_data_in[0]) in the user_project_wrapper.v?
    reg RSTB;
    // QUESTION: do we need `reg CSB;`?
    reg CSB;

    reg power1, power2;
    reg power3, power4;

    wire gpio;
    wire [37:0] mprj_io;
    // END WIRE/REGISTER DECLARATION }}}

    // BEGIN MODULE SPECIFIC WIRE DECLARATION {{{
    wire i_data_clk;
    wire i_value;
    wire i_select_output_channel;

    wire o_multiplexed_wavelet_out;
    wire o_active;

    // END MODULE SPECIFIC WIRE DECLARATION }}}

    // QUESTION: CSB line needed?
    assign mprj_io[3] = (CSB == 1'b1) ? 1'b1 : 1'bz;

    // BEGIN INITIALIZATION SECTION {{{
    always #12.5 clk <= (clk === 1'b0);

    initial begin
      clk = 0;
    end

    initial begin
      RSTB <= 1'b0;
      CSB  <= 1'b1;   // Force CSB high
      #2000;
      RSTB <= 1'b1;       // Release reset
      #300000;
      CSB = 1'b0;   // CSB can be released
    end

    initial begin   // Power-up sequence
      power1 <= 1'b0;
      power2 <= 1'b0;
      power3 <= 1'b0;
      power4 <= 1'b0;
      #100;
      power1 <= 1'b1;
      #100;
      power2 <= 1'b1;
      #100;
      power3 <= 1'b1;
      #100;
      power4 <= 1'b1;
    end

    initial begin
      $dumpfile ("wavelet_transform.vcd");
      $dumpvars (0, wavelet_transform_tb);
      #1;
      // repeat 25 cycles of 1000 clk edges for testbench
      repeat (25) begin
        repeat (100) @(posedge clk);
        // $display("+1000 cycles");
      end
      $finish;
    end
    // END INITIALIZATION SECTION }}}

    // BEGIN IN/OUT HUMAN READABLE ALIASES SECTION {{{
    // QUESTION: should these match inputs in user_project_wrapper?
    // For inputs seems these are on the right
    assign mprj_io[8] = i_data_clk;
    assign mprj_io[16:9] = i_value;
    assign mprj_io[24:17] = i_select_output_channel;

    // For outputs seems these are on the left
    assign o_multiplexed_wavelet_out = mprj_io[32:25];
    assign o_active = mprj_io[33];
    // END IN/OUT HUMAN READABLE ALIASES SECTION }}}

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
