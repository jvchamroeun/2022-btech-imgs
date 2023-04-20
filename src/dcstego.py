#!/usr/bin/python3
import argparse
from dcutils import *

#-----------------------------------------------------------------------------
# FUNCTION:    check_password
#
#  PROGRAMMER:  Jason Soukchamroeun
#
#  INTERFACE:   def check_password(password)
#               password - Text string to be padded to length of 8, 16 or 24
#
#  RETURNS:     password - Text string padded to length 8, 16, 24
#
#  NOTES: The password is entered by the user and is required to be less than
#         24 of length. The text string is padded determined by the length
#         which is later used for a key to encrypt and decrypt the secret image.
#
# ----------------------------------------------------------------------------


def check_password(password):
    length = len(password)
    if length > 24:
        print("Error: Invalid password length")
        print("Password must be of length < 24")
        sys.exit()
    if length <= 8 and length % 8 != 0:
        password = "{:<8}".format(password)

    elif length <= 16 and length % 8 != 0:
        password = "{:<16}".format(password)
    else:
        password = "{:<24}".format(password)

    return password
#-----------------------------------------------------------------------------
# FUNCTION:    check_extension
#
#  PROGRAMMER:  Jason Soukchamroeun
#
#  INTERFACE:   def check_extension(filename)
#               filename - filename given to be parsed
#
#  RETURNS:
#
#  NOTES: The file name is required to be in BMP otherwise the application
#         will close.
#
# ----------------------------------------------------------------------------


def check_extension(filename):
    if not filename.endswith('.bmp'):
        print("Error: Invalid file extension:")
        print(filename + ", must be of type .bmp")
        sys.exit()
#-----------------------------------------------------------------------------
# FUNCTION:    main
#
#  PROGRAMMER:  Jason Soukchamroeun
#
#  INTERFACE:   def main()
#
#  RETURNS:     Result on success or failure.
#
#  NOTES: Main entry point into the program. Initializes command-line argument
#         parsing. Encrypts or decrypts secret image based on input.
#
# ----------------------------------------------------------------------------


def main():
    action_parser = argparse.ArgumentParser(description='stegonography')

    # either encrypt or decrypt
    group = action_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--create", help="create steganography image", action='store_true')
    group.add_argument("-e", "--extract", help="extract secret image", action='store_true')

    # parser for option --create
    parser_create = argparse.ArgumentParser()
    parser_create.add_argument("cover_img", metavar="cover_image", help="cover image file")
    parser_create.add_argument("secret_img", metavar="secret_image", help="secret image file")
    parser_create.add_argument("output_name", metavar="output_name", help="name of the output file")
    parser_create.add_argument("password", metavar="password", help="password for encrypt/decrypt secret image")

    # parser for option --extract
    parser_extract = argparse.ArgumentParser()
    parser_extract.add_argument("stego_img", metavar="stego_image", help="image file to extract")
    parser_extract.add_argument("password", metavar="password", help="password required for decryption")

    # evaluate which action to perform [create or extract]
    args = action_parser.parse_known_args(sys.argv[1:])
    if args[0].create:
        args = parser_create.parse_args(sys.argv[2:])
        args.password = check_password(args.password)
        check_extension(args.cover_img)
        check_extension(args.secret_img)
        check_extension(args.output_name)
        create_image(args.cover_img, args.secret_img, args.output_name, args.password)
    else:
        args = parser_extract.parse_args(sys.argv[2:])
        args.password = check_password(args.password)
        check_extension(args.stego_img)
        extract_image(args.stego_img, args.password)


# main function
if __name__ == "__main__":
    main()
