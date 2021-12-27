"""Hardware control"""

import logging
import time

import RPIO
import RPIO.PWM
import smbus2

import mcp960x


GPIO_ESTOP = 21
GPIO_FAN = 26

DMA_CH_SSR = 0
GPIO_SSR1 = 13
GPIO_SSR2 = 12
DMA_CH_BUZZER = 1
GPIO_BUZZER = 27

I2C_BUS = 1

TC_ADC_RES = mcp960x.ADCRes.ADC_16_BIT
TC_COLD_RES = mcp960x.ColdRes.COLD_0_25C
TC1_ADDR = 0x60
TC1_TYPE = mcp960x.TcType.K_TYPE
TC2_ADDR = 0x61
TC2_TYPE = mcp960x.TcType.K_TYPE

LOOP_RATE = 10		# Hz


def main(exit):
	"""Main loop"""

	try:
		# E-stop and convection fan GPIO
		RPIO.setup(GPIO_ESTOP, RPIO.IN)
		logging.info("Initialized e-stop input")

		RPIO.setup(GPIO_FAN, RPIO.OUT, initial=RPIO.LOW)
		logging.info("Initialized convection fan output")

		# SSR and buzzer PWM
		RPIO.PWM.setup()
		RPIO.PWM.init_channel(DMA_CH_SSR, subcycle_time_us=1e6 / LOOP_RATE)
		logging.info("Initialized SSR PWM")

		RPIO.PWM.init_channel(DMA_CH_BUZZER, subcycle_time_us=2000)
		logging.info("Initialize buzzer PWM")

		# Thermocouple ICs
		i2c = None
		i2c = smbus2.SMBus(I2C_BUS)
		logging.info(f"Initialized I2C bus {I2C_BUS}")

		tc1 = mcp960x.MCP960x(i2c, TC1_ADDR, tc_type=TC1_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)
		logging.info("Initialized thermocouple 1")
		tc2 = mcp960x.MCP960x(i2c, TC2_ADDR, tc_type=TC2_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)
		logging.info("Initialized thermocouple 2")

		# Main control loop
		logging.info(f"Loop rate is {LOOP_RATE} Hz")
		logging.info("Entering main loop...")
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

			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 0, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 25, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 50, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 75, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 100, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 125, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 150, 13)
			RPIO.PWM.add_channel_pulse(DMA_CH_BUZZER, GPIO_BUZZER, 175, 13)
			time.sleep(1)
			RPIO.PWM.clear_channel_gpio(DMA_CH_BUZZER, GPIO_BUZZER)
			time.sleep(5)

			if exit is not None and exit.is_set():
				logging.info("Exit event received, shutting down...")
				break

	finally:
		# Cleanup
		if i2c is not None: i2c.close()
		RPIO.PWM.cleanup()
		RPIO.cleanup()


if __name__ == "__main__":
	# run the hardware control process by itself
	logging.info("Running hardware control process by itself")
	main(None)
