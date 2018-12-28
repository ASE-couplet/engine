import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def poetry_vertical(poetry, font_path=None):
    font_size = 40
    sentences = poetry.split('\n')
    num_words = len(sentences[0])

    image = Image.new("RGB", ((num_words) * font_size, 150), "white")
    draw = ImageDraw.Draw(image)

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
        print(font)
    else:
        font = None

    draw.multiline_text(xy=(0, 0), text=poetry, fill=(0, 0, 0), font=font,
                        spacing=30, align='left')

    del draw
    image = image.rotate(270, expand=1)
    return image


def poetry_vertical_v2(poetry, font_path=None):
    font_size = 40
    sentences = poetry.split('\n')
    num_words = len(sentences[0])

    image = Image.new("RGB", (150, (num_words + 4) * font_size), "white")
    draw = ImageDraw.Draw(image)

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
        print(font)
    else:
        font = None
    w = 150 - font_size
    for sen in sentences:
        h = 0
        for word in sen:
            if word in [',', '，']:
                draw.text(xy=(w, h - font_size * 0.5), text=word, fill=(0, 0, 0), font=font, align='right')
                h += font_size
            elif word in ['.', '。']:
                pass
            else:
                draw.text(xy=(w, h), text=word, fill=(0, 0, 0), font=font, align='right')
                h += font_size + 5
        w -= (font_size + 20)

    del draw
    return image


def resize_image(img, size=(100, 100)):
    """
    :param img:
    :param size:
    :return:
    """
    if img.mode not in ('L', 'RGB'):
        img = img.convert('RGB')
    img = img.resize(size)
    return img


def card_vertical(image_path, poetry, QRcode_path, font_path, logo_path, output_path):
    # load and resize image
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_w, img_h = img.size
        scale = img_h / img_w
        img_w = int(max(scale * 680, 1000))
        img = resize_image(img, (680, img_w))
        img_w, img_h = img.size
    else:
        raise RuntimeError('image path :{} not exists '.format(image_path))
    # load and resize QRcode
    if os.path.exists(QRcode_path):
        QRcode = Image.open(QRcode_path)
        QRcode = resize_image(QRcode, (150, 150))
    else:
        raise RuntimeError("QRcode path :{} not exists ".format(QRcode_path))
    # load and resize logo
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logo_w, logo_h = logo.size
        scale = logo_h / logo_w
        logo = resize_image(logo, (40, int(40 * scale)))
    else:
        raise RuntimeError("logo path :{} not exists ".format(logo_path))
    # get poetry
    poetry_img = poetry_vertical_v2(poetry, font_path)

    blank_img = Image.new('RGB', (940, img_h), "white")
    blank_img.paste(img, (0, 0))
    blank_img.paste(logo, (img_w + 20, 50))
    blank_img.paste(poetry_img, (img_w + 80, 50))
    blank_img.paste(QRcode, (img_w + 80, img_h - 210))

    # show and save
    # blank_img.show()
    blank_img.save(output_path)
    return blank_img


def poetry_horizontal(poetry, font_path=None):
    font_size = 40
    sentences = poetry.split('\n')
    num_words = len(sentences[0])

    image = Image.new("RGB", ((num_words) * font_size, 150), "white")
    draw = ImageDraw.Draw(image)

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
        print(font)
    else:
        font = None

    draw.multiline_text(xy=(0, 0), text=poetry, fill=(0, 0, 0), font=font,
                        spacing=30, align='left')

    del draw
    return image


def card_horizontal(image_path, poetry, QRcode_path, font_path, logo_path, output_path):
    # load and resize image
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_w, img_h = img.size
        scale = img_h / img_w
        img_w = int(scale * 980)
        img = resize_image(img, (980, img_w))
        img_w, img_h = img.size
    else:
        raise RuntimeError('image path :{} not exists '.format(image_path))
    # load and resize QRcode
    if os.path.exists(QRcode_path):
        QRcode = Image.open(QRcode_path)
        QRcode = resize_image(QRcode, (150, 150))
    else:
        raise RuntimeError("QRcode path :{} not exists ".format(QRcode_path))
    # load and resize logo
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        logo_w, logo_h = logo.size
        scale = logo_w / logo_h
        logo = resize_image(logo, (int(40 * scale), 40))
    else:
        raise RuntimeError("logo path :{} not exists ".format(logo_path))
    # get poetry
    poetry_img = poetry_horizontal(poetry, font_path)

    blank_img = Image.new('RGB', (980, img_h + 250), "white")
    blank_img.paste(img, (0, 0))
    blank_img.paste(poetry_img, (45, img_h + 40))
    blank_img.paste(logo, (45, img_h + 190))
    blank_img.paste(QRcode, (980 - 200, img_h + 60))

    # show and save
    blank_img.show()
    blank_img.save(output_path)
    return blank_img


def generate_card(image_path, poetry, QRcode_path, font_path, logo_prefix, output_path):
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img_w, img_h = img.size
    else:
        raise RuntimeError('image path :{} not exists '.format(image_path))
    if img_w > img_h:
        logo_path = logo_prefix + '_horizontal.png'
        card_horizontal(image_path, poetry, QRcode_path, font_path, logo_path, output_path)
    else:
        logo_path = logo_prefix + '_vertical.png'
        card_vertical(image_path, poetry, QRcode_path, font_path, logo_path, output_path)
    return True

if __name__ == "__main__":
    image_path = 'kuan.png'
    poetry = u'落霞与孤鹜齐飞，秋水共长天一色。 \n落霞与孤鹜齐飞，秋水共长天一色。 \n'
    QRcode_path = 'QR.png'
    font_path = 'Light.ttc'
    logo_prefix = 'logo'
    output_path = './3.png'
    generate_card(image_path, poetry, QRcode_path, font_path, logo_prefix, output_path)
    # card_vertical(image_path, poetry, QRcode_path, font_path, logo_path, output_path)
    # card_horizontal(image_path, poetry, QRcode_path, font_path, logo_path, output_path)