import numpy as np
import cv2 as cv
from skimage.restoration import inpaint


def inpaint_algorithms(img_path, mask_path, img_mask, r=3, flag=cv.INPAINT_NS):
    try:
        img_to_inpaint = cv.imread(f"{img_path}")
        if mask_path:
            mask = cv.imread(f"{mask_path}", cv.IMREAD_GRAYSCALE)
        elif img_mask is not None:
            mask = cv.resize(img_mask, dsize=(img_to_inpaint.shape[1], img_to_inpaint.shape[0]),
                             interpolation=cv.INTER_AREA)
            _, mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)
            kernel = np.ones((4, 4), np.uint8)
            mask = cv.dilate(mask, kernel, iterations=3)
        else:
            raise NotImplementedError("Couldn't handle lack of mask")

        if flag in [0, 1]:
            img_inpainted = cv.inpaint(img_to_inpaint, mask, inpaintRadius=r, flags=flag)
            img_inpainted = cv.cvtColor(img_inpainted, cv.COLOR_BGR2RGB)
        elif flag == 2:
            img_inpainted = np.zeros_like(img_to_inpaint)
            _, inverse_mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY_INV)
            cv.xphoto.inpaint(src=img_to_inpaint, mask=inverse_mask, dst=img_inpainted, algorithmType=2)
            img_inpainted = cv.cvtColor(img_inpainted, cv.COLOR_BGR2RGB)
        elif flag == 3:
            img_inpainted = np.zeros_like(img_to_inpaint)
            _, inverse_mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY_INV)
            cv.xphoto.inpaint(src=img_to_inpaint, mask=inverse_mask, dst=img_inpainted, algorithmType=1)
            img_inpainted = cv.cvtColor(img_inpainted, cv.COLOR_BGR2RGB)
        elif flag == 4:
            img_to_inpaint = cv.cvtColor(img_to_inpaint, cv.COLOR_BGR2RGB)
            img_lab = cv.cvtColor(src=img_to_inpaint, code=cv.COLOR_RGB2Lab)
            dst_img = np.zeros_like(img_to_inpaint)
            _, inverse_mask = cv.threshold(mask, 127, 255, cv.THRESH_BINARY_INV)
            cv.xphoto.inpaint(src=img_lab, mask=inverse_mask, dst=dst_img, algorithmType=cv.xphoto.INPAINT_SHIFTMAP)
            img_inpainted = cv.cvtColor(src=dst_img, code=cv.COLOR_Lab2RGB)
        else:
            kernel = np.ones((2, 2), np.uint8)
            mask = cv.dilate(mask, kernel, iterations=1)
            img_to_inpaint = cv.cvtColor(img_to_inpaint, cv.COLOR_BGR2RGB)
            img_inpainted = inpaint.inpaint_biharmonic(img_to_inpaint, mask, channel_axis=-1)
            img_inpainted = (img_inpainted * 255).astype('uint8')
    except Exception as e:
        return [], e
    return img_inpainted, None
