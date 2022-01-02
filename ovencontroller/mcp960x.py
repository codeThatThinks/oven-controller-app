"""MCP9600/MCP9601 I2C driver"""

import enum
import logging
import time
from smbus2 import i2c_msg


BURST_TIMEOUT = 1


# registers and bitfields
REG_TEMP_HOT		= 0x00			# 16-bit two's complement
REG_TEMP_DELTA		= 0x01			# 16-bit two's complement
REG_TEMP_COLD		= 0x02			# 12-bit two's complement
REG_RAW_ADC			= 0x03			# 18-bit two's complement

REG_STATUS			= 0x04
ALERT1_STATUS		= (0x1 << 0)
ALERT2_STATUS		= (0x1 << 1)
ALERT3_STATUS		= (0x1 << 2)
ALERT4_STATUS		= (0x1 << 3)
OPEN_CIRCUIT		= (0x1 << 4)
SHORT_CIRCUIT		= (0x1 << 5)
TH_UPDATE			= (0x1 << 6)
BURST_COMPLETE		= (0x1 << 7)

REG_TC_CONF			= 0x05
FILTER_COEFF		= (0x7 << 0)
TC_TYPE				= (0x7 << 4)

REG_DEV_CONF		= 0x06
SHUTDOWN_MODE		= (0x3 << 0)
BURST_SAMPLES		= (0x7 << 2)
ADC_RESOLUTION		= (0x3 << 5)
COLD_RESOLUTION		= (0x1 << 7)

REG_ALERT1_CONF		= 0x08
REG_ALERT2_CONF		= 0x09
REG_ALERT3_CONF		= 0x0A
REG_ALERT4_CONF 	= 0x0B
ALERT_ENABLE		= (0x1 << 0)
ALERT_MODE			= (0x1 << 1)
ALERT_POL			= (0x1 << 2)
ALERT_DIR			= (0x1 << 3)
ALERT_TEMP			= (0x1 << 4)
ALERT_CLEAR			= (0x1 << 7)

REG_ALERT1_HYS		= 0x0C			# 8-bit unsigned
REG_ALERT2_HYS		= 0x0D
REG_ALERT3_HYS		= 0x0E
REG_ALERT4_HYS		= 0x0F

REG_ALERT1_LIM		= 0x10			# 16-bit two's complement
REG_ALERT2_LIM		= 0x11
REG_ALERT3_LIM		= 0x12
REG_ALERT4_LIM		= 0x13

REG_DEV_REV			= 0x20
REV_MINOR			= (0xF << 0)
REV_MAJOR			= (0xF << 4)


logger = logging.getLogger(__name__)


class TcType(enum.IntEnum):
	"""Thermocouple type"""
	K_TYPE			= 0b000
	J_TYPE			= 0b001
	T_TYPE			= 0b010
	N_TYPE			= 0b011
	S_TYPE			= 0b100
	E_TYPE			= 0b101
	B_TYPE			= 0b110
	R_TYPE			= 0b111


class Mode(enum.IntEnum):
	"""Shutdown modes"""
	NORMAL			= 0b00
	SHUTDOWN		= 0b01
	BURST			= 0b10


class BurstSamples(enum.IntEnum):
	"""Burst mode samples"""
	BURST_1			= 0b000
	BURST_2			= 0b001
	BURST_4			= 0b010
	BURST_8			= 0b011
	BURST_16		= 0b100
	BURST_32		= 0b101
	BURST_64		= 0b110
	BURST_128		= 0b111


class ADCRes(enum.IntEnum):
	"""ADC measurement resolution"""
	ADC_18_BIT		= 0b00
	ADC_16_BIT		= 0b01
	ADC_14_BIT		= 0b10
	ADC_12_BIT		= 0b11


class ColdRes(enum.IntEnum):
	"""Cold junction resolution"""
	COLD_0_0625C	= 0
	COLD_0_25C		= 1


class MCP960x:
	"""MCP960x base class"""

	def __init__(self, bus, addr, tc_type=TcType.K_TYPE, filter_level=0, adc_res=ADCRes.ADC_18_BIT, cold_res=ColdRes.COLD_0_0625C, burst_samples=BurstSamples.BURST_1):
		"""Class constructor"""

		self.bus = bus
		self.addr = addr

		# device info
		self.chip = ""
		self.rev_major = 0
		self.rev_minor = 0

		# status flags
		self.open_circuit = False
		self.short_circuit = False

		# probe chip
		rev = self._read(REG_DEV_REV, 2)

		if rev[0] == 0x40:
			self.chip = "MCP9600"
		elif rev[0] == 0x41:
			self.chip = "MCP9601"
		else:
			logger.critical(f"I2C device at 0x{self.addr:02X} is not an MCP9600 or MCP9601!")
			raise Exception(f"I2C device at 0x{self.addr:02X} is not an MCP9600 or MCP9601!")

		logger.info(f"Found a {self.chip} at I2C address 0x{self.addr:02X}")

		self.rev_major = (rev[1] & 0xf) >> 4
		self.rev_minor = rev[1] & 0xf

		# configure chip
		self.configure(tc_type, filter_level, adc_res, cold_res)


	def configure(self, tc_type=TcType.K_TYPE, filter_level=0, adc_res=ADCRes.ADC_18_BIT, cold_res=ColdRes.COLD_0_0625C, burst_samples=BurstSamples.BURST_1):
		"""Configure chip"""

		if tc_type not in [item.value for item in TcType]:
			logger.warning("Invalid thermocouple type; defaulting to K-type...")
			tc_type = TcType.K_TYPE

		if filter_level not in range(0,8):
			logger.warning("Invalid filter level; defaulting to 0 (off)...")
			filter_level = 0

		if adc_res not in [item.value for item in ADCRes]:
			logger.warning("Invalid ADC resolution; defaulting to 18-bit...")
			adc_res = ADCRes.ADC_18_BIT

		if cold_res not in [item.value for item in ColdRes]:
			logger.warning("Invalid cold junction resolution; defaulting to 0.0625°C...")
			cold_res = ColdRes.COLD_0_0625C

		if burst_samples not in [item.value for item in BurstSamples]:
			logger.warning("Invalid number of burst samples; defaulting to 1...")
			burst_samples = BurstSamples.BURST_1

		self.tc_type = tc_type
		self.filter_level = filter_level
		self.adc_res = adc_res
		self.cold_res = cold_res
		self.burst_samples = burst_samples

		self._write(REG_TC_CONF, bytearray([(tc_type << 4) | filter_level]))
		self._write(REG_DEV_CONF, bytearray([(cold_res << 7) | (adc_res << 5) | (burst_samples << 2) | Mode.SHUTDOWN]))


	def read_temp(self):
		"""Perform a thermocouple hot junction measurement and return the value in Celsius"""

		self._set_mode(Mode.BURST)

		self._write(REG_STATUS, bytearray([0x00]))
		burst_start_time = time.time()
		while(((self._read(REG_STATUS, 1))[0] & 0x80) != 0x80):
			if time.time() > (burst_start_time + BURST_TIMEOUT):
				logger.warning("Timed out waiting for temperature conversion")
				break

			time.sleep(0.001)	# don't eat CPU

		self._set_mode(Mode.SHUTDOWN)

		data = self._read(REG_TEMP_HOT, 2)
		temp = (data[0] << 8) | data[1]

		if temp > (pow(2, 15) - 1):
			temp = temp - pow(2, 16)

		return temp / pow(2, 4)


	def update_status(self):
		"""Read status register and update fields"""

		data = self._read(REG_STATUS, 1)

		self.open_circuit = (data[0] & OPEN_CIRCUIT) == OPEN_CIRCUIT
		self.short_circuit = (data[0] & SHORT_CIRCUIT) == SHORT_CIRCUIT


	def _set_mode(self, mode):
		"""Set device mode"""

		if mode not in [item.value for item in Mode]:
			logger.error("Invalid device mode...")
			return

		data = self._read(REG_DEV_CONF, 1)
		data[0] &= 0xFC
		data[0] |= mode
		self._write(REG_DEV_CONF, data)


	def _read(self, reg, len):
		"""Read from a specified register"""

		write = i2c_msg.write(self.addr, bytearray([reg]))
		read = i2c_msg.read(self.addr, len)
		self.bus.i2c_rdwr(write, read)

		return bytearray(bytes(read))


	def _write(self, reg, data):
		"""Write to a specified register"""

		write = i2c_msg.write(self.addr, bytearray([reg]) + data)
		self.bus.i2c_rdwr(write)
