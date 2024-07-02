// LFSR = Linear Feedback Shift Registers
// We define a DFF first, then connect a few DFFs in a chain to form LFSR.
// Reference on LFSR basics,
// https://www.eetimes.com/tutorial-linear-feedback-shift-registers-lfsrs-part-3
// Standard Form n-bit LFSR: Qn-1=>Qn-2=>...=>Q1=>Q0, D=f(Q_all)=>Qn-1
// https://vlsitutorials.com/lfsr-and-ring-generator/
// Test Pattern Generator(TG) and Response Analyzer (RA) are often
// implemented by LFSRs. An RA is often an MISR (Multiple Input Signature
// Register), which is a little bit like CRC computing for a data series.
//
// When using iverilog to simulate this file, run 3 commands below,
// iverilog -o lfsr -s test_top lfsr.v
// ./lfsr
// gtkwave lfsr_wave.vcd
// ; to see the resulted waveforms (commands also saved in a BASH file)


`timescale 1ns/100ps

module dff(
    output reg Q,
    input D,
    input Clk,
    input Set
);

    always @(posedge Clk) begin
        if (Set) begin // notice the begin+end pair
            #1 Q <= 1;
	end
	else begin
            #1 Q <= D; // next clock change -> Q change after #1 delay
        end
    end
endmodule

// A characteristic polynomial represents the LFSR structure.
// A primitive polynomial is a polynomial that makes an LFSR with
// maximum possible period.
module tpg1(
    input Clk,
    input Set,
    output [3:0] Q
);
    wire D;

    // LFSR with all bits=0 could not work with XOR feedback (as it always
    // results 0). Choose tap positions to generate sequence as long as
    // possible; the maximal length is (2^n-1)
    // length=15 for [q0^q3] <= x^4 + x^3 + 1 (see the powers of 4, 3, 0)
    assign #2 D = Q[0] ^ Q[3]; // Q change -> D change after #2 prop. delay
    dff dff3(Q[3], D, Clk, Set);
    dff dff2(Q[2], Q[3], Clk, Set);
    dff dff1(Q[1], Q[2], Clk, Set);
    dff dff0(Q[0], Q[1], Clk, Set);
endmodule

module tpg2(
    input Clk,
    input Set,
    output [3:0] Q
);
    wire D;

    // length=15 for [q0^q1] <= x^4 + x + 1 (see the powers of 4, 1, 0)
    assign #2 D = Q[0] ^ Q[1];
    dff dff3(Q[3], D, Clk, Set);
    dff dff2(Q[2], Q[3], Clk, Set);
    dff dff1(Q[1], Q[2], Clk, Set);
    dff dff0(Q[0], Q[1], Clk, Set);
endmodule

// RA using MISR structure. See reference,
// https://vlsitutorials.com/lbist-response-analyzer/
// For an 8-bit MISR, how to choose the characteristic polynomial
// to make the longest output period (i.e., 255)?
// First, choose a polynomial that cannot be factored in terms of
// modulo-2 multiplication, i.e., being irreducible in XOR operation.
// e.g., x^8+x^5+x^4+x^2+1 = (x^6+x^5+x^2+x+1)*(x^2+x+1), is reducible
// i.e., (100110101) = (1100111) mod2* (111), and so cannot be used.
// Second, for irreducible polynomials there are maximumly 255 outputs,
// and since 255 = 3*5*17, so check Q_t0 with Q_t85, Q_t51 and Q_t15,
// to make sure Q is not periodic on these positions.
// It is alright to exhaustively search for the simplest solution.
// Here we use: Q(x) = x^8+x^4+x^3+x^2+1
module ra_misr(
    input Clk,
    input Set,
    input [7:0] Data,
    output [7:0] Q
);
    wire [7:0] D;
    wire feedback;
    assign #6 feedback = Q[0] ^ Q[2] ^ Q[3] ^ Q[4];
    assign #1 D[7] = feedback ^ Data[7];
    assign #1 D[6] = Q[7] ^ Data[6];
    assign #1 D[5] = Q[6] ^ Data[5];
    assign #1 D[4] = Q[5] ^ Data[4];
    assign #1 D[3] = Q[4] ^ Data[3];
    assign #1 D[2] = Q[3] ^ Data[2];
    assign #1 D[1] = Q[2] ^ Data[1];
    assign #1 D[0] = Q[1] ^ Data[0];

    dff dff7(Q[7], D[7], Clk, Set);
    dff dff6(Q[6], D[6], Clk, Set);
    dff dff5(Q[5], D[5], Clk, Set);
    dff dff4(Q[4], D[4], Clk, Set);
    dff dff3(Q[3], D[3], Clk, Set);
    dff dff2(Q[2], D[2], Clk, Set);
    dff dff1(Q[1], D[1], Clk, Set);
    dff dff0(Q[0], D[0], Clk, Set);
endmodule

module test_top;
    reg clk;
    always #5 clk = !clk;

    reg on;
    wire [3:0] tp1, tp2;
    wire [7:0] signature;

    tpg1 tpg1_1
    (
	.Clk(clk),
	.Set(on),
	.Q(tp1)
    );

    tpg2 tpg2_1
    (
	.Clk(clk),
	.Set(on),
	.Q(tp2)
    );

    ra_misr ra1
    (
	.Clk(clk),
	.Set(on),
	.Data(prod),
	.Q(signature)
    );

    wire [7:0] prod, mul_1, mul_2;
    assign mul_1 = {4'b0000, tp1};
    assign mul_2 = {4'b0000, tp2};

    /* 2 lines below to test RA when input data stream is all 0's 
    assign mul_1 = 8'b00000000;
    assign mul_2 = 8'b00000000;
    */

    assign #1 prod = mul_1 * mul_2;

    /* 2 lines below deliberately add some bit errors in the multiplication 
    assign err = mul_1 & 8'h03 ? 1'b0 : mul_1 & mul_2 & 8'h08 ? 1'b1 : 1'b0;
    assign prod = mul_1 * mul_2 + err;
    */
   
    integer i;
    initial begin
	$dumpfile("lfsr_wave.vcd");
	$dumpvars(0, test_top);

	clk = 0; on = 1;
	#10
	on = 0;

	for (i=0; i < 300; i = i + 1) begin
	    @(posedge clk);
	    $write(i, ":", tp1, "*", tp2, "=", prod); // write -> no newline
	    $display(" ::RA signature is ", signature);  // display 
	end

	$finish();
    end
endmodule
