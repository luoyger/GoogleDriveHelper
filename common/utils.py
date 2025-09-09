# -*- coding: utf-8 -*-
import asyncio
import datetime
import hashlib
import mimetypes
import os
import random
import re
import socket
import string
import uuid
from typing import Union, Tuple, IO

import httpx
import requests
import unicodedata
from datetime import timedelta
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup
from pikepdf import Pdf, Rectangle
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from common.logger import logger


def save_pid():
    """
    保存当前进程pid到文件，可用于停止服务。

    :return: None
    """
    with open("pid.txt", "w") as f:
        f.write(str(os.getpid()))


def generate_request_id():
    return str(uuid.uuid4()).replace('-', '')


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def get_public_ip() -> str:
    try:
        ip = requests.get('https://ifconfig.me').text
    except Exception:
        ip = "127.0.0.1"
    return ip


def run_async_task_in_thread(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    # 设置为当前线程的事件循环
    asyncio.set_event_loop(loop)
    task = loop.run_until_complete(func(*args, **kwargs))
    loop.close()
    return task


def get_redirect_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
        return final_url
    except requests.RequestException as e:
        print(f"Error accessing final url {url}: {e}")
        return None


def is_url_accessible(url):
    try:
        response = requests.head(url, allow_redirects=True)
        # 检查状态码是否在 200-299 范围内
        if 200 <= response.status_code < 300:
            return True
        else:
            return False
    except requests.RequestException as e:
        # 捕获所有请求异常
        print(f"Error accessing {url}: {e}")
        return False


def get_relative_path(file_path):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    relative_path = os.path.relpath(file_path, root_dir)
    return relative_path


def format_milliseconds_to_hour_minute_seconds(milliseconds):
    delta = timedelta(milliseconds=milliseconds)
    format_time = '00:00'
    if delta.total_seconds() < 3600:
        # 小于一小时，只显示分秒的样式
        minutes = delta.seconds // 60
        seconds = delta.seconds % 60
        format_time = f"{minutes:02d}:{seconds:02d}"
    else:
        # 大于等于一小时，显示时分秒的样式
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        format_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return format_time


def format_seconds_to_hour_minute_seconds(seconds):
    delta = timedelta(seconds=seconds)
    format_time = '00:00'
    if delta.total_seconds() < 3600:
        # 小于一小时，只显示分秒的样式
        minutes = delta.seconds // 60
        seconds = delta.seconds % 60
        format_time = f"{minutes:02d}分{seconds:02d}秒"
    else:
        # 大于等于一小时，显示时分秒的样式
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        format_time = f"{hours:02d}时{minutes:02d}分{seconds:02d}秒"

    return format_time


def format_milliseconds_to_seconds(milliseconds):
    delta = timedelta(milliseconds=milliseconds)
    return delta.total_seconds()


def timestamp_to_string(timestamp):
    # 使用datetime模块的fromtimestamp()方法将时间戳转换为datetime对象
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    # 使用strftime()方法将datetime对象格式化为字符串
    string = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return string


def hash_url(url, algorithm='sha256'):
    # 将URL编码为字节
    url_bytes = url.encode('utf-8')
    # 创建哈希对象
    hash_object = hashlib.new(algorithm)
    # 更新哈希对象
    hash_object.update(url_bytes)
    # 获取哈希值
    hash_value = hash_object.hexdigest()
    return hash_value[:32]


def sanitize_title(title):
    """
    处理标题中的特殊字符，将其替换为下划线

    :param title: 原始标题
    :return: 处理后的标题
    """
    # 使用正则表达式将非字母数字字符替换为下划线
    sanitized_title = re.sub(r'\W+', '_', title)
    return sanitized_title


def generate_random_string(length=8):
    """
    生成指定长度的随机字符串

    :param length: 随机字符串的长度
    :return: 随机字符串
    """
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for i in range(length))
    return random_string


def get_current_time_string():
    """
    获取当前时间的字符串表示，格式为YYYYMMDDHHMMSS

    :return: 当前时间的字符串表示
    """
    now = datetime.datetime.now()
    time_string = now.strftime("%Y%m%d%H%M%S")
    return time_string


def generate_id(title):
    """
    生成唯一的ID，由标题、随机字符串和当前时间组成

    :param title: 原始标题
    :return: 生成的唯一ID
    """
    sanitized_title = sanitize_title(title)
    random_string = generate_random_string()
    time_string = get_current_time_string()
    unique_id = f"{sanitized_title}_{random_string}_{time_string}"
    return unique_id


def add_custom_parameter(url, param_name, param_value):
    # 解析 URL
    parsed_url = urlparse(url)
    # 获取查询字符串并转换成字典
    query_params = parse_qs(parsed_url.query)

    # 添加或更新参数
    query_params[param_name] = param_value

    # 重新构建查询字符串
    new_query_string = urlencode(query_params, doseq=True)

    # 重新构建完整的 URL
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))

    return new_url


def count_words(text):
    def auto_space(s):
        out = ""
        for char in s:
            out = add_space_at_boundary(out, char)
        return out

    def add_space_at_boundary(prefix, next_char):
        if len(prefix) == 0:
            return next_char
        last_char = prefix[-1]
        if is_latin(last_char) != is_latin(next_char) and is_allow_space(next_char) and is_allow_space(last_char):
            return prefix + " " + next_char
        return prefix + next_char

    def is_latin(char):
        return len(char.encode('utf-8')) == 1

    def is_allow_space(char):
        return not char.isspace() and not unicodedata.category(char).startswith('P')

    word_count = 0
    plain_words = auto_space(text).split()
    for word in plain_words:
        rune_count = len(word)
        if len(word.encode('utf-8')) == rune_count:  # 英文
            word_count += 1
        else:  # 中文
            word_count += len(word)
    return word_count


# 该函数占用内存较多，对于5M的图片，内存占用达9G
def add_watermark_to_image_old(fp: Union[str, bytes, os.PathLike[str], os.PathLike[bytes], IO[bytes]],
                               output_image_path: str,
                               watermark_text: str,
                               font_path: str = None,
                               font_size: int = 24,
                               color: tuple = (128, 128, 128),  # 灰色
                               opacity: int = 128,  # 半透明
                               angle: int = 30,  # 倾斜角度
                               x_space: int = 100,  # 水印x轴间隔
                               y_space: int = 100  # 水印y轴间隔
                               ):
    base_image = Image.open(fp).convert("RGBA")
    width, height = base_image.size

    # 创建一个比原始图片更大的图层，以便在旋转后仍然覆盖整个图片
    diagonal = int((width ** 2 + height ** 2) ** 0.5)
    txt = Image.new('RGBA', (diagonal, diagonal), (255, 255, 255, 0))

    if font_path is None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = f'{file_dir}/font/方正楷体简体.ttf'
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(txt)

    # 获取水印文本的边界框
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 计算行数和列数
    rows = (diagonal // (text_height + y_space)) + 1
    cols = (diagonal // (text_width + x_space)) + 1

    # 在透明图层上绘制水印文本
    for row in range(rows):
        for col in range(cols):
            x = col * (text_width + x_space)
            y = row * (text_height + y_space)
            draw.text((x, y), watermark_text, font=font, fill=color + (opacity,))

    # 旋转水印图层
    txt = txt.rotate(angle, expand=1)

    # 创建一个与输入图片大小相同的透明图层
    rotated_txt = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

    # 计算粘贴旋转后水印图层的位置，使其居中
    txt_width, txt_height = txt.size
    paste_x = (base_image.size[0] - txt_width) // 2
    paste_y = (base_image.size[1] - txt_height) // 2
    rotated_txt.paste(txt, (paste_x, paste_y), txt)

    # 将旋转后的水印图层与原始图片合成
    watermarked = Image.alpha_composite(base_image, rotated_txt)

    # 保存带有水印的图片
    watermarked.save(output_image_path)


def add_watermark_to_image_old2(fp, output_image_path, watermark_text, font_path=None, font_size=24,
                                color=(128, 128, 128), opacity=128, angle=30, x_space=100, y_space=100):
    base_image = Image.open(fp).convert("RGBA")
    width, height = base_image.size

    if font_path is None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(file_dir, 'font', '方正楷体简体.ttf')
    font = ImageFont.truetype(font_path, font_size)

    # 创建一个与原始图片大小相同的透明图层
    txt = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)

    # 使用textbbox获取文本边界框尺寸
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    cols = (width // (text_width + x_space)) + 1
    rows = (height // (text_height + y_space)) + 1

    # 在透明图层上绘制水印文本
    for row in range(rows):
        for col in range(cols):
            x = col * (text_width + x_space)
            y = row * (text_height + y_space)
            draw.text((x, y), watermark_text, font=font, fill=color + (opacity,))

    # 旋转水印图层
    txt = txt.rotate(angle, expand=1)

    # 将旋转后的水印图层与原始图片合成
    watermarked = Image.alpha_composite(base_image, txt)

    # 保存带有水印的图片
    watermarked.save(output_image_path)


def add_watermark_to_image(image_path, output_path, text, font_path=None, font_size=40, color=(255, 255, 255, 128),
                           spacing=100, angle=30):
    # 打开图片
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size

    # 加载字体
    if font_path:
        try:
            # 使用绝对路径
            font_path = os.path.abspath(font_path)
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            print(f"Cannot open font resource: {font_path}. Using default font.")
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    # 计算文本大小
    dummy_image = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(dummy_image)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 创建一个单个水印文本的图层
    single_watermark_layer = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    single_draw = ImageDraw.Draw(single_watermark_layer)
    single_draw.text((0, 0), text, font=font, fill=color)

    # 旋转单个水印文本图层
    single_watermark_layer = single_watermark_layer.rotate(angle, expand=1)

    # 获取旋转后图层的大小
    rotated_width, rotated_height = single_watermark_layer.size

    # 创建一个新的透明图层用于绘制水印
    watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))

    # 在整个图层上重复绘制旋转后的水印文本
    for y in range(0, height, rotated_height + spacing):
        for x in range(0, width, rotated_width + spacing):
            watermark_layer.paste(single_watermark_layer, (x, y), single_watermark_layer)

    # 将水印图层与原始图片合成
    watermarked_image = Image.alpha_composite(image, watermark_layer)

    # 保存图片
    watermarked_image.save(output_path, 'PNG')


def add_watermark_to_html(input_html_content, watermark):
    js_code = """
    function watermark(settings) {
        //默认设置
        var defaultSettings = {
            watermark_txt: "watermark",
            watermark_x: 20, //水印起始位置x轴坐标
            watermark_y: 20, //水印起始位置Y轴坐标
            watermark_rows: 20, //水印行数
            watermark_cols: 20, //水印列数
            watermark_x_space: 100, //水印x轴间隔
            watermark_y_space: 50, //水印y轴间隔
            watermark_color: '#aaa', //水印字体颜色
            watermark_alpha: 0.2, //水印透明度
            watermark_fontsize: '15px', //水印字体大小
            watermark_font: '微软雅黑', //水印字体
            watermark_width: 210, //水印宽度
            watermark_height: 80, //水印长度
            watermark_angle: 30 //水印倾斜度数
        };
        if (arguments.length === 1 && typeof arguments[0] === "object") {
            var src = arguments[0] || {};
            for (key in src) {
                if (src[key] && defaultSettings[key] && src[key] === defaultSettings[key]) continue;
                else if (src[key]) defaultSettings[key] = src[key];
            }
        }
    
        function createWatermark() {
            var oTemp = document.createDocumentFragment();
            //获取页面最大宽度
            var page_width = Math.max(document.body.scrollWidth, document.body.clientWidth);
            // var cutWidth = page_width * 0.0150;
            // var page_width = page_width - cutWidth;
            //获取页面最大高度
            var page_height = Math.max(document.body.scrollHeight, document.body.clientHeight) + 450;
            page_height = Math.max(page_height, window.innerHeight - 30);
    
            //如果将水印列数设置为0，或水印列数设置过大，超过页面最大宽度，则重新计算水印列数和水印x轴间隔
            watermark_cols = defaultSettings.watermark_cols;
            watermark_x_space = defaultSettings.watermark_x_space
            if (defaultSettings.watermark_cols == 0 || (parseInt(defaultSettings.watermark_x + defaultSettings.watermark_width * defaultSettings.watermark_cols + defaultSettings.watermark_x_space * (defaultSettings.watermark_cols - 1)) > page_width)) {
                watermark_cols = parseInt((page_width - defaultSettings.watermark_x + watermark_x_space) / (defaultSettings.watermark_width + watermark_x_space));
                watermark_x_space = parseInt((page_width - defaultSettings.watermark_x - defaultSettings.watermark_width * watermark_cols) / (watermark_cols - 1));
                console.log("existidefaultSettings.watermark_cols:", defaultSettings.watermark_cols)
            }
            //如果将水印行数设置为0，或水印行数设置过大，超过页面最大长度，则重新计算水印行数和水印y轴间隔
            if (defaultSettings.watermark_rows == 0 || (parseInt(defaultSettings.watermark_y + defaultSettings.watermark_height * defaultSettings.watermark_rows + defaultSettings.watermark_y_space * (defaultSettings.watermark_rows - 1)) > page_height)) {
                defaultSettings.watermark_rows = parseInt((defaultSettings.watermark_y_space + page_height - defaultSettings.watermark_y) / (defaultSettings.watermark_height + defaultSettings.watermark_y_space));
                defaultSettings.watermark_y_space = parseInt(((page_height - defaultSettings.watermark_y) - defaultSettings.watermark_height * defaultSettings.watermark_rows) / (defaultSettings.watermark_rows - 1));
            }
            var x;
            var y;
            for (var i = 0; i < defaultSettings.watermark_rows; i++) {
                y = defaultSettings.watermark_y + (defaultSettings.watermark_y_space + defaultSettings.watermark_height) * i;
                for (var j = 0; j < watermark_cols; j++) {
                    x = defaultSettings.watermark_x + (defaultSettings.watermark_width + watermark_x_space) * j;
                    var mask_div = document.createElement('div');
                    mask_div.id = 'mask_div' + i + j;
                    mask_div.className = 'mask_div';
                    mask_div.appendChild(document.createTextNode(defaultSettings.watermark_txt));
                    //设置水印div倾斜显示
                    mask_div.style.webkitTransform = "rotate(-" + defaultSettings.watermark_angle + "deg)";
                    mask_div.style.MozTransform = "rotate(-" + defaultSettings.watermark_angle + "deg)";
                    mask_div.style.msTransform = "rotate(-" + defaultSettings.watermark_angle + "deg)";
                    mask_div.style.OTransform = "rotate(-" + defaultSettings.watermark_angle + "deg)";
                    mask_div.style.transform = "rotate(-" + defaultSettings.watermark_angle + "deg)";
                    mask_div.style.visibility = "";
                    mask_div.style.position = "fixed"; // 修改为fixed
                    mask_div.style.left = x + 'px';
                    mask_div.style.top = y + 'px';
                    mask_div.style.overflow = "hidden";
                    mask_div.style.zIndex = "9999";
                    //让水印不遮挡页面的点击事件
                    mask_div.style.pointerEvents = 'none';
                    mask_div.style.opacity = defaultSettings.watermark_alpha;
                    mask_div.style.fontSize = defaultSettings.watermark_fontsize;
                    mask_div.style.fontFamily = defaultSettings.watermark_font;
                    mask_div.style.color = defaultSettings.watermark_color;
                    mask_div.style.textAlign = "center";
                    mask_div.style.whiteSpace = "pre-wrap"; /* 保留换行符 */
                    mask_div.style.width = defaultSettings.watermark_width + 'px';
                    mask_div.style.height = defaultSettings.watermark_height + 'px';
                    mask_div.style.display = "block";
                    oTemp.appendChild(mask_div);
                }
            }
            // 清除已有的水印
            var existingWatermarks = document.querySelectorAll('.mask_div');
            existingWatermarks.forEach(function (watermark) {
                watermark.parentNode.removeChild(watermark);
            });
            document.body.appendChild(oTemp);
        }
    
        // 初始创建水印
        createWatermark();
    
        // 监听窗口大小变化事件
        window.addEventListener('resize', function () {
            createWatermark();
        });
    }
    watermark({"watermark_txt": {watermarkContent} });"""

    # # 读取HTML文件
    # with open(input_html_path, 'r', encoding='utf-8') as file:
    #     soup = BeautifulSoup(input_html_path, 'lxml')
    soup = BeautifulSoup(input_html_content, 'lxml')

    # 创建一个新的<script>标签
    script_tag = soup.new_tag('script')
    watermark = watermark.replace('\n', '\\n')
    script_tag.string = js_code.replace('{watermarkContent}', f'"{watermark}"')

    # 如果没有<head>标签，则插入到<body>标签的末尾
    if soup.body:
        soup.body.append(script_tag)
    else:
        # 如果没有<body>标签，则直接插入到HTML文档的末尾
        soup.append(script_tag)

    # 将修改后的HTML写回文件
    # with open(output_html_path, 'w', encoding='utf-8') as file:
    #     file.write(str(soup))
    return str(soup)


def add_watermark_to_pdf(input_pdf, output_pdf, watermark_text):
    def create_pdf_watermark(content: str,
                             filename: str,
                             width: Union[int, float],
                             height: Union[int, float],
                             font: str,
                             fontsize: int,
                             angle: Union[int, float] = 30,
                             text_stroke_color_rgb: Tuple[int, int, int] = (0, 0, 0),
                             text_fill_color_rgb: Tuple[int, int, int] = (0, 0, 0),
                             text_fill_alpha: Union[int, float] = 1) -> None:
        # 创建PDF文件，指定文件名及尺寸，以像素为单位
        c = canvas.Canvas(filename, pagesize=(width * units.mm, height * units.mm))

        # 画布平移保证文字完整性
        c.translate(0.1 * width * units.mm, 0.1 * height * units.mm)

        # 设置旋转角度
        c.rotate(angle)

        # 设置字体大小
        c.setFont(font, fontsize)

        # 设置字体轮廓彩色
        c.setStrokeColorRGB(*text_stroke_color_rgb)

        # 设置填充色
        c.setFillColorRGB(*text_fill_color_rgb)

        # 设置字体透明度
        c.setFillAlpha(text_fill_alpha)

        # 绘制字体内容
        c.drawString(0, 0, content)

        # 保存文件

        c.save()

    def add_pdf_watermark(target_pdf_path: str,
                          output_pdf_path: str,
                          watermark_pdf_path: str,
                          nrow: int,
                          ncol: int,
                          skip_pages=None):
        # 选择需要添加水印的pdf文件
        if skip_pages is None:
            skip_pages = []
        target_pdf = Pdf.open(target_pdf_path)

        # 读取水印pdf文件并提取水印
        watermark_pdf = Pdf.open(watermark_pdf_path)
        watermark_page = watermark_pdf.pages[0]

        # 遍历目标pdf文件中的所有页，批量添加水印
        for idx, target_page in enumerate(target_pdf.pages):
            for x in range(ncol):
                for y in range(nrow):
                    # 向目标页指定范围添加水印
                    target_page.add_overlay(watermark_page,
                                            Rectangle(target_page.trimbox[2] * x / ncol,
                                                      target_page.trimbox[3] * y / nrow,
                                                      target_page.trimbox[2] * (x + 1) / ncol,
                                                      target_page.trimbox[3] * (y + 1) / nrow
                                                      ))
        # 保存PDF文件，同时对pdf文件进行重命名，从文件名第7位置写入后缀名
        target_pdf.save(output_pdf_path)

    file_dir = os.path.dirname(os.path.abspath(__file__))
    pdfmetrics.registerFont(TTFont('方正楷体简体', f'{file_dir}/font/方正楷体简体.ttf'))
    watermark_pdf_path = f'{input_pdf[:-4]}_watermark_template.pdf'
    create_pdf_watermark(content=watermark_text,
                         filename=watermark_pdf_path,
                         width=200,
                         height=200,
                         font='方正楷体简体',
                         fontsize=24,
                         text_fill_alpha=0.2)
    add_pdf_watermark(target_pdf_path=input_pdf,
                      output_pdf_path=output_pdf,
                      # 把生成的水印示例，添加到目标水印文件中
                      watermark_pdf_path=watermark_pdf_path,
                      nrow=3,
                      ncol=2,
                      skip_pages=[0])
    os.remove(watermark_pdf_path)


def get_content_type(url):
    try:
        # 发送一个 HEAD 请求
        response = requests.head(url, allow_redirects=False)

        # 检查是否是重定向
        if response.status_code == 302:
            # 获取重定向的 URL
            redirect_url = response.headers.get('Location')
            # 发送 GET 请求到重定向的 URL
            response = requests.get(redirect_url)

        # 检查响应状态码
        if response.status_code == 200:
            # 获取 Content-Type
            content_type = response.headers.get('Content-Type')
            return content_type
        else:
            logger.error(f"Failed to retrieve URL. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"An error occurred for get content type: {e}")
        return None


async def download_file(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/126.0.0.0 Safari/537.36',
    }
    # 补充的根据Content-Type确定文件后缀，其余可以按/切分获取，如Content-Type: audio/wav
    _extra_type = {
        "application/octet-stream": ".mp4",
        "audio/mpeg": ".mp3",
        "audio/aac": ".aac",
        "audio/x-aac": ".aac",
        "audio/mp4": ".m4a"
    }
    suffix = ''

    result = urlparse(url)
    if result.scheme is None or len(result.scheme) == 0:
        return None, suffix, None

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try_count = 0
        max_try_count = 3
        while try_count < max_try_count:
            try_count += 1
            logger.info(f'try download file: the {try_count} time')
            try:
                response = await client.get(url, headers=headers, timeout=3600)
                if response.status_code == 302:
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        # Follow the redirect
                        response = await client.get(redirect_url, headers=headers)
                response.raise_for_status()

                # 如果文件没有后缀名，获取文件的Content-Type来确定后缀名
                content_type = response.headers.get('Content-Type')
                if content_type is None:
                    logger.warning("Content-Type header is missing. Cannot determine file extension.")
                    return None, suffix, content_type
                # 根据Content-Type获取文件扩展名
                extension = mimetypes.guess_extension(content_type)
                if extension and extension != '.bin':
                    suffix = extension
                else:
                    if content_type in _extra_type:
                        suffix = _extra_type[content_type]
                    else:
                        names = content_type.split('/')
                        extension = '.' + content_type if len(names) == 1 else names[1]
                        suffix = extension
                        logger.warning(f"Could not determine file extension from Content-Type: {content_type},"
                                       f" set it as file extension")
                return response.content, suffix, content_type
            except httpx.ConnectError as e:
                logger.error(f'download file: {url} httpx.ConnectError: {e}')
            except Exception as e:
                logger.error(f'download file: {url} error: {e}')


def get_canonical_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    canonical_link = soup.find('link', {'rel': 'canonical'})
    if canonical_link:
        return canonical_link['href']
    return None


def normalize_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    sorted_query = sorted((k, v) for k, v in query_params.items())
    normalized_query = urlencode(sorted_query, doseq=True)
    normalized_url = parsed_url._replace(query=normalized_query).geturl()
    return normalized_url
