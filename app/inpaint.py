import numpy as np
import cv2 as cv
from skimage.restoration import inpaint
import imghdr
from typing import Optional
from numpy import ndarray


def inpaint_algorithms(
        img_path: str,
        mask_path: Optional[str],
        img_mask: Optional[ndarray],
        flag: Optional[int] = cv.INPAINT_NS
) -> tuple:
    try:
        img_to_inpaint, mask = read_image_and_mask(img_path, mask_path, img_mask)
        validate_mask_and_image_same_shape(img_to_inpaint, mask)

        if flag in [0, 1]:
            img_inpainted = cv.inpaint(img_to_inpaint, mask, inpaintRadius=3, flags=flag)
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
    except Exception as error:
        return [], error
    return img_inpainted, None


def read_image_and_mask(img_path: str, mask_path: Optional[str], img_mask: Optional[ndarray]) -> tuple:
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
    return img_to_inpaint, mask


def file_has_graphic_extension(filename: str) -> bool:
    if imghdr.what(filename) in ["jpg", "jpeg", "png", "gif", "bmp"]:
        return True
    return False


def validate_mask_and_image_same_shape(img: ndarray, mask: ndarray) -> None:
    if img.shape[0] == mask.shape[0] and img.shape[1] == mask.shape[1]:
        return
    raise AssertionError(f"image and mask are different shapes {img.shape[0], img.shape[1]} != {mask.shape}")
