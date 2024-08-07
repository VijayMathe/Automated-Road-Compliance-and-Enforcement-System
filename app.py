# import cv2
# import streamlit as st
# from ultralytics import YOLO
# from sort.sort import *
# import string
# import easyocr
# import numpy as np
# import pandas as pd
# import mysql.connector
# from datetime import datetime, date

# # Initialize the OCR reader
# reader = easyocr.Reader(['en'], gpu=False)

# # Mapping dictionaries for character conversion
# dict_char_to_int = {'O': '0', 'I': '1', 'J': '3', 'A': '4', 'G': '6', 'S': '5'}

# dict_int_to_char = {'0': 'O', '1': 'I', '3': 'J', '4': 'A', '6': 'G', '5': 'S'}

# # Function to connect to MySQL database
# def connect_to_database():
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         passwd="Vijay@2004",  # Change this to your MySQL password
#         database="EDI"  # Change this to your database name
#     )
#     return connection

# def fetch_vehicle_details(state, district, series_char, series_num):
#     connection = connect_to_database()
#     cursor = connection.cursor()

#     query = f"SELECT * FROM VEHICLE_DETAILS WHERE state='{state}' AND district={district} AND series_char='{series_char}' AND series_num='{series_num}'"
#     cursor.execute(query)
#     result = cursor.fetchall()

#     # Convert result to DataFrame
#     df = pd.DataFrame(result, columns=["state", "district", "series_char", "series_num", "owner_name", "owner_mob_no", "ins_valid_from", "ins_valid_to", "puc_valid_from", "puc_valid_to"])

#     connection.close()

#     return df

# # Function to check if a date is expired
# def is_expired(date_string):
#     if date_string:
#         if isinstance(date_string, date):
#             date_string = date_string.strftime("%Y-%m-%d")
#         date_obj = datetime.strptime(date_string, "%Y-%m-%d")
#         return date_obj < datetime.now()
#     return False

# # Function to write CSV results
# def write_csv(results, output_path):
#     with open(output_path, 'w') as f:
#         f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
#                                                 'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
#                                                 'license_number_score'))

#         for frame_nmr in results.keys():
#             for car_id in results[frame_nmr].keys():
#                 if 'car' in results[frame_nmr][car_id].keys() and \
#                         'license_plate' in results[frame_nmr][car_id].keys() and \
#                         'text' in results[frame_nmr][car_id]['license_plate'].keys():
#                     f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
#                                                             car_id,
#                                                             '[{} {} {} {}]'.format(
#                                                                 results[frame_nmr][car_id]['car']['bbox'][0],
#                                                                 results[frame_nmr][car_id]['car']['bbox'][1],
#                                                                 results[frame_nmr][car_id]['car']['bbox'][2],
#                                                                 results[frame_nmr][car_id]['car']['bbox'][3]),
#                                                             '[{} {} {} {}]'.format(
#                                                                 results[frame_nmr][car_id]['license_plate']['bbox'][0],
#                                                                 results[frame_nmr][car_id]['license_plate']['bbox'][1],
#                                                                 results[frame_nmr][car_id]['license_plate']['bbox'][2],
#                                                                 results[frame_nmr][car_id]['license_plate']['bbox'][3]),
#                                                             results[frame_nmr][car_id]['license_plate']['bbox_score'],
#                                                             results[frame_nmr][car_id]['license_plate']['text'],
#                                                             results[frame_nmr][car_id]['license_plate']['text_score'])
#                             )
#         f.close()

# # Function to check if the license plate format complies
# def license_complies_format(text):
#     if len(text) != 10:
#         return False

#     if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
#             (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
#             (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
#             (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
#             (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
#             (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
#             (text[6] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[6] in dict_char_to_int.keys()) and \
#             (text[7] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[7] in dict_char_to_int.keys()) and \
#             (text[8] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[8] in dict_char_to_int.keys()) and \
#             (text[9] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[9] in dict_char_to_int.keys()):
#         return True
#     else:
#         return False

# # Function to format the license plate
# def format_license(text):
#     license_plate_ = ''
#     mapping = {0: dict_int_to_char, 1: dict_int_to_char, 4: dict_int_to_char, 5: dict_int_to_char,
#                2: dict_char_to_int, 3: dict_char_to_int, 6: dict_char_to_int, 7: dict_char_to_int, 8: dict_char_to_int,
#                9: dict_char_to_int}
#     for j in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
#         if text[j] in mapping[j].keys():
#             license_plate_ += mapping[j][text[j]]
#         else:
#             license_plate_ += text[j]
#     return license_plate_

# # Function to read the license plate
# def read_license_plate(license_plate_crop):
#     detections = reader.readtext(license_plate_crop)
#     for detection in detections:
#         bbox, text, score = detection
#         text = ''.join(ch for ch in text if ch.isalnum())  # Remove special characters
#         text = text.upper()  # Convert to uppercase
#         if license_complies_format(text):
#             return format_license(text), score
#     return None, None

# # Function to get the car details
# def get_car(license_plate, vehicle_track_ids):
#     global car_indx
#     x1, y1, x2, y2, score, class_id = license_plate
#     foundIt = False
#     for j in range(len(vehicle_track_ids)):
#         xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]
#         if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
#             car_indx = j
#             foundIt = True
#             break
#     if foundIt:
#         return vehicle_track_ids[car_indx]
#     return -1, -1, -1, -1, -1

# # Function to process the video
# def process_video(uploaded_file):
#     vehicles = [2, 3, 5, 7]
#     # Initialize results dictionary
#     results = {}
#     # Initialize the Sort tracker
#     mot_tracker = Sort()

#     # Temporary file path
#     temp_video_path = "temp/temp_video.mp4"
#     # Save uploaded file to a temporary location
#     with open(temp_video_path, "wb") as f:
#         f.write(uploaded_file.getvalue())

#     # Create a VideoCapture object
#     cap = cv2.VideoCapture(temp_video_path)

#     # Your YOLO and other model initialization code here
#     coco_model = YOLO('models/yolov8n.pt')
#     licence_plate_detector = YOLO('models/LicencePlateModel.pt')
#     mot_tracker = Sort()

#     # Read frames
#     frame_nmr = -1
#     while True:
#         frame_nmr += 1
#         if frame_nmr > 100:
#             break
#         ret, frame = cap.read()
#         if not ret:
#             break  # Exit the loop if reading frame fails

#         # Initialize results for the current frame
#         results[frame_nmr] = {}

#         # Detect vehicles
#         detections = coco_model(frame)[0]
#         detections_ = []
#         for detection in detections.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = detection
#             if int(class_id) in vehicles:
#                 detections_.append([x1, y1, x2, y2, score])

#         # Track vehicles
#         track_ids = mot_tracker.update(np.asarray(detections_))

#         # Detect license plates
#         license_plates = licence_plate_detector(frame)[0]
#         for license_plate in license_plates.boxes.data.tolist():
#             x1, y1, x2, y2, score, class_id = license_plate

#             # Assign license plate to a vehicle
#             xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

#             if car_id != -1:
#                 # Crop license plate
#                 license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

#                 # Process license plate
#                 license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
#                 _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

#                 # Read license plate
#                 license_plate_text, license_plate_score = read_license_plate(license_plate_crop_thresh)

#                 if license_plate_text is not None:
#                     # Scale back bounding box coordinates to original frame size
#                     x1_orig, y1_orig, x2_orig, y2_orig = int(x1 * frame.shape[1] / 128), int(
#                         y1 * frame.shape[0] / 224), int(x2 * frame.shape[1] / 128), int(y2 * frame.shape[0] / 224)
#                     results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
#                                                   'license_plate': {'bbox': [x1_orig, y1_orig, x2_orig, y2_orig],
#                                                                     'text': license_plate_text,
#                                                                     'bbox_score': score,
#                                                                     'text_score': license_plate_score}}

#     # Write results to CSV
#     csv_path = 'temp/test.csv'
#     write_csv(results, csv_path)
#     return csv_path

# # Streamlit UI
# def main():
#     # st.set_page_config(page_title="License Plate Detection App", page_icon=":car:")
#     # page_bg_img = f"""
#     # <style>
#     # [data-testid="stAppViewContainer"] > .main {{
#     # background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
#     # background-size: cover;
#     # background-position: center center;
#     # background-repeat: no-repeat;
#     # background-attachment: local;
#     # }}
#     # [data-testid="stHeader"] {{
#     # background: rgba(0,0,0,0);
#     # }}
#     # </style>
#     # """
#     #
#     # st.markdown(page_bg_img, unsafe_allow_html=True)
#     st.title("License Plate Detection App")
#     uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
#     if uploaded_file is not None:
#         with st.spinner('Processing video...'):
#             results_csv = process_video(uploaded_file)
#         st.success("License plate details extracted successfully!")
#         st.write("Download the results CSV file:")
#         st.download_button(label="Download CSV", data=open(results_csv, 'rb').read(),
#                            file_name="license_plate_results.csv", mime="text/csv")
#         # Display the fetched vehicle details
#         st.write("Vehicle Details:")
#         df = pd.read_csv(results_csv)
#         for car_id, group in df.groupby('car_id'):
#             max_score_row = group.loc[group['license_number_score'].idxmax()]
#             license_plate_number = max_score_row['license_number']
#             st.write(f"Car ID: {car_id}, License Plate Number: {license_plate_number}")
#             # Extract state, district, series_char, and series_num from the license plate number
#             state = license_plate_number[:2]
#             district = int(license_plate_number[2:4])
#             series_char = license_plate_number[4:6]
#             series_num = license_plate_number[6:]
#             # Fetch vehicle details from the database
#             vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
#             if not vehicle_details.empty:
#                 # Check insurance and PUC expiration dates
#                 today = datetime.now().date()
#                 vehicle_details['Insurance_Expired'] = vehicle_details['ins_valid_to'] < today
#                 vehicle_details['PUC_Expired'] = vehicle_details['puc_valid_to'] < today
#                 st.write("Details:")
#                 st.write(vehicle_details)
#             else:
#                 st.write("No details found for the provided license plate number.")

# if __name__ == "__main__":
#     main()


# import pandas as pd
# from datetime import datetime
# import tempfile
# import cv2
# import time
# from utils import process_video

# def main():
#     print("Automated Road Compliance and Enforcement System")
    
#     mode = input("Select Mode (Upload Video / Real-Time Video): ").strip().lower()

#     if mode == "upload video":
#         video_path = input("Enter the path to the video file: ").strip()
#         if video_path:
#             print('Processing video...')
#             results_csv = process_video(video_path)
#             print("License plate details extracted successfully!")
#             print("Results saved to:", results_csv)
#             display_vehicle_details(results_csv)
#     elif mode == "real-time video":
#         record = input('Press Enter to start recording (Recording will stop automatically after 20 seconds): ').strip()
#         if record == '':
#             print("Recording...")
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
#                 record_video(temp_video.name, 20)
#                 print('Processing video...')
#                 results_csv = process_video(temp_video)
#                 print("License plate details extracted successfully!")
#                 print("Results saved to:", results_csv)
#                 display_vehicle_details(results_csv)
#     else:
#         print("Invalid mode selected. Please choose either 'Upload Video' or 'Real-Time Video'.")

# def display_vehicle_details(results_csv):
#     print("Vehicle Details:")
#     df = pd.read_csv(results_csv)
#     for car_id, group in df.groupby('car_id'):
#         max_score_row = group.loc[group['license_number_score'].idxmax()]
#         license_plate_number = max_score_row['license_number']
#         print(f"License Plate Number: {license_plate_number}")
#         state = license_plate_number[:2]
#         district = int(license_plate_number[2:4])
#         series_char = license_plate_number[4:6]
#         series_num = license_plate_number[6:]
#         # vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
#         # if not vehicle_details.empty:
#         if (0):  # Simulate vehicle details fetch
#             today = datetime.now().date()
#             has_fine = False
#             for index, row in vehicle_details.iterrows():
#                 ins_expired = row['ins_valid_to'] < today
#                 puc_expired = row['puc_valid_to'] < today
#                 if ins_expired or puc_expired:
#                     has_fine = True
#                     account_sid = 'ACd30e800c1d0ebdd2f6dcf9c4955f0f5c'
#                     auth_token = 'cec3b83b492d527a4bfbdd23cdb6d689'
#                     client = Client(account_sid, auth_token)
#                     to_number_with_country_code = "+91" + str(row['owner_mob_no'])
#                     message = client.messages.create(
#                         from_='+12232671810',
#                         body='Fine For Not Having Active Insurance or PUC',
#                         to=to_number_with_country_code
#                     )
#                     break
#             if has_fine:
#                 print("Fine For Not Having Active Insurance or PUC")
#             else:
#                 print("No fine detected for this vehicle.")
#         else:
#             print("No details found for the provided license plate number.")

# def record_video(output_path, duration):
#     cap = cv2.VideoCapture(0)
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    
#     start_time = time.time()
#     while int(time.time() - start_time) < duration:
#         ret, frame = cap.read()
#         if ret:
#             out.write(frame)
#         else:
#             break
#     cap.release()
#     out.release()

# if __name__ == "__main__":
#     main()


import pandas as pd
from datetime import datetime
import tempfile
import cv2
import time
from utils import process_video
import requests

import pandas as pd
from datetime import datetime
import tempfile
import cv2
import time
from utils import process_video  # Assuming you have a utils module with this function
import requests
import pandas as pd
from datetime import datetime
import tempfile
import cv2
import time
from utils import process_video  # Assuming you have a utils module with this function
import requests
def get_vehicle_info(registration_number):
    url = "https://rto-vehicle-information-verification-india.p.rapidapi.com/api/v1/rc/vehicleinfo"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "02804354d9mshe9359843b45764fp1d91f2jsna8e8c77061d3",
        "X-RapidAPI-Host": "rto-vehicle-information-verification-india.p.rapidapi.com"
    }
    payload = {
        "reg_no": registration_number,
        "consent": "Y",
        "consent_text": "I hereby declare my consent agreement for fetching my information via AITAN Labs API"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        vehicle_info = response.json()['result']
        print("Vehicle Information:")
        print(f"Owner Name: {vehicle_info['owner_name']}")
        print(f"Mobile Number: {vehicle_info.get('mobile_no', 'N/A')}")
        
        # Handle vehicle_pucc_details separately
        vehicle_pucc_details = vehicle_info.get('vehicle_pucc_details')
        if vehicle_pucc_details:
            print(f"PUCC From: {vehicle_pucc_details.get('pucc_from', 'N/A')}")
            print(f"PUCC Upto: {vehicle_pucc_details.get('pucc_upto', 'N/A')}")
            print(f"PUCC Number: {vehicle_pucc_details.get('pucc_no', 'N/A')}")
        else:
            print("PUCC Details: N/A")
        
        print(f"Insurance From: {vehicle_info.get('vehicle_insurance_details', {}).get('insurance_from', 'N/A')}")
        print(f"Insurance Upto: {vehicle_info.get('vehicle_insurance_details', {}).get('insurance_upto', 'N/A')}")
        return vehicle_info
    else:
        print("Failed to retrieve vehicle information.")
        return None

# Define registration number
registration_number = "MH12RK6291"

# Display vehicle details
get_vehicle_info(registration_number)

def main():
    print("Automated Road Compliance and Enforcement System")
    
    mode = input("Select Mode (Upload Video (1)/ Real-Time Video(0)): ").strip().lower()

    if mode == "1":
        video_path = input("Enter the path to the video file: ").strip()
        if video_path:
            print('Processing video...')
            results_csv, output_video_path, unique_license_numbers = process_video(video_path)
            print("License plate details extracted successfully!")
            print("Results saved to:", results_csv)
            for license_plate_number in unique_license_numbers:
                get_vehicle_info(license_plate_number)
                print("\n")
                print("\n")
            # display_vehicle_details(results_csv)
    elif mode == "0":
        record = input('Press Enter to start recording (Recording will stop automatically after 20 seconds): ').strip()
        if record == '':
            print("Recording...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                record_video(temp_video.name, 20)
                print('Processing video...')
                results_csv, output_video_path, unique_license_numbers = process_video(temp_video.name)

                print("License plate details extracted successfully!")
                print("Results saved to:", results_csv)
                for license_plate_number in unique_license_numbers:
                    print(unique_license_numbers)
                    print("\n")
                    get_vehicle_info(license_plate_number)
                    print("\n")
                    print("\n")
                # display_vehicle_details(results_csv)
    else:
        print("Invalid mode selected. Please choose either 'Upload Video' or 'Real-Time Video'.")


def display_vehicle_details(results_paths):
    csv_path, video_path = results_paths
    df = pd.read_csv(csv_path)
    print("Vehicle Details:")
    print(df.head())
    print("Video saved to:", video_path)

def record_video(output_path, duration):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break
    cap.release()
    out.release()

if __name__ == "__main__":
    main()