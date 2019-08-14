# -*- coding: utf-8 -*-
import crcCCITT

stx = bytearray([0x32])
etx = bytearray([0x34])


def gen_preamble():
    preamble = []
    for i in range(0, 100):
        preamble.append(0x55)

    return bytearray(preamble)


def gen_packet(sa, da, command, numberMsg, msg_set, preableCheck):

    body = bytearray(sa + da + command + numberMsg + msg_set)

    crc_code = intTo2Bytes(crcCCITT.crcb(body))
    length = calPacketLength(body, crc_code)

    if preableCheck:
        preamble = gen_preamble()
        packet = preamble + stx + length + body + crc_code + etx
    else:
        packet = stx + length + body + crc_code + etx

    return packet


def calPacketLength(msg, crc):
    lenPacket = 2 + int(len(msg)) + int(len(crc))

    return intTo2Bytes(lenPacket)


def intTo2Bytes(n):
    b = bytearray([0, 0])
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF

    return b


def intTo4Bytes(n):
    b = bytearray([0, 0, 0, 0])
    b[3] = n & 0xFF
    n >>= 8
    b[2] = n & 0xFF
    n >>= 8
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF

    return b


def bytes2ToInt(b, offset):
    n = (b[offset + 0] << 8) + b[offset + 1]
    return n


def bytes4ToInt(b, offset):
    n = (b[offset + 0] << 24) + (b[offset + 1] << 16) + (b[offset + 2] << 8) + b[offset + 3]
    return n


def intArrayToHexArray(b):
    result = []

    for i in b:
        result.append("0x%02X" % i)

    return result
