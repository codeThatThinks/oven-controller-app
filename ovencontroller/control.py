"""Hardware control"""

import logging
import multiprocessing
import time

import gpio
import rpi_hardware_pwm as pwm
import smbus2

from buzzer import Buzzer
import mcp960x


GPIO_ESTOP = 21
GPIO_FAN = 26

PWM_CH_SSR1 = 1
PWM_CH_SSR2 = 0

GPIO_BUZZER = 27
BUZZER_FREQ = 4000	# Hz

I2C_BUS = 2

TC_ADC_RES = mcp960x.ADCRes.ADC_16_BIT
TC_COLD_RES = mcp960x.ColdRes.COLD_0_25C
TC1_ADDR = 0x60
TC1_TYPE = mcp960x.TcType.K_TYPE
TC2_ADDR = 0x61
TC2_TYPE = mcp960x.TcType.K_TYPE

LOOP_RATE = 10		# Hz


logger = logging.getLogger(__name__)


def main(exit):
	"""Main loop"""

	pwm_ssr1 = None
	pwm_ssr2 = None
	buzzer = None
	i2c = None
	tc1 = None
	tc2 = None

	try:
		# E-stop and convection fan GPIO
		gpio.setup(GPIO_ESTOP, gpio.IN)
		logger.info("Initialized e-stop input")

		gpio.setup(GPIO_FAN, gpio.OUT, initial=gpio.LOW)
		logger.info("Initialized convection fan output")

		# SSR PWM
		pwm_ssr1 = pwm.HardwarePWM(pwm_channel=PWM_CH_SSR1, hz=LOOP_RATE)
		pwm_ssr1.stop()
		pwm_ssr2 = pwm.HardwarePWM(pwm_channel=PWM_CH_SSR2, hz=LOOP_RATE)
		pwm_ssr2.stop()
		logger.info("Initialized SSR PWM")

		# Buzzer soft-PWM process
		buzzer = Buzzer(GPIO_BUZZER, BUZZER_FREQ)
		logger.info("Initialized buzzer")

		# Thermocouple ICs
		i2c = smbus2.SMBus(I2C_BUS)
		logger.info(f"Initialized I2C bus {I2C_BUS}")

		tc1 = mcp960x.MCP960x(i2c, TC1_ADDR, tc_type=TC1_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)
		logger.info("Initialized thermocouple 1")
		tc2 = mcp960x.MCP960x(i2c, TC2_ADDR, tc_type=TC2_TYPE, adc_res=TC_ADC_RES, cold_res=TC_COLD_RES)
		logger.info("Initialized thermocouple 2")

		buzzer.beep(0.1)
		buzzer.pause(1)
		buzzer.beep(0.1)

		# Main control loop
		logger.info(f"Loop rate is {LOOP_RATE} Hz")
		logger.info("Entering main loop...")
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

			time.sleep(1)

			if exit is not None and exit.is_set():
				logger.info("Exit event received, shutting down...")
				break

	finally:
		# Cleanup
		if i2c is not None: i2c.close()
		if buzzer is not None: buzzer.cleanup()
		if pwm_ssr1 is not None: pwm_ssr1.stop()
		if pwm_ssr2 is not None: pwm_ssr2.stop()
		gpio.cleanup(GPIO_ESTOP)
		gpio.cleanup(GPIO_FAN)


if __name__ == "__main__":
	# run the hardware control process by itself
	logging.basicConfig(level=logging.DEBUG)
	logger.info("Running hardware control process by itself")
	main(None)
