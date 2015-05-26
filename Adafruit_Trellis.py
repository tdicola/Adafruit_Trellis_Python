# This is a library for the Adafruit Trellis w/HT16K33
#
#   Designed specifically to work with the Adafruit Trellis 
#   ----> https://www.adafruit.com/products/1616
#   ----> https://www.adafruit.com/products/1611
#
#   These displays use I2C to communicate, 2 pins are required to  
#   interface
#   Adafruit invests time and resources providing this open source code, 
#   please support Adafruit and open-source hardware by purchasing 
#   products from Adafruit!
#
#   Written by Limor Fried/Ladyada for Adafruit Industries.  
#   MIT license, all text above must be included in any redistribution
#
#   Python port created by Tony DiCola (tony@tonydicola.com

try:
	import Adafruit_I2C
except ImportError:
	raise ImportError('Could not find Adafruit_I2C library.  If running on the Beaglebone make sure the' \
		' Adafruit_BBIO library is installed.  If running on the Raspberry Pi make sure the Adafruit_I2C.py' \
		' file is in the same directory as your script.')


LED_ON = 1
LED_OFF = 0
HT16K33_BLINK_CMD = 0x80
HT16K33_BLINK_DISPLAYON = 0x01
HT16K33_BLINK_OFF = 0
HT16K33_BLINK_2HZ = 1
HT16K33_BLINK_1HZ = 2
HT16K33_BLINK_HALFHZ  = 3
HT16K33_CMD_BRIGHTNESS = 0x0E

ledLUT =  [ 0x3A, 0x37, 0x35, 0x34, 
			0x28, 0x29, 0x23, 0x24, 
			0x16, 0x1B, 0x11, 0x10, 
			0x0E, 0x0D, 0x0C, 0x02 ]

buttonLUT = [ 0x07, 0x04, 0x02, 0x22,
			  0x05, 0x06, 0x00, 0x01,
			  0x03, 0x10, 0x30, 0x21,
			  0x13, 0x12, 0x11, 0x31 ]


class Adafruit_Trellis(object):
	def __init__(self):
		"""Create a Trellis object."""
		self.displaybuffer = [0] * 8
		self._keys = [0] * 6
		self._lastkeys = [0] * 6
		self._i2c = None

	def begin(self, addr = 0x70, bus = -1):
		"""Initialize the Trellis at the provided I2C address and bus number."""
		self._i2c = Adafruit_I2C.Adafruit_I2C(addr, bus)
		self._i2c.writeList(0x21, []) # Turn on the oscillator.
		self.blinkRate(HT16K33_BLINK_OFF)
		self.setBrightness(15) # Max brightness.
		self._i2c.writeList(0xA1, []) # Turn on interrupt, active high.

	def setBrightness(self, b):
		"""Set the brightness of the LEDs to the provided value.
		   Value should be any integer 0 to 15--values outside that range will be
		   clamped to the boundary value.
		"""
		self._check_i2c()
		b = 15 if b > 15 else b
		b = 0 if b < 0 else b
		self._i2c.writeList(0xE0 | b, [])

	def blinkRate(self, b):
		"""Set the blink rate to the provided value.
		   Value should be an integer 0 to 3--values outside that range will default
		   to 0.
		"""
		self._check_i2c()
		b = 0 if b > 3 else b # turn off if not sure
		b = 0 if b < 0 else b
		self._i2c.writeList(HT16K33_BLINK_CMD | HT16K33_BLINK_DISPLAYON | (b << 1), [])

	def writeDisplay(self):
		"""Write the LED display buffer values to the hardware."""
		self._check_i2c()
		data = []
		for buf in self.displaybuffer:
			data.append(buf & 0xFF)
			data.append(buf >> 8)
		self._i2c.writeList(0, data)

	def clear(self):
		"""Clear all the LEDs in the display buffer."""
		self.displaybuffer = [0] * 8

	def isKeyPressed(self, k):
		"""Check if the specified key was pressed during the last readSwitches call."""
		if k > 16 or k < 0: return False
		return (self._keys[buttonLUT[k] >> 4] & (1 << (buttonLUT[k] & 0x0F))) > 0

	def wasKeyPressed(self, k):
		"""Check if the specified key was pressed before the last readSwitches call."""
		if k > 16 or k < 0: return False
		return (self._lastkeys[buttonLUT[k] >> 4] & (1 << (buttonLUT[k] & 0x0F))) > 0

	def isLED(self, x):
		"""Return True if the specified LED is illuminated in the display buffer."""
		if x > 16 or x < 0: return False
		return (self.displaybuffer[ledLUT[x] >> 4] & (1 << (ledLUT[x] & 0x0F))) > 0

	def setLED(self, x):
		"""Turn on the specified LED in the display buffer."""
		if x > 16 or x < 0: return  
		self.displaybuffer[ledLUT[x] >> 4] |= (1 << (ledLUT[x] & 0x0F))

	def clrLED(self, x):
		"""Turn off the specified LED in the display buffer."""
		if x > 16 or x < 0: return
		self.displaybuffer[ledLUT[x] >> 4] &= ~(1 << (ledLUT[x] & 0x0F))

	def readSwitches(self):
		"""Read the state of the buttons from the hardware.
		   Returns True if a button is pressed, False otherwise.
		"""
		self._check_i2c()
		self._lastkeys = self._keys
		self._keys = self._i2c.readList(0x40, 6)
		return any(map(lambda key, lastkey: key != lastkey, self._keys, self._lastkeys))

	def justPressed(self, k):
		"""Return True if the specified key was first pressed in the last readSwitches call."""
		return self.isKeyPressed(k) and not self.wasKeyPressed(k)

	def justReleased(self, k):
		"""Return True if the specified key was just released in the last readSwitches call."""
		return not self.isKeyPressed(k) and self.wasKeyPressed(k)

	def _check_i2c(self):
		assert self._i2c is not None, 'begin() must be called first!'


class Adafruit_TrellisSet(object):

	def __init__(self, *matrices):
		"""Create a Trellis set from the provided Trellis instances.
		   Each argument should be a unique Trellis instance.
		"""
		self._matrices = matrices

	def begin(self, *addrs):
		"""Initialize the Trellis set at the provided I2C addresses and bus numbers.
		   Each parameter should be a tuple with (I2C address, I2C bus number).
		"""
		assert len(addrs) == len(self._matrices), 'Number of addresses does not match number of Trellis matrices!'
		for matrix, addr in zip(self._matrices, addrs):
			matrix.begin(addr[0], addr[1])

	def setBrightness(self, b):
		"""Set the brightness of the LEDs to the provided value.
		   Value should be any integer 0 to 15--values outside that range will be
		   clamped to the boundary value.
		"""
		for matrix in self._matrices:
			matrix.setBrightness(b)

	def blinkRate(self, b):
		"""Set the blink rate to the provided value.
		   Value should be an integer 0 to 3--values outside that range will default
		   to 0.
		"""
		for matrix in self._matrices:
			matrix.blinkRate(b)

	def writeDisplay(self):
		"""Write the LED display buffer values to the hardware."""
		for matrix in self._matrices:
			matrix.writeDisplay()

	def clear(self):
		"""Clear all the LEDs in the display buffer."""
		for matrix in self._matrices:
			matrix.clear()

	def isKeyPressed(self, k):
		"""Check if the specified key was pressed during the last readSwitches call."""
		matrix, key = self._get_matrix(k)
		if matrix is None: return False
		return matrix.isKeyPressed(key)

	def wasKeyPressed(self, k):
		"""Check if the specified key was pressed before the last readSwitches call."""
		matrix, key = self._get_matrix(k)
		if matrix is None: return False
		return matrix.wasKeyPressed(key)

	def isLED(self, x):
		"""Return True if the specified LED is illuminated in the display buffer."""
		matrix, led = self._get_matrix(x)
		if matrix is None: return False
		return matrix.isLED(led)

	def setLED(self, x):
		"""Turn on the specified LED in the display buffer."""
		matrix, led = self._get_matrix(x)
		if matrix is None: return False
		return matrix.setLED(led)

	def clrLED(self, x):
		"""Turn off the specified LED in the display buffer."""
		matrix, led = self._get_matrix(x)
		if matrix is None: return False
		return matrix.clrLED(led)

	def readSwitches(self):
		"""Read the state of the buttons from the hardware.
		   Returns True if a button is pressed, False otherwise.
		"""
		return any(map(lambda matrix: matrix.readSwitches(), self._matrices))

	def justPressed(self, k):
		"""Return True if the specified key was first pressed in the last readSwitches call."""
		return self.isKeyPressed(k) and not self.wasKeyPressed(k)

	def justReleased(self, k):
		"""Return True if the specified key was just released in the last readSwitches call."""
		return not self.isKeyPressed(k) and self.wasKeyPressed(k)

	def _get_matrix(self, position):
		"""Get the matrix for the associated global LED/key position.
		   Returns a tuple with matrix, and local position inside that matrix.
		   If position is not within the range of possible values, returns None.
		"""
		if position > 16*len(self._matrices) or position < 0: return None, None
		matrix = position / 16
		offset = position % 16
		return self._matrices[matrix], offset
