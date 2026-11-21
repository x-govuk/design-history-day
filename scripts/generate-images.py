"""Regenerate browser icons and the social card using macOS sips."""

from pathlib import Path
import struct
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1] / "src" / "assets"
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def render(source, output, *options):
    subprocess.run(
        ["sips", "-s", "format", "png", *options, str(source), "--out", str(output)],
        check=True,
    )


def place(artwork, name, x, y, width, height):
    layer = ET.parse(ASSETS / name).getroot()
    for key, value in zip(("x", "y", "width", "height"), (x, y, width, height)):
        layer.set(key, str(value))
    artwork.append(layer)
    return layer


def square_icon(show_labels):
    artwork = ET.Element(f"{{{SVG}}}svg", width="512", height="512", viewBox="0 0 512 512")
    ET.SubElement(artwork, f"{{{SVG}}}rect", width="512", height="512", fill="#ffeb3b")
    brick = place(artwork, "brick.svg", 40, 54, 432, 404)
    if not show_labels:
        for group in list(brick):
            if group.find(f"{{{SVG}}}text") is not None:
                brick.remove(group)
        ET.SubElement(brick, f"{{{SVG}}}path", {
            "d": "M661 737l94 50M613 828l118 63",
            "fill": "none",
            "stroke": "#202a32",
            "stroke-width": "18",
            "stroke-linecap": "round",
        })
    return ET.ElementTree(artwork)


def generate():
    social = ET.Element(f"{{{SVG}}}svg", width="1200", height="630")
    ET.SubElement(social, f"{{{SVG}}}rect", width="1200", height="630", fill="#ffeb3b")
    place(social, "title-design.svg", 70, 94, 494, 106)
    place(social, "title-history.svg", 70, 217, 570, 106)
    place(social, "title-day.svg", 70, 340, 253, 102)
    place(social, "title-year.svg", 338, 335, 320, 109)
    place(social, "brick.svg", 680, 100, 450, 421)
    date = ET.SubElement(social, f"{{{SVG}}}text", {
        "x": "70", "y": "521", "fill": "#202a32", "font-family": "Helvetica, Arial, sans-serif",
        "font-size": "36", "font-weight": "bold",
    })
    date.text = "Friday 18 December 2026"

    with TemporaryDirectory() as temporary:
        scratch = Path(temporary)
        social_svg = scratch / "social.svg"
        ET.ElementTree(social).write(social_svg, encoding="utf-8")
        render(social_svg, ASSETS / "social-card.png")

        square_icon(show_labels=False).write(ASSETS / "favicon.svg", encoding="utf-8")
        touch_svg = scratch / "touch.svg"
        square_icon(show_labels=True).write(touch_svg, encoding="utf-8")
        for size, name in ((180, "apple-touch-icon"), (192, "icon-192"), (512, "icon-512")):
            render(touch_svg, ASSETS / f"{name}.png", "-z", str(size), str(size))

        frames = []
        for size in (16, 32, 48):
            frame = scratch / f"{size}.png"
            render(ASSETS / "favicon.svg", frame, "-z", str(size), str(size))
            frames.append((size, frame.read_bytes()))

        offset = 6 + 16 * len(frames)
        with (ASSETS / "favicon.ico").open("wb") as icon:
            icon.write(struct.pack("<HHH", 0, 1, len(frames)))
            for size, frame in frames:
                icon.write(struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(frame), offset))
                offset += len(frame)
            for _, frame in frames:
                icon.write(frame)


if __name__ == "__main__":
    generate()
