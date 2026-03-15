import cv2
import cv2 as cv
import numpy as np

class Record:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.flag = False
        self.video = cv.VideoWriter("meet_your_vocaloid_waifu.mp4", cv.VideoWriter_fourcc(*"mp4v"), 15, (int(w), int(h)))
    def chang_flag(self):
        if self.flag:
            self.flag = False
        else:
            self.flag = True

    def rec(self, img, time):
        gap = 30
        if self.flag:
            self.video.write(img)
            if time % gap > gap // 2:
                cv.circle(img, (50, 50), 15, (0, 0, 255), -1)


class Button:
    def __init__(self, pos, color, text, callback):
        self.boarder_size = 7
        self.size = (50, 300)
        self.pt1 = pos
        self.pt2 = (pos[0] + self.size[1], pos[1] + self.size[0])
        self.color = color
        self.text = text
        self.callback = callback

        self.on_flag = False

    def set_image(self, img):
        self.img = img

    def draw_button(self, img):
        inner_color = (int(self.color[0] * 0.8), int(self.color[1] * 0.8), int(self.color[2] * 0.8))
        x1, y1 = self.pt1
        x2, y2 = self.pt2
        zoom = 3
        font_size = 2.0
        if self.on_flag:
            x1, y1, x2, y2 = x1 - zoom, y1 - zoom, x2 + zoom, y2 + zoom
            font_size = 2.2

        boarder = self.boarder_size
        text_offset = [(x1 + x2) // 2, (y1 + y2) // 2]
        text_size, base =  cv.getTextSize(self.text, cv.FONT_HERSHEY_PLAIN, font_size, 1)
        text_offset[0] -= text_size[0] // 2
        text_offset[1] -= text_size[1] //2 - int(base * 1.9)


        cv.rectangle(img, (x1, y1), (x2, y2), inner_color, -1)
        cv.rectangle(img, (x1 + boarder, y1 + boarder), (x2 - boarder, y2 - boarder), self.color, -1)
        cv.putText(img, self.text, text_offset, cv.FONT_HERSHEY_PLAIN, font_size, (250, 250, 250))

    def is_on_it(self, mouse):
        x, y = mouse
        if self.pt1[0] <= x <= self.pt2[0]:
            if self.pt1[1] <= y <= self.pt2[1]:
                return True
        return False

    def on_click(self):
        self.callback(self.text, self)
        return self.text

def initial_mouse_handler(event, x, y, flags, btns):
    if event == cv.EVENT_MOUSEMOVE:
        for btn in btns:
            if btn.is_on_it((x, y)):
                btn.on_flag = True
            else:
                btn.on_flag = False

    if event == cv.EVENT_LBUTTONUP:
        for btn in btns:
            if btn.on_flag:
                print(btn.on_click())

def show_initial_UI(canvas, window_name):
    teto_button = Button((80, 180), (0, 0, 225), "Kasane Teto", show_waifu)
    teto_img = cv.imread("./data/teto_heart.png", cv.IMREAD_UNCHANGED)
    teto_img = teto_img[:, ::-1, :]
    teto_img = cv.resize(teto_img, None, fx = 1.5, fy = 1.5)
    teto_button.set_image(teto_img)

    miku_button = Button((80, 280), (255, 0, 0), "Hatsune Miku", show_waifu)
    miku_img = cv.imread("./data/miku_heart.png", cv.IMREAD_UNCHANGED)
    miku_img = miku_img[:, ::-1, :]
    miku_img = cv.resize(miku_img, None, fx = 1.19, fy = 1.19)
    miku_button.set_image(miku_img)

    btns = [teto_button, miku_button]
    cv.setMouseCallback(window_name, initial_mouse_handler, btns)
    cv.putText(canvas, "Meet Your Vocaloid Waifu", (30, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
    cv.putText(canvas, "press space bar to record", (120, 130), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

    while True:
        copy = canvas.copy()
        for button in btns:
            button.draw_button(copy)
        cv.imshow(win_name, copy)
        key = cv.waitKey(1)
        if key == 27:
            break
    cv.destroyAllWindows()

def calc_waifu(canvas, img, time):
    h, w, *_ = canvas.shape
    ih, iw, ic = img.shape
    ox, oy = min((time * 150) - 3000, 700), 0
    cx1, cy1 = max(ox, 0), max(oy, 0)
    cx2, cy2 = min(ox + iw, w), min(oy + ih, h)

    if cx1 >= cx2 or cy1 >= cy2:
        return canvas

    ix1, iy1 = cx1 - ox, cy1 - oy
    ix2, iy2 = ix1 + cx2 - cx1, iy1 + cy2 - cy1
    src = img[iy1:iy2, ix1:ix2]
    bgr = src[:, :, :3]
    alpha = src[:, :, 3] / 255.0
    dst = canvas[cy1:cy2, cx1:cx2]
    for c in range(3):
        dst[:, :, c] = (
            alpha * bgr[:, :, c] +
            (1 - alpha) * dst[:, :, c]
        )

    return canvas

def show_waifu(window_name, button):
    waifu_img = button.img
    cam = cv.VideoCapture(0)
    cam_w = cam.get(cv.CAP_PROP_FRAME_WIDTH)
    cam_h = cam.get(cv.CAP_PROP_FRAME_HEIGHT)
    record = Record(cam_h, cam_w)

    time = 0
    if cam.isOpened():
        while True:
            time += 1
            vaild, img = cam.read()
            if not vaild:
                break

            img = img[:, ::-1, :].copy()
            calc_waifu(img, waifu_img, time)
            record.rec(img, time)
            cv.imshow(window_name, img)
            key = cv.waitKey(1)
            if key == 32:
                record.chang_flag()
            if key == 27:
                record.video.release()
                break
    cv.destroyAllWindows()

if __name__ == "__main__":
    win_name = "Temp"

    canvas = np.full((500, 500, 3) , 255, dtype = np.uint8)
    cv.namedWindow(win_name)
    show_initial_UI(canvas, win_name)

