guide used: 
- https://core-electronics.com.au/guides/raspberry-pi/face-recognition-with-raspberry-pi-and-opencv/
- https://core-electronics.com.au/guides/face-identify-raspberry-pi/

# personal notes
1. set up venv and install opencv because we dont use picamera,, need to use another library compared to the guides
```
python3 -m venv myenv
source myenv/bin/activate
pip install opencv-python
```
2.  other packages (will take awhile)
```
pip install imutils
sudo apt install cmake
pip install face-recognition
```
3. on Thonny, go to Run > Configure Interpreter,, find the venv python3. Should be home/user/myvenv/bin/python3
4. On image_capture.py, change PERSON_NAME to the person you wanna add into the dataset (around line 5)
```
PERSON_NAME = "lucas"
# this will create a new folder in /dataset under the name lucas
```
5. Run image_capture.py
	- Camera UI should come up
	- Press SPACE to take photo, Q to quit
	- Advised to take at least 10 photos,, but I think 5 is enough,, front, up, down, left, right angles
6. in facial_recognition_hardware.py, add authorised names to the list (around line 32)
```
authorized_names = ["claris", "lucas"]
# replace with names you wish to authorise,, case sensitive
```
7. run model_training.py. This will run the model training using all images in ../dataset
8. after done, run facial_recognition.py
	- the camera UI should come up
	- recognised face should be boxed with the identified name as per the set name in step 4
	- unrecognised people should be just boxed and "unrecognised"
