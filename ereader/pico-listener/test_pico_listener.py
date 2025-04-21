from mockito import when, verify, mock, unstub
import unittest
from pico_listener import Pico_Listener
import queue
import serial

class TestPicoListener(unittest.TestCase):
    def setUp(self):
        # Mock the serial.Serial object
        self.mock_serial = mock()
        when(self.mock_serial).in_waiting.thenReturn(1)  # Simulate data available
        when(self.mock_serial).readline().thenReturn(b'{"select": 1}\n')  # Simulate a JSON signal

        # Patch the Pico_Listener to use the mocked serial object
        when(serial).Serial("/dev/ttyACM0", 115200, timeout=1).thenReturn(self.mock_serial)

        # Create an instance of Pico_Listener
        self.listener = Pico_Listener()

    def tearDown(self):
        unstub()  # Clean up mocks after each test

    def test_read_signal(self):
        # Start the listener in a separate thread
        self.listener.listening()

        # Retrieve the signal from the queue
        signal = self.listener.get_signal_queue().get(timeout=1)  # Wait for the signal
        self.assertEqual(signal, "select")  # Verify the signal is correct

        # Verify that the serial object was used as expected
        verify(self.mock_serial, times=1).readline()

    def test_stop_listening(self):
        # Start the listener
        self.listener.listening()

        # Stop the listener
        self.listener.stop_listening()

        # Verify that the serial connection was closed
        verify(self.mock_serial, times=1).close()

if __name__ == "__main__":
    unittest.main()

