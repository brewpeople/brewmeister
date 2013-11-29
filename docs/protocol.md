# Arduino Brew Control Protocol

The Arduino Brew Control Protocol (short ABCP) is a *simple*, *compact*,
*stateless* and *command-based* wire protocol for communicating with a
Brewmeister-compatible Arduino.

The following specification assumes, the *host* to be the machine that
communicates with the Arduino via a serial line interface.

## Protocol sequence

Communication is *always* initiated by the host using a simple call-response
sequence:

1. Host sends command packet specifying either to *read* or to *write* data.
2. The Arduino answers with a status code and depending on the command, optional
   data.


## Command packet

The command packet is sent by the host and consists of one header byte that is
split into two MSBs specifying the type of the command, four bits specifying the
object that the command refers to and two bits specifying the optional data
type.

     0 1 2 3 4 5 6 7
    +-+-+-+-+-+-+-+-+
    | C |   O   | D |
    +-+-+-+-+-+-+-+-+

The command bits can take four values, of which two are invalid. On the Arduino,
the MSB should be checked and if set return with a "invalid command" error.

Code    | Command
--------|----------
0x0     | set value
0x1     | get value
0x2     | reserved
0x3     | reserved

The object bits specify the actor/sensor that is refered to. At the moment two
instruments are specified:

Code    | Instrument    | Set               | Get
--------|---------------|-------------------|-------
0x0     | Temperature   | FP, deg Celsius   | Dito
0x1     | Stir          | Boolean           | Dito

A `set` command, requires the last two bits to specify the type of data that is
following. On a `get` command, these are ignored on the Arduino:

Code    | Data type     | Structure
--------|---------------|---------------------------------------
0x0     | Decimal       | 4 bytes, fixed width point 24.8
0x1     | String        | NULL-terminated variable length string
0x2     | Boolean       | 0 == False, anything else is True
0x3     | reserved      | n/a


## Result packet

After each command, the Arduino *must* acknowledge receiving the command packet
with a result packet. It consists of one header byte, split into 6 bits reserved
for status codes and 2 bits for the returned data type (see above).

     0 1 2 3 4 5 6 7
    +-+-+-+-+-+-+-+-+
    |      S    | D |
    +-+-+-+-+-+-+-+-+

Code    | Description
--------|--------------------
0x0     | OK
0x1     | Command invalid
0x2     | Set command invalid
0x3     | Get command invalid
