# This file contains code for interacting with the SEEED LoRa-E5 HF module using AT commands (in AT+TEST mode)
# This is by no means the best way of using the capabilities of the radio module, but it lets us accomplish some
# very basic P2P functionality without needing to use a special programmer to load new firmware onto the LoRa module.

# The functions in this file handle:
# 1) initializing the radio module into AT+TEST mode and setting the receive parameters to reasonable values
# 2)


# NOTE: We are using power level 5 dBm here, whereas 14 dBm is the max. I had some issues where badge would come disconnected
# from USB while trying to use the higher transmit power. It might work okay to use the higher power on battery though, but the
# range seems okay with 5 dBm so for now I am leaving it.
from machine import Timer, Pin, UART
import time

class LoraE5Radio():
    def __init__(self, uart_baudrate=9600, uart_tx_pin=8, uart_rx_pin=9, uart_timeout=250):
        self.radio_uart = UART(1, baudrate=uart_baudrate, tx=Pin(uart_tx_pin), rx=Pin(uart_rx_pin), timeout=uart_timeout)

        self.rx_buf = b""
        self.last_rx_arm = time.ticks_ms()
        self.rx_is_armed = False
        self.init_radio()
        self.arm_radio_rx()

    def init_radio(self):
        time.sleep_ms(300) # Seems to sometimes help when turning on after a long time of being off
        print(self.send_at("AT", delay_ms=100))
        print(self.send_at("AT+MODE=TEST", delay_ms=100))
        print(self.send_at("AT+TEST=RFCFG,903.3,SF7,125,12,15,5,ON,OFF,OFF", delay_ms=100))

    def arm_radio_rx(self, verbose=False, delay_ms=100):
        self.rx_is_armed = True
        if verbose:
            print(self.send_at("AT+TEST=RXLRPKT", delay_ms=delay_ms))
        else:
            self.send_at("AT+TEST=RXLRPKT", delay_ms=delay_ms)

    def flush_uart(self):
        # drain any stale bytes
        while self.radio_uart.any():
            self.radio_uart.read()
            time.sleep_ms(5)

    def send_at(self, cmd, delay_ms=200):
        self.flush_uart()
        self.radio_uart.write(cmd + "\r\n")
        time.sleep_ms(delay_ms)
        resp = b""
        # read whatever arrived
        while self.radio_uart.any():
            chunk = self.radio_uart.read()
            if chunk:
                resp += chunk
            time.sleep_ms(10)
        # return plain text (ignore decode errors)
        return resp.decode('utf-8', 'ignore').strip()

    def hex_to_ascii(self,s):
        # incoming payload appears as hex bytes (e.g. 48656C6C6F...)
        try:
            b = bytes.fromhex(s)
            # decode ASCII but fall back to repr if weird bytes
            try:
                return b.decode('utf-8')
            except:
                return str(b)
        except:
            return None
            
    def check_for_boop_message(self, expected_msg="boop"):
        # checks to see if boop message received since last call
        # collect any incoming bytes
        found_boop = False
        if self.radio_uart.any():
            self.rx_buf += self.radio_uart.read()

            # pull out complete lines (delimited by \n)
            while b"\n" in self.rx_buf:
                line_bytes, self.rx_buf = self.rx_buf.split(b"\n", 1)
                line = line_bytes.decode("utf-8", "ignore").strip()
                if not line:
                    continue

                # show raw UART content for debugging
                # print("RAW:", line)

                # examples the modem emits:
                # +TEST: LEN:12, RSSI:-45, SNR:10
                # +TEST: RX "48656C6C6F20576F726C6421"
                if line.startswith("+TEST: RX"):
                    q1 = line.find('"')
                    q2 = line.rfind('"')
                    payload_hex = None
                    if q1 != -1 and q2 != -1 and q2 > q1 + 1:
                        payload_hex = line[q1+1:q2]
                    msg = self.hex_to_ascii(payload_hex) if payload_hex else None
                    if msg is not None:
                        print("RX ASCII:", msg)
                        if msg == expected_msg:
                            found_boop = True
                    else:
                        # print("RX RAW  :", line) # print full line for debugging
                        pass
                else:
                    # print(line) # print RSSI/SNR for debugging
                    pass

        if time.ticks_diff(time.ticks_ms(), self.last_rx_arm) > 15000:
            # Periodically re-arm radio
            self.arm_radio_rx()
            self.last_rx_arm = time.ticks_ms()
            
        return found_boop

    def tx_boop(self, msg="boop", arm_rx_after_sent=False):
        print(self.send_at('AT+TEST=TXLRSTR,"{}"'.format(msg), delay_ms=150))
        self.rx_is_armed = False
        if arm_rx_after_sent:
            time.sleep_ms(100)
        self.arm_radio_rx()
