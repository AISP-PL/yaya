"""
    Detections handling code.
"""

from helpers.boxes import GetContainingBox, tiles_iou


def tiles_detections_merge(
    tiles_detections: list[list[tuple]],
    iou_threshold: float = 0.8,
) -> list[tuple]:
    """
    Merge detections from different tiles
    using boxes tiles_iou metric. Each detections is
    represented as tuple (label, confidence, box).

    """
    # Check : No tiles
    if len(tiles_detections) == 0:
        return []

    # Check : Single tile
    if len(tiles_detections) == 1:
        return tiles_detections[0]

    # Detections : Use first tile as base
    detections = tiles_detections[0]

    # For every tile
    for tile_detections in tiles_detections[1:]:
        # For every tile detection
        for tile_detection in tile_detections:
            # IOU with all detections
            ious = [
                tiles_iou(tile_detection[2], detection[2]) for detection in detections
            ]

            # Check : Empty detections
            if len(ious) == 0:
                detections.append(tile_detection)
                continue

            # Check : No IOU above threshold
            if max(ious) < iou_threshold:
                detections.append(tile_detection)
                continue

            # Otherwise, get index of max IOU
            max_iou_idx = ious.index(max(ious))

            # Merged bbox : Containing box
            containing_box = GetContainingBox(
                tile_detection[2], detections[max_iou_idx][2]
            )
            # Label and confidence : Get
            if tile_detection[1] > detections[max_iou_idx][1]:
                label = tile_detection[0]
                confidence = tile_detection[1]
            else:
                label = detections[max_iou_idx][0]
                confidence = detections[max_iou_idx][1]

            # Replace detection
            detections[max_iou_idx] = (label, confidence, containing_box)

    return detections
