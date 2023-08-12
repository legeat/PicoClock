import pulseio
import board
import adafruit_irremote

pulsein = pulseio.PulseIn(board.GP28, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

while True:
    pulses = decoder.read_pulses(pulsein)
    try:
        received_code = decoder.decode_bits(pulses)
    except adafruit_irremote.IRNECRepeatException:
        continue
    except adafruit_irremote.IRDecodeException as e:
        continue
    if received_code == (255, 0, 151, 104):
        print ("0")
    if received_code == (255, 0, 207, 48):
        print ("1")
    if received_code == (255, 0, 231, 24):
        print ("2")
    if received_code == (255, 0, 133, 122):
        print ("3")
    if received_code == (255, 0, 239, 16):
        print ("4")
    if received_code == (255, 0, 199, 56):
        print ("5")
    if received_code == (255, 0, 165, 90):
        print ("6")
    if received_code == (255, 0, 189, 66):
        print ("7")
    if received_code == (255, 0, 181, 74):
        print ("8")
    if received_code == (255, 0, 173, 82):
        print ("9")
