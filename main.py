import cv2
import numpy as np
from time import sleep
import webbrowser

with open('data.txt', 'r') as file:
    data = []
    for lines in file:
        data.append(lines.rstrip('\n'))
    camera_var = data[0]
    if camera_var.isnumeric():
        camera_var = int(camera_var)
    data[1] = data[1].split(",")
    num_list = []
    for d in data[1]:
        num_list.append(int(d))
    cursor_color = tuple(num_list)

cap = cv2.VideoCapture(camera_var)
fw, fh = 1080, 720
w, h = 640, 480

doonce = 0
pointsList = []
prevX, prevY = 0, 0
old_bg = (0, 0, 0)
canvas = np.zeros((fw, fh, 3), np.uint8)
canvas_copy = np.zeros((fw, fh, 3), np.uint8)
canvas[:] = (0, 0, 0)
currX, currY = 0, 0
control_panel = np.zeros((100, 600, 3), np.uint8)
# Tuple to store undo redo x,y and t
x_y_t = []
global undo_redo_index
undo_redo_index = 0
bucket_selected = False
print("Print ESC Key To Close")
# Disable Tool
disable_tools = False
counter = 0
info_var = -1

# Status Variables
tool_ed, tool_sel, tool_color, bgr_color, tool_size, display_ed, undo_option = "No", "Brush", "(0,0,255)", "(0,0,0)", "1", "Disable", "Not Available"


def getPoints(event, x, y, flags, param):
    global pointsList, doonce
    if event == cv2.EVENT_LBUTTONDOWN:
        if x >= 414 and x <= 637 and y >= 345 and y <= 390:

            if (len(pointsList) != 0):
                pointsList.pop()
        pointsList.append([x, y])
        if (len(pointsList) > 3):
            print("Warp Points : ", pointsList)
            print("--------------------------------------------------------")
            print("Keyboard Shortcuts : Brush-b, Eraser-e, Bucket Fill-f")
            print("Undo-z, Disable/Enable Tools-k, Close-ESC, Info-i")
            print("--------------------------------------------------------")
            create_Trackbars()
            doonce = 1


def empty(a):
    pass


def create_Trackbars():
    cv2.namedWindow("Control Panel")
    cv2.resizeWindow("Control Panel", 600, 640)
    cv2.createTrackbar("Main Feed", "Control Panel", 0, 1, empty)
    cv2.createTrackbar("Pen Red", "Control Panel", 255, 255, empty)
    cv2.createTrackbar("Pen Green", "Control Panel", 0, 255, empty)
    cv2.createTrackbar("Pen Blue", "Control Panel", 0, 255, empty)
    cv2.createTrackbar("Pen/E Size", "Control Panel", 1, 50, empty)
    cv2.createTrackbar("Bg Red", "Control Panel", 0, 255, empty)
    cv2.createTrackbar("Bg Green", "Control Panel", 0, 255, empty)
    cv2.createTrackbar("Bg Blue", "Control Panel", 0, 255, empty)
    cv2.createTrackbar("B / E / F", "Control Panel", 0, 2, empty)


def GetStatus():
    global tool_ed, tool_sel, tool_color, bgr_color, tool_size, display_ed, undo_option
    print("--------------------------------------------------------")
    print("Keyboard Shortcuts : Brush-b, Eraser-e, Bucket Fill-f")
    print("Undo-z, Disable/Enable Tools-k, Close-ESC, Info-i")
    print("--------------------------------------------------------")
    print("Tools Disabled : " + tool_ed)
    print("Tool Selected : " + tool_sel)
    print("Tool Color : " + tool_color)
    print("Background Color : " + bgr_color)
    print("Tool Size : " + tool_size)
    print("Main Feed Enabled/Disable : " + display_ed)
    print("Undo Option : " + undo_option)


def warpImage(frame):
    frame = cv2.resize(frame, (fw, fh))
    pts1 = np.float32([pointsList[3], pointsList[2], pointsList[1], pointsList[0]])
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    output = cv2.warpPerspective(frame, matrix, (w, h))
    return output


if doonce == 0:
    global imgr
    ret, img = cap.read()
    imgr = cv2.resize(img, (fh, fw))
    cv2.putText(imgr, "Point 1", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(imgr, "Point 2", (954, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(imgr, "Point 3", (5, 705), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(imgr, "Point 4", (954, 705), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(imgr, "Click at the points in sequence", (180, 330), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)
    cv2.putText(imgr, "CLICK HERE !", (420, 377), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.rectangle(imgr, (414, 345), (637, 390), (0, 0, 255), 3)
    cv2.imshow("Frame", imgr)
    cv2.setMouseCallback('Frame', getPoints)

while True:
    if doonce == 1:
        cv2.destroyWindow("Frame")
        disp_mainfeed = cv2.getTrackbarPos("Main Feed", "Control Panel")
        red_value = cv2.getTrackbarPos("Pen Red", "Control Panel")
        green_value = cv2.getTrackbarPos("Pen Green", "Control Panel")
        blue_value = cv2.getTrackbarPos("Pen Blue", "Control Panel")
        pen_color = (blue_value, green_value, red_value)
        pen_thickness = cv2.getTrackbarPos("Pen/E Size", "Control Panel")
        bg_red = cv2.getTrackbarPos("Bg Red", "Control Panel")
        bg_green = cv2.getTrackbarPos("Bg Green", "Control Panel")
        bg_blue = cv2.getTrackbarPos("Bg Blue", "Control Panel")
        tool_select = cv2.getTrackbarPos("B / E / F", "Control Panel")
        if old_bg != (bg_blue, bg_green, bg_red):
            canvas[:] = (bg_blue, bg_green, bg_red)
            old_bg = (bg_blue, bg_green, bg_red)
        if pen_thickness < 1:
            pen_thickness = 1
        ret, frame = cap.read()
        output = warpImage(frame)
        output = cv2.resize(output, (fw, fh))
        input_image = output.copy()
        low_b = np.uint8([255, 255, 255])
        high_b = np.uint8([255, 255, 255])
        mask = cv2.inRange(output, high_b, low_b)
        contours, heirarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        tool_color = str(pen_color)
        bgr_color = str((bg_blue, bg_green, bg_red))
        tool_size = str(pen_thickness)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M["m00"] != 0:
                currX = int(M['m10'] / M['m00'])
                currY = int(M['m01'] / M['m00'])
                if prevX == 0 and prevY == 0:
                    prevX = currX
                    prevY = currY
                if tool_select == 0 and disable_tools == 0:
                    undo_option = "Available"
                    cv2.line(canvas, (prevX, prevY), (currX, currY), pen_color, pen_thickness)
                    all_values = (currX, currY), (prevX, prevY), pen_thickness, (bg_blue, bg_green, bg_red)
                    x_y_t.append(all_values)
                    undo_redo_index = len(x_y_t) - 1
                    if len(x_y_t) > 250:
                        x_y_t.pop(0)
                        undo_redo_index = len(x_y_t) - 1
                if tool_select == 1 and disable_tools == 0:
                    undo_option = "Not Available"
                    cv2.line(canvas, (prevX, prevY), (currX, currY), (bg_blue, bg_green, bg_red), pen_thickness)
                if tool_select == 2 and disable_tools == 0:
                    undo_option = "Not Available"
                    mask_fill = np.zeros([fh + 2, fw + 2], np.uint8)
                    cv2.floodFill(canvas, mask_fill, (currX, currY), pen_color, (100, 100, 100), (50, 50, 50),
                                  cv2.FLOODFILL_FIXED_RANGE)
                if disable_tools == -1:
                    undo_option = "Not Available"
                    if counter == 0:
                        canvas_copy = canvas.copy()
                        canvas_copy2 = canvas.copy()
                        counter = 1
                    if counter == 1:
                        canvas_copy3 = canvas_copy2
                        cv2.circle(canvas_copy3, (currX, currY), 3, cursor_color, cv2.FILLED)
                        canvas = canvas_copy3
                        cv2.imshow("XORDINARY TOUCH 2.0", canvas)
                        sleep(0.01)
                        canvas = canvas_copy2
                if disable_tools == 0:
                    canvas = canvas_copy
                    counter = 0
                prevX = currX
                prevY = currY
                # print("Detected")
        else:
            prevX = 0
            prevY = 0
            canvas = canvas_copy
            counter = 0
            # print("Not Detected")
        if disp_mainfeed == 1:
            display_ed = "Enabled"
            cv2.imshow("Main Feed", input_image)
        else:
            display_ed = "Disabled"
            cv2.destroyWindow("Main Feed")
        if info_var == 0:
            GetStatus()
        cv2.imshow("XORDINARY TOUCH 2.0", canvas)
        if disable_tools == 0:
            control_panel[0:39] = pen_color
            control_panel[59:100] = (bg_blue, bg_green, bg_red)
        elif disable_tools == -1:
            control_panel[0:39] = cursor_color
            control_panel[59:100] = cursor_color
        cv2.putText(control_panel, "Brush Color -", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (bg_blue, bg_green, bg_red),
                    2)
        cv2.putText(control_panel, "BGR Color -", (5, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, pen_color, 2)
        cv2.imshow("Control Panel", control_panel)

    key = cv2.waitKey(1) & 0xff
    if key == ord('z') and disable_tools == 0:
        if undo_redo_index > 0 and x_y_t[undo_redo_index][3] == (bg_blue, bg_green, bg_red):
            cv2.line(canvas, x_y_t[undo_redo_index][0], x_y_t[undo_redo_index][1], x_y_t[undo_redo_index][3],
                     x_y_t[undo_redo_index][2])
            undo_redo_index -= 1
        else:
            undo_redo_index = 0
            x_y_t.clear()
            all_values = 0
    if key == ord('b'):
        cv2.setTrackbarPos("B / E / F", "Control Panel", 0)
        tool_sel = "Brush"
        GetStatus()
    if key == ord('e'):
        cv2.setTrackbarPos("B / E / F", "Control Panel", 1)
        tool_sel = "Eraser"
        GetStatus()
    if key == ord('f'):
        cv2.setTrackbarPos("B / E / F", "Control Panel", 2)
        tool_sel = "Bucket Fill"
        GetStatus()
    if key == ord('k'):
        disable_tools = ~ disable_tools
        if disable_tools == 0:
            tool_ed = "No"
        if disable_tools == -1:
            tool_ed = "Yes"
            tool_sel = "Not Available"
            undo_option = "Not Available"
        GetStatus()
    if key == ord('i'):
        info_var = ~info_var
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()