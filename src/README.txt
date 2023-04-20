To run the program, one of the following two commands must be written...
	• dcstego.py [-c] cover_image secret_image output_name password
		– -c/–create is the switch to create a steganography image
		– cover_image is the user provided cover image to be used
		– secret_image is the user provided secret image to be used
		– output_name is the name to provide for the outputted steganogprahy image
		– password is a word of no more than 24 length to encrypt the secret image

	• dcstego.py [-e] stego_image password
		– -e/–extract is the switch to extract from a steganography image
		– stego_image is the user provided steganography image to be used
		– password is a word of no more than 24 length to decrypt the secret image

	• example of create:
		- $ dcstego.py -c coverimage.bmp secretimage.bmp newimagename.bmp PasswordisCool

	• example of extract:
		- $ dcstego.py -e newimagename.bmp PasswordisCool
