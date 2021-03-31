# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}pdf <page num> <reply to pdf file>`
    Extract nd Send page as a Image.(note-: For Extraction all pages just use .pdf)

• `{i}pdtext <page num> <reply to pdf file>`
    Extract Text From the Pdf.(note-: For Extraction all text just use .pdtext)

• `{i}pdscan <reply to image>`
    It scan, crop nd send img as pdf.

• `{i}pdsave <reply to image/pdf>`
    It scan, crop nd save file to merge u can merge many pages as a single pdf.

• `{i}pdsend `
    Merge nd send the Pdf to collected from .pdsave.
"""

import os
import shutil

import cv2
import imutils
import numpy as np
import PIL
from imutils.perspective import four_point_transform
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from skimage.filters import threshold_local

from . import *

if not os.path.exists("pdf/"):
    os.makedirs("pdf/")


@ultroid_cmd(
    pattern="pdf ?(.*)",
)
async def pdfseimg(event):
    ok = await event.get_reply_message()
    msg = event.pattern_match.group(1)
    if not ok and ok.document and ok.document.mime_type == "application/pdf":
        await eor(event, "`Reply The pdf u Want to Download..`")
        return
    xx = await eor(event, "Processing...")
    if not msg:
        d = os.path.join("pdf/", "hehe.pdf")
        await event.client.download_media(ok, d)
        pdfp = "pdf/hehe.pdf"
        pdfp.replace(".pdf", "")
        pdf = PdfFileReader(pdfp)
        for num in range(pdf.numPages):
            pw = PdfFileWriter()
            pw.addPage(pdf.getPage(num))
            with open(os.path.join("pdf/ult{}.png".format(num + 1)), "wb") as f:
                pw.write(f)
        os.remove(pdfp)
        a = os.listdir("pdf/")
        for z in a:
            lst = [f"pdf/{z}"]
            await event.client.send_file(event.chat_id, lst, album=True)
        shutil.rmtree("pdf")
        os.makedirs("pdf/")
        await xx.delete()
    if msg:
        o = int(msg) - 1
        d = os.path.join("pdf/", "hehe.pdf")
        await event.client.download_media(ok, d)
        pdfp = "pdf/hehe.pdf"
        pdfp.replace(".pdf", "")
        pdf = PdfFileReader(pdfp)
        pw = PdfFileWriter()
        pw.addPage(pdf.getPage(o))
        with open(os.path.join("ult.png"), "wb") as f:
            pw.write(f)
        os.remove(pdfp)
        await event.client.send_file(
            event.chat_id,
            "ult.png",
            reply_to=event.reply_to_msg_id,
        )
        os.remove("ult.png")
        await xx.delete()


@ultroid_cmd(
    pattern="pdtext ?(.*)",
)
async def pdfsetxt(event):
    ok = await event.get_reply_message()
    msg = event.pattern_match.group(1)
    if not ok and ok.document and ok.document.mime_type == "application/pdf":
        await eor(event, "`Reply The pdf u Want to Download..`")
        return
    xx = await eor(event, "`Processing...`")
    if not msg:
        dl = await event.client.download_media(ok)
        pdf = PdfFileReader(dl)
        text = f"{dl.split('.')[0]}.txt"
        with open(text, "w") as f:
            for page_num in range(pdf.numPages):
                pageObj = pdf.getPage(page_num)
                txt = pageObj.extractText()
                f.write("Page {}\n".format(page_num + 1))
                f.write("".center(100, "-"))
                f.write(txt)
        await event.client.send_file(
            event.chat_id,
            text,
            reply_to=event.reply_to_msg_id,
        )
        os.remove(text)
        os.remove(dl)
        await xx.delete()
        return
    if "_" in msg:
        u, d = msg.split("_")
        dl = await event.client.download_media(ok)
        a = PdfFileReader(dl)
        str = ""
        for i in range(int(u) - 1, int(d)):
            str += a.getPage(i).extractText()
        text = f"{dl.split('.')[0]} {msg}.txt"
        with open(text, "w") as f:
            f.write(str)
        await event.client.send_file(
            event.chat_id,
            text,
            reply_to=event.reply_to_msg_id,
        )
        os.remove(text)
        os.remove(dl)
    else:
        u = int(msg) - 1
        dl = await event.client.download_media(ok)
        a = PdfFileReader(dl)
        str = a.getPage(u).extractText()
        text = f"{dl.split('.')[0]} Pg-{msg}.txt"
        with open(text, "w") as f:
            f.write(str)
        await event.client.send_file(
            event.chat_id,
            text,
            reply_to=event.reply_to_msg_id,
        )
        os.remove(text)
        os.remove(dl)
    await xx.delete()


@ultroid_cmd(
    pattern="pdscan ?(.*)",
)
async def imgscan(event):
    ok = await event.get_reply_message()
    if not (ok and (ok.media)):
        await eor(event, "`Reply The pdf u Want to Download..`")
        return
    ultt = await ok.download_media()
    if not ultt.endswith(("png", "jpg", "jpeg", "webp")):
        await eor(event, "`Reply to a Image only...`")
        os.remove(ultt)
        return
    xx = await eor(event, "`Processing...`")
    image = cv2.imread(ultt)
    original_image = image.copy()
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
    edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
    contours, hierarchy = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    polygons = []
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        polygons.append(cv2.approxPolyDP(hull, 0.01 * cv2.arcLength(hull, True), False))
        sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
        cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
        simplified_cnt = sortedPoly[0]
    if len(simplified_cnt) == 4:
        cropped_image = four_point_transform(
            original_image,
            simplified_cnt.reshape(4, 2) * ratio,
        )
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        T = threshold_local(gray_image, 11, offset=10, method="gaussian")
        ok = (gray_image > T).astype("uint8") * 255
    if len(simplified_cnt) != 4:
        ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
    cv2.imwrite("o.png", ok)
    image1 = PIL.Image.open("o.png")
    im1 = image1.convert("RGB")
    scann = f"Scanned {ultt.split('.')[0]}.pdf"
    im1.save(scann)
    await event.client.send_file(event.chat_id, scann, reply_to=event.reply_to_msg_id)
    await xx.delete()
    os.remove(ultt)
    os.remove("o.png")
    os.remove(scann)


@ultroid_cmd(
    pattern="pdsave ?(.*)",
)
async def savepdf(event):
    ok = await event.get_reply_message()
    if not (ok and (ok.media)):
        await eor(
            event,
            "`Reply to Images/pdf which u want to merge as a single pdf..`",
        )
        return
    ultt = await ok.download_media()
    if ultt.endswith(("png", "jpg", "jpeg", "webp")):
        xx = await eor(event, "`Processing...`")
        image = cv2.imread(ultt)
        original_image = image.copy()
        ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
        image_y[:, :] = image_yuv[:, :, 0]
        image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
        edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
        contours, hierarchy = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        polygons = []
        for cnt in contours:
            hull = cv2.convexHull(cnt)
            polygons.append(
                cv2.approxPolyDP(hull, 0.01 * cv2.arcLength(hull, True), False),
            )
            sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
            cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
            simplified_cnt = sortedPoly[0]
        if len(simplified_cnt) == 4:
            cropped_image = four_point_transform(
                original_image,
                simplified_cnt.reshape(4, 2) * ratio,
            )
            gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            T = threshold_local(gray_image, 11, offset=10, method="gaussian")
            ok = (gray_image > T).astype("uint8") * 255
        if len(simplified_cnt) != 4:
            ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
        cv2.imwrite("o.png", ok)
        image1 = PIL.Image.open("o.png")
        im1 = image1.convert("RGB")
        a = dani_ck("pdf/scan.pdf")
        im1.save(a)
        await xx.edit(
            f"Done, Now Reply Another Image/pdf if completed then use {hndlr}pdsend to merge nd send all as pdf",
        )
        os.remove("o.png")
    elif ultt.endswith(".pdf"):
        a = dani_ck("pdf/scan.pdf")
        await ultroid_bot.download_media(ok, a)
        await eor(
            event,
            f"Done, Now Reply Another Image/pdf if completed then use {hndlr}pdsend to merge nd send all as pdf",
        )
    else:
        await eor(event, "`Reply to a Image/pdf only...`")
    os.remove(ultt)


@ultroid_cmd(
    pattern="pdsend ?(.*)",
)
async def sendpdf(event):
    if not os.path.exists("pdf/scan.pdf"):
        await eor(
            event,
            "first select pages by replying .pdsave of which u want to make multi page pdf file",
        )
        return
    msg = event.pattern_match.group(1)
    if msg:
        ok = f"{msg}.pdf"
    else:
        ok = "My PDF File.pdf"
    merger = PdfFileMerger()
    for item in os.listdir("pdf/"):
        if item.endswith("pdf"):
            merger.append(f"pdf/{item}")
    merger.write(ok)
    await event.client.send_file(event.chat_id, ok, reply_to=event.reply_to_msg_id)
    os.remove(ok)
    shutil.rmtree("pdf/")
    os.makedirs("pdf/")


HELP.update({f"{__name__.split('.')[1]}": f"{__doc__.format(i=HNDLR)}"})
