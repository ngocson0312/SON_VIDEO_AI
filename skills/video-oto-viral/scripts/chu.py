# -*- coding: utf-8 -*-
"""Chữ của mẫu: TÊN HÃNG trắng phông đứng hẹp giãn chữ rất rộng, gõ từng ký tự theo móc đơn (22,16 → 23,7 s);
DÒNG XE đỏ nghiêng đậm hiện giữa cú glitch (24,13 s). Vẽ bằng PIL ra lớp RGBA, dán bằng numpy."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import chung as C


def _dan(img, rgba, x, y, alpha=1.0):
    H, W = img.shape[:2]
    h, w = rgba.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return img
    s = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = s[..., 3:4] / 255.0 * alpha
    roi = img[y0:y1, x0:x1].astype(np.float32)
    img[y0:y1, x0:x1] = np.clip(roi * (1 - a) + s[..., :3] * a, 0, 255).astype(np.uint8)
    return img


class TieuDe:
    """Tên hãng: từng ký tự đặt sẵn đúng chỗ cuối cùng (chữ đầu hiện ở bên trái, không canh giữa lại)."""

    def __init__(self, text, W, H, kho):
        cfg = C.CHU['tieu_de']
        self.text = text.upper()
        self.W, self.H = W, H
        fp = C.font(cfg['font'])
        rong = cfg['rong'][kho] * W
        cao_max = cfg['cao_max'][kho] * H
        size = int(cao_max * 1.35)
        for _ in range(40):
            f = ImageFont.truetype(fp, size)
            ws = [f.getbbox(ch)[2] - f.getbbox(ch)[0] if ch != ' ' else size * 0.3 for ch in self.text]
            gian = cfg['gian'] * size * 0.62
            tong = sum(ws) + gian * (len(self.text) - 1)
            cap = f.getbbox('H')[3] - f.getbbox('H')[1]
            if tong <= rong and cap <= cao_max:
                break
            size = int(size * 0.95)
        self.f = f
        self.cap = cap
        x = (W - tong) / 2
        self.cx = []
        for ch, w in zip(self.text, ws):
            self.cx.append(x); x += w + gian
        bb = f.getbbox('H')
        self.y = int(cfg['y'][kho] * H - cap / 2 - bb[1])
        # lớp chữ từng ký tự (đã kèm bóng)
        pad = int(size * 0.3)
        self.lop = []
        for ch, x in zip(self.text, self.cx):
            if ch == ' ':
                self.lop.append(None); continue
            b = f.getbbox(ch)
            w, h = b[2] + 2 * pad, b[3] + 2 * pad
            m = Image.new('L', (w, h), 0)
            ImageDraw.Draw(m).text((pad, pad), ch, font=f, fill=255)
            m = np.array(m).astype(np.float32)
            sh = cv2.GaussianBlur(m, (0, 0), size * 0.05)
            sh = np.roll(np.roll(sh, int(size * 0.03), 0), int(size * 0.02), 1) * cfg['bong']
            rgba = np.zeros((h, w, 4), np.float32)
            col = np.array(cfg['mau'], np.float32)[::-1]
            a = m / 255.0; s_ = sh / 255.0
            tot = a + s_ * (1 - a)
            rgba[..., :3] = (col * a[..., None]) / np.maximum(tot, 1e-4)[..., None]
            rgba[..., 3] = tot * 255
            self.lop.append((np.clip(rgba, 0, 255).astype(np.uint8), int(x) - pad, self.y - pad))

    def ve(self, img, n, alpha=1.0):
        for k in range(min(n, len(self.lop))):
            if self.lop[k] is None:
                continue
            rgba, x, y = self.lop[k]
            _dan(img, rgba, x, y, alpha)
        return img

    def hop(self):
        """Hộp bao (tỉ lệ) để HUD né."""
        return (self.cx[0] / self.W - 0.02, (self.y - self.cap * 0.3) / self.H, (self.cx[-1] + self.cap) / self.W + 0.02,
                (self.y + self.cap * 1.5) / self.H)


class DongXe:
    """Dòng xe đỏ nghiêng đậm, gradient đỏ sáng → đỏ thẫm, bóng mềm."""

    def __init__(self, text, W, H, kho):
        cfg = C.CHU['dong_xe']
        self.text = text.upper()
        fp = C.font(cfg['font'])
        cao = cfg['cao'][kho] * H
        size = int(cao * 1.4)
        for _ in range(40):
            f = ImageFont.truetype(fp, size)
            cap = f.getbbox('H')[3] - f.getbbox('H')[1]
            bb = f.getbbox(self.text)
            if cap <= cao and (bb[2] - bb[0]) <= 0.8 * W:
                break
            size = int(size * 0.95)
        pad = int(size * 0.3)
        bb = f.getbbox(self.text)
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] + 2 * pad
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).text((pad - bb[0], pad), self.text, font=f, fill=255)
        m = np.array(m).astype(np.float32) / 255
        ys = np.nonzero(m.max(1) > 0.1)[0]
        g = np.zeros(h, np.float32)
        if len(ys):
            g = np.clip((np.arange(h) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)
        top = np.array(cfg['mau_tren'][::-1], np.float32); bot = np.array(cfg['mau_duoi'][::-1], np.float32)
        col = top[None, None, :] * (1 - g)[:, None, None] + bot[None, None, :] * g[:, None, None]
        sh = cv2.GaussianBlur(m, (0, 0), size * 0.05)
        sh = np.roll(np.roll(sh, int(size * 0.035), 0), int(size * 0.025), 1) * cfg['bong']
        tot = m + sh * (1 - m)
        rgba = np.zeros((h, w, 4), np.float32)
        rgba[..., :3] = col * (m / np.maximum(tot, 1e-4))[..., None]
        rgba[..., 3] = tot * 255
        self.rgba = np.clip(rgba, 0, 255).astype(np.uint8)
        cap = f.getbbox('H')[3] - f.getbbox('H')[1]
        self.x = int(cfg['x'][kho] * W - w / 2)
        self.y = int(cfg['y'][kho] * H - pad - (bb[1] + cap / 2) + 0)
        self.y = int(cfg['y'][kho] * H - (pad + f.getbbox('H')[1] + cap / 2))

    def ve(self, img, alpha=1.0, phong=1.0):
        if phong != 1.0:
            h, w = self.rgba.shape[:2]
            r = cv2.resize(self.rgba, (int(w * phong), int(h * phong)), interpolation=cv2.INTER_LINEAR)
            return _dan(img, r, self.x - (r.shape[1] - w) // 2, self.y - (r.shape[0] - h) // 2, alpha)
        return _dan(img, self.rgba, self.x, self.y, alpha)
