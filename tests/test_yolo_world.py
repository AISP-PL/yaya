import cv2
from inference.models.yolo_world import YOLOWorld


def test_yolo_world():
    """Test YOLO World model."""
    image = cv2.imread("tests/yolo_world/image.png")

    model = YOLOWorld(model_id="yolo_world/l")
    classes = ["person", "bus", "shop"]
    results = model.infer(image, text=classes, confidence=0.03)
    assert results is not None


if __name__ == "__main__":
    test_yolo_world()
