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
        "X-RapidAPI-Key": "56d0a4ae12mshe8145978a31952ap16f064jsn69aaa462c8bf",
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
    
    mode = input("Select Mode (Upload Video / Real-Time Video): ").strip().lower()

    if mode == "upload video":
        video_path = input("Enter the path to the video file: ").strip()
        if video_path:
            print('Processing video...')
            results_csv = process_video(video_path)
            print("License plate details extracted successfully!")
            print("Results saved to:", results_csv)
            display_vehicle_details(results_csv)
    elif mode == "real-time video":
        record = input('Press Enter to start recording (Recording will stop automatically after 20 seconds): ').strip()
        if record == '':
            print("Recording...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                record_video(temp_video.name, 20)
                print('Processing video...')
                results_csv = process_video(temp_video)
                print("License plate details extracted successfully!")
                print("Results saved to:", results_csv)
                display_vehicle_details(results_csv)
    else:
        print("Invalid mode selected. Please choose either 'Upload Video' or 'Real-Time Video'.")

def display_vehicle_details(results_csv):
    print("Vehicle Details:")
    df = pd.read_csv(results_csv)
    for car_id, group in df.groupby('car_id'):
        max_score_row = group.loc[group['license_number_score'].idxmax()]
        license_plate_number = max_score_row['license_number']
        print(f"License Plate Number: {license_plate_number}")
        print("hello")
        park=get_vehicle_info(license_plate_number)
        # print(park)
        state = license_plate_number[:2]
        district = int(license_plate_number[2:4])
        series_char = license_plate_number[4:6]
        series_num = license_plate_number[6:]
        # vehicle_details = fetch_vehicle_details(state, district, series_char, series_num)
        # if not vehicle_details.empty:
        if (0):  # Simulate vehicle details fetch
            today = datetime.now().date()
            has_fine = False
            for index, row in vehicle_details.iterrows():
                ins_expired = row['ins_valid_to'] < today
                puc_expired = row['puc_valid_to'] < today
                if ins_expired or puc_expired:
                    has_fine = True
                    account_sid = 'ACd30e800c1d0ebdd2f6dcf9c4955f0f5c'
                    auth_token = 'cec3b83b492d527a4bfbdd23cdb6d689'
                    client = Client(account_sid, auth_token)
                    to_number_with_country_code = "+91" + str(row['owner_mob_no'])
                    message = client.messages.create(
                        from_='+12232671810',
                        body='Fine For Not Having Active Insurance or PUC',
                        to=to_number_with_country_code
                    )
                    break
            if has_fine:
                print("Fine For Not Having Active Insurance or PUC")
            else:
                print("No fine detected for this vehicle.")
        else:
            print("No details found for the provided license plate number.")

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