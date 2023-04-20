from PIL import Image


class PixelLoader:
    img = ''
    row_max = 0
    col_max = 0
    row = 0
    col = 0
    count = 0

    def __init__(self, filename):
        _img = Image.open(filename)
        self.img = _img.convert('RGB')
        self.row_max = _img.size[0]
        self.col_max = _img.size[1]
        self.count = self.total = _img.size[0] * _img.size[1]

    def next_pixel_coordinate(self):
        coordinate = (self.row, self.col)
        if self.count > 0:
            self.count -= 1
            self.col += 1
            self.row = (self.row + 1) if self.col >= self.col_max else self.row
            self.col = self.col%self.col_max
            return coordinate
        else:
            return 0

    def get_dimension(self):
        return (self.row_max, self.col_max)

    def to_int_arry(self):
        index = 0
        array = []
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                pixel = self.img.getpixel((i, j))
                array.append(pixel[0]) # R
                array.append(pixel[1]) # G
                array.append(pixel[2]) # B
        return array

    def get_pixel_at(self, coordinate):
        return self.img.getpixel(coordinate)

    def edit_pixel_at(self, coordinate, new_pixel):
        self.img.putpixel(coordinate, new_pixel)

    def save(self, _filename):
        self.img.save(_filename)
