import sys
import struct


def encode_varint(value):
    bytes_list = []
    while True:
        byte = value & 0x7F
        value >>= 7
        if (value == 0 and byte & 0x40 == 0) or (value == -1 and byte & 0x40 != 0):
            bytes_list.append(byte)
            break
        else:
            byte |= 0x80  # Set continuation bit
            bytes_list.append(byte)

    return struct.pack('B' * len(bytes_list), *bytes_list)

def read_varint(bytes_list):
    value = 0
    position = 0

    for current_byte in bytes_list:
        value |= (current_byte & 0x7F) << position
        position += 7

        if not (current_byte & 0x80):
            break

    if position > 64:
        raise ValueError("Invalid variable-length integer encoding")

    if position > 32 and value & (1 << 31):
        value -= (1 << 32)
    
    return value


def encode_signed_integer(value):
    """Encode a signed integer into bytes."""
    if value < 0:
        raise ValueError("Negative values not supported for automatic byte size determination.")
    
    byte_size = (value.bit_length() + 7) // 8 or 1  # Determine byte size
    format_string = f'>{byte_size}b'
    
    return struct.pack(format_string, *(value.to_bytes(byte_size, 'big', signed=True)))

def read_signed_integer(data):
    """Decode bytes into a signed integer."""
    byte_size = len(data)
    format_string = f'>{byte_size}b'
    
    return int.from_bytes(struct.unpack(format_string, data), 'big', signed=True)


def encode_string(value):
    encoded_length = encode_varint(len(value))
    encoded_value = value.encode('utf-8')
    return encoded_length + encoded_value

def verify(pkt):
    # If uncompressed
    if sys.getsizeof(pkt) > 2097151:
        return False
    
    # If compressed