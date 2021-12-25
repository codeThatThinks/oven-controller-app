"""Hardware control"""

import logging
import smbus2

import mcp960x


LOOP_RATE = 10		# Hz

TC_ADC_RES = mcp960x.ADCRes.ADC_16_BIT
TC_COLD_RES = mcp960x.ColdRes.COLD_0_25C
TC1_ADDR = 0x40
TC1_TYPE = mcp960x.TcType.K_TYPE
TC2_ADDR = 0x41
TC2_TYPE = mcp960x.TcType.K_TYPE


"""Main loop"""
def main(exit):
	try:
		# - initialize gpio
		#	- set ssr 1 output to off
		#	- set ssr 2 output to off
		#	- set fan output to off
		#	- set buzzer to off

		i2c = None
		i2c = smbus2.SMBus(1)

		tc1 = mcp960x.MCP960x(i2c, TC1_ADDR, tc_type=TC1_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)
		tc1 = mcp960x.MCP960x(i2c, TC1_ADDR, tc_type=TC2_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)

		while(True):
			# infrequent safety checks
			# - check e-stop status
			# - check thermocouple 1 for open/shorted
			# - check thermocouple 2 for open/shorted

			# if enabled, sample thermocouple 1
			# if enabled, sample thermocouple 2

			# mix thermocouple 1 and 2 readings

			# if running,
				# get next setpoint value
				# calculate pid output value

				# if enabled, set ssr 1 output duty cycle
				# if enabled, set ssr 2 output duty cycle

			if exit is not None and exit.is_set():
				break

	finally:
		if i2c is not None:
			i2c.close()


if __name__ == "__main__":
	# run the hardware control loop by itself
	main(None)
