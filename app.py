import numpy as np
import cv2 as cv
from skimage.restoration import inpaint

def inpaint_algorithms(img_path, mask_path, r=3, flag=cv.INPAINT_NS):
    img_to_inpaint = load_image_from_path(img_path)
    mask = load_image_from_path(mask_path)

    if flag in [0, 1]:
        img_inpainted = cv.inpaint(img_to_inpaint, mask, inpaintRadius=r, flags=flags)
    elif flag == 2:
        img_inpainted = np.zeros_like(img_to_inpaint)
        _, inverse_mask = cv.threshold(mask,127,255,cv.THRESH_BINARY_INV)
        cv.xphoto.inpaint(src=img_to_inpaint, mask=inverse_mask, dst=img_inpainted, algorithmType=2)
    elif flag == 3:
        img_inpainted = np.zeros_like(img_to_inpaint)
        _, inverse_mask = cv.threshold(mask,127,255,cv.THRESH_BINARY_INV)
        cv.xphoto.inpaint(src=img_to_inpaint, mask=inverse_mask, dst=img_inpainted, algorithmType=1)
    elif flag == 4:
        img_to_inpaint = cv.cvtColor(img_to_inpaint, cv.COLOR_BGR2RGB)
        img_lab = cv.cvtColor(src=img_to_inpaint, code=cv.COLOR_RGB2Lab)
        dst_img = np.zeros_like(img_to_inpaint)
        _, inverse_mask = cv.threshold(mask,127,255,cv.THRESH_BINARY_INV)
        cv.xphoto.inpaint(src=img_lab, mask=inverse_mask,dst=dst_img, algorithmType=cv.xphoto.INPAINT_SHIFTMAP)
        after = cv.cvtColor(src=dst_img, code=cv.COLOR_Lab2RGB)
        img_inpainted = cv.cvtColor(after, cv.COLOR_BGR2RGB)
    elif flag == 5:
        before = cv.cvtColor(img_to_inpaint, cv.COLOR_BGR2RGB)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv.dilate(mask, kernel, iterations=1)
        img_inpainted = inpaint.inpaint_biharmonic(before, mask, channel_axis=-1)
        after = (img_inpainted*255).astype('uint8')
        img_inpainted = cv.cvtColor(after, cv.COLOR_BGR2RGB)
    return img_inpainted

def load_image_from_path(path):
    return cv.imread(f"{path}")
