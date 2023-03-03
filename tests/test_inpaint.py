from numpy import ndarray
from app.inpaint import validate_mask_and_image_same_shape, file_has_graphic_extension
import pytest


def test_inpaint_shape_validation():
    array5x5 = ndarray((5,5))
    array3x5 = ndarray((3,5))
    array3x3 = ndarray((3,3))
    with pytest.raises(AssertionError):
        validate_mask_and_image_same_shape(array3x5, array3x3)
        validate_mask_and_image_same_shape(array3x5, array3x3)
    assert validate_mask_and_image_same_shape(array5x5, array5x5) is None
    assert validate_mask_and_image_same_shape(array3x5, array3x5) is None
    assert validate_mask_and_image_same_shape(array3x3, array3x3) is None


