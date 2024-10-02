import time
from bitarray import bitarray

def tail_f_bits_with_delimiters(file_path, start_bits, end_bits):
    with open(file_path, 'rb') as f:
        f.seek(0, 2)  # Move to the end of file

        bit_buffer = bitarray()
        collecting = False
        data_bits_buffer = bitarray()

        # Convert start and end bits to bitarray
        start_bitarray = bitarray(start_bits)
        end_bitarray = bitarray(end_bits)

        while True:
            chunk = f.read(1024)
            if not chunk:
                time.sleep(0.1)
                continue

            # Convert bytes to bits and append to bit_buffer
            bits = bitarray()
            bits.frombytes(chunk)
            bit_buffer.extend(bits)

            # Process the bit buffer
            while True:
                if not collecting:
                    # Search for start_bits in bit_buffer
                    idx = bit_buffer.search(start_bitarray)
                    if idx:
                        collecting = True
                        index = idx[0] + len(start_bitarray)
                        bit_buffer = bit_buffer[index:]
                        data_bits_buffer.clear()
                    else:
                        # Keep last len(start_bits)-1 bits in case start_bits is split
                        bit_buffer = bit_buffer[-(len(start_bitarray) - 1):]
                        break  # Need more data
                else:
                    # Search for end_bits in bit_buffer
                    idx = bit_buffer.search(end_bitarray)
                    if idx:
                        data_bits_buffer.extend(bit_buffer[:idx[0]])
                        # Convert bits to bytes
                        data_bytes = data_bits_buffer.tobytes()
                        # Output the collected data
                        print(data_bytes.decode('utf-8', errors='replace'))
                        # Reset for next sequence
                        collecting = False
                        index = idx[0] + len(end_bitarray)
                        bit_buffer = bit_buffer[index:]
                        data_bits_buffer.clear()
                    else:
                        # Accumulate data bits
                        data_bits_buffer.extend(bit_buffer)
                        # Clear bit_buffer to read more data
                        bit_buffer.clear()
                        break  # Need more data

if __name__ == "__main__":
    file_path = 'hiero3'  # Replace with your output file path

    # Define the start and end bit patterns for "AAAA" and "BBBB"
    start_bits = '01000001010000010100000101000001'  # "AAAA"
    end_bits = '01000010010000100100001001000010'    # "BBBB"

    tail_f_bits_with_delimiters(file_path, start_bits, end_bits)
