import cv2
import numpy as np

def detect_balls(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_ranges = {
        'white': ([10, 10, 230], [40, 50, 255]),
        'orange': ([5, 130, 100], [6, 255, 255]),
        'green': ([85, 0, 60], [100, 255, 120]),
        'yellow': ([20, 100, 100], [40, 255, 255])
    }

    detected_balls = []
    
    # Process each color
    for color_name, (lower_color, upper_color) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower_color), np.array(upper_color))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500: 
                x, y, w, h = cv2.boundingRect(contour)
                
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    detected_balls.append((color_name, (cx, cy)))
                        
                    # Draw a circle around the ball
                    cv2.circle(image, (cx, cy), 70, (0, 0, 255), 5)  # Green circle
    
    return image, detected_balls

def main():
    output = [['Time', 'Quardent', 'Ball Color', 'Type']]

    ball_state = {
        "quardent": {
            'white': None,
            'orange': None,
            'green': None,
            'yellow': None
        },
        "time_stamp": {
            'white': None,
            'orange': None,
            'green': None,
            'yellow': None
        },
        "entry": {
            'white': False,
            'orange': False,
            'green': False,
            'yellow': False
        }
    }

    # How to find (check in "Ball Tracking.ipynb")
    quardent = {
        1: [1247, 537, 495, 477],
        2: [781, 537, 437, 479],
        3: [791, 15, 464, 493],
        4: [1251, 11, 494, 498]
    }

    current_frame = 30

    video_path = 'AI Assignment video.mp4'
    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while current_frame < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        r, frame = cap.read()

        # To detect balls
        image, ball_color_cord = detect_balls(frame)

        for color, value in ball_color_cord:
            x = value[0]
            y = value[1]

            for i in quardent:
                X, Y, W, H = quardent.get(i)
                
                if (x > X and X + W > x and y > Y and Y + H > y):  # if ball inside quardent range
                    if ball_state['quardent'][color] is None:
                        # Check that ball remain in same quardent for next frame of time if yes then set quardent value and time
                        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame + 30)
                        r, frame = cap.read()
                        image, ball_color_cord = detect_balls(frame)

                        for item in ball_color_cord:
                            if item[0] == color:
                                x = item[1][0]
                                y = item[1][1]
                                for j in quardent:
                                    X, Y, W, H = quardent.get(j)
                                    if (x > X and X + W > x and y > Y and Y + H > y):
                                        if i == j:                 
                                            ball_state['quardent'][color] = i
                                            ball_state['time_stamp'][color] = current_frame / fps
                                        
                    elif ball_state['quardent'][color] == i:  # ball remain in same quardent mean entry type so update output file
                        if ball_state['entry'][color] is False:
                            output.append([ball_state['time_stamp'][color], i, color, "Entry"])
                            ball_state['entry'][color] = True
                    
                    else:  # ball in different quardent then before mean exit type for confirm check entry field True mean entry already done
                        if ball_state['entry'][color] is True:
                            ball_state['quardent'][color] = None
                            ball_state['time_stamp'][color] = None
                            ball_state['entry'][color] = False
                            output.append([current_frame / fps, i, color, "Exit"])
     
        # Ball with entry true but not detect in frame mean very fast exit of ball
        colors_to_check = ['white', 'orange', 'green', 'yellow']

        for color in colors_to_check:
            found = False
            for item in ball_color_cord:
                if item[0] == color:
                    found = True
                    break
            if not found:
                if (ball_state['quardent'][color] is not None and ball_state['entry'][color] is True):
                    output.append([current_frame / fps, ball_state['quardent'][color], color, "Exit"])
                    ball_state['quardent'][color] = None
                    ball_state['time_stamp'][color] = None
                    ball_state['entry'][color] = False
                
        current_frame += 30  # Update current frame 30 because fps = 30 hence check for each second
    
    print("Processing Complete ----- Check the Output")

    output.append([])
    output.append([])
    output.append([])
    output.append(["The last output values vary because in the video persons hand cover the ball so algo thinks ball is exit. And when hand uncovered the ball it again enter the ball"])

    with open(r'output.txt', 'w') as fp:
        for item in output:
            fp.write("%s\n" % item)
        print('Done')

if __name__ == "__main__":
    main()
