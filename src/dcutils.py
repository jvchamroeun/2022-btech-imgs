import sys, ntpath
from des import DesKey
from dcimage import *

#-----------------------------------------------------------------------------
# FUNCTION:    create_image
#
#  PROGRAMMER:  Jason Soukchamroeun
#
#  INTERFACE:   def create_image(cover, secret, output, password)
#               cover - cover image used for the steganography
#               secret - secret image to be put into cover image
#               output - file name of the converted steganography image
#               password - password used for encryption of pixels and filename
#
#  RETURNS:     Saved steganography image coverted from cover and secret images
#
#  NOTES:       A header length (integer value) and encrypted header is embedded
#               before the pixel data of the secret image which details the filename
#               and size of the secret image. The encryption functionality will be
#               implemented with the symmetric-key algorithm ”DES”. The user input
#               password will be factored into a key of length 8, 16, or 24 bytes,
#               and used for encrypting or decrypting the pixels and filename of
#               the secret image. The idea is to hide a single bit in the last bit
#               of a rgb value. Each pixel of the secret image can be split and hidden
#               into 9 pixels of the cover image.
#
# ----------------------------------------------------------------------------


def create_image(cover, secret, output, password):
    # load both cover and secret image
    pixel_obj = PixelLoader(cover)
    pixel_obj2 = PixelLoader(secret)

    # craft header data
    filename = path_leaf(secret)
    dimension = pixel_obj2.get_dimension()
    header = filename + " " + str(dimension[0]) + " " + str(dimension[1]) + " "
    header_len = len(header)
    if header_len % 8 != 0:
        header_len += 8 - header_len % 8

    # check if cover image is big enough to hide secret data
    cover_d = pixel_obj.get_dimension()
    cover_size = cover_d[0] * cover_d[1]
    required_pixels = (dimension[0] * dimension[1]) * 9 + (header_len + 1) * 3
    if cover_size < required_pixels:
        print("Error: Cover image does not have sufficent space, needs to be larger")
        print("Cover img size: " + str(cover_size))
        print("Required size: >=" + str(required_pixels))
        sys.exit()

    # generate DES key
    key = DesKey(bytes(password, "utf-8"))

    # encrypt header data
    array = []
    for c in header:
        array.append(ord(c))
    cipher_text = key.encrypt(bytes(array), padding=True).hex()
    encrypted_header = [cipher_text[i:i + 2] for i in range(0, len(cipher_text), 2)]

    for c in str(header_len) + " ":
        hide_1byte_in_9pixels(pixel_obj, ascii_to_bits(c))
    for hex_string in encrypted_header:
        hide_1byte_in_9pixels(pixel_obj, int_to_bits(int(hex_string, 16)))

    # encrypt image data
    data_array = pixel_obj2.to_int_arry()
    cipher_text = key.encrypt(bytes(data_array), padding=True).hex()
    encrypted_rgb = [cipher_text[i:i + 2] for i in range(0, len(cipher_text), 2)]
    for hex_string in encrypted_rgb:
        hide_1byte_in_9pixels(pixel_obj, int_to_bits(int(hex_string, 16)))

    # save steganography image
    pixel_obj.save(output)
    print("--> DONE!")
#-----------------------------------------------------------------------------
# FUNCTION:    extract_image
#
#  PROGRAMMER:  Jason Soukchamroeun
#
#  INTERFACE:   extract_image(stego_img, password)
#               stego_img - steganography image to be extracted and decrypted
#               password - password used for decryption of pixels and filename
#
#  RETURNS:     Saved secret image hidden inside steganography image
#
#  NOTES:       The application will read the header length and the retrieve
#               header length of bytes will then be decrypted to acquire header
#               information. It will then proceed to do the same process to
#               acquire the pixels for the secret image before finally
#               saving the secret image.
#
# ----------------------------------------------------------------------------


def extract_image(stego_img, password):
    pixel_obj3 = PixelLoader(stego_img)

    # create DES key from password
    key = DesKey(bytes(password, "utf-8"))

    # extract/decrypt header information
    header_len = extract_int(pixel_obj3, " ")
    hex_array = extract_hex_stream(pixel_obj3, header_len)
    decrypted_header = key.decrypt(bytes(hex_array)).hex()
    decrypted_header = [decrypted_header[i:i+2] for i in range(0, len(decrypted_header), 2)]
    header = []
    for hex_string in decrypted_header:
        header.append(chr(int(hex_string, 16)))
    header = ''.join(header)

    header_info = header.split(" ")
    if len(header_info) != 4:
        print("Error: password invalid")
        sys.exit()

    filename = header_info[0]
    row_n = int(header_info[1])
    col_n = int(header_info[2])

    # extract image
    secret_img = Image.new('RGB', (row_n, col_n))

    n = (row_n * col_n) * 3
    if n % 8 != 0:
        n += 8 - (n % 8)

    values = []
    for i in range(n):
        pixels = []
        for j in range(3):
            coordinate = pixel_obj3.next_pixel_coordinate()
            pixels.append(pixel_obj3.get_pixel_at(coordinate))
        values.append(extract_hex_from_pixels(pixels))

    # decrypt RGB values
    key = DesKey(bytes(password, "utf-8"))
    decrypted_rgb = key.decrypt(bytes(values)).hex()
    decrypted_rgb = [decrypted_rgb[i:i+2] for i in range(0, len(decrypted_rgb), 2)]

    index = 0
    for row in range(row_n):
        for col in range(col_n):
            r = int(decrypted_rgb[index], 16)
            index += 1
            g = int(decrypted_rgb[index], 16)
            index += 1
            b = int(decrypted_rgb[index], 16)
            index += 1
            secret_img.putpixel((row, col), (r,g,b))

    secret_img.save(filename)
    print("--> DONE!")


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def ascii_to_bits(c):
    result = []
    bits = bin(ord(c))[2:]
    bits = '00000000'[len(bits):] + bits
    result.extend([int(bit) for bit in bits])
    return result


def bits_to_ascii(bits):
    return chr(int(''.join([str(bit) for bit in bits]), 2))


def int_to_bits(n):
    result = []
    bits = bin(n)[2:]
    bits = '00000000'[len(bits):] + bits
    result.extend([int(bit) for bit in bits])
    return result


def bits_to_int(bits):
    return int(''.join([str(bit) for bit in bits]), 2)


def hide_3bits_in_pixel(original_pixel, bit_1, bit_2, bit_3):
    r, g, b = original_pixel
    new_r = (r & 254) + bit_1
    new_g = (g & 254) + bit_2
    new_b = (b & 254) + bit_3
    return (new_r, new_g, new_b)


def hide_2bits_in_pixel(original_pixel, bit_1, bit_2):
    r, g, b = original_pixel
    r = (r & 254) + bit_1
    g = (g & 254) + bit_2
    return (r, g, b)


def hide_1byte_in_9pixels(loader, bits):
    coordinate = loader.next_pixel_coordinate()
    tmp = loader.get_pixel_at(coordinate)
    new_pixel = hide_3bits_in_pixel(tmp, bits[0], bits[1], bits[2])
    loader.edit_pixel_at(coordinate, new_pixel)

    coordinate = loader.next_pixel_coordinate()
    tmp = loader.get_pixel_at(coordinate)
    new_pixel = hide_3bits_in_pixel(tmp, bits[3], bits[4], bits[5])
    loader.edit_pixel_at(coordinate, new_pixel)

    coordinate = loader.next_pixel_coordinate()
    tmp = loader.get_pixel_at(coordinate)
    new_pixel = hide_2bits_in_pixel(tmp, bits[6], bits[7])
    loader.edit_pixel_at(coordinate, new_pixel)


def extract_hex_from_pixels(pixels):
    color_values = [value for pixel in pixels for value in pixel]
    bits = []
    for i in range(8):
        bits.append(int_to_bits(color_values[i])[7])
    return bits_to_int(bits)


def extract_ascii_from_pixels(pixels):
    bits = []
    values = [value for pixel in pixels for value in pixel]
    for i in range(8):
        bits.append(int_to_bits(values[i])[7])
    return (bits_to_ascii(bits))


def extract_int(loader, delim):
    c_list = []
    while True:
        pixels = []
        for i in range(3):
            coordinate = loader.next_pixel_coordinate()
            pixels.append(loader.get_pixel_at(coordinate))
        c = extract_ascii_from_pixels(pixels)
        if c == delim:
            break
        c_list.append(c)
    return int(''.join(c_list))


def extract_hex_stream(loader, len):
    hex_list = []
    for i in range(len):
        pixels = []
        for i in range(3):
            coordinate = loader.next_pixel_coordinate()
            pixels.append(loader.get_pixel_at(coordinate))
        hex_value = extract_hex_from_pixels(pixels)
        hex_list.append(hex_value)
    return hex_list